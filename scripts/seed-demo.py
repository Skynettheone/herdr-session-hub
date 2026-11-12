"""Create disposable synthetic histories and runtime; never inspect real histories."""
import json
from pathlib import Path
import shutil
import sqlite3
import sys
import uuid

repo = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(repo / "tests"))
from test_hub import hub, fixture, encode

base = repo / ".dev"
app = base / "herdr-app"
project = base / "projects" / "Demo workspace"
project.mkdir(parents=True, exist_ok=True)
mod = app / "mods/session-hub"
mod.mkdir(parents=True, exist_ok=True)
for name in ("main.js", "model.js", "ui.js", "tabs.js", "mod.json"):
    shutil.copyfile(repo / "mods/session-hub" / name, mod / name)
shutil.copytree(repo / "mods/session-hub/helper", mod / "helper", dirs_exist_ok=True, ignore=shutil.ignore_patterns("__pycache__"))
shutil.copytree(repo / "mods/session-hub/icons", mod / "icons", dirs_exist_ok=True)
shutil.copytree(repo / "mods/session-hub/assets", mod / "assets", dirs_exist_ok=True)
state = app / "data/session-hub"
profiles = []
titles = {"claude": "Polish the command palette", "codex": "Add offline search", "pi": "Review the release checklist"}
for provider in ("claude", "codex", "pi"):
    config = base / "histories" / provider
    root = config / ("projects" if provider == "claude" else "sessions")
    root.mkdir(parents=True, exist_ok=True)
    session_id = str(uuid.uuid5(uuid.NAMESPACE_URL, "hub-demo-" + provider))
    filename = session_id + ".jsonl" if provider == "claude" else ("rollout-demo-" if provider == "codex" else "2026-11-12_") + session_id + ".jsonl"
    rows = fixture(provider, project, session_id)
    if provider == "claude":
        rows[0]["message"]["content"] = titles[provider]
    elif provider == "codex":
        rows[1]["payload"]["content"][0]["text"] = titles[provider]
    else:
        rows[1]["message"]["content"] = titles[provider]
    (root / filename).write_bytes(encode(rows))
    exe = shutil.which(provider + ".exe") or sys.executable
    profiles.append({"id": "demo-" + provider, "label": "Demo " + provider, "provider": provider,
                     "roots": [str(root)], "configHome": str(config), "executable": exe, "content": False})
config = base / "config/opencode"
config.mkdir(parents=True, exist_ok=True)
root = base / "data/opencode"
root.mkdir(parents=True, exist_ok=True)
db = sqlite3.connect(root / "opencode.db")
db.execute("CREATE TABLE IF NOT EXISTS session(id TEXT PRIMARY KEY,title TEXT,directory TEXT,time_created INTEGER,time_updated INTEGER,version TEXT,parent_id TEXT)")
db.execute("INSERT OR REPLACE INTO session VALUES (?,?,?,?,?,?,NULL)", ("ses_syntheticDemo123", "Design the history panel", str(project), 1793440800000, 1793440800000, "1.3.17"))
db.commit()
db.close()
profiles.append({"id": "demo-opencode", "label": "Demo OpenCode", "provider": "opencode", "roots": [str(root)],
                 "configHome": str(config), "executable": shutil.which("opencode.exe"), "content": False})
with hub.Store(state) as store:
    for profile in profiles:
        hub.rpc(store, {"action": "profile-save", "profile": profile})
    hub.refresh(store)
(mod / "runtime.json").write_text(json.dumps({"schema": 1, "python": str(repo / ".venv/Scripts/python.exe"),
    "helper": str(mod / "helper/hub.py"), "state": str(state), "base": str(mod)}, indent=2), encoding="utf-8")
# Only the isolated home receives settings; production settings are never read.
(app / "settings.json").write_text(json.dumps({"telemetry": False}), encoding="utf-8")
(app / "layouts").mkdir(exist_ok=True)
(app / "layouts/hub-demo.json").write_text(json.dumps({"id":"root","type":"block","content":{"mod":"session-hub"}}), encoding="utf-8")
(app / "shared.json").write_text(json.dumps({"layout":"hub-demo"}), encoding="utf-8")
print("Synthetic demo prepared under .dev; no production configuration changed")
