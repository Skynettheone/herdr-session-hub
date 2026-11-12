"""OS services for Hub-owned state only; never reads a provider credential store.

Windows DPAPI remains in hub.py. POSIX encryption uses PyCA AES-GCM with a
random key held by Keychain/Secret Service, with no plaintext-key fallback.
Interface references and native verification limits: docs/PORTABILITY_DESIGN.md.
"""
import base64
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


class PlatformError(Exception):
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
    except (InvalidTag, ValueError):
        raise PlatformError("Encrypted state could not be opened; preserve state and its original keyring key") from None
