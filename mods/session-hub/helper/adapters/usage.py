"""Pure local accounting. No filesystem, provider SDK, credentials or network.

Channels are disjoint; unknown cost is None. See docs/USAGE_DESIGN.md for sources.
Only numeric accounting and bounded identifiers leave these parsers.
"""
from __future__ import annotations

import datetime as dt
import hashlib
import json
import math
import re

CHANNELS = ("input", "output", "cacheRead", "cacheWrite")
VERSION = 3
MAX_EVENTS = 200000
UTC = dt.timezone.utc


def obj(value):
    return value if isinstance(value, dict) else {}


def number(value, maximum=10**12):
    return (value if type(value) in (int, float) and 0 <= value <= maximum
            and math.isfinite(value) and value == int(value) else None)


def identifier(value):
    # No control/bidi sequences, free text, paths, query parameters or secret blobs.
    return value if (isinstance(value, str) and not value.lower().startswith(("sk-", "ghp_", "github_pat_", "bearer"))
                     and re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.:/@+-]{0,239}", value)) else "unknown"


def qualified_model(backend, model):
    return identifier(backend) + "/" + identifier(model)


def gemini_billing_records(rows):
    """Retain billed journal entries across conversation rewind/removal.

    Gemini's token recorder appends the complete message again when counters
    arrive. Stable IDs/timestamps deduplicate these updates. Content patches and
    active-conversation ordering never undo recorded inference work.
    """
    for row in rows:
        if not isinstance(row, dict):
            continue
        value = obj(row.get("$set", row))
        messages = value.get("messages")
        if isinstance(messages, list):
            yield from messages
        elif row.get("type") == "gemini":
            yield row


def instant(value):
    try:
        if isinstance(value, str) and len(value) <= 40:
            parsed = dt.datetime.fromisoformat(value.replace("Z", "+00:00"))
            if parsed.tzinfo:
                return parsed.astimezone(UTC).isoformat()
        if type(value) in (int, float) and 946684800000 <= value <= 4102444800000 and math.isfinite(value):
            return dt.datetime.fromtimestamp(value / 1000, UTC).isoformat()
    except (ValueError, OverflowError, OSError):
        pass
    return None


def key(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def event(provider, identity, at, model, channels, cost=None):
    at = instant(at)
    values = [number(n) for n in channels]
    if not at or not identity or len(values) != 4 or any(n is None for n in values) or not sum(values):
        return None
    usd = cost if type(cost) in (int, float) and 0 < cost <= 10**9 and math.isfinite(cost) else None
    return dict(id=key([provider, identity]), provider=provider, model=identifier(model), at=at,
                **dict(zip(CHANNELS, values)), reportedCost=usd)


def counts(usage, names):
    return [usage.get(name, 0) for name in names]


def codex_counts(value):
    u = obj(value)
    names = ("input_tokens", "output_tokens", "cached_input_tokens", "cache_write_input_tokens", "reasoning_output_tokens")
    values = [number(u.get(name, 0)) for name in names]
    if not u or any(v is None for v in values):
        return None
    inp, out, read, write, reasoning = values
    total = number(u.get("total_tokens", inp + out))
    if read + write > inp or reasoning > out or total is None or total < inp + out:
        return None
    return [inp - read - write, out, read, write]


def parse(provider, rows, state=None):
    """Return events, bounded resumable parser state, accounting warning counts."""
    state = dict(state or {})
    if provider == "gemini":
        rows = gemini_billing_records(rows)
    events, warnings, limits = [], {}, []

    def warn(code):
        warnings[code] = warnings.get(code, 0) + 1

    def add(value):
        if value:
            events.append(value)
        else:
            warn("invalid usage or timestamp")

    for x in rows:
        if not isinstance(x, dict):
            warn("malformed record")
            continue
        kind = x.get("type")
        m = obj(x.get("message"))
        if provider == "claude" and kind == "assistant" and isinstance(m.get("usage"), dict):
            if m.get("model") == "<synthetic>":
                continue
            identity = [m.get("id"), x.get("requestId")]
            if not identity[0]:
                warn("missing billed message identity")
                continue
            add(event(provider, identity, x.get("timestamp"), m.get("model"),
                      counts(m["usage"], ("input_tokens", "output_tokens", "cache_read_input_tokens", "cache_creation_input_tokens")), x.get("costUSD")))
            if m["usage"].get("iterations"):
                warn("advisor iteration accounting unavailable")
        elif provider == "pi":
            u = obj(m.get("usage")) if kind == "message" else obj(x.get("usage"))
            if not u:
                continue
            if not x.get("id"):
                warn("missing billed message identity")
                continue
            model = qualified_model(m.get("provider", x.get("provider")), m.get("responseModel", m.get("model", x.get("model"))))
            if model.startswith("unknown/"):
                warn("upstream model provider is unavailable")
            add(event(provider, [x["id"], x.get("timestamp"), model], x.get("timestamp"), model,
                      counts(u, ("input", "output", "cacheRead", "cacheWrite")), obj(u.get("cost")).get("total")))
        elif provider == "opencode" and x.get("role") == "assistant" and isinstance(x.get("tokens"), dict):
            u = x["tokens"]
            out, reasoning = number(u.get("output", 0)), number(u.get("reasoning", 0))
            if not x.get("id") or out is None or reasoning is None:
                warn("invalid usage or identity")
                continue
            model = qualified_model(obj(x.get("model")).get("providerID", x.get("providerID")), obj(x.get("model")).get("id", x.get("modelID")))
            if model.startswith("unknown/"):
                warn("upstream model provider is unavailable")
            add(event(provider, x["id"], obj(x.get("time")).get("created", x.get("time_created")), model,
                      [u.get("input", 0), out + reasoning, obj(u.get("cache")).get("read", 0), obj(u.get("cache")).get("write", 0)], x.get("cost")))
        elif provider == "gemini" and kind == "gemini" and isinstance(x.get("tokens"), dict):
            u = x["tokens"]
            inp, out, read, thoughts, total = [number(u.get(n, 0)) for n in ("input", "output", "cached", "thoughts", "total")]
            if not x.get("id") or any(n is None for n in (inp, out, read, thoughts, total)) or read > inp or total != inp + out + thoughts:
                warn("unsupported Gemini token summary")
                continue
            add(event(provider, [x["id"], x.get("timestamp")], x.get("timestamp"), x.get("model"), [inp - read, out + thoughts, read, 0]))
        elif provider == "codex":
            p = obj(x.get("payload"))
            if kind == "session_meta" and "native" not in state:
                native = p.get("id", p.get("session_id"))
                if not isinstance(native, str) or not 1 <= len(native) <= 120:
                    warn("missing Codex native identity")
                    continue
                state["native"] = key(native)
                state["fork"] = bool(p.get("forked_from_id") or isinstance(p.get("source"), dict))
            elif kind == "turn_context":
                state["model"] = identifier(p.get("model"))
            elif kind == "token_usage_record":
                warn("standalone request accounting unavailable")
            elif kind == "event_msg" and p.get("type") == "token_count":
                at = instant(x.get("timestamp"))
                rate = obj(p.get("rate_limits"))
                for name in ("primary", "secondary"):
                    window = obj(rate.get(name))
                    used, minutes, reset = window.get("used_percent"), window.get("window_minutes"), window.get("resets_at")
                    if (at and type(used) in (int, float) and 0 <= used <= 100 and math.isfinite(used)
                            and number(minutes, 525600) and type(reset) in (int, float) and 946684800 <= reset <= 4102444800):
                        limits.append(dict(window=name, used=used, minutes=minutes, resetsAt=dt.datetime.fromtimestamp(reset, UTC).isoformat(), at=at))
                info = obj(p.get("info"))
                last = codex_counts(info.get("last_token_usage"))
                total = codex_counts(info.get("total_token_usage"))
                has_total = info.get("total_token_usage") is not None
                if last is None or (has_total and total is None) or not at or "native" not in state:
                    if info:
                        warn("invalid Codex usage")
                    continue
                previous = state.get("total")
                replay = key([at, last, total])
                if replay == state.get("replay") or total is not None and total == previous:
                    continue
                state["replay"] = replay
                state["total"] = total
                if state.get("fork"):
                    warn("ambiguous Codex fork inheritance")
                    continue
                if not sum(last):
                    continue
                raw_last = obj(info.get("last_token_usage"))
                if raw_last.get("total_tokens", sum(last)) != sum(last) or total and any(total[i] < last[i] for i in range(4)):
                    warn("inconsistent Codex request counters")
                    continue
                if previous is None and total and total != last:
                    warn("unattributed initial Codex cumulative prefix")
                if previous and total and total != last and any(total[i] - previous[i] != last[i] for i in range(4)):
                    warn("unattributed Codex cumulative gap")
                if total is None:
                    signature = key(last)
                    if signature == state.get("legacyLast"):
                        continue
                    state["legacyLast"] = signature
                add(event(provider, [state["native"], at, total, last], at, state.get("model"), last))
    return events, state, warnings, limits


def merge_events(events):
    """Deduplicate streaming updates/copies before filters, using channel maxima."""
    by_id = {}
    for item in events:
        old = by_id.get(item["id"])
        if not old:
            by_id[item["id"]] = dict(item)
            continue
        for channel in CHANNELS:
            old[channel] = max(old[channel], item[channel])
        old["reportedCost"] = max(old.get("reportedCost") or 0, item.get("reportedCost") or 0) or None
        old["at"] = min(old["at"], item["at"])
        if old["model"] == "unknown":
            old["model"] = item["model"]
    return list(by_id.values())


def price(item, rates):
    rate = rates.get(item["provider"] + ":" + item["model"])
    if rate is not None:
        cost = sum(item[c] * rate[c] for c in CHANNELS) / 1000000
        savings = item["cacheRead"] * max(0, rate["input"] - rate["cacheRead"]) / 1000000
        return cost, savings
    return item.get("reportedCost"), None


def period(request, now=None):
    now = now or dt.datetime.now(UTC)
    preset = request.get("period", "30d")
    if preset == "custom":
        start = dt.datetime.strptime(request.get("start", ""), "%Y-%m-%d").replace(tzinfo=UTC)
        end = dt.datetime.strptime(request.get("end", ""), "%Y-%m-%d").replace(tzinfo=UTC) + dt.timedelta(days=1)
        if end <= start or end - start > dt.timedelta(days=366) or start.year < 2000 or end.year > 2101:
            raise ValueError("Choose a valid custom UTC range of at most 366 days")
    elif preset in ("24h", "7d", "30d", "90d"):
        end = now
        start = end - dt.timedelta(hours=24) if preset == "24h" else end - dt.timedelta(days=int(preset[:-1]))
    else:
        raise ValueError("Choose a supported usage period")
    return start, end, preset == "24h"


def aggregate(events, request, rates, now=None):
    start, end, hourly = period(request, now)
    fmt = "%Y-%m-%dT%H:00Z" if hourly else "%Y-%m-%d"
    zero = lambda: dict(**dict.fromkeys(CHANNELS, 0), tokens=0, events=0, cost=None, pricedEvents=0, savings=None)
    totals, models, projects, providers, days, sessions = zero(), {}, {}, {}, {}, {}
    cursor = start.replace(minute=0, second=0, microsecond=0) if hourly else start.replace(hour=0, minute=0, second=0, microsecond=0)
    step = dt.timedelta(hours=1) if hourly else dt.timedelta(days=1)
    while cursor < end:
        days[cursor.strftime(fmt)] = zero()
        cursor += step

    def add(target, item, cost, savings):
        for channel in CHANNELS:
            target[channel] += item[channel]
        target["tokens"] += sum(item[c] for c in CHANNELS)
        target["events"] += 1
        if cost is not None:
            target["cost"] = (target["cost"] or 0) + cost
            target["pricedEvents"] += 1
        if savings is not None:
            target["savings"] = (target["savings"] or 0) + savings

    # Authorization and shared-root deduplication occur in the caller; billing
    # deduplication still precedes date/provider/model filtering here.
    for item in merge_events(events):
        if not start.isoformat() <= item["at"] < end.isoformat():
            continue
        if request.get("provider", "all") not in ("all", item["provider"]) or request.get("model") and request["model"] != item["provider"] + ":" + item["model"]:
            continue
        cost, savings = price(item, rates)
        day = dt.datetime.fromisoformat(item["at"]).strftime(fmt)
        model = item["provider"] + ":" + item["model"]
        project, session = item.get("projectIdentity", item.get("project", "Unknown project")), item.get("session", item["id"])
        project_group = projects.setdefault(project, dict(zero(), label=item.get("project", "Unknown project")))
        for target in (totals, models.setdefault(model, zero()), project_group,
                       providers.setdefault(item["provider"], zero()), days[day], sessions.setdefault(session, zero())):
            add(target, item, cost, savings)
        add(days[day].setdefault("series", {}).setdefault(item["provider"], zero()), item, cost, savings)
    totals["sessions"] = len(sessions)
    denominator = totals["input"] + totals["cacheRead"]
    totals["cacheHit"] = totals["cacheRead"] / denominator if denominator else None
    ordered = sorted(sessions.values(), key=lambda item: item["tokens"])
    trim = len(ordered) // 10 if request.get("trim") else 0
    sample = ordered[trim:len(ordered)-trim] if trim else ordered
    averages = dict(tokens=sum(s["tokens"] for s in sample) / len(sample) if sample else None,
                    events=sum(s["events"] for s in sample) / len(sample) if sample else None,
                    cost=sum(s["cost"] or 0 for s in sample) / len(sample) if sample and all(s["pricedEvents"] == s["events"] for s in sample) else None,
                    sessions=len(sample), trimmed=trim * 2)
    def ranked(values):
        return [dict(key=k, **v) for k, v in sorted(values.items(), key=lambda pair: (-pair[1]["tokens"], pair[0]))[:100]]
    return dict(totals=totals, averages=averages, models=ranked(models), projects=ranked(projects), providers=ranked(providers),
                timeline=[dict(key=k, **v) for k, v in days.items()], start=start.isoformat(), end=end.isoformat(), timezone="UTC",
                breakdownOmitted=max(0, len(models)-100) + max(0, len(projects)-100))
