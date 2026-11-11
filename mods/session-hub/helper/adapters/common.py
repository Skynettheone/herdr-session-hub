"""Conversation-only normalization shared by independent provider readers."""
import datetime as dt
import re
import unicodedata

LINE = 1024 * 1024

def clean(value, limit=300):
    if not isinstance(value, str):
        return ""
    return "".join(c for c in value if c in "\n\t" or unicodedata.category(c) not in {"Cc", "Cf", "Cs"})[:limit]


def redact(value):
    value = re.sub(r"(?i)(bearer\s+|(?:api[_-]?key|password|token|secret)\s*[:=]\s*)[^\s,;]+", r"\1[redacted]", value)
    return re.sub(r"\b(?:sk-[A-Za-z0-9_-]{12,}|gh[pousr]_[A-Za-z0-9]{16,})\b", "[redacted]", value)


def timestamp(value):
    try:
        if isinstance(value, (int, float)) and not isinstance(value, bool):
            return dt.datetime.fromtimestamp(value / 1000, dt.timezone.utc).isoformat()
        if isinstance(value, str):
            return dt.datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(dt.timezone.utc).isoformat()
    except (ValueError, OSError, OverflowError):
        pass
    return None



def text_blocks(content):
    if isinstance(content, str):
        return clean(content, LINE)
    if isinstance(content, list):
        return "\n".join(clean(x.get("text"), LINE) for x in content[:1000]
                         if isinstance(x, dict) and x.get("type") in ("text", "input_text", "output_text"))[:LINE]
    return ""



def identity(meta, native):
    if native:
        if meta.get("nativeId") and meta["nativeId"] != native:
            meta["identityConflict"] = True
        meta["nativeId"] = clean(native, 100)


def message(role, content):
    return (role, text_blocks(content))
