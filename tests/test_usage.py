"""Accounting invariants and read-only encrypted integration, using synthetic data."""
import datetime as dt
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch
from compression import zstd

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("usage_hub", ROOT / "mods/session-hub/helper/hub.py")
hub = importlib.util.module_from_spec(spec)
spec.loader.exec_module(hub)
usage = hub._adapters.usage
AT = "2026-11-10T12:00:00Z"
NOW = dt.datetime(2026, 11, 12, 12, tzinfo=dt.timezone.utc)
ID = "11111111-2222-4333-8444-555555555555"


def encoded(rows):
    return ("\n".join(json.dumps(r) for r in rows) + "\n").encode()


def claude(identity="bill-1", output=20):
    return {"type": "assistant", "sessionId": ID, "version": "2.1.322", "timestamp": AT, "requestId": "req-1",
            "message": {"id": identity, "model": "test-model", "role": "assistant", "content": "DO NOT CACHE TEXT",
                        "usage": {"input_tokens": 10, "output_tokens": output,
                                  "cache_read_input_tokens": 70, "cache_creation_input_tokens": 5}}}


def codex(last, total, at=AT):
    return {"type": "event_msg", "timestamp": at, "payload": {"type": "token_count", "info": {
        "last_token_usage": last, "total_token_usage": total}}}


def tokens(inp=100, out=20, read=70, reasoning=5):
    return dict(input_tokens=inp, output_tokens=out, cached_input_tokens=read,
                reasoning_output_tokens=reasoning, total_tokens=inp+out)


class AccountingTests(unittest.TestCase):
    def test_claude_streams_and_copies_deduplicate_before_date_filter(self):
        events, _, _, _ = usage.parse("claude", [claude(output=10), claude(output=20)])
        duplicate = dict(events[0], at="2026-11-11T12:00:00+00:00")
        summary = usage.aggregate(events + [duplicate], {"period": "7d"}, {}, NOW)
        self.assertEqual(summary["totals"]["tokens"], 105)
        self.assertEqual(summary["totals"]["events"], 1)
        self.assertEqual(summary["totals"]["cacheHit"], .875)
        self.assertIsNone(summary["totals"]["cost"])
        outside = usage.aggregate(events + [duplicate], {"period": "custom", "start": "2026-11-11", "end": "2026-11-11"}, {}, NOW)
        self.assertEqual(outside["totals"]["tokens"], 0)

    def test_codex_cumulative_cache_reasoning_reset_and_gap(self):
        header = [{"type": "session_meta", "payload": {"id": ID}}, {"type": "turn_context", "payload": {"model": "test-model"}}]
        first = tokens()
        second = tokens(200, 40, 140, 10)
        rows = header + [codex(first, first), codex(first, first, "2026-11-10T12:01:00Z"),
                         codex(first, second, "2026-11-10T12:02:00Z"),
                         codex(first, first, "2026-11-10T12:03:00Z")]
        events, state, warnings, _ = usage.parse("codex", rows)
        self.assertEqual(len(events), 3)
        self.assertEqual(events[0]["input"], 30)
        self.assertEqual(events[0]["output"], 20)  # reasoning already included
        self.assertFalse(warnings)
        extra, _, warnings, _ = usage.parse("codex", [codex(first, tokens(500, 100, 350, 25), "2026-11-10T12:04:00Z")], state)
        self.assertEqual(len(extra), 1)  # only attributable last request, never the gap
        self.assertIn("unattributed Codex cumulative gap", warnings)

    def test_codex_fork_and_invalid_channels_fail_closed(self):
        rows = [{"type": "session_meta", "payload": {"id": ID, "forked_from_id": "parent"}}, codex(tokens(), tokens())]
        events, _, warnings, _ = usage.parse("codex", rows)
        self.assertFalse(events)
        self.assertIn("ambiguous Codex fork inheritance", warnings)
        self.assertIsNone(usage.codex_counts(tokens(read=101)))
        self.assertIsNone(usage.codex_counts(tokens(reasoning=21)))
        self.assertIsNone(usage.codex_counts(tokens(inp=True)))

    def test_pi_and_opencode_reasoning_and_unknown_cost(self):
        pi = {"type": "message", "id": "a", "timestamp": AT, "message": {"role": "assistant", "model": "m", "usage": {
            "input": 10, "output": 20, "cacheRead": 70, "cacheWrite": 5, "cost": {"total": 0}}}}
        events, _, _, _ = usage.parse("pi", [pi, pi])
        self.assertEqual(len(usage.merge_events(events)), 1)
        self.assertIsNone(events[0]["reportedCost"])
        oc = {"id": "msg-a", "role": "assistant", "modelID": "m", "time": {"created": 1794312000000},
              "tokens": {"input": 10, "output": 20, "reasoning": 5, "cache": {"read": 70, "write": 5}}, "cost": .25}
        events, _, _, _ = usage.parse("opencode", [oc])
        self.assertEqual(events[0]["output"], 25)
        self.assertEqual(events[0]["reportedCost"], .25)

    def test_gemini_conservation_and_copilot_unavailable(self):
        record = {"type": "gemini", "id": "m1", "timestamp": AT, "model": "gemini-test", "tokens": {
            "input": 100, "output": 20, "cached": 70, "thoughts": 5, "total": 125}}
        events, _, warnings, _ = usage.parse("gemini", [record])
        self.assertEqual([events[0][c] for c in usage.CHANNELS], [30, 25, 70, 0])
        self.assertFalse(warnings)
        record["tokens"]["total"] = 126
        self.assertTrue(usage.parse("gemini", [record])[2])
        self.assertFalse(usage.parse("copilot", [{"type": "assistant.usage", "data": {"inputTokens": 100}}])[0])

    def test_local_prices_partial_cost_and_zero_rate_are_explicit(self):
        events = usage.parse("claude", [claude()])[0]
        other = dict(events[0], id="different", model="unpriced")
        rates = {"claude:test-model": dict(input=1, output=5, cacheRead=.1, cacheWrite=2)}
        result = usage.aggregate(events + [other], {"period": "7d"}, rates, NOW)
        self.assertAlmostEqual(result["totals"]["cost"], .000127)
        self.assertEqual(result["totals"]["pricedEvents"], 1)
        self.assertIsNone(result["averages"]["cost"])
        rates["claude:test-model"] = dict.fromkeys(usage.CHANNELS, 0)
        self.assertEqual(usage.aggregate(events, {"period": "7d"}, rates, NOW)["totals"]["cost"], 0)

    def test_period_edges_empty_buckets_trim_and_invalid_dates(self):
        events = []
        for index in range(10):
            events.append(dict(usage.parse("claude", [claude(str(index), index+1)])[0][0], session=str(index)))
        result = usage.aggregate(events, {"period": "7d", "trim": True}, {}, NOW)
        self.assertEqual(result["averages"]["sessions"], 8)
        self.assertEqual(result["averages"]["trimmed"], 2)
        self.assertEqual(len(result["timeline"]), 8)  # rolling 7 days includes two partial UTC days
        self.assertEqual(len(usage.aggregate([], {"period": "24h"}, {}, NOW)["timeline"]), 24)
        for req in ({"period": "bad"}, {"period": "custom", "start": "2026-11-12", "end": "2026-11-10"}):
            with self.assertRaises(ValueError):
                usage.period(req, NOW)

    def test_invalid_accounting_never_becomes_nan_or_negative(self):
        for bad in (-1, True, float("nan"), float("inf"), 1e50, "10", None):
            record = claude()
            record["message"]["usage"]["input_tokens"] = bad
            events, _, warnings, _ = usage.parse("claude", [record])
            self.assertFalse(events)
            self.assertTrue(warnings)

    def test_invalid_cumulative_is_not_treated_as_legacy_request(self):
        header = {"type": "session_meta", "payload": {"id": ID}}
        for invalid in (tokens(inp=-1), tokens(inp=10, read=30), {"input_tokens": "100"}):
            events, _, warnings, _ = usage.parse("codex", [header, codex(tokens(), invalid)])
            self.assertFalse(events)
            self.assertIn("invalid Codex usage", warnings)
        invalid = tokens()
        invalid["total_tokens"] = 999
        self.assertFalse(usage.parse("codex", [header, codex(invalid, invalid)])[0])

    def test_same_name_projects_remain_separate(self):
        a = dict(usage.parse("claude", [claude("a")])[0][0], project="project", projectIdentity="first")
        b = dict(usage.parse("claude", [claude("b")])[0][0], project="project", projectIdentity="second")
        result = usage.aggregate([a, b], {"period": "7d"}, {}, NOW)
        self.assertEqual(len(result["projects"]), 2)
        self.assertTrue(all(p["label"] == "project" for p in result["projects"]))


class UsageIntegrationTests(unittest.TestCase):
    def setUp(self):
        (ROOT / ".dev/tests").mkdir(parents=True, exist_ok=True)
        self.tmp = tempfile.TemporaryDirectory(prefix="usage-", dir=ROOT / ".dev/tests")
        self.base = Path(self.tmp.name)
        self.root = self.base / "profile/projects"
        self.root.mkdir(parents=True)
        self.path = self.root / (ID + ".jsonl")
        self.profile = dict(id="personal", label="Personal", provider="claude", roots=[str(self.root)],
                            configHome=str(self.root.parent), executable=sys.executable, enabled=True, content=False)
        self.path.write_bytes(encoded([claude()]))

    def tearDown(self):
        self.tmp.cleanup()

    def setup_store(self, store):
        hub.rpc(store, dict(action="profile-save", profile=self.profile))
        hub.refresh(store)

    def refresh_usage(self, store):
        return hub.rpc(store, dict(action="usage-refresh", period="custom", start="2026-11-01", end="2026-11-12"))

    def test_append_partial_rewrite_and_numeric_only_encrypted_cache(self):
        original = self.path.read_bytes()
        state = self.base / "state"
        with hub.Store(state) as store:
            self.setup_store(store)
            first = self.refresh_usage(store)
            self.assertEqual(first["totals"]["tokens"], 105)
            self.assertEqual(first["pending"], 0)
            self.assertEqual(store.db.execute("SELECT count(*) FROM content").fetchone()[0], 0)
            with self.path.open("ab") as out:
                out.write(encoded([claude("bill-2")])[:-1])
            waiting = self.refresh_usage(store)
            self.assertEqual(waiting["totals"]["events"], 1)
            self.assertIn("incomplete tail or replay budget", waiting["coverage"])
            with self.path.open("ab") as out:
                out.write(b"\n")
            self.assertEqual(self.refresh_usage(store)["totals"]["events"], 2)
            # Rewrite prefix while growing: guard must reject accidental append.
            self.path.write_bytes(encoded([claude("bill-X"), claude("bill-Y"), claude("bill-Z")]))
            self.assertEqual(self.refresh_usage(store)["totals"]["events"], 3)
            raw = store.db.execute("SELECT v FROM kv WHERE k LIKE 'usage:file:%'").fetchone()[0]
            self.assertNotIn("DO NOT CACHE TEXT", raw)
            self.assertNotIn("bill-X", raw)
            self.assertFalse(store.get("profiles")[0]["content"])
        self.assertNotIn(b"test-model", (state / "state.hub").read_bytes())
        with hub.Store(state) as store:
            self.assertEqual(self.refresh_usage(store)["totals"]["events"], 3)
        self.assertTrue(original.startswith(b'{"type"'))

    def test_shared_profiles_exclusions_disable_and_clear(self):
        original = self.path.read_bytes()
        with hub.Store(self.base / "state") as store:
            self.setup_store(store)
            other = dict(self.profile, id="work", label="Work")
            hub.rpc(store, dict(action="profile-save", profile=other))
            hub.refresh(store)
            self.assertEqual(self.refresh_usage(store)["totals"]["events"], 1)
            profiles = store.get("profiles")
            profiles[0]["enabled"] = False
            profiles[1]["excluded"] = [str(self.root)]
            store.set("profiles", profiles)
            self.assertEqual(self.refresh_usage(store)["totals"]["events"], 0)
            hub.rpc(store, dict(action="usage-clear"))
            self.assertEqual(store.db.execute("SELECT count(*) FROM kv WHERE k LIKE 'usage:file:%'").fetchone()[0], 0)
        self.assertEqual(self.path.read_bytes(), original)

    def test_price_validation_and_compressed_rollout(self):
        with hub.Store(self.base / "state") as store:
            self.setup_store(store)
            for rate in (dict(input=-1), dict.fromkeys(usage.CHANNELS, float("nan")), dict.fromkeys(usage.CHANNELS, True)):
                with self.assertRaises(hub.HubError):
                    hub.rpc(store, dict(action="usage-price", rateProvider="claude", rateModel="test-model", rate=rate))
            hub.rpc(store, dict(action="usage-price", rateProvider="claude", rateModel="test-model", rate=dict.fromkeys(usage.CHANNELS, 1)))
            self.assertIsNotNone(self.refresh_usage(store)["totals"]["cost"])
            codex_root = self.base / "codex/sessions"
            codex_root.mkdir(parents=True)
            path = codex_root / ("rollout-date-" + ID + ".jsonl.zst")
            data = encoded([{"type": "session_meta", "payload": {"id": ID, "cwd": str(self.base), "cli_version": "0.164.0"}}, codex(tokens(), tokens())])
            path.write_bytes(zstd.compress(data))
            p = dict(self.profile, id="codex", provider="codex", roots=[str(codex_root)], configHome=str(codex_root.parent))
            hub.rpc(store, dict(action="profile-save", profile=p))
            hub.refresh(store)
            self.assertEqual(self.refresh_usage(store)["totals"]["tokens"], 225)

    def test_concurrent_mutation_discards_batch(self):
        with hub.Store(self.base / "state") as store:
            self.setup_store(store)
            native = hub.source_records
            def changing(*args, **kwargs):
                result = native(*args, **kwargs)
                with self.path.open("ab") as out:
                    out.write(b"\n")
                return result
            with patch.object(hub, "source_records", changing):
                result = self.refresh_usage(store)
            self.assertEqual(result["totals"]["events"], 0)
            self.assertIn("source unavailable or changed during read", result["coverage"])

    def test_separate_stores_do_not_merge_reused_native_or_billing_ids(self):
        other = self.base / "work/projects"
        other.mkdir(parents=True)
        (other / self.path.name).write_bytes(self.path.read_bytes())
        with hub.Store(self.base / "state") as store:
            self.setup_store(store)
            hub.rpc(store, dict(action="profile-save", profile=dict(self.profile, id="work", roots=[str(other)], configHome=str(other.parent))))
            hub.refresh(store)
            result = self.refresh_usage(store)
            self.assertEqual(result["totals"]["events"], 2)
            self.assertEqual(result["totals"]["sessions"], 2)
            selected = hub.rpc(store, dict(action="usage", profile="work", period="90d"))
            self.assertEqual(selected["totals"]["events"], 1)

    def test_record_budget_continues_even_when_byte_window_reaches_eof(self):
        # 10,001 small committed records fit in one byte window but not one parse batch.
        self.path.write_bytes(encoded([{"type":"ignored"}] * 10000 + [claude()]))
        with hub.Store(self.base / "state") as store:
            self.setup_store(store)
            # Initial discovery cannot see the trailing usage/version; expose a valid
            # synthetic metadata version at the beginning as a native file would.
            data = self.path.read_bytes()
            self.path.write_bytes(encoded([dict(type="user", sessionId=ID, version="2.1.322")])+data)
            hub.refresh(store)
            first = self.refresh_usage(store)
            self.assertEqual(first["pending"], 1)
            self.assertEqual(first["totals"]["events"], 0)
            second = self.refresh_usage(store)
            self.assertEqual(second["pending"], 0)
            self.assertEqual(second["totals"]["events"], 1)


if __name__ == "__main__":
    unittest.main()
