"""Prepare hash-locked POSIX candidate install bundles; never installs or publishes."""
import argparse
import datetime as dt
import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
import zipfile

REPO = Path(__file__).resolve().parents[1]


def build(target):
    if target not in ("linux-x64", "macos-arm64"):
        raise ValueError("Unsupported port bundle target")
    path = REPO / "scripts/package_payload.py"
    spec = importlib.util.spec_from_file_location("candidate_payload", path)
    payload = importlib.util.module_from_spec(spec)
    exec(compile(path.read_bytes(), str(path), "exec"), payload.__dict__)
    version = payload.release_config(REPO)
    if version["releaseReady"]:
        raise ValueError("Native POSIX acceptance is pending; prepare an explicit release candidate")
    name = "herdr-session-hub-" + version["version"] + "-" + target + "-" + dt.datetime.now(dt.timezone.utc).strftime("%Y%m%d%H%M%S")
    stage = REPO / "dist" / name
    count = payload.write_payload(REPO, stage, target)
    archive = stage.parent / (stage.name + ".zip")
    with zipfile.ZipFile(archive, "x", zipfile.ZIP_DEFLATED) as output:
        for path in sorted(stage.rglob("*")):
            if path.is_file():
                output.write(path, stage.name + "/" + path.relative_to(stage).as_posix())
    checksum = hashlib.sha256(archive.read_bytes()).hexdigest()
    Path(str(archive) + ".sha256").write_text(f"{checksum}  {archive.name}\n", encoding="utf-8")
    (REPO / ".dev").mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(dir=REPO / ".dev", prefix="port-package-") as scratch:
        with zipfile.ZipFile(archive) as source:
            source.extractall(scratch)
        if payload.policy(REPO).verify(Path(scratch) / stage.name) != count:
            raise ValueError("Fresh extraction verification failed")
    return dict(archive=str(archive), sha256=checksum, files=count, platform=target, releaseReady=False)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--target", required=True, choices=("linux-x64", "macos-arm64"))
    parser.add_argument("--allow-unverified", action="store_true")
    args = parser.parse_args()
    if not args.allow_unverified:
        parser.error("Native POSIX acceptance is pending; --allow-unverified is required for a local candidate")
    print(json.dumps(build(args.target), indent=2))
