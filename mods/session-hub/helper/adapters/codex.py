"""Read-only codex conversation records; tool payloads are omitted."""
from .common import clean, text_blocks, LINE


def parse(x, meta):
    kind = x.get("type")
    msg = None
    p = x.get("payload")
    if not isinstance(p, dict):
        return None
    if kind == "session_meta":
        native = p.get("id") or p.get("session_id")
        if native:
            if meta.get("nativeId") and meta["nativeId"] != native:
                meta["identityConflict"] = True
            meta["nativeId"] = clean(native, 100)
        meta["cwd"] = clean(p.get("cwd"), 32000)
        meta["sourceVersion"] = clean(p.get("cli_version"), 30)
        meta["formatSupported"] = bool(native and p.get("cwd"))
        meta["subagent"] = isinstance(p.get("source"), dict) or p.get("source") in ("subagent", "exec", "internal", "mcp")
        meta["historyBase"] = bool(p.get("history_base"))
    if kind == "response_item" and p.get("type") == "message" and p.get("role") in ("user", "assistant"):
        msg = (p["role"], text_blocks(p.get("content")))
    elif kind == "event_msg" and p.get("type") == "user_message":
        msg = ("user", clean(p.get("message"), LINE))
    return msg
