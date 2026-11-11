"""Read-only pi conversation records; tool payloads are omitted."""
from .common import clean, text_blocks


def parse(x, meta):
    kind = x.get("type")
    msg = None
    if kind == "session":
        meta.update(nativeId=clean(x.get("id"), 100), cwd=clean(x.get("cwd"), 32000),
                    sourceVersion=str(x.get("version", 1)), formatSupported=x.get("version", 1) in (1, 2, 3))
    if kind == "session_info":
        meta["title"] = clean(x.get("name"), 160)
    if kind == "message" and isinstance(x.get("message"), dict):
        m = x["message"]
        if m.get("role") in ("user", "assistant"):
            msg = (m["role"], text_blocks(m.get("content")))
    return msg
