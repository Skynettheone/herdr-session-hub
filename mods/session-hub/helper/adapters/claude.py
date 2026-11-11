"""Read-only claude conversation records; tool payloads are omitted."""
from .common import clean, text_blocks


def parse(x, meta):
    kind = x.get("type")
    msg = None
    if x.get("isSidechain") or x.get("isMeta") or x.get("isCompactSummary"):
        return None
    if x.get("sessionId"):
        if meta.get("nativeId") and meta["nativeId"] != x["sessionId"]:
            meta["identityConflict"] = True
        meta["nativeId"] = clean(x["sessionId"], 100)
    if x.get("cwd") and not meta.get("cwd"):
        meta["cwd"] = clean(x["cwd"], 32000)
    if x.get("version"):
        meta["sourceVersion"] = clean(x["version"], 30)
        meta["formatSupported"] = str(x["version"]).split(".")[0] in ("1", "2")
    if kind in ("custom-title", "ai-title"):
        meta["title"] = clean(x.get("customTitle") or x.get("aiTitle"), 160)
    if kind in ("user", "assistant") and isinstance(x.get("message"), dict):
        msg = (kind, text_blocks(x["message"].get("content")))
    return msg
