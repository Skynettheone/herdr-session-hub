import concurrent.futures
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import sqlite3
import sys
import tempfile
import time
import tracemalloc
import unittest
from unittest.mock import patch
from compression import zstd

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("hub", ROOT / "mods/session-hub/helper/hub.py")
hub = importlib.util.module_from_spec(spec)
spec.loader.exec_module(hub)
ID = "11111111-2222-4333-8444-555555555555"
OTHER = "aaaaaaaa-bbbb-4ccc-8ddd-eeeeeeeeeeee"


def encode(rows):
    return ("\n".join(json.dumps(x, ensure_ascii=False) for x in rows) + "\n").encode()


def fixture(provider, cwd, native=ID):
    at = "2026-10-01T10:00:00Z"
    if provider == "claude":
        return [{"type": "user", "sessionId": native, "cwd": str(cwd), "version": "2.1.322", "timestamp": at,
                 "message": {"content": "Build a café ; $(whoami) \u202e safe title"}},
                {"type": "assistant", "timestamp": at, "message": {"content": [{"type": "text", "text": "offline zephyr searchable response"}, {"type": "tool_use", "input": "DO NOT INDEX TOOL"}]}}]
    if provider == "codex":
        return [{"type": "session_meta", "payload": {"id": native, "cwd": str(cwd), "cli_version": "0.164.0", "source": "cli"}},
                {"type": "response_item", "timestamp": at, "payload": {"type": "message", "role": "user", "content": [{"type": "input_text", "text": "Build a café"}]}},
                {"type": "response_item", "timestamp": at, "payload": {"type": "message", "role": "assistant", "content": [{"type": "output_text", "text": "offline zephyr searchable response"}]}}]
    return [{"type": "session", "version": 3, "id": native, "cwd": str(cwd), "timestamp": at},
            {"type": "message", "id": "a", "parentId": None, "timestamp": at, "message": {"role": "user", "content": "Build a café"}},
            {"type": "message", "id": "b", "parentId": "a", "timestamp": at, "message": {"role": "assistant", "content": [{"type": "text", "text": "offline zephyr searchable response"}]}}]


class HubTests(unittest.TestCase):
    def setUp(self):
        (ROOT / ".dev/tests").mkdir(parents=True, exist_ok=True)
        self.tmp = tempfile.TemporaryDirectory(prefix="hub-test-", dir=ROOT / ".dev/tests")
        self.base = Path(self.tmp.name)
        self.cwd = self.base / "Café project (spaces)"
        self.cwd.mkdir()
        self.state = self.base / "hub-state"

    def tearDown(self):
        self.tmp.cleanup()

    def provider(self, provider="claude", native=ID, label="personal", content=False):
        config = self.base / label / provider
        root = config / ("projects" if provider == "claude" else "sessions")
        root.mkdir(parents=True, exist_ok=True)
        path = root / ({"claude": native + ".jsonl", "codex": "rollout-date-" + native + ".jsonl", "pi": "2026-10-01_" + native + ".jsonl"}[provider])
        path.write_bytes(encode(fixture(provider, self.cwd, native)))
        p = {"id": label + "-" + provider, "provider": provider, "label": label, "roots": [str(root)],
             "configHome": str(config), "executable": str(Path(sys.executable)), "content": content}
        return p, path

    def save(self, store, profile):
        hub.rpc(store, {"action": "profile-save", "profile": profile})

    def scan(self, store, profile, content=False):
        self.save(store, profile)
        hub.refresh(store, content)
        return store.get("records")[0]

    def additional_provider(self, provider, content=True):
        config = self.base / (".gemini" if provider == "gemini" else "copilot")
        root = config / ("tmp/project/chats" if provider == "gemini" else "session-state/" + ID)
        root.mkdir(parents=True)
        profile = {"id": provider, "provider": provider, "roots": [str(root)], "configHome": str(config),
                   "executable": "", "content": content}
        return profile, root / ("session-example.jsonl" if provider == "gemini" else "events.jsonl")

    def test_copilot_offline_events_and_unavailable_resume(self):
        profile, path = self.additional_provider("copilot")
        path.write_bytes(encode([
            {"type": "session.start", "data": {"sessionId": ID, "version": 1, "context": {"cwd": str(self.cwd)}}},
            {"id": "u", "type": "user.message", "timestamp": "2026-11-01T10:00:00Z", "data": {"content": "Copilot synthetic title"}},
            {"type": "tool.execution_complete", "data": {"content": "do not index tool"}},
            {"type": "assistant.message", "data": {"content": "do not index subagent", "parentToolCallId": "t"}},
            {"type": "assistant.message", "agentId": "subagent", "data": {"content": "do not index agent id"}},
            {"type": "session.context_changed", "agentId": "subagent", "data": {"cwd": "C:/incorrect"}},
            {"type": "assistant.message", "data": {"content": "zephyr visible response"}}
        ]))
        original = path.read_bytes()
        with hub.Store(self.state) as store:
            row = self.scan(store, profile, True)
            self.assertEqual(row["nativeId"], ID)
            self.assertEqual(row["cwd"], str(self.cwd))
            self.assertEqual(hub.list_records(store, {"query": "zephyr", "fullText": True})["total"], 1)
            preview = hub.preview(store, row["key"])
            self.assertEqual(len(preview["messages"]), 2)
            self.assertIn("not been verified", store.get("profiles")[0]["resumeDisabled"])
            with self.assertRaises(hub.HubError):
                hub.resume_spec(store, row["key"], profile["id"], lambda _: False)
        self.assertEqual(path.read_bytes(), original)

    def test_gemini_journal_replay_patches_rewind_and_project_mapping(self):
        profile, path = self.additional_provider("gemini")
        profile["projectPath"] = str(self.cwd)
        rows = [{"sessionId": ID, "projectHash": hashlib.sha256(str(self.cwd).encode()).hexdigest(), "kind": "main"},
                {"id": "u", "type": "user", "timestamp": "2026-11-01T10:00:00Z", "content": "Gemini synthetic title"},
                {"id": "a", "type": "gemini", "content": [{"text": "old zephyr response"}, {"functionCall": {"args": "do not index"}}]},
                {"$patch": {"id": "a", "content": [{"text": "new visible response"}]}},
                {"id": "removed", "type": "user", "content": "removed text"}, {"$rewindTo": "removed"}]
        path.write_bytes(encode(rows))
        with hub.Store(self.state) as store:
            row = self.scan(store, profile, True)
            self.assertEqual(row["cwd"], str(self.cwd))
            self.assertTrue(row["formatSupported"])
            self.assertEqual([m["text"] for m in hub.preview(store, row["key"])["messages"]], ["Gemini synthetic title", "new visible response"])
            self.assertEqual(hub.list_records(store, {"query": "zephyr", "fullText": True})["total"], 0)
            self.assertEqual(hub.list_records(store, {"query": "new visible", "fullText": True})["total"], 1)
            # Append operations can remove text: replace the indexed projection.
            path.write_bytes(encode(rows + [{"$patch": {"removeIds": ["a"]}}]))
            hub.refresh(store, True)
            self.assertEqual(hub.list_records(store, {"query": "new visible", "fullText": True})["total"], 0)
            hub.refresh(store)  # unchanged-file refresh must remain safe

    def test_gemini_legacy_json_unknown_cwd_and_oversized_fallback(self):
        profile, path = self.additional_provider("gemini")
        path = path.with_suffix(".json")
        record = {"sessionId": ID, "projectHash": "unknown", "directories": [str(self.cwd)],
                  "messages": [{"id": "u", "type": "user", "content": "legacy Gemini"}, {"id": "a", "type": "gemini", "content": "unique deleted response"}]}
        path.write_text(json.dumps(record))
        with hub.Store(self.state) as store:
            row = self.scan(store, profile, True)
            self.assertEqual(row["cwd"], "")
            self.assertEqual(hub.preview(store, row["key"])["messages"][0]["text"], "legacy Gemini")
            path.write_text(json.dumps({**record, "padding": "x" * (hub.CHUNK + 1)}))
            hub.refresh(store, True)
            row = next(r for r in store.get("records") if not r["stale"])
            self.assertFalse(row["formatSupported"])
            self.assertIn("metadata only", row["contentWarning"])
            self.assertTrue(hub.preview(store, row["key"])["partial"])
            self.assertEqual(hub.list_records(store, {"query": "unique deleted", "fullText": True})["total"], 0)
            self.assertTrue(next(r for r in store.get("records") if r["nativeId"] == ID)["stale"])

    def test_gemini_reordered_replaced_and_malformed_journals(self):
        replay = hub._adapters.gemini.replay
        rows = replay([{"sessionId": ID, "projectHash": "h"}, {"id": "a", "type": "user", "content": "a"},
                       {"id": "b", "type": "gemini", "content": "b"}, {"$patch": {"orderIds": ["a", "a"]}}])
        self.assertEqual([r.get("id") for r in rows[1:]], ["b", "a"])
        rows = replay([{"sessionId": ID}, {"id": "a"}, {"$set": {"messages": [{"id": "b", "type": "user"}]}}])
        self.assertEqual([r.get("id") for r in rows[1:]], ["b"])
        with self.assertRaises(ValueError):
            replay([{"$set": {"messages": [{"id": str(n)} for n in range(10000)]}}, {"id": "overflow"}])
        profile, path = self.additional_provider("gemini")
        path.write_bytes(encode([{"sessionId": ID, "projectHash": "h"}, {"$patch": {"updates": 42}}]))
        with hub.Store(self.state) as store:
            row = self.scan(store, profile)
            self.assertFalse(row["formatSupported"])
            self.assertGreater(row["malformed"], 0)

    def test_dpapi_atomic_backup_and_no_plaintext(self):
        with hub.Store(self.state) as store:
            store.set("sensitive", "SYNTHETIC PRIVATE CONTENT")
        self.assertNotIn(b"PRIVATE", (self.state / "state.hub").read_bytes())
        with hub.Store(self.state) as store:
            self.assertEqual(store.get("sensitive"), "SYNTHETIC PRIVATE CONTENT")
            store.set("next", True)
        self.assertTrue((self.state / "state.hub.bak").is_file())
        self.assertFalse(list(self.state.glob("*.tmp")))

    def test_shared_content_search_respects_profile_opt_out(self):
        opted_in, _ = self.provider(content=True)
        opted_out = {**opted_in, "id": "private-view", "content": False}
        with hub.Store(self.state) as store:
            self.save(store, opted_in)
            self.save(store, opted_out)
            hub.refresh(store, True)
            self.assertEqual(hub.list_records(store, {"query": "zephyr", "fullText": True, "profile": opted_out["id"]})["total"], 0)
            self.assertEqual(hub.list_records(store, {"query": "zephyr", "fullText": True, "profile": opted_in["id"]})["total"], 1)

    def test_content_terms_can_match_across_index_chunks(self):
        profile, _ = self.provider(content=True)
        with hub.Store(self.state) as store:
            row = self.scan(store, profile)
            for term in ("firstchunkword", "secondchunkword"):
                store.db.execute("INSERT INTO content VALUES (?,?)", (row["canonicalSourceIdentity"], term))
            self.assertEqual(hub.list_records(store, {"query": "firstchunkword secondchunkword", "fullText": True})["total"], 1)

    def test_record_budget_exhaustion_is_partial(self):
        profile, path = self.provider()
        rows = fixture("claude", self.cwd)[:1] + [{"type": "progress"}] * 10000
        rows += [{"type": "assistant", "timestamp": "2026-11-12T00:00:00Z", "message": {"content": "after record budget"}}]
        path.write_bytes(encode(rows))
        with hub.Store(self.state) as store:
            row = self.scan(store, profile)
            self.assertNotEqual(row["timestampCoverage"], "complete")
            self.assertTrue(hub.preview(store, row["key"])["partial"])

    def test_recovery_failure_keeps_current_state(self):
        with hub.Store(self.state) as store:
            store.set("keep", "original")
        with hub.Store(self.state) as store:
            store.set("newer", True)
        before = (self.state / "state.hub").read_bytes()
        with patch.object(hub, "atomic", side_effect=OSError("interrupted replacement")):
            with self.assertRaises(OSError):
                hub.recover(self.state)
        self.assertEqual((self.state / "state.hub").read_bytes(), before)

    def test_keep_local_never_applies_an_absent_annotation(self):
        profile, _ = self.provider()
        with hub.Store(self.state) as store:
            row = self.scan(store, profile)
            item = {"origin": "b" * 64, "provider": "claude", "nativeId": ID, "annotation": {"alias": "Incoming"}}
            portable_key = "foreign:" + hub.digest(item)
            store.set(portable_key, item)
            hub.rpc(store, {"action": "portable-apply", "key": row["key"], "portableKey": portable_key, "conflictChoice": "keep-local"})
            self.assertIsNone(store.get("annotation:" + row["key"]))

    def test_all_file_providers_original_hashes(self):
        for provider in ("claude", "codex", "pi"):
            with self.subTest(provider=provider):
                p, path = self.provider(provider)
                before = hashlib.sha256(path.read_bytes()).digest()
                with hub.Store(self.state / provider) as store:
                    row = self.scan(store, p)
                    self.assertEqual(row["nativeId"], ID)
                    self.assertEqual(row["cwd"], str(self.cwd))
                    self.assertTrue(row["formatSupported"])
                    self.assertGreaterEqual(len(hub.preview(store, row["key"])["messages"]), 2)
                    hub.rpc(store, {"action": "annotate", "key": row["key"], "alias": "Review", "archived": True})
                    self.assertEqual(len(hub.list_records(store, {"archived": True})["rows"]), 1)
                    for _ in range(3):
                        hub.refresh(store)
                    self.assertEqual(len(store.get("records")), 1)
                self.assertEqual(before, hashlib.sha256(path.read_bytes()).digest())

    def test_fts_opt_in_clear_and_backup_purge(self):
        p, path = self.provider(content=False)
        with hub.Store(self.state) as store:
            self.scan(store, p)
            self.assertEqual(hub.list_records(store, {"query": "zephyr", "fullText": True})["total"], 0)
            p["content"] = True
            self.save(store, p)
            hub.refresh(store, True)
            self.assertEqual(hub.list_records(store, {"query": "zephyr", "fullText": True})["total"], 1)
            self.assertEqual(hub.list_records(store, {"query": "DO NOT INDEX TOOL", "fullText": True})["total"], 0)
            hub.clear_content(store)
        for name in ("state.hub", "state.hub.bak"):
            db = sqlite3.connect(":memory:")
            db.deserialize(hub.protect((self.state / name).read_bytes(), True))
            self.assertEqual(db.execute("SELECT count(*) FROM content").fetchone()[0], 0)
            db.close()

    def test_append_incremental_search(self):
        p, path = self.provider(content=True)
        with hub.Store(self.state) as store:
            row = self.scan(store, p, True)
            offset = row["indexBytes"]
            with path.open("ab") as f:
                f.write(encode([{"type": "user", "timestamp": "2026-10-02T10:00:00Z", "message": {"content": "newlyappended"}}]))
            hub.refresh(store, True)
            row = store.get("records")[0]
            self.assertGreater(row["indexBytes"], offset)
            self.assertEqual(hub.list_records(store, {"query": "newlyappended", "fullText": True})["total"], 1)

    def test_partial_writer_malformed_and_unknown_metadata(self):
        p, path = self.provider()
        with path.open("ab") as f:
            f.write(b'bad JSON\n{"type":"user"')
        with hub.Store(self.state) as store:
            row = self.scan(store, p)
            self.assertEqual(row["nativeId"], ID)
            self.assertGreater(row["malformed"], 0)
            self.assertGreater(len(hub.preview(store, row["key"])["messages"]), 0)

    def test_credentials_never_candidates(self):
        p, path = self.provider()
        (path.parent / "auth.json").write_text("NEVER READ")
        (path.parent / "tokens.jsonl").write_text("NEVER READ")
        found, problems = hub.enumerate_sources(p)
        self.assertEqual([str(x[0]) for x in found], [str(path)])
        self.assertFalse(problems)

    def test_duplicate_native_ids_different_sources_and_shared_profiles(self):
        a, path = self.provider(label="personal")
        b, _ = self.provider(label="company")
        shared = {**a, "id": "shared", "label": "shared"}
        with hub.Store(self.state) as store:
            for p in (a, b, shared):
                self.save(store, p)
            hub.refresh(store)
            rows = store.get("records")
            self.assertEqual(len(rows), 2)
            self.assertEqual(sorted(len(r["targets"]) for r in rows), [1, 2])

    def test_mtime_is_not_conversation_activity(self):
        p, path = self.provider()
        with path.open("ab") as f:
            f.write(encode([{"type": "progress", "timestamp": "2026-11-12T10:00:00Z"}]))
        with hub.Store(self.state) as store:
            row = self.scan(store, p)
            self.assertTrue(row["lastConversationAt"].startswith("2026-10-01"))
            self.assertNotEqual(row["lastConversationAt"], row["fileModifiedAt"])

    def test_zstd_and_corruption_ratio_limits(self):
        p, path = self.provider("codex")
        data = path.read_bytes()
        path.unlink()
        compressed = path.with_suffix(".jsonl.zst")
        compressed.write_bytes(zstd.compress(data))
        with hub.Store(self.state) as store:
            row = self.scan(store, p)
            self.assertEqual(row["nativeId"], ID)
            self.assertEqual(len(hub.preview(store, row["key"])["messages"]), 2)
            compressed.write_bytes(b"invalid zstd")
            hub.refresh(store)
            self.assertEqual(len(store.get("records")), 1)
            self.assertEqual(store.get("statuses")[0]["state"], "partial")
        compressed.write_bytes(zstd.compress(b"A" * (8 * hub.CHUNK)))
        with self.assertRaises(hub.HubError):
            hub.read_window(compressed, 0, 4 * hub.CHUNK)

    def test_concatenated_zstd_frames_and_partial_compressed_input(self):
        p, path = self.provider("codex")
        rows = fixture("codex", self.cwd)
        compressed = path.with_suffix(".jsonl.zst")
        compressed.write_bytes(zstd.compress(encode(rows[:1])) + zstd.compress(encode(rows[1:])))
        decoded, eof = hub.read_window(compressed)
        self.assertTrue(eof)
        self.assertEqual(decoded, encode(rows))
        compressed.write_bytes(compressed.read_bytes()[:-8])
        with self.assertRaises(hub.HubError):
            hub.read_window(compressed)

    def test_large_incremental_content_and_huge_line_skip(self):
        p, path = self.provider(content=True)
        with path.open("ab") as f:
            f.write(b"x" * (hub.CHUNK * 2) + b"\n")
            f.write(encode([{"type": "user", "message": {"content": "afterhugeentry"}}]))
        with hub.Store(self.state) as store:
            self.scan(store, p, True)
            for _ in range(6):
                hub.refresh(store, True)
            self.assertTrue(store.get("file:" + store.get("records")[0]["canonicalSourceIdentity"])["complete"])
            self.assertFalse(store.get("records")[0]["indexComplete"], "oversized omitted records are not complete coverage")
            self.assertEqual(hub.list_records(store, {"query": "afterhugeentry", "fullText": True})["total"], 1)

    def test_native_version_fingerprint_blocks_update(self):
        p, path = self.provider()
        with hub.Store(self.state) as store:
            row = self.scan(store, p)
            profiles = store.get("profiles")
            profiles[0].update(versionVerified=True, trustedProjects=[str(self.cwd)], verifiedExecutableStamp=["outdated"])
            store.set("profiles", profiles)
            with self.assertRaisesRegex(hub.HubError, "executable changed"):
                hub.resume_spec(store, row["key"], p["id"], lambda _: False)

    def test_sparse_gigabyte_and_large_metadata_bounded(self):
        p, path = self.provider()
        for size in (50 * 1024**2, 100 * 1024**2, 1024**3 + 1):
            with path.open("r+b") as f:
                import ctypes, msvcrt
                kernel = ctypes.WinDLL("kernel32", use_last_error=True)
                kernel.DeviceIoControl.argtypes = [ctypes.c_void_p, ctypes.c_ulong, ctypes.c_void_p, ctypes.c_ulong, ctypes.c_void_p, ctypes.c_ulong, ctypes.c_void_p, ctypes.c_void_p]
                returned = ctypes.c_ulong()
                self.assertTrue(kernel.DeviceIoControl(msvcrt.get_osfhandle(f.fileno()), 0x900c4, None, 0, None, 0, ctypes.byref(returned), None))
                f.seek(size)
                f.write(b'\n{"type":"progress"}\n')
            tracemalloc.start()
            with hub.Store(self.state) as store:
                row = self.scan(store, p)
                self.assertEqual(row["nativeId"], ID)
                self.assertEqual(row["timestampCoverage"], "partial head/tail")
                self.assertTrue(hub.preview(store, row["key"])["partial"])
            _, peak = tracemalloc.get_traced_memory()
            tracemalloc.stop()
            self.assertLess(peak, 25 * 1024**2)

    def test_junction_symlink_and_hardlink_refusal(self):
        p, path = self.provider()
        linked = path.with_name(OTHER + ".jsonl")
        os.link(path, linked)
        found, problems = hub.enumerate_sources(p)
        self.assertEqual(found, [])
        self.assertEqual(problems["unreadable"], 2)
        with self.assertRaises(hub.HubError):
            hub.source_file(linked, p["roots"][0])

    def test_path_rejection(self):
        for value in ("relative/path", "C:\\", str(Path.home()), "\\\\server\\share", "C:\\bad\npath"):
            with self.subTest(value=value), self.assertRaises(hub.HubError):
                hub.approved_root(value)

    def test_long_unicode_source_path(self):
        config = self.base.joinpath(*(["Café long project directory"] * 8)) / "claude"
        root = config / "projects"
        root.mkdir(parents=True)
        path = root / (ID + ".jsonl")
        path.write_bytes(encode(fixture("claude", self.cwd)))
        self.assertGreater(len(str(path)), 260)
        p = {"id": "long", "provider": "claude", "roots": [str(root)], "configHome": str(config), "executable": sys.executable}
        with hub.Store(self.state) as store:
            row = self.scan(store, p)
            self.assertEqual(row["nativeId"], ID)
            self.assertEqual(len(hub.preview(store, row["key"])["messages"]), 2)

    def test_resume_exact_vector_profile_and_guards(self):
        for provider in ("claude", "codex", "pi"):
            with self.subTest(provider=provider), hub.Store(self.state / provider) as store:
                p, path = self.provider(provider)
                row = self.scan(store, p)
                profiles = store.get("profiles")
                profiles[0].update(versionVerified=True, trustedProjects=[str(self.cwd)], verifiedExecutableStamp=hub.file_stamp(Path(p["executable"])))
                store.set("profiles", profiles)
                command = hub.resume_spec(store, row["key"], p["id"], lambda _: False)
                suffix = ["--resume", ID] if provider == "claude" else ["resume", ID] if provider == "codex" else ["--session", str(path)]
                self.assertEqual(command["argv"], [p["executable"], *suffix])
                self.assertEqual(command["cwd"], str(self.cwd))
                for active in (True, None):
                    with self.assertRaises(hub.HubError):
                        hub.resume_spec(store, row["key"], p["id"], lambda _: active)
                with self.assertRaises(hub.HubError):
                    hub.resume_spec(store, row["key"], "wrong-profile", lambda _: False)
                with path.open("ab") as f:
                    f.write(b"\n")
                with self.assertRaises(hub.HubError):
                    hub.resume_spec(store, row["key"], p["id"], lambda _: False)

    def test_unsupported_versions_and_untrusted_project(self):
        p, path = self.provider()
        data = path.read_bytes().replace(b"2.1.322", b"9.0.000")
        path.write_bytes(data)
        with hub.Store(self.state) as store:
            row = self.scan(store, p)
            self.assertFalse(row["formatSupported"])
            with self.assertRaises(hub.HubError):
                hub.resume_spec(store, row["key"], p["id"], lambda _: False)
            with self.assertRaises(hub.HubError):
                hub.rpc(store, {"action": "trust-project", "key": row["key"], "profile": p["id"], "confirmation": "wrong"})

    def test_pi_active_branch_and_cycle(self):
        p, path = self.provider("pi")
        rows = fixture("pi", self.cwd)
        rows += [{"type": "message", "id": "c", "parentId": "a", "message": {"role": "assistant", "content": "active branch"}}]
        path.write_bytes(encode(rows))
        with hub.Store(self.state) as store:
            row = self.scan(store, p)
            preview = hub.preview(store, row["key"])
            self.assertEqual(preview["messages"][-1]["text"], "active branch")
            self.assertNotIn("offline zephyr", str(preview["messages"]))
            rows[-1]["parentId"] = "c"
            path.write_bytes(encode(rows))
            with self.assertRaises(hub.HubError):
                hub.preview(store, row["key"])

    def test_profile_env_injection_and_custom_root(self):
        p, path = self.provider()
        for env in ({"OPENAI_API_KEY": "forbidden"}, {"CLAUDE_CONFIG_DIR": str(self.cwd)}):
            with self.assertRaises(hub.HubError):
                hub.profile_validate({**p, "env": env})
        with self.assertRaises(hub.HubError):
            hub.profile_validate({**p, "executable": "cmd /c arbitrary"})
        self.assertIn("resumeDisabled", hub.profile_validate({**p, "roots": [str(self.cwd)]}))

    def test_missing_cli_does_not_hide_history(self):
        p, path = self.provider()
        p["executable"] = str(self.base / "missing.exe")
        with hub.Store(self.state) as store:
            row = self.scan(store, p)
            self.assertEqual(row["nativeId"], ID)
            self.assertFalse(store.get("statuses")[0]["cliInstalled"])
            self.assertEqual(len(hub.preview(store, row["key"])["messages"]), 2)
            with self.assertRaises(hub.HubError):
                hub.resume_spec(store, row["key"], p["id"], lambda _: False)

    def test_account_environment_is_not_silently_inherited(self):
        with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "SYNTHETIC", "OPENAI_BASE_URL": "https://invalid.example", "CLAUDE_CONFIG_DIR": "wrong", "HC_TERMINAL_ID": "test-keep"}):
            env = hub.profile_environment({"CLAUDE_CONFIG_DIR": str(self.cwd)})
            self.assertNotIn("ANTHROPIC_API_KEY", env)
            self.assertNotIn("OPENAI_BASE_URL", env)
            self.assertEqual(env["CLAUDE_CONFIG_DIR"], str(self.cwd))
            self.assertEqual(env["HC_TERMINAL_ID"], "test-keep")

    def test_refresh_batches_new_sources_and_missing_stale(self):
        p, path = self.provider()
        for n in range(269):
            native = str(__import__("uuid").uuid5(__import__("uuid").NAMESPACE_URL, str(n)))
            (path.parent / (native + ".jsonl")).write_bytes(encode(fixture("claude", self.cwd, native)))
        with hub.Store(self.state) as store:
            self.save(store, p)
            for expected in (142, 14, 0):
                result = hub.refresh(store)
                self.assertEqual(result["statuses"][0]["remaining"], expected)
            self.assertEqual(len(store.get("records")), 270)
            path.unlink()
            hub.refresh(store)
            old = next(r for r in store.get("records") if r["nativeId"] == ID)
            self.assertTrue(old["stale"])

    def test_disabled_dangerous_actions(self):
        with hub.Store(self.state) as store:
            for action in ("delete-original", "native-import", "remote-sync"):
                with self.assertRaises(hub.HubError):
                    hub.rpc(store, {"action": action})

    def test_encrypted_portable_roundtrip_wrong_key_tamper_conflict(self):
        p, path = self.provider()
        with hub.Store(self.state) as store:
            row = self.scan(store, p)
            hub.rpc(store, {"action": "annotate", "key": row["key"], "alias": "Portable alias"})
            manifest = hub.metadata_manifest(store)
            blob = hub.portable_encrypt(manifest, "synthetic passphrase 123")
            self.assertNotIn(b"Portable alias", blob)
            self.assertNotIn(str(path).encode(), json.dumps(manifest).encode())
            decoded = hub.portable_decrypt(blob, "synthetic passphrase 123")
            self.assertEqual(manifest, decoded)
            for corrupt, password in ((blob, "wrong"), (blob[:-1], "synthetic passphrase 123"), (blob[:40], "synthetic passphrase 123")):
                with self.assertRaises(hub.HubError):
                    hub.portable_decrypt(corrupt, password)
            hub.rpc(store, {"action": "annotate", "key": row["key"], "alias": "Local edit"})
            self.assertEqual(hub.merge_manifest(store, manifest)["conflicts"], 1)
            self.assertEqual(store.get("annotation:" + row["key"])["alias"], "Local edit")
            hub.merge_manifest(store, manifest, True)
            self.assertEqual(store.get("annotation:" + row["key"])["alias"], "Local edit")
        with hub.Store(self.state / "foreign") as store:
            self.assertEqual(hub.merge_manifest(store, manifest, True)["foreign"], 1)
            self.assertIsNone(store.get("records"))

    def test_schema_upgrade_crash_keeps_previous(self):
        with hub.Store(self.state) as store:
            store.set("schema", 1)
            store.set("kept", "yes")
        before = (self.state / "state.hub").read_bytes()
        with self.assertRaises(OSError), patch.object(hub.os, "replace", side_effect=OSError("interrupted")):
            with hub.Store(self.state) as store:
                store.set("new", True)
        self.assertEqual(before, (self.state / "state.hub").read_bytes())
        with hub.Store(self.state) as store:
            self.assertEqual(store.get("schema"), 2)
            self.assertEqual(store.get("kept"), "yes")

    def test_corrupt_state_refuses_silent_reset(self):
        self.state.mkdir()
        path = self.state / "state.hub"
        path.write_bytes(b"corrupt")
        with self.assertRaises(hub.HubError):
            with hub.Store(self.state):
                pass
        self.assertEqual(path.read_bytes(), b"corrupt")

    def test_recovery_preserves_damaged_evidence_and_blocks_active_helper(self):
        with hub.Store(self.state) as store:
            store.set("kept", True)
        with hub.Store(self.state) as store:
            store.set("newer", True)
            with self.assertRaises(hub.HubError):
                hub.recover(self.state)
        (self.state / "state.hub").write_bytes(b"damaged")
        hub.recover(self.state)
        with hub.Store(self.state) as store:
            self.assertTrue(store.get("kept"))
        evidence = list(self.state.glob("damaged-*.hub"))
        self.assertEqual(len(evidence), 1)
        self.assertEqual(evidence[0].read_bytes(), b"damaged")

    def test_same_store_collision_and_provider_reconfiguration(self):
        p, path = self.provider("codex")
        twin = path.with_name("rollout-other-" + ID + ".jsonl")
        twin.write_bytes(path.read_bytes())
        with hub.Store(self.state) as store:
            self.scan(store, p)
            self.assertEqual(len(store.get("records")), 2)
            self.assertTrue(all(r["collision"] for r in store.get("records")))
            p["provider"] = "pi"
            self.save(store, p)
            self.assertEqual(store.get("records"), [])

    def test_portable_metadata_explicit_binding(self):
        p, path = self.provider()
        with hub.Store(self.state) as store:
            row = self.scan(store, p)
            portable = {"origin": "b" * 64, "provider": "claude", "nativeId": ID, "annotation": {"alias": "Incoming"}}
            key = "foreign:" + hub.digest(portable)
            store.set(key, portable)
            self.assertEqual(hub.rpc(store, {"action": "portable-list"})["foreign"][0]["alias"], "Incoming")
            hub.rpc(store, {"action": "annotate", "key": row["key"], "alias": "Local"})
            with self.assertRaises(hub.HubError):
                hub.rpc(store, {"action": "portable-apply", "key": row["key"], "portableKey": key})
            hub.rpc(store, {"action": "portable-apply", "key": row["key"], "portableKey": key, "conflictChoice": "use-imported"})
            self.assertEqual(store.get("annotation:" + row["key"])["alias"], "Incoming")

    def test_parallel_state_writers(self):
        def write(number):
            with hub.Store(self.state) as store:
                store.set("writer:" + str(number), True)
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
            list(pool.map(write, range(8)))
        with hub.Store(self.state) as store:
            self.assertTrue(all(store.get("writer:" + str(n)) for n in range(8)))

    def opencode(self):
        root = self.base / "data" / "opencode"
        root.mkdir(parents=True)
        config = self.base / "config" / "opencode"
        config.mkdir(parents=True)
        path = root / "opencode.db"
        db = sqlite3.connect(path)
        db.executescript('''CREATE TABLE session(id TEXT,title TEXT,directory TEXT,time_created INTEGER,time_updated INTEGER,version TEXT,parent_id TEXT);
            CREATE TABLE message(id TEXT,session_id TEXT,time_created INTEGER,data TEXT);
            CREATE TABLE part(id TEXT,message_id TEXT,session_id TEXT,time_created INTEGER,data TEXT);''')
        db.execute("INSERT INTO session VALUES (?,?,?,?,?,?,NULL)", ("ses_synthetic123", "OpenCode fixture", str(self.cwd), 1790848800000, 1790848800000, "1.3.17"))
        db.execute("INSERT INTO message VALUES (?,?,?,?)", ("m1", "ses_synthetic123", 1790848800000, json.dumps({"role": "user"})))
        db.execute("INSERT INTO part VALUES (?,?,?,?,?)", ("p1", "m1", "ses_synthetic123", 1790848800000, json.dumps({"type": "text", "text": "OpenCode zephyr content"})))
        db.commit()
        db.close()
        p = {"id": "opencode", "provider": "opencode", "roots": [str(root)], "configHome": str(config), "executable": sys.executable, "content": True}
        return p, path

    def test_opencode_read_only_preview_search_and_live_wal(self):
        p, path = self.opencode()
        before = path.read_bytes()
        before_files = sorted(x.name for x in path.parent.iterdir())
        with hub.Store(self.state) as store:
            row = self.scan(store, p, True)
            self.assertEqual(row["nativeId"], "ses_synthetic123")
            self.assertEqual(hub.preview(store, row["key"])["messages"][0]["role"], "user")
            self.assertEqual(hub.list_records(store, {"query": "zephyr", "fullText": True})["total"], 1)
            self.assertEqual(path.read_bytes(), before)
            self.assertEqual(sorted(x.name for x in path.parent.iterdir()), before_files)
            path.with_name("opencode.db-wal").write_bytes(b"live WAL")
            hub.refresh(store)
            self.assertTrue(store.get("records")[0]["stale"])
            self.assertEqual(store.get("statuses")[0]["state"], "unavailable")

    def test_ten_thousand_records_search_pagination(self):
        with hub.Store(self.state) as store:
            records = [{"key": hub.digest(n), "provider": "claude", "targets": ["p"], "nativeId": ID,
                        "title": "Session " + str(n), "cwd": str(self.cwd), "canonicalSourceIdentity": str(n),
                        "lastConversationAt": "2026-10-01T10:00:00+00:00"} for n in range(10000)]
            store.set("records", records)
            start = time.perf_counter()
            page = hub.list_records(store, {"offset": 60})
            elapsed = time.perf_counter() - start
            self.assertEqual(page["total"], 10000)
            self.assertEqual(len(page["rows"]), 60)
            self.assertLess(elapsed, 5)
            print(f"PERF 10000 records: list/search page {elapsed:.3f}s")


if __name__ == "__main__":
    unittest.main(verbosity=2)
