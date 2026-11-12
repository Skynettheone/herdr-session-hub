"""Manual user-owned cloud-account acceptance; never opens credential files."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess

REPO = Path(__file__).resolve().parents[1]
BASE = REPO / ".dev/account-lab"
spec = importlib.util.spec_from_file_location("hub", REPO / "mods/session-hub/helper/hub.py")
hub = importlib.util.module_from_spec(spec)
spec.loader.exec_module(hub)


def environment(label):
    home = BASE / label
    env = hub.profile_environment({"CLAUDE_CONFIG_DIR": str(home / "claude")})
    for name in ("HOME", "USERPROFILE", "APPDATA", "LOCALAPPDATA", "XDG_CONFIG_HOME", "XDG_DATA_HOME", "XDG_STATE_HOME", "XDG_CACHE_HOME"):
        env[name] = str(home / "environment" / name)
    return env


def prepare():
    if BASE.exists():
        raise RuntimeError("Refusing to overwrite existing account acceptance data")
    for label in ("personal", "company"):
        (BASE / label / "claude/projects").mkdir(parents=True)
        (BASE / label / "project").mkdir()
        for name in ("HOME", "USERPROFILE", "APPDATA", "LOCALAPPDATA", "XDG_CONFIG_HOME", "XDG_DATA_HOME", "XDG_STATE_HOME", "XDG_CACHE_HOME"):
            Path(environment(label)[name]).mkdir(parents=True, exist_ok=True)
        # Only safe settings written by this harness; native login owns auth data.
        (BASE / label / "claude/settings.json").write_text(json.dumps({"env": {"CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC": "1"}}), encoding="utf-8")
    print("Prepared two empty account homes. Sign in yourself in each named terminal.")


def status(executable, label):
    result = subprocess.run([executable, "auth", "status", "--json"], env=environment(label),
                            cwd=BASE / label / "project", capture_output=True, timeout=20)
    try:
        value = json.loads(result.stdout)
    except ValueError:
        raise RuntimeError("Native auth status was unavailable; no diagnostic body retained") from None
    # Native metadata only, no settings/auth file reads or raw output in evidence.
    identity = [value.get(key) for key in ("email", "orgId", "accountId")]
    return {"loggedIn": value.get("loggedIn") is True,
            "identityDigest": hashlib.sha256(json.dumps(identity).encode()).hexdigest() if any(identity) else None,
            "authMethod": value.get("authMethod")}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=("prepare", "login", "status", "create"))
    parser.add_argument("label", nargs="?", choices=("personal", "company"))
    args = parser.parse_args()
    if args.action == "prepare":
        prepare()
    else:
        executable = hub.probe()["providers"]["claude"]["executable"]
        if not executable or not args.label or not (BASE / args.label / "project").is_dir():
            raise SystemExit("Prepare the lab and choose a named profile first")
        if args.action == "login":
            print("USER SIGN-IN: " + args.label.upper(), flush=True)
            raise SystemExit(subprocess.call([executable, "auth", "login"], env=environment(args.label),
                                             cwd=BASE / args.label / "project", shell=False))
        if args.action == "status":
            print(json.dumps(status(executable, args.label)))
        elif args.action == "create":
            marker = "ACCOUNT_" + args.label.upper() + "_3c71b6"
            result = subprocess.run([executable, "-p", "Remember this marker for this conversation: " + marker + ". Reply only with that marker. Do not use tools.",
                                     "--output-format", "json", "--tools", ""], env=environment(args.label),
                                    cwd=BASE / args.label / "project", capture_output=True, timeout=90)
            try:
                value = json.loads(result.stdout)
            except ValueError:
                raise SystemExit("Native cloud response unavailable; no diagnostic body retained") from None
            evidence = {"label": args.label, "nativeId": value.get("session_id"), "markerObserved": marker in value.get("result", ""), "exitCode": result.returncode}
            (BASE / (args.label + "-create.json")).write_text(json.dumps(evidence), encoding="utf-8")
            print(json.dumps(evidence))
