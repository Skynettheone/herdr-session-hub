"""Manual Gemini native-session acceptance against the loopback fixture."""
import argparse
import importlib.util
import json
from pathlib import Path
import subprocess

REPO = Path(__file__).resolve().parents[1]
LAB = REPO / ".dev/native-lab"
spec = importlib.util.spec_from_file_location("hub", REPO / "mods/session-hub/helper/hub.py")
hub = importlib.util.module_from_spec(spec)
spec.loader.exec_module(hub)
HOME = LAB / "gemini"
CONFIG = HOME / ".gemini"
PROJECT = LAB / "projects/Gemini café continuity"


def environment():
    env = hub.profile_environment({"GEMINI_CLI_HOME": str(HOME)})
    for name in ("HOME", "USERPROFILE", "APPDATA", "LOCALAPPDATA", "XDG_CONFIG_HOME", "XDG_DATA_HOME", "XDG_STATE_HOME", "XDG_CACHE_HOME"):
        env[name] = str(LAB / "environment" / name)
    return env


def prepare():
    if CONFIG.exists():
        raise RuntimeError("Refusing to overwrite an existing Gemini test home")
    CONFIG.mkdir(parents=True)
    PROJECT.mkdir(parents=True)
    settings = {"security": {"auth": {"selectedType": "gemini-api-key"}},
                "telemetry": {"enabled": False}, "model": {"name": "gemini-2.5-flash"},
                "general": {"disableAutoUpdate": True}, "advanced": {"autoConfigureMemory": False}}
    (CONFIG / "settings.json").write_text(json.dumps(settings), encoding="utf-8")
    url = json.loads((LAB / "server.json").read_text(encoding="utf-8"))["url"]
    # All values are deliberately synthetic. Only the native CLI reads this file.
    (PROJECT / ".env").write_text("GEMINI_API_KEY=local-test-not-a-secret\nGOOGLE_GEMINI_BASE_URL=" + url + "\n", encoding="utf-8")
    print("Prepared isolated Gemini config/project and synthetic loopback routing")


def run(action):
    found = hub.probe()["providers"]["gemini"]
    args = [found["executable"], found["launchScript"], "-m", "gemini-2.5-flash", "-o", "json", "--skip-trust"]
    if action == "resume":
        paths = sorted((CONFIG / "tmp").glob("*/chats/session-2026-*"))
        if not paths:
            raise RuntimeError("Create the native Gemini fixture session first")
        header = json.loads(paths[0].read_text(encoding="utf-8").splitlines()[0])
        args += ["--resume", header["sessionId"], "-p", "VERIFY_CONTEXT"]
    else:
        args += ["-p", "Create a synthetic local continuity test. Do not use tools."]
    result = subprocess.run(args, env=environment(), cwd=PROJECT, capture_output=True, timeout=90)
    (LAB / ("gemini-" + action + ".txt")).write_bytes(result.stdout + result.stderr)
    print(json.dumps({"exitCode": result.returncode, "contextObserved": b"CONTINUITY_OK" in result.stdout,
                      "nonceObserved": b"HUB_NATIVE_CONTEXT_7e251cf4" in result.stdout}))
    if result.returncode:
        print(result.stderr.decode("utf-8", "replace")[-2500:])


def audit_duplicates():
    found = hub.probe()["providers"]["gemini"]
    profile = {"id":"gemini-duplicates","provider":"gemini","roots":[str(CONFIG / "tmp")],
               "configHome":str(CONFIG),"projectPath":str(PROJECT),"executable":found["executable"],"launchScript":found["launchScript"]}
    with hub.Store(LAB / "gemini-duplicates-state") as store:
        hub.rpc(store,{"action":"profile-save","profile":profile})
        hub.rpc(store,{"action":"verify-version","profile":profile["id"]})
        hub.refresh(store)
        rows = store.get("records")
        refused = []
        for row in rows:
            try:
                hub.resume_spec(store,row["key"],profile["id"])
                refused.append(False)
            except hub.HubError as error:
                refused.append("ambiguous" in str(error))
        evidence = {"nativeSnapshots":len(rows),"duplicateGuard":len(rows)>1 and all(refused)}
    (LAB / "gemini-duplicate-evidence.json").write_text(json.dumps(evidence),encoding="utf-8")
    print(json.dumps(evidence))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=("prepare", "create", "resume", "audit-duplicates"))
    action = parser.parse_args().action
    if action == "prepare":
        prepare()
    elif action == "audit-duplicates":
        audit_duplicates()
    else:
        run(action)
