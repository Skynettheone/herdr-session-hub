"""OS services for Hub-owned state only; never reads a provider credential store.

Windows DPAPI remains in hub.py. POSIX encryption uses PyCA AES-GCM with a
random key held by Keychain/Secret Service, with no plaintext-key fallback.
Interface references and native verification limits: docs/PORTABILITY_DESIGN.md.
"""
import base64
import contextlib
import ctypes
import hashlib
import os
from pathlib import Path
import secrets
import stat
import subprocess
import sys

SERVICE = b"dev.herdr.session-hub.local-state"
HEADER = b"HSH-POSIX1\x00"
CREDENTIAL_NAMES = {"auth.json", "credentials.json", "config.json", "settings.json", "config.toml", "tokens.json", ".env"}


def local_filesystem(path):
    """Fail closed on network/unknown mounts; query only the selected ancestor.

    Linux statfs.f_type and Darwin statfs64.f_flags follow their published C
    ABIs. An oversized output buffer avoids depending on trailing struct fields.
    """
    path = Path(path)
    while not path.exists() and path.parent != path:
        path = path.parent
    library = ctypes.CDLL(None, use_errno=True)
    if sys.platform == "linux":
        call = library.statfs
    elif sys.platform == "darwin":
        call = getattr(library, "statfs$INODE64", None) or getattr(library, "statfs64", None) or getattr(library, "statfs", None)
        if call is None:
            raise PlatformError("Native local-filesystem validation is unavailable")
    else:
        raise PlatformError("This operating system has no local-filesystem adapter")
    call.argtypes = [ctypes.c_char_p, ctypes.c_void_p]
    call.restype = ctypes.c_int
    buffer = ctypes.create_string_buffer(4096)
    if call(os.fsencode(path), buffer):
        raise PlatformError("Filesystem type could not be verified")
    if sys.platform == "linux":
        magic = ctypes.c_ulong.from_buffer(buffer).value & 0xffffffff
        # ext[234], btrfs, xfs, tmpfs, overlayfs, zfs, f2fs, ramfs.
        if magic not in {0xef53, 0x9123683e, 0x58465342, 0x01021994, 0x794c7630, 0x2fc12fc1, 0xf2f52010, 0x858458f6}:
            raise PlatformError("Network, shared-host or unverified filesystem refused")
    elif (not ctypes.c_uint32.from_buffer(buffer, 64).value & 0x1000  # Darwin MNT_LOCAL
          or buffer.raw[72:88].split(b"\x00", 1)[0] not in (b"apfs", b"hfs", b"tmpfs")):
        raise PlatformError("Network or unverified filesystem refused")


@contextlib.contextmanager
def sqlite_sources(path, validate):
    """Cooperative Unix SQLite locks, held through all bounded source reads.

    A WAL database without an existing SHM is refused: creating a source SHM
    would violate the read-only contract. No source SQLite connection is made.
    """
    import fcntl
    with contextlib.ExitStack() as stack:
        def opened(source):
            stream = stack.enter_context(os.fdopen(os.open(source, os.O_RDONLY | os.O_NOFOLLOW), "rb"))
            info = os.fstat(stream.fileno())
            if not stat.S_ISREG(info.st_mode) or info.st_nlink != 1:
                raise PlatformError("Linked or non-regular database source refused")
            return stream
        try:
            database = opened(path)
            # Shared locks across pending/reserved/shared bytes block cooperative
            # rollback writers and checkpoints, without writing any source byte.
            fcntl.lockf(database.fileno(), fcntl.LOCK_SH | fcntl.LOCK_NB, 514, 0x40000000, os.SEEK_SET)
            header = database.read(100)
            database.seek(0)
            wal = path.with_name(path.name + "-wal")
            shared = None
            if wal.exists() or header[18:20] == b"\x02\x02":
                shared_path = validate(path.with_name(path.name + "-shm"))
                shared = opened(shared_path)
                # SQLite's Unix deadman-switch lock prevents its last connection
                # unlinking/resetting this SHM generation while we hold a reader.
                fcntl.lockf(shared.fileno(), fcntl.LOCK_SH | fcntl.LOCK_NB, 1, 128, os.SEEK_SET)
                fcntl.lockf(shared.fileno(), fcntl.LOCK_SH | fcntl.LOCK_NB, 3, 120, os.SEEK_SET)
            journal = opened(validate(wal)) if wal.exists() else None
            yield database, journal
            if shared is not None:
                current = shared_path.stat()
                held = os.fstat(shared.fileno())
                if (current.st_dev, current.st_ino) != (held.st_dev, held.st_ino):
                    raise PlatformError("Database lock source was replaced during read")
        except OSError:
            raise PlatformError("Database is writing or its read-only lock files are unavailable; retry when quiescent") from None


def native_executable(path):
    # A PATH alias can resolve to a credential-named file. Refuse before even
    # reading a binary header, consistently with the history/source boundary.
    if path.name.casefold() in CREDENTIAL_NAMES or not path.is_file() or not os.access(path, os.X_OK):
        return False
    with path.open("rb") as stream:
        magic = stream.read(4)
    return magic in {b"\x7fELF", b"\xcf\xfa\xed\xfe", b"\xfe\xed\xfa\xcf", b"\xca\xfe\xba\xbe", b"\xca\xfe\xba\xbf"}


def process_owned(provider, executable=None):
    """Names only. Every Node instance conservatively blocks a Node provider."""
    names = {provider, Path(executable).name if executable else provider}
    if provider in ("pi", "gemini") or executable and Path(executable).name in ("node", "nodejs"):
        names.update(("node", "nodejs"))
    try:
        result = subprocess.run(["/bin/ps", "-A", "-o", "pid=,comm="], stdin=subprocess.DEVNULL,
                                capture_output=True, timeout=6, shell=False)
        if result.returncode or len(result.stdout) > 1024 * 1024:
            return None
        lines = result.stdout.decode("utf-8", "strict").splitlines()
        if not lines or len(lines) > 20000:
            return None
        for line in lines:
            pid, name = line.strip().split(maxsplit=1)
            if not pid.isdigit() or not name:
                return None
            if int(pid) != os.getpid() and Path(name).name in names:
                return True
        return False
    except (OSError, ValueError, UnicodeError, subprocess.TimeoutExpired):
        return None


class PlatformError(ValueError):
    """Fixed messages only; key-store errors and key material are never logged."""


def lock_file(stream, unlock=False):
    stream.seek(0)
    if os.name == "nt":
        import msvcrt
        msvcrt.locking(stream.fileno(), msvcrt.LK_UNLCK if unlock else msvcrt.LK_NBLCK, 1)
    else:
        import fcntl
        fcntl.flock(stream.fileno(), fcntl.LOCK_UN if unlock else fcntl.LOCK_EX | fcntl.LOCK_NB)


def private_directory(root):
    root.mkdir(parents=True, exist_ok=True, mode=0o700)
    if os.name != "nt":
        info = root.lstat()
        if not stat.S_ISDIR(info.st_mode) or info.st_uid != os.getuid() or info.st_mode & 0o077:
            raise PlatformError("Hub state needs an owned private directory (mode 0700); no permissions were changed")


def account(root):
    return hashlib.sha256(os.fsencode(str(Path(root).resolve()))).hexdigest().encode("ascii")


def mac_key(identity, create=False):
    # Exact documented C APIs; no shell, key argv, provider item or keychain dump.
    security = ctypes.CDLL("/System/Library/Frameworks/Security.framework/Security")
    security.SecKeychainSetUserInteractionAllowed.argtypes = [ctypes.c_bool]
    security.SecKeychainSetUserInteractionAllowed.restype = ctypes.c_int32
    security.SecKeychainFindGenericPassword.argtypes = [ctypes.c_void_p, ctypes.c_uint32, ctypes.c_char_p,
        ctypes.c_uint32, ctypes.c_char_p, ctypes.POINTER(ctypes.c_uint32), ctypes.POINTER(ctypes.c_void_p), ctypes.c_void_p]
    security.SecKeychainFindGenericPassword.restype = ctypes.c_int32
    security.SecKeychainItemFreeContent.argtypes = [ctypes.c_void_p, ctypes.c_void_p]
    security.SecKeychainItemFreeContent.restype = ctypes.c_int32
    security.SecKeychainAddGenericPassword.argtypes = [ctypes.c_void_p, ctypes.c_uint32, ctypes.c_char_p,
        ctypes.c_uint32, ctypes.c_char_p, ctypes.c_uint32, ctypes.c_void_p, ctypes.c_void_p]
    security.SecKeychainAddGenericPassword.restype = ctypes.c_int32
    if security.SecKeychainSetUserInteractionAllowed(False):
        raise PlatformError("Keychain is unavailable; unlock it in macOS before opening Hub")
    length, pointer = ctypes.c_uint32(), ctypes.c_void_p()
    status = security.SecKeychainFindGenericPassword(None, len(SERVICE), SERVICE, len(identity), identity,
                                                    ctypes.byref(length), ctypes.byref(pointer), None)
    if status == 0:
        try:
            if length.value != 32:
                raise PlatformError("Hub Keychain item is invalid; preserve state and recover the original key")
            return ctypes.string_at(pointer, length.value)
        finally:
            security.SecKeychainItemFreeContent(None, pointer)
    if status != -25300 or not create:  # errSecItemNotFound; never replace a missing decryption key.
        raise PlatformError("Hub Keychain key is missing or locked; preserve state and unlock the original keychain")
    key = secrets.token_bytes(32)
    buffer = (ctypes.c_ubyte * len(key)).from_buffer_copy(key)
    if security.SecKeychainAddGenericPassword(None, len(SERVICE), SERVICE, len(identity), identity, len(key), buffer, None):
        raise PlatformError("Could not create the Hub Keychain item; no unencrypted state was saved")
    if mac_key(identity) != key:
        raise PlatformError("Hub Keychain creation could not be verified; no state was saved")
    return key


def linux_key(identity, create=False):
    tool = Path("/usr/bin/secret-tool")
    if not tool.is_file():
        raise PlatformError("Linux needs secret-tool and an unlocked desktop Secret Service; no plaintext fallback")
    attributes = ["application", SERVICE.decode(), "scope", identity.decode()]
    try:
        found = subprocess.run([str(tool), "lookup", *attributes], stdin=subprocess.DEVNULL,
                               stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, timeout=8, shell=False)
        if found.returncode == 0:
            encoded = found.stdout.strip()
            if len(encoded) > 64:
                raise ValueError("Invalid key length")
            key = base64.b64decode(encoded, validate=True)
            if len(key) != 32:
                raise ValueError("Invalid key length")
            return key
        if found.returncode != 1 or not create:
            raise PlatformError("Hub Secret Service key is missing or locked; preserve state and unlock the original keyring")
        key = secrets.token_bytes(32)
        saved = subprocess.run([str(tool), "store", "--label=Herdr Session Hub local state", *attributes],
                               input=base64.b64encode(key), stdout=subprocess.DEVNULL,
                               stderr=subprocess.DEVNULL, timeout=8, shell=False)
        if saved.returncode or linux_key(identity) != key:
            raise PlatformError("Could not create the Hub Secret Service key; no unencrypted state was saved")
        return key
    except PlatformError:
        raise
    except (OSError, subprocess.TimeoutExpired, ValueError):
        raise PlatformError("Hub Secret Service is unavailable or invalid; unlock the desktop keyring and retry") from None


def state_key(root, create=False):
    if sys.platform == "darwin":
        return mac_key(account(root), create)
    if sys.platform == "linux":
        return linux_key(account(root), create)
    raise PlatformError("This operating system has no verified state encryption adapter")


def protect(data, root, decrypt=False):
    from cryptography.exceptions import InvalidTag
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM
    if root is None:
        raise PlatformError("POSIX encrypted state requires its explicit Hub directory")
    try:
        new = not (Path(root) / "state.hub").exists() and not (Path(root) / "state.hub.bak").exists()
        key = state_key(root, create=not decrypt and new)
        aad = HEADER + account(root)
        if decrypt:
            if not data.startswith(HEADER) or len(data) < len(HEADER) + 28:
                raise ValueError("Unsupported encrypted state")
            nonce = data[len(HEADER):len(HEADER) + 12]
            return AESGCM(key).decrypt(nonce, data[len(HEADER) + 12:], aad)
        nonce = secrets.token_bytes(12)
        return HEADER + nonce + AESGCM(key).encrypt(nonce, data, aad)
    except PlatformError:
        raise
    except (InvalidTag, ValueError):
        raise PlatformError("Encrypted state could not be opened; preserve state and its original keyring key") from None
