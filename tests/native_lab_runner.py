"""Launch only an explicitly selected disposable native-lab session in hc."""
import argparse
import importlib.util
from pathlib import Path
import subprocess
import sys

repo = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("hub", repo / "mods/session-hub/helper/hub.py")
hub = importlib.util.module_from_spec(spec)
spec.loader.exec_module(hub)
parser = argparse.ArgumentParser()
parser.add_argument("provider", choices=("claude", "codex", "pi", "opencode"))
args = parser.parse_args()
base = repo / ".dev/native-lab"
with hub.Store(base / "hub-state") as store:
    hub.refresh(store)
    record = next(row for row in store.get("records") if row["provider"] == args.provider and not row.get("stale"))
    profile = next(p for p in store.get("profiles") if p["id"] == args.provider)
    # Use the actual product guard; no testing bypass or injected probe.
    launch = hub.resume_spec(store, record["key"], profile["id"])
    command = launch["argv"]
env = hub.profile_environment(profile["env"])
for name in ("HOME", "USERPROFILE", "APPDATA", "LOCALAPPDATA", "XDG_CONFIG_HOME", "XDG_DATA_HOME", "XDG_STATE_HOME", "XDG_CACHE_HOME"):
    env[name] = str(base / "environment" / name)
env["OPENCODE_DISABLE_AUTOUPDATE"] = "1"
env["OPENCODE_DISABLE_MODELS_FETCH"] = "1"
env["PI_OFFLINE"] = "1"
sys.exit(subprocess.call(command, cwd=record["cwd"], env=env, shell=False))
