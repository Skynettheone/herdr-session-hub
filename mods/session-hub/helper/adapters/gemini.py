"""Bounded replay of Gemini JSON/JSONL. No thoughts or tool records are exposed."""
from .common import clean, identity


def replay(records):
    """Project user-visible messages, including replacement, rewind and patches.

    The caller must supply a complete bounded file. Partial journals cannot be
    projected safely because a later record can remove or replace earlier text.
    """
    metadata, messages = {}, {}
    for record in records:
        if not isinstance(record, dict):
            raise ValueError("Invalid Gemini record")
        if "$rewindTo" in record:
            ids = list(messages)
            target = record["$rewindTo"]
            keep = ids[:ids.index(target)] if target in messages else []
            messages = {key: messages[key] for key in keep}
        elif "$patch" in record:
            patch = record["$patch"]
            if not isinstance(patch, dict):
                raise ValueError("Invalid Gemini patch")
            updates = ([patch] if "id" in patch else []) + patch.get("updates", [])
            for update in updates:
                key = update.get("id")
                if key in messages and "content" in update:
                    messages[key] = {**messages[key], "content": update["content"]}
            for key in patch.get("removeIds", []):
                messages.pop(key, None)
            order = list(dict.fromkeys(key for key in patch.get("orderIds", []) if key in messages))
            messages = {**{key: value for key, value in messages.items() if key not in order},
                        **{key: messages[key] for key in order}}
        elif "$set" in record or "sessionId" in record:
            value = record.get("$set", record)
            if not isinstance(value, dict):
                raise ValueError("Invalid Gemini metadata")
            if "sessionId" in value:
                identity(metadata, value["sessionId"])
            for key in ("projectHash", "startTime", "lastUpdated", "summary", "kind"):
                if key in value:
                    metadata[key] = value[key]
            if "messages" in value:
                if not isinstance(value["messages"], list) or len(value["messages"]) > 10000:
                    raise ValueError("Gemini message budget exceeded")
                messages = {item["id"]: item for item in value["messages"] if isinstance(item, dict) and isinstance(item.get("id"), str)}
        elif isinstance(record.get("id"), str):
            messages[record["id"]] = record
        if len(messages) > 10000:
            raise ValueError("Gemini message budget exceeded")
    return [{**metadata, "type": "hub.gemini.metadata"}, *messages.values()]


def parse(x, meta):
    if x.get("type") == "hub.gemini.metadata":
        identity(meta, x.get("nativeId"))
        if x.get("identityConflict"):
            meta["identityConflict"] = True
        meta.update(projectHash=clean(x.get("projectHash"), 100), subagent=x.get("kind") == "subagent",
                    formatSupported=bool(x.get("nativeId") and x.get("projectHash")), sourceVersion="0.49.0 schema")
    if x.get("type") in ("user", "gemini"):
        content = x.get("content")
        if isinstance(content, list):
            content = "\n".join(clean(item.get("text"), 1024 * 1024) for item in content[:1000] if isinstance(item, dict)
                                and not str(item.get("text", "")).lstrip().startswith("<session_context>"))
        elif isinstance(content, str) and content.lstrip().startswith("<session_context>"):
            return None
        return ("user" if x["type"] == "user" else "assistant", clean(content, 1024 * 1024))
    return None
