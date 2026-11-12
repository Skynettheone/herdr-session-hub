"""Explicit offline macOS/Linux installer. No production target is implicit.

Use a verified platform bundle, CPython 3.14 and installed Herdr. Experimental
ports retain their continuation guard until native acceptance is recorded.
"""
import argparse
import importlib.util
import json
import os
from pathlib import Path
import platform
import shutil
import subprocess
import sys
import uuid

REPO = Path(__file__).resolve().parents[1]


def no_links(path):
    for item in (path, *path.parents):
        if item.is_symlink():
            raise ValueError("Linked installation path refused")


def target():
    pair = (sys.platform, platform.machine().lower())
    if pair in (("linux", "x86_64"), ("linux", "amd64")):
        return "linux-x64"
    if pair in (("darwin", "arm64"), ("darwin", "aarch64")):
        return "macos-arm64"
    raise ValueError("This port currently requires Linux x64 or Apple Silicon macOS; other architectures remain unavailable")


def verifier():
    path = REPO / "scripts/verify-package.py"
    spec = importlib.util.spec_from_file_location("session_hub_package", path)
    module = importlib.util.module_from_spec(spec)
    # Execute only this fixed shipped module without writing __pycache__ into
    # the verified source bundle, even when the caller omitted Python's -B flag.
    exec(compile(path.read_bytes(), str(path), "exec"), module.__dict__)
    return module


def app_home(value, production=False):
    home = Path(value).expanduser()
    if not home.is_absolute() or home == Path(home.anchor):
        raise ValueError("Choose an absolute app home")
    no_links(home)
    home = Path(os.path.abspath(home))
    if not production and not home.is_relative_to(REPO.parent / ".dev"):
        raise ValueError("Without --install-production choose a disposable app home below the bundle parent's .dev directory")
    return home


def run(argv, **options):
    result = subprocess.run([str(item) for item in argv], stdin=subprocess.DEVNULL,
                            capture_output=True, timeout=180, shell=False, **options)
    if result.returncode:
        raise ValueError("Installation check failed; previous mod/runtime retained. Verify Python, offline wheels and Herdr compatibility")


def record(path, value):
    temporary = path.with_name(path.name + "." + uuid.uuid4().hex + ".tmp")
    try:
        with os.fdopen(os.open(temporary, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600), "w", encoding="utf-8") as stream:
            json.dump(value, stream, indent=2)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
        descriptor = os.open(path.parent, os.O_RDONLY | os.O_DIRECTORY)
        try:
            os.fsync(descriptor)
        finally:
            os.close(descriptor)
    finally:
        temporary.unlink(missing_ok=True)


def install(home, herdr=None):
    import fcntl
    package = verifier()
    package.verify(REPO)  # Before any target writes or process execution.
    config = json.loads((REPO / "version.json").read_text())
    if config.get("platform") != target() or sys.version_info[:2] != (3, 14):
        raise ValueError("Bundle platform and CPython 3.14 must match this host")
    import re
    version = config.get("version", "")
    if not isinstance(version, str) or not re.fullmatch(r"[0-9]+\.[0-9]+\.[0-9]+(?:-[A-Za-z0-9.-]+)?", version):
        raise ValueError("Invalid package version")
    selected = herdr or shutil.which("herdr-app")
    if not selected or not Path(selected).is_file() or not os.access(selected, os.X_OK):
        raise ValueError("Install Herdr separately, then select its executable with --herdr")
    selected = Path(selected).resolve(strict=True)
    transaction = home / "data/session-hub-install"
    no_links(transaction)
    transaction.mkdir(parents=True, exist_ok=True, mode=0o700)
    lockpath = transaction / "install.lock"
    no_links(lockpath)
    with os.fdopen(os.open(lockpath, os.O_RDWR | os.O_CREAT, 0o600), "a+b") as lock:
        try:
            fcntl.flock(lock.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            raise ValueError("Another installer is active; retry after it finishes") from None
        pending = transaction / "pending.json"
        no_links(pending)
        if pending.exists():
            raise ValueError("Interrupted installation receipt found; recover the recorded mod backup before retrying")
        token = version + "-" + uuid.uuid4().hex
        runtime = home / "data/session-hub-runtime" / token
        destination = home / "mods/session-hub"
        staging = home / "mods" / (".session-hub-stage-" + uuid.uuid4().hex)
        backups = home / "data/session-hub-mod-backups"
        state = home / "data/session-hub"
        for path in (runtime, destination, staging, backups, state):
            no_links(path)
        runtime.mkdir(parents=True, mode=0o700)
        state.mkdir(parents=True, exist_ok=True, mode=0o700)
        info = state.lstat()
        if info.st_uid != os.getuid() or info.st_mode & 0o077:
            raise ValueError("Hub state needs a private owned directory (0700); permissions were not changed")
        environment = dict(os.environ)
        environment.update(PIP_NO_INDEX="1", PIP_DISABLE_PIP_VERSION_CHECK="1", PYTHONDONTWRITEBYTECODE="1")
        run([sys.executable, "-I", "-m", "venv", runtime / "venv"], env=environment)
        python = runtime / "venv/bin/python"
        run([python, "-I", "-m", "pip", "install", "--no-index", "--find-links", REPO / "wheelhouse", "--require-hashes",
             "-r", REPO / package.LOCKFILES[target()]], env=environment)
        shutil.copytree(REPO / "mods/session-hub", staging)
        record(staging / "runtime.json", dict(schema=1, python=str(python), helper=str(destination / "helper/hub.py"),
                                             state=str(state), base=str(destination), herdr=str(selected)))
        scratch = runtime / "sdk-check"
        scratch.mkdir(mode=0o700)
        for name in ("HOME", "USERPROFILE", "APPDATA", "LOCALAPPDATA", "XDG_CONFIG_HOME", "XDG_DATA_HOME", "XDG_STATE_HOME", "XDG_CACHE_HOME"):
            environment[name] = str(scratch / name)
        environment.update(HERDR_APP_HOME=str(scratch), HC_SESSION="session-hub-posix-install-check", HERDR_TELEMETRY="0", DO_NOT_TRACK="1")
        run([selected, "check", staging], env=environment)
        backup = None
        if destination.exists():
            backups.mkdir(parents=True, exist_ok=True, mode=0o700)
            backup = backups / token
        record(pending, dict(schema=1, destination=str(destination), backup=str(backup) if backup else None,
                             staging=str(staging), runtime=str(runtime)))
        try:
            if backup:
                os.replace(destination, backup)
            os.replace(staging, destination)
        except OSError:
            if backup and not destination.exists() and backup.exists():
                os.replace(backup, destination)
            if not backup or destination.exists():
                pending.unlink()
            raise
        pending.unlink()
    print("Session Hub installed with place=none; existing layouts, settings and provider histories were not changed")


def uninstall(home, purge=False, dry_run=False):
    names = ["mods/session-hub"]
    if purge:
        names += ["data/session-hub", "data/session-hub-runtime", "data/session-hub-mod-backups", "data/session-hub-install"]
    for name in names:
        path = home / name
        no_links(path)
        if not path.is_relative_to(home):
            raise ValueError("Uninstall target escaped the selected home")
        if path.exists() and not dry_run:
            # Each literal target is verified inside the explicitly selected home.
            if path.is_dir():
                shutil.rmtree(path)
            else:
                path.unlink()
    print("Hub-only uninstall preview" if dry_run else "Hub-only uninstall complete; OS keyring items retained for encrypted-backup recovery")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("install", "uninstall"))
    parser.add_argument("--app-home", required=True)
    parser.add_argument("--install-production", action="store_true")
    parser.add_argument("--herdr")
    parser.add_argument("--purge-hub-data", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    try:
        target()
        home = app_home(args.app_home, args.install_production)
        if args.action == "install":
            if args.dry_run or args.purge_hub_data:
                raise ValueError("Install does not accept uninstall options")
            install(home, args.herdr)
        else:
            uninstall(home, args.purge_hub_data, args.dry_run)
    except ValueError as error:
        print(str(error), file=sys.stderr)
        return 1
    except (OSError, subprocess.SubprocessError):
        print("Operation refused or failed safely. Check platform, bundle integrity, paths and the local recovery instructions.", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
