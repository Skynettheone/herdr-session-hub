"""Bounded package integrity check. Hashes do not authenticate a publisher."""
import hashlib
import os
from pathlib import Path, PurePosixPath
import re
import stat
import sys

REQUIRED = frozenset({
    "LICENSE", "version.json", "requirements-windows.lock", "README.md", "SECURITY.md",
    "scripts/install.ps1", "scripts/uninstall.ps1", "scripts/check-native.ps1", "scripts/verify-package.py",
    *("mods/session-hub/" + name for name in ("main.js", "model.js", "ui.js", "usage.js", "tabs.js", "mod.json")),
    "mods/session-hub/helper/hub.py", "mods/session-hub/assets/HERDR-LICENSE.txt", "mods/session-hub/assets/herdr-logo.svg",
    *("mods/session-hub/helper/adapters/" + name + ".py" for name in
      ("__init__", "common", "claude", "codex", "pi", "gemini", "copilot", "sqlite_snapshot", "usage", "platform_io")),
    *("mods/session-hub/icons/" + name + ".svg" for name in
      ("alert", "archive", "back", "chevron-down", "chevron-right", "close", "copy", "export", "folder",
       "forward", "history", "lock", "more", "plus", "profiles", "refresh", "search", "settings", "sidebar", "sort")),
    *("wheelhouse/" + name for name in ("cryptography-50.0.2-cp311-abi3-win_amd64.whl",
      "cffi-2.1.1-cp314-cp314-win_amd64.whl", "pycparser-3.12-py3-none-any.whl")),
})
PRIVATE = frozenset({"runtime.json", "auth.json", "state.hub", ".dev", ".research", ".venv", "__pycache__"})
MAX_FILES, MAX_BYTES = 4096, 256 * 1024 * 1024


def regular(path, directory=False):
    info = path.lstat()
    if (info.st_file_attributes & stat.FILE_ATTRIBUTE_REPARSE_POINT if hasattr(info, "st_file_attributes") else path.is_symlink()):
        raise ValueError("Linked package path refused")
    if not (stat.S_ISDIR(info.st_mode) if directory else stat.S_ISREG(info.st_mode)):
        raise ValueError("Non-regular package path refused")
    if not directory and info.st_nlink != 1:
        raise ValueError("Hard-linked package file refused")
    return info


def verify(root):
    root = Path(os.path.abspath(root))
    for folder in (root, *root.parents):
        regular(folder, directory=True)
    manifest = root / "SHA256SUMS.txt"
    if regular(manifest).st_size > 1024 * 1024:
        raise ValueError("Oversized package manifest")
    expected, folded = {}, set()
    for line in manifest.read_text(encoding="utf-8-sig").splitlines():
        match = re.fullmatch(r"([0-9a-f]{64})  (.+)", line)
        if not match:
            raise ValueError("Invalid package manifest")
        checksum, name = match.groups()
        parts = PurePosixPath(name).parts
        if (not parts or PurePosixPath(name).is_absolute() or any(p in (".", "..") or p.endswith((".", " ")) for p in parts)
                or ":" in name or "\\" in name or "/".join(parts) != name or name == "SHA256SUMS.txt"):
            raise ValueError("Unsafe package path")
        if name.casefold() in folded:
            raise ValueError("Duplicate package manifest entry")
        folded.add(name.casefold())
        expected[name] = checksum
        if len(expected) > MAX_FILES:
            raise ValueError("Package file budget exceeded")
    if not REQUIRED.issubset(expected):
        raise ValueError("Incomplete package; required runtime, installer or wheel missing")
    actual, total = set(), 0
    for folder, directories, files in os.walk(root, followlinks=False):
        for name in directories:
            regular(Path(folder) / name, directory=True)
            if name.casefold() in PRIVATE:
                raise ValueError("Private development directory included")
        for name in files:
            path = Path(folder) / name
            info = regular(path)
            relative = path.relative_to(root).as_posix()
            if name.casefold() in PRIVATE or name.endswith((".pyc", ".hub", ".hsh")):
                raise ValueError("Private development file included")
            if relative == "SHA256SUMS.txt":
                continue
            total += info.st_size
            if total > MAX_BYTES or len(actual) >= MAX_FILES:
                raise ValueError("Package size budget exceeded")
            if relative not in expected:
                raise ValueError("Unexpected package file")
            digest = hashlib.sha256()
            with path.open("rb") as stream:
                while chunk := stream.read(1024 * 1024):
                    digest.update(chunk)
            if digest.hexdigest() != expected[relative]:
                raise ValueError("Package checksum mismatch")
            actual.add(relative)
    if actual != expected.keys():
        raise ValueError("Package file missing")
    return len(actual)


if __name__ == "__main__":
    try:
        count = verify(sys.argv[1])
    except (OSError, ValueError, IndexError):
        raise SystemExit("Package verification failed: damaged, incomplete or unsafe bundle") from None
    print(f"Verified {count} files; no development state, auth or runtime config included")
