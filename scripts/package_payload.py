"""Explicit install payload shared by platform builders; source-only build tool."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import shutil


def policy(repo):
    path = repo / "scripts/verify-package.py"
    spec = importlib.util.spec_from_file_location("install_payload_policy", path)
    module = importlib.util.module_from_spec(spec)
    exec(compile(path.read_bytes(), str(path), "exec"), module.__dict__)
    return module


def release_config(repo):
    config = json.loads((repo / "version.json").read_text(encoding="utf-8"))
    version = config.get("version", "")
    if not isinstance(version, str) or not re.fullmatch(r"[0-9]+\.[0-9]+\.[0-9]+(?:-(?:dev|rc\.[1-9][0-9]*))?", version):
        raise ValueError("Use an explicit stable, development or release-candidate version")
    if type(config.get("releaseReady")) is not bool or config["releaseReady"] != ("-" not in version):
        raise ValueError("Stable versions require recorded release readiness; unverified builds require a candidate suffix")
    return config


def write_payload(repo, stage, target):
    repo, stage = Path(repo).resolve(strict=True), Path(stage).absolute()
    rules = policy(repo)
    required = rules.target_files(target)
    config = release_config(repo)
    if target != "windows-x64" and config["releaseReady"]:
        raise ValueError("Native POSIX desktop acceptance is pending; prepare a candidate bundle")
    if stage.resolve().parent != (repo / "dist").resolve() or stage.exists():
        raise ValueError("Choose a fresh payload directory directly below dist")
    locked = set(re.findall(r"--hash=sha256:([0-9a-f]{64})", (repo / rules.LOCKFILES[target]).read_text()))
    inputs = {}
    for relative in sorted(required):
        if relative.startswith("wheelhouse/"):
            directory = repo / ".research/wheels" if target == "windows-x64" else repo / ".research/ports/wheels" / target
            source = directory / Path(relative).name
        else:
            source = repo / relative
        if source.is_symlink() or not source.resolve(strict=True).is_relative_to(repo) or source.stat().st_nlink != 1:
            raise ValueError("Linked or external build input refused")
        if relative.startswith("wheelhouse/") and hashlib.sha256(source.read_bytes()).hexdigest() not in locked:
            raise ValueError("Target wheel does not match the pinned lockfile")
        inputs[relative] = source
    stage.mkdir(parents=True)
    for relative, source in inputs.items():
        destination = stage / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, destination)
    config.update(platform=target, payload="install")
    if target != "windows-x64":
        config["nativeContinuationVerified"] = False
    (stage / "version.json").write_text(json.dumps(config, indent=2) + "\n", encoding="utf-8")
    manifest = stage / "SHA256SUMS.txt"
    manifest.write_text("".join(f"{hashlib.sha256((stage / name).read_bytes()).hexdigest()}  {name}\n" for name in sorted(required)), encoding="utf-8")
    return rules.verify(stage)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stage", required=True)
    parser.add_argument("--target", required=True, choices=("windows-x64", "linux-x64", "macos-arm64"))
    args = parser.parse_args()
    count = write_payload(Path(__file__).resolve().parents[1], Path(args.stage), args.target)
    print(f"Prepared {count} allowlisted install files")
