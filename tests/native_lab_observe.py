"""Capture redacted acceptance evidence from the repository's isolated hc core."""
import argparse
import importlib.util
import json
import subprocess
import time

import herdr_update_lab as lab

parser = argparse.ArgumentParser()
parser.add_argument("provider", choices=("claude", "codex", "pi", "opencode"))
parser.add_argument("terminal")
args = parser.parse_args()
spec = importlib.util.spec_from_file_location("hub", lab.REPO / "mods/session-hub/helper/hub.py")
hub = importlib.util.module_from_spec(spec)
spec.loader.exec_module(hub)


def core(*argv):
    result = subprocess.run([str(lab.CORE), *argv], env=lab.environment(), capture_output=True, timeout=15, check=True)
    return json.loads(result.stdout)


with hub.Store(lab.HOME / "data/session-hub") as store:
    row = next(r for r in store.get("records") if r["provider"] == args.provider)
    profile = next(p for p in store.get("profiles") if p["id"] in row["targets"])
    terminal = core("get", args.terminal, "--json")
    if "Native acceptance workspace / Native " not in terminal.get("labels", {}).get("where", ""):
        raise SystemExit("Refusing a terminal outside the named disposable workspace")
    screen = core("read", args.terminal, "--json")
    active = (hub.codex_writer_owned(profile, row["nativeId"]) if args.provider == "codex"
              else hub.running_provider(args.provider, profile["executable"]))
    evidence = {"provider": args.provider, "nativeId": row["nativeId"],
                "cwdMatched": terminal["cwd"] == row["cwd"],
                "wrapperMatched": str(lab.HOME / "mods/session-hub/helper/hub.py") in "\n".join(terminal["argv"]),
                "contextVisible": "CONTINUITY_OK" in json.dumps(screen),
                "activeOwnership": active, "observedAt": time.time()}
path = lab.LAB / "continuity-gui.json"
previous = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}
previous[args.provider] = evidence
path.write_text(json.dumps(previous, indent=2), encoding="utf-8")
print(json.dumps(evidence))
