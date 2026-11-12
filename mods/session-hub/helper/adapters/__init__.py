"""Fixed local parser registry. No provider runtime or plugin is imported."""
from . import claude, codex, pi, copilot, gemini, sqlite_snapshot as sqlite_snapshot, usage as usage
from .common import clean, redact, timestamp, text_blocks as text_blocks

PARSERS = {"claude": claude.parse, "codex": codex.parse, "pi": pi.parse,
           "copilot": copilot.parse, "gemini": gemini.parse}


def parse_record(provider, x, meta):
    if not isinstance(x, dict):
        return None
    parser = PARSERS.get(provider)
    msg = parser(x, meta) if parser else None
    if msg and msg[1]:
        at = timestamp(x.get("timestamp"))
        if at:
            meta["createdAt"] = min(meta.get("createdAt") or at, at)
            meta["lastConversationAt"] = max(meta.get("lastConversationAt") or at, at)
        if not meta.get("title") and msg[0] == "user":
            meta["title"] = clean(msg[1].split("\n")[0], 160)
        return {"role": msg[0], "text": redact(msg[1]), "at": at,
                "id": clean(x.get("id"), 100), "parentId": clean(x.get("parentId"), 100)}
    return None
