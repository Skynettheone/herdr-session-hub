"""Prepare hash-locked experimental POSIX bundles; never installs or publishes."""
import argparse
import datetime as dt
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import shutil
import tempfile
import zipfile

REPO = Path(__file__).resolve().parents[1]


def build(target):
    if target not in ("linux-x64", "macos-arm64"):
        raise ValueError("Unsupported port bundle target")
    spec = importlib.util.spec_from_file_location("port_package", REPO / "scripts/verify-package.py")
    package = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(package)
    version = json.loads((REPO / "version.json").read_text())
    if version.get("releaseReady") or not re.fullmatch(r"[0-9]+\.[0-9]+\.[0-9]+-dev", str(version.get("version", ""))):
        raise ValueError("POSIX bundles require an explicit development version until native acceptance passes")
    name = "herdr-session-hub-" + version["version"] + "-" + target + "-" + dt.datetime.now(dt.timezone.utc).strftime("%Y%m%d%H%M%S")
    stage = REPO / "dist" / name
    stage.mkdir(parents=True)
    for name in ("LICENSE", "README.md", "RECIPE.md", "SECURITY.md", "CONTRIBUTING.md", "CHANGELOG.md", "THIRD_PARTY_NOTICES.md", "version.json", "preview.png"):
        shutil.copyfile(REPO / name, stage / name)
    for lock in ("requirements-windows.lock", "requirements-linux-x64.lock", "requirements-macos-arm64.lock"):
        shutil.copyfile(REPO / lock, stage / lock)
    for folder in ("mods/session-hub", "scripts", "tests", "docs"):
        for source in (REPO / folder).rglob("*"):
            if not source.is_file() or source.name.endswith((".pyc", ".d.ts")) or source.name in ("runtime.json", "jsconfig.json") or "__pycache__" in source.parts:
                continue
            if source.is_symlink() or not source.resolve().is_relative_to(REPO) or source.stat().st_nlink != 1:
                raise ValueError("Linked build input refused")
            destination = stage / source.relative_to(REPO)
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source, destination)
    version.update(platform=target, releaseReady=False, nativeContinuationVerified=False)
    (stage / "version.json").write_text(json.dumps(version, indent=2) + "\n")
    wheelhouse = stage / "wheelhouse"
    wheelhouse.mkdir()
    locked = set(re.findall(r"--hash=sha256:([0-9a-f]{64})", (REPO / package.LOCKFILES[target]).read_text()))
    for filename in (*package.WHEELS[target], "pycparser-3.12-py3-none-any.whl"):
        source = REPO / ".research/ports/wheels" / target / filename
        if hashlib.sha256(source.read_bytes()).hexdigest() not in locked:
            raise ValueError("Offline wheel hash did not match the target lockfile")
        shutil.copyfile(source, wheelhouse / filename)
    manifest = stage / "SHA256SUMS.txt"
    manifest.write_text("".join(f"{hashlib.sha256(p.read_bytes()).hexdigest()}  {p.relative_to(stage).as_posix()}\n"
                               for p in sorted(stage.rglob("*")) if p.is_file() and p != manifest))
    count = package.verify(stage)
    archive = stage.parent / (stage.name + ".zip")
    with zipfile.ZipFile(archive, "x", zipfile.ZIP_DEFLATED) as output:
        for path in sorted(stage.rglob("*")):
            if path.is_file():
                output.write(path, stage.name + "/" + path.relative_to(stage).as_posix())
    checksum = hashlib.sha256(archive.read_bytes()).hexdigest()
    Path(str(archive) + ".sha256").write_text(f"{checksum}  {archive.name}\n")
    (REPO / ".dev").mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(dir=REPO / ".dev", prefix="port-package-") as scratch:
        with zipfile.ZipFile(archive) as source:
            source.extractall(scratch)
        if package.verify(Path(scratch) / stage.name) != count:
            raise ValueError("Fresh extraction verification failed")
    return dict(archive=str(archive), sha256=checksum, files=count, platform=target, releaseReady=False)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--target", required=True, choices=("linux-x64", "macos-arm64"))
    parser.add_argument("--allow-unverified", action="store_true")
    args = parser.parse_args()
    if not args.allow_unverified:
        parser.error("Native POSIX acceptance is pending; --allow-unverified is required for a development bundle")
    print(json.dumps(build(args.target), indent=2))
