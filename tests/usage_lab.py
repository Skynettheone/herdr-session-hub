"""Manual native acceptance harness; synthetic files in .dev/usage-lab only.

Not a CI test, production installer or provider launcher. No credentials copied.
"""
import argparse
import datetime as dt
import hashlib
import importlib.util
import json
import math
import os
from pathlib import Path
import shutil
import sqlite3
import subprocess
import uuid

REPO = Path(__file__).resolve().parents[1]
BASE = REPO / ".dev/usage-lab"
HOME = BASE / "app-home"
SPEC = importlib.util.spec_from_file_location("usage_lab_hub", REPO / "mods/session-hub/helper/hub.py")
hub = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(hub)


def environment():
    env = dict(os.environ)
    for name in ("HOME", "USERPROFILE", "APPDATA", "LOCALAPPDATA", "XDG_CONFIG_HOME", "XDG_DATA_HOME", "XDG_STATE_HOME", "XDG_CACHE_HOME"):
        env[name] = str(BASE / "environment" / name)
    env.update(HERDR_APP_HOME=str(HOME), HC_SESSION="hub-usage-acceptance", HERDR_TELEMETRY="0", DO_NOT_TRACK="1")
    return env


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value), encoding="utf-8")


def layout(width=None, theme=None):
    content = dict(id="usage-hub", type="block", content={"mod": "session-hub"})
    root = content if not width else dict(id="usage-root", type="row", children=[
        dict(id="spacer", type="block", content={"mod": "usage-spacer"}), dict(content, size={"px": width})])
    if theme:
        root["theme"] = theme
    return root


def prepare():
    if BASE.exists():
        raise RuntimeError("Refusing existing lab; use sync for owned runtime files")
    shipped = REPO / ".dev/acceptance/app-home"
    (HOME / "mods").mkdir(parents=True)
    for directory in ("icons", "themes"):
        shutil.copytree(shipped / directory, HOME / directory)
    for path in (shipped / "mods").iterdir():
        if path.is_dir() and path.name != "session-hub":
            shutil.copytree(path, HOME / "mods" / path.name, ignore=shutil.ignore_patterns("__pycache__", "runtime.json"))
    for name in ("AGENTS.md", "herdr.d.ts", "gpui-kit.d.ts"):
        shutil.copyfile(shipped / name, HOME / name)
    for folder, filename, source in (("install", "herdr-app.exe", ".dev/acceptance/install/herdr-app.exe"), ("core", "hc.exe", ".dev/acceptance/core/hc.exe")):
        (BASE / folder).mkdir()
        shutil.copyfile(REPO / source, BASE / folder / filename)
    write(HOME / "settings.json", {"telemetry": False, "core": str(BASE / "core/hc.exe")})
    write(HOME / "layouts/usage-wide.json", layout())
    write(HOME / "layouts/usage-narrow.json", layout(360))
    write(HOME / "layouts/usage-light.json", layout(theme="paper"))
    write(HOME / "layouts/usage-community.json", layout(theme="atom-one-dark"))
    write(HOME / "shared.json", {"layout": "usage-wide"})
    spacer = HOME / "mods/usage-spacer"
    spacer.mkdir()
    write(spacer / "mod.json", {"place": "none"})
    (spacer / "main.js").write_text('import {View,div} from "gpui-kit";export default class extends View{render(){return div().size_full();}}', encoding="utf-8")
    project = BASE / "projects/Synthetic dashboard"
    project.mkdir(parents=True)
    now = dt.datetime.now(dt.timezone.utc)
    profiles = []
    with hub.Store(HOME / "data/session-hub") as store:
        for index, provider in enumerate(("claude", "codex", "pi", "gemini", "opencode", "copilot")):
            native = str(uuid.uuid5(uuid.NAMESPACE_URL, "hub-usage-" + provider))
            config = BASE / "profiles" / provider / (".gemini" if provider == "gemini" else "config")
            root = config / ("projects" if provider == "claude" else "tmp/project/chats" if provider == "gemini" else "session-state/"+native if provider == "copilot" else "sessions")
            root.mkdir(parents=True)
            if provider == "opencode":
                config = BASE / "opencode-config/opencode"
                config.mkdir(parents=True)
                root = BASE / "opencode-data/opencode"
                root.mkdir(parents=True)
            p = dict(id=provider, label="Synthetic "+provider, provider=provider, roots=[str(root)], configHome=str(config), executable="", content=False)
            profiles.append(p)
            model = "synthetic-"+provider
            rows = []
            if provider == "claude":
                rows.append(dict(type="user", sessionId=native, cwd=str(project), version="2.1.322", timestamp=now.isoformat(), message={"content":"Synthetic Usage dashboard"}))
            elif provider == "codex":
                rows.extend([dict(type="session_meta", payload=dict(id=native,cwd=str(project),cli_version="0.164.0",source="cli")), dict(type="turn_context",payload={"model":model})])
            elif provider == "pi":
                rows.append(dict(type="session", version=3, id=native, cwd=str(project), timestamp=now.isoformat()))
            messages, cumulative_in, cumulative_out, cumulative_read = [], 0, 0, 0
            for day in range(90):
                at = (now-dt.timedelta(days=day, hours=1)).isoformat()
                inp = int((abs(math.sin(day*.49))+0.1)*5000)*(index+1)
                out, read, cachewrite = inp//8, inp*4, inp//2
                identity = "synthetic-bill-"+str(day)
                if provider == "claude":
                    rows.append(dict(type="assistant",timestamp=at,requestId="request-"+str(day),message=dict(id=identity,model=model,usage=dict(input_tokens=inp,output_tokens=out,cache_read_input_tokens=read,cache_creation_input_tokens=cachewrite))))
                elif provider == "pi":
                    rows.append(dict(type="message",id=identity,timestamp=at,message=dict(role="assistant",model=model,usage=dict(input=inp,output=out,cacheRead=read,cacheWrite=cachewrite,cost={"total":(inp+out)/1000000}))))
                elif provider == "codex":
                    cumulative_in += inp+read
                    cumulative_out += out
                    cumulative_read += read
                    rows.append(dict(type="event_msg",timestamp=at,payload=dict(type="token_count",info=dict(last_token_usage=dict(input_tokens=inp+read,output_tokens=out,cached_input_tokens=read),total_token_usage=dict(input_tokens=cumulative_in,output_tokens=cumulative_out,cached_input_tokens=cumulative_read)),
                        rate_limits=dict(primary=dict(used_percent=61,window_minutes=10080,resets_at=int((now+dt.timedelta(days=4)).timestamp()))))))
                elif provider == "gemini":
                    messages.append(dict(type="gemini",id=identity,timestamp=at,model=model,content="Synthetic response",tokens=dict(input=inp+read,output=out,cached=read,thoughts=0,total=inp+read+out)))
                elif provider == "opencode":
                    messages.append(dict(id=identity,role="assistant",modelID=model,time={"created":int(dt.datetime.fromisoformat(at).timestamp()*1000)},tokens=dict(input=inp,output=out,reasoning=0,cache=dict(read=read,write=cachewrite)),cost=(inp+out)/1000000))
            filename = native+".jsonl" if provider == "claude" else "rollout-synthetic-"+native+".jsonl" if provider == "codex" else "2026-11-12_"+native+".jsonl" if provider == "pi" else "session-synthetic.json" if provider == "gemini" else "events.jsonl"
            if provider == "gemini":
                write(root / filename, dict(sessionId=native,projectHash=hashlib.sha256(str(project).encode()).hexdigest(),startTime=now.isoformat(),messages=messages))
            elif provider == "opencode":
                db=sqlite3.connect(root / "opencode.db")
                db.execute("CREATE TABLE session(id TEXT PRIMARY KEY,title TEXT,directory TEXT,time_created INTEGER,time_updated INTEGER,version TEXT,parent_id TEXT)")
                db.execute("CREATE TABLE message(id TEXT PRIMARY KEY,session_id TEXT,time_created INTEGER,data TEXT)")
                db.execute("INSERT INTO session VALUES(?,?,?,?,?,?,NULL)",(native,"Synthetic OpenCode",str(project),0,0,"1.3.17"))
                db.executemany("INSERT INTO message VALUES(?,?,?,?)",[(m["id"],native,m["time"]["created"],json.dumps(m)) for m in messages])
                db.commit()
                db.close()
            else:
                if provider == "copilot":
                    rows=[dict(type="session.start",data=dict(sessionId=native,version=1,context={"cwd":str(project)}))]
                (root / filename).write_bytes(("\n".join(json.dumps(r) for r in rows)+"\n").encode())
            hub.rpc(store,dict(action="profile-save",profile=p))
            if provider != "copilot":
                store.set("usage:rates", {**store.get("usage:rates", {}), provider+":"+model:dict(input=1,output=5,cacheRead=.1,cacheWrite=2)})
        hub.refresh(store)
    originals={str(p.relative_to(BASE)):hashlib.sha256(p.read_bytes()).hexdigest() for p in (BASE / "profiles").rglob("*") if p.is_file()}
    originals.update({str(p.relative_to(BASE)):hashlib.sha256(p.read_bytes()).hexdigest() for p in (BASE / "opencode-data").rglob("*") if p.is_file()})
    write(BASE / "original-hashes.json",originals)
    sync()


def sync():
    mod = HOME / "mods/session-hub"
    mod.mkdir(parents=True,exist_ok=True)
    for name in ("main.js","model.js","ui.js","usage.js","tabs.js","mod.json"):
        shutil.copyfile(REPO / "mods/session-hub" / name, mod / name)
    for name in ("helper","icons","assets"):
        shutil.copytree(REPO / "mods/session-hub" / name,mod / name,dirs_exist_ok=True,ignore=shutil.ignore_patterns("__pycache__"))
    write(mod / "runtime.json",dict(schema=1,python=str(REPO / ".venv/Scripts/python.exe"),helper=str(mod / "helper/hub.py"),state=str(HOME / "data/session-hub"),base=str(mod)))


def verify_accounting():
    """Independent arithmetic oracle for the closed-form synthetic fixture.

    Deliberately does not call the usage parsers or their aggregation helpers.
    """
    source = next((BASE / "profiles/claude/config/projects").glob("*.jsonl"))
    generated = dt.datetime.fromisoformat(json.loads(source.read_text().splitlines()[0])["timestamp"])
    evidence = []
    with hub.Store(HOME / "data/session-hub") as store:
        for period in ("24h", "7d", "30d", "90d"):
            result = hub.rpc(store, dict(action="usage", period=period))
            start, end = dt.datetime.fromisoformat(result["start"]), dt.datetime.fromisoformat(result["end"])
            expected = dict(input=0, output=0, cacheRead=0, cacheWrite=0, events=0)
            cost = 0
            for index, provider in enumerate(("claude", "codex", "pi", "gemini", "opencode")):
                for day in range(90):
                    at = generated - dt.timedelta(days=day, hours=1)
                    if not start <= at < end:
                        continue
                    inp = int((abs(math.sin(day * .49)) + .1) * 5000) * (index + 1)
                    out, read = inp // 8, inp * 4
                    cachewrite = inp // 2 if provider in ("claude", "pi", "opencode") else 0
                    expected["input"] += inp
                    expected["output"] += out
                    expected["cacheRead"] += read
                    expected["cacheWrite"] += cachewrite
                    expected["events"] += 1
                    cost += (inp + out * 5 + read * .1 + cachewrite * 2) / 1000000
            actual = result["totals"]
            assert all(actual[key] == value for key, value in expected.items()), (period, expected, actual)
            assert abs(actual["cost"] - cost) < 1e-9
            assert actual["tokens"] == sum(expected[c] for c in ("input", "output", "cacheRead", "cacheWrite"))
            assert actual["tokens"] == sum(bucket["tokens"] for bucket in result["timeline"])
            assert actual["tokens"] == sum(model["tokens"] for model in result["models"])
            assert actual["pricedEvents"] == actual["events"]
            evidence.append(dict(period=period, expected=expected, expectedCost=cost, matched=True))
    write(BASE / "accounting-evidence.json", evidence)
    print(json.dumps(evidence, indent=2))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("action",choices=("prepare","sync","start","status","commands","wide","narrow","light","community","stop","verify","verify-accounting","seed-rates","shot"))
    parser.add_argument("output", nargs="?")
    args=parser.parse_args()
    if args.action=="prepare":
        prepare()
    elif args.action=="sync":
        sync()
    elif args.action=="verify-accounting":
        verify_accounting()
    elif args.action=="seed-rates":
        # Old synthetic fixtures intentionally lack backend identity. Explicit
        # fixture-only rates preserve the oracle without editing those originals.
        with hub.Store(HOME / "data/session-hub") as store:
            for provider in ("pi", "opencode"):
                hub.rpc(store, dict(action="usage-price", rateProvider=provider, rateModel="unknown/synthetic-"+provider,
                                    rate=dict(input=1,output=5,cacheRead=.1,cacheWrite=2)))
    elif args.action=="start":
        subprocess.run([str(BASE / "core/hc.exe"),"server","start"],env=environment(),check=True,capture_output=True,timeout=30,creationflags=subprocess.CREATE_NO_WINDOW)
        p=subprocess.Popen([str(BASE / "install/herdr-app.exe")],env=environment(),cwd=BASE)
        write(BASE / "process.json",{"appPid":p.pid})
        print("Started disposable Usage GUI",p.pid)
    elif args.action=="verify":
        original=json.loads((BASE / "original-hashes.json").read_text())
        if not all(hashlib.sha256((BASE / path).read_bytes()).hexdigest()==value for path,value in original.items()):
            raise RuntimeError("Synthetic original changed")
        with hub.Store(HOME / "data/session-hub") as store:
            assert all(not p["content"] for p in store.get("profiles"))
        print("Original hashes match; all content search remains off")
    else:
        command=[args.action] if args.action in ("status","commands") else ["shot",args.output] if args.action=="shot" else ["do","window.close"] if args.action=="stop" else ["do","layout.switch",json.dumps({"name":"usage-"+args.action})]
        result=subprocess.run([str(BASE / "install/herdr-app.exe"),*command],env=environment(),capture_output=True,timeout=30,check=True)
        print(result.stdout.decode("utf-8","replace"))


if __name__=="__main__":
    main()
