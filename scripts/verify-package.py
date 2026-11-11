"""Verify a prepared, unpacked development bundle without importing its runtime."""
import hashlib
from pathlib import Path
import sys

root = Path(sys.argv[1]).resolve(strict=True)
expected = set()
for line in (root / "SHA256SUMS.txt").read_text(encoding="utf-8-sig").splitlines():
    checksum, name = line.split("  ", 1)
    path = root / name
    if not path.resolve(strict=True).is_relative_to(root) or path.is_symlink():
        raise SystemExit("Unsafe package path")
    if hashlib.sha256(path.read_bytes()).hexdigest() != checksum:
        raise SystemExit("Package checksum mismatch")
    expected.add(name)
for path in root.rglob("*"):
    if not path.is_file():
        continue
    relative = path.relative_to(root).as_posix()
    if relative != "SHA256SUMS.txt" and relative not in expected:
        raise SystemExit("Unexpected package file")
    if path.name in ("runtime.json", "auth.json", "state.hub") or any(p in (".dev", ".research", ".venv") for p in path.relative_to(root).parts):
        raise SystemExit("Private development file included")
print(f"Verified {len(expected)} files; no development state, auth or runtime config included")
