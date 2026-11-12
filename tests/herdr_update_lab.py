"""Manual real-updater acceptance, confined to .dev/acceptance.

Requires checksum-verified official 0.1.14/0.1.15 archives under .research and
the loopback native_lab_server. Never invokes a production binary or installer.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

REPO = Path(__file__).resolve().parents[1]
BASE = REPO / ".dev/acceptance"
HOME = BASE / "app-home"
INSTALL = BASE / "install"
CORE = BASE / "core/hc.exe"
LAB = REPO / ".dev/native-lab"


def confined(path):
    resolved = path.resolve()
    if not resolved.is_relative_to(BASE.resolve()) or path.is_symlink():
        raise RuntimeError("Acceptance target is outside its disposable root")
    return resolved


def environment():
    env = dict(os.environ)
    for name in ("HOME", "USERPROFILE", "APPDATA", "LOCALAPPDATA", "XDG_CONFIG_HOME", "XDG_DATA_HOME", "XDG_STATE_HOME", "XDG_CACHE_HOME"):
        env[name] = str(LAB / "environment" / name)
    env.update(HERDR_APP_HOME=str(HOME), HC_SESSION="hub-native-acceptance", HERDR_TELEMETRY="0", DO_NOT_TRACK="1",
               HERDR_RELEASES_URL=json.loads((LAB / "server.json").read_text(encoding="utf-8"))["url"])
    return env


def app(*args):
    result = subprocess.run([str(INSTALL / "herdr-app.exe"), *args], env=environment(), cwd=BASE,
                            capture_output=True, timeout=15, check=True)
    return result.stdout.decode("utf-8", "replace")


def mirror(version):
    name = "herdr-0.1.14-manifest.json" if version == "0.1.14" else "herdr-latest.json"
    manifest = json.loads((REPO / ".research" / name).read_text(encoding="utf-8"))
    archive = REPO / ".research/herdr-binaries" / (version + ".tar.gz")
    target = manifest["targets"]["windows-x86_64"]
    if hashlib.sha256(archive.read_bytes()).hexdigest() != target["sha256"]:
        raise RuntimeError("Official archive checksum differs")
    site = LAB / "app";site.mkdir(exist_ok=True)
    shutil.copyfile(archive, site / (version + ".tar.gz"))
    target["url"] = environment()["HERDR_RELEASES_URL"] + "/app/" + version + ".tar.gz"
    (site / "latest.json").write_text(json.dumps(manifest), encoding="utf-8")
    core = LAB / "core";core.mkdir(exist_ok=True)
    (core / "latest.json").write_text(json.dumps({"version":"0.1.20","generation":1}), encoding="utf-8")


def stop_isolated_app():
    # window.close hides the Windows app in the tray; it does not release the
    # loaded executable. Scope process termination to the confined copied image.
    target = confined(INSTALL / "herdr-app.exe")
    env = environment()
    env["HUB_ACCEPTANCE_EXE"] = str(target)
    script = "Get-Process -Name herdr-app -ErrorAction SilentlyContinue | Where-Object { $_.Path -eq $env:HUB_ACCEPTANCE_EXE } | ForEach-Object { Stop-Process -Id $_.Id -Force -ErrorAction Stop }"
    subprocess.run(["pwsh.exe", "-NoProfile", "-NonInteractive", "-Command", script],
                   env=env, check=True, capture_output=True, timeout=15)


def prepare():
    for path in (HOME, INSTALL, BASE / "install.new", BASE / "install.old", BASE / "install.download", BASE / "backup-0.1.14", BASE / "preserved-0.1.15"):
        confined(path)
    if INSTALL.exists():
        raise RuntimeError("Acceptance install already exists; use a fresh test root")
    for name in ("install", "backup-0.1.14"):
        shutil.copytree(REPO / ".research/herdr-binaries/0.1.14/herdr-app", BASE / name)
    mod = HOME / "mods/session-hub"
    shutil.copytree(REPO / "mods/session-hub", mod, ignore=shutil.ignore_patterns("__pycache__", "*.d.ts", "runtime.json"))
    state = HOME / "data/session-hub"
    shutil.copytree(LAB / "hub-state", state)
    (mod / "runtime.json").write_text(json.dumps({"schema":1,"python":sys.executable,"helper":str(mod / "helper/hub.py"),"base":str(mod),"state":str(state),"herdr":str(INSTALL / "herdr-app.exe")}), encoding="utf-8")
    (HOME / "settings.json").write_text(json.dumps({"core":str(CORE),"telemetry":False}), encoding="utf-8")
    (HOME / "layouts").mkdir(exist_ok=True)
    sentinel = {"id":"preserved-layout","type":"block","content":{"mod":"session-hub"}}
    (HOME / "layouts/preserved-personal.json").write_text(json.dumps(sentinel), encoding="utf-8")
    mirror("0.1.14")
    print("Prepared real 0.1.14 installation and isolated core/home")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=("prepare", "start", "stage", "apply", "status", "rollback"))
    args = parser.parse_args()
    if args.action == "prepare":
        prepare()
    elif args.action == "start":
        process = subprocess.Popen([str(INSTALL / "herdr-app.exe")], env=environment(), cwd=BASE)
        print("Isolated app process", process.pid)
    elif args.action == "stage":
        mirror("0.1.15")
        print(app("do", "app.check_updates"))
    elif args.action == "apply":
        if not (BASE / "install.new/herdr-app.exe").is_file():
            raise RuntimeError("No verified staged update")
        print(app("do", "app.update"))
    elif args.action == "rollback":
        try:
            print(app("do", "window.close"))
        except subprocess.CalledProcessError:
            print("No responsive isolated window; stopping only the confined image")
        stop_isolated_app()
        # Allow Windows to release only this known install's executable handle.
        import time
        time.sleep(2)
        source, saved = confined(INSTALL), confined(BASE / "preserved-0.1.15")
        for attempt in range(15):
            try:
                source.rename(saved)
                break
            except PermissionError:
                if attempt == 14:
                    raise
                time.sleep(1)
        shutil.copytree(confined(BASE / "backup-0.1.14"), source)
        mirror("0.1.14")
        process = subprocess.Popen([str(source / "herdr-app.exe")], env=environment(), cwd=BASE)
        print("Restored actual 0.1.14 backup; isolated app process", process.pid)
    else:
        print(app("--version").strip())
        print(app("status"))
