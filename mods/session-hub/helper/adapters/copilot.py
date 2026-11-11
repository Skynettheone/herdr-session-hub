"""Copilot persisted event-log reader, independently based on the public SDK schema."""
from .common import clean, identity


def parse(x, meta):
    data = x.get("data")
    if not isinstance(data, dict):
        return None
    if x.get("agentId") or data.get("agentId") or x.get("parentToolCallId") or data.get("parentToolCallId"):
        return None
    kind = x.get("type")
    if kind == "session.start":
        identity(meta, data.get("sessionId"))
        context = data.get("context")
        if isinstance(context, dict):
            meta["cwd"] = clean(context.get("cwd"), 32000)
        meta["sourceVersion"] = clean(data.get("copilotVersion"), 30)
        # Disk discovery is supported; no locally verified native Copilot CLI yet.
        meta["formatSupported"] = False
    if kind == "session.context_changed":
        meta["cwd"] = clean(data.get("cwd"), 32000) or meta.get("cwd", "")
    if kind == "session.title_changed":
        meta["title"] = clean(data.get("title"), 160)
    if kind in ("session.snapshot_rewind", "session.truncation", "session.context_cleared"):
        meta["historyBase"] = True
    if kind in ("user.message", "assistant.message"):
        return ("user" if kind == "user.message" else "assistant", clean(data.get("content"), 1024 * 1024))
    return None
