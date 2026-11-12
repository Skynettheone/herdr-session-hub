"""Session Hub: offline, read-only provider adapters and Hub-owned encrypted state.

No provider module is imported; no provider command runs during discovery.
Python 3.14 is required for the standard-library zstd reader.
"""
from __future__ import annotations

import argparse
import contextlib
import ctypes
from ctypes import wintypes
import datetime as dt
import getpass
import importlib.util
import hashlib
import io
import json
import os
from pathlib import Path
import re
import shutil
import sqlite3
import stat
import subprocess
import sys
import time
import unicodedata
import uuid
from compression import zstd

SCHEMA = 2
PARSER = 4
CHUNK = 2 * 1024 * 1024
LINE = 1024 * 1024
MAX_STATE = 256 * 1024 * 1024
MAX_FILES = 20000
UUID = re.compile(r"[0-9a-f]{8}(?:-[0-9a-f]{4}){3}-[0-9a-f]{12}", re.I)
KEY = re.compile(r"[0-9a-f]{64}")
PROVIDERS = ("claude", "codex", "opencode", "pi", "copilot", "gemini")
SECRET_NAMES = {"auth.json", "credentials.json", "config.json", "settings.json", "config.toml", "tokens.json", ".env"}
ENV_NAMES = {"claude": {"CLAUDE_CONFIG_DIR"}, "codex": {"CODEX_HOME"},
             "pi": {"PI_CODING_AGENT_DIR", "PI_CODING_AGENT_SESSION_DIR"},
             "opencode": {"XDG_DATA_HOME", "XDG_CONFIG_HOME"},
             "copilot": {"COPILOT_HOME"}, "gemini": {"GEMINI_CLI_HOME"}}


# Isolated Python (-I) deliberately excludes the script directory from sys.path.
# Load only this shipped package by its fixed absolute path, without exposing
# user roots, cwd or provider installation directories to Python imports.
_adapter_spec = importlib.util.spec_from_file_location("session_hub_adapters", Path(__file__).parent / "adapters/__init__.py")
_adapters = importlib.util.module_from_spec(_adapter_spec)
sys.modules[_adapter_spec.name] = _adapters
_adapter_spec.loader.exec_module(_adapters)
clean, redact, timestamp, text_blocks = _adapters.clean, _adapters.redact, _adapters.timestamp, _adapters.text_blocks
parse_record = _adapters.parse_record


class HubError(Exception):
    """Only fixed, privacy-safe error messages are returned to the UI."""


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=True).encode()).hexdigest()



def is_link(path):
    s = path.lstat()
    return stat.S_ISLNK(s.st_mode) or bool(getattr(s, "st_file_attributes", 0) & 0x400)


def local_path(value, directory=False):
    if not isinstance(value, str) or not value or len(value) > 32000 or any(ord(c) < 32 for c in value):
        raise HubError("Invalid path")
    p = Path(value)
    if not p.is_absolute() or value.startswith(("\\\\", "//")):
        raise HubError("Only absolute local paths are supported; UNC and WSL are disabled")
    # Reject every reparse component, including ancestors of the approved root.
    for part in [p, *p.parents]:
        if part.exists() and is_link(part):
            raise HubError("Symlink or reparse-point paths are disabled")
    if directory and not p.is_dir():
        raise HubError("Directory is missing or inaccessible")
    return p


def approved_root(value):
    p = local_path(value, True)
    if p == Path(p.anchor) or p.resolve() == Path.home().resolve() or len(p.parts) < 3:
        raise HubError("Choose a narrow session directory, not a home or drive")
    return p


def source_file(path, root):
    p = local_path(str(path))
    r = approved_root(str(root))
    try:
        p.resolve(strict=True).relative_to(r.resolve(strict=True))
    except (ValueError, OSError):
        raise HubError("Source is outside the approved root or missing") from None
    if p.name.lower() in SECRET_NAMES or not p.is_file() or p.stat().st_nlink > 1:
        raise HubError("Credential, non-file, or hard-linked source refused")
    return p


def file_stamp(path):
    s = path.stat()
    return [s.st_dev, str(s.st_ino), s.st_size, s.st_mtime_ns, getattr(s, "st_birthtime_ns", 0)]


def physical(path):
    s = path.stat()
    return [s.st_dev, str(s.st_ino)] if s.st_ino else [os.path.normcase(str(path.resolve()))]


def protect(data, decrypt=False):
    if os.name != "nt":
        raise HubError("Encrypted local state requires Windows DPAPI in this build")
    class Blob(ctypes.Structure):
        _fields_ = [("cbData", wintypes.DWORD), ("pbData", ctypes.POINTER(ctypes.c_ubyte))]
    buf = (ctypes.c_ubyte * len(data)).from_buffer_copy(data)
    src, dst = Blob(len(data), buf), Blob()
    lib = ctypes.WinDLL("crypt32", use_last_error=True)
    kernel = ctypes.WinDLL("kernel32", use_last_error=True)
    kernel.LocalFree.argtypes = [ctypes.c_void_p]
    kernel.LocalFree.restype = ctypes.c_void_p
    if decrypt:
        ok = lib.CryptUnprotectData(ctypes.byref(src), None, None, None, None, 1, ctypes.byref(dst))
    else:
        ok = lib.CryptProtectData(ctypes.byref(src), "Herdr Session Hub", None, None, None, 1, ctypes.byref(dst))
    if not ok:
        raise HubError("Encrypted state could not be opened; keep the backup and use recovery")
    try:
        return ctypes.string_at(dst.pbData, dst.cbData)
    finally:
        kernel.LocalFree(dst.pbData)


def atomic(path, data, backup=False):
    # Caller holds the cross-process state lock. Never target provider directories.
    if path.exists() and is_link(path):
        raise HubError("Linked state target refused")
    tmp = path.with_name(path.name + "." + uuid.uuid4().hex + ".tmp")
    try:
        with tmp.open("xb") as f:
            f.write(data)
            f.flush()
            os.fsync(f.fileno())
        if backup and path.exists():
            previous = path.with_name(path.name + ".bak")
            if previous.exists() and is_link(previous):
                raise HubError("Linked backup refused")
            shutil.copyfile(path, previous)
        os.replace(tmp, path)
    finally:
        tmp.unlink(missing_ok=True)


class Store:
    def __init__(self, root):
        self.root = local_path(str(root))
        self.root.mkdir(parents=True, exist_ok=True)
        self.path = self.root / "state.hub"
        self.lock = None

    def __enter__(self):
        import msvcrt
        lockpath = self.root / "state.lock"
        if lockpath.exists() and is_link(lockpath):
            raise HubError("Linked state lock refused")
        self.lock = lockpath.open("a+b")
        # Windows allows locking beyond EOF; never read/write a byte another
        # process may currently have locked while acquiring this mutex.
        end = time.monotonic() + 8
        while True:
            try:
                self.lock.seek(0)
                msvcrt.locking(self.lock.fileno(), msvcrt.LK_NBLCK, 1)
                break
            except OSError:
                if time.monotonic() >= end:
                    self.lock.close()
                    raise HubError("Another Hub operation is running; retry shortly") from None
                time.sleep(0.05)
        self.db = sqlite3.connect(":memory:")
        try:
            if self.path.exists():
                if is_link(self.path) or self.path.stat().st_size > MAX_STATE:
                    raise HubError("State size or path is unsafe")
                self.db.deserialize(protect(self.path.read_bytes(), True))
            elif self.path.with_name("state.hub.bak").exists():
                raise HubError("Current state is missing but a backup exists; run offline recovery")
            self.db.execute("CREATE TABLE IF NOT EXISTS kv (k TEXT PRIMARY KEY,v TEXT NOT NULL)")
            version = self.get("schema", SCHEMA)
            if version not in (1, SCHEMA):
                raise HubError("Newer state schema; restore the matching Hub version")
            # v1 -> v2 adds receipts; old encrypted state is backed up on commit.
            self.set("schema", SCHEMA)
            self.db.execute("CREATE VIRTUAL TABLE IF NOT EXISTS content USING fts5(k UNINDEXED, text, tokenize='unicode61 remove_diacritics 2')")
            self.dirty = version != SCHEMA
            return self
        except Exception:
            self.__exit__(*sys.exc_info())
            raise

    def get(self, key, default=None):
        r = self.db.execute("SELECT v FROM kv WHERE k=?", (key,)).fetchone()
        return json.loads(r[0]) if r else default

    def set(self, key, value):
        self.db.execute("INSERT OR REPLACE INTO kv VALUES (?,?)", (key, json.dumps(value, ensure_ascii=True)))
        self.dirty = True

    def save(self):
        self.db.commit()
        data = protect(self.db.serialize())
        if len(data) > MAX_STATE:
            raise HubError("Encrypted index reached its 256 MiB limit; clear content or exclude profiles")
        atomic(self.path, data, True)
        if getattr(self, "purge_backup", False):
            atomic(self.path.with_name("state.hub.bak"), data)
        self.dirty = False

    def __exit__(self, typ, value, tb):
        try:
            if typ is None and self.dirty:
                self.save()
        finally:
            if hasattr(self, "db"):
                self.db.close()
            if self.lock:
                import msvcrt
                self.lock.seek(0)
                msvcrt.locking(self.lock.fileno(), msvcrt.LK_UNLCK, 1)
                self.lock.close()



def read_window(path, offset=0, budget=CHUNK):
    """Bounded read; zstd has a finite replay and ratio budget, no unbounded seek."""
    if path.suffix == ".zst":
        if offset + budget > 64 * CHUNK:
            raise HubError("Compressed content exceeds the bounded replay window; metadata remains visible")
        result = bytearray()
        decoder = zstd.ZstdDecompressor(options={zstd.DecompressionParameter.window_log_max: 23})
        total_in = total_out = 0
        pending = b""
        complete = False
        with path.open("rb") as f:
            while total_out < offset + budget:
                if pending:
                    chunk, pending = pending, b""
                elif decoder.needs_input:
                    chunk = f.read(65536)
                    total_in += len(chunk)
                else:
                    chunk = b""
                if not chunk and decoder.needs_input:
                    if not complete:
                        raise HubError("Truncated compressed rollout")
                    break
                out = decoder.decompress(chunk, max_length=min(65536, offset + budget - total_out))
                begin = max(0, offset - total_out)
                result.extend(out[begin:])
                total_out += len(out)
                if total_in > 8 * CHUNK or total_out > max(CHUNK, total_in * 200):
                    raise HubError("Compressed input exceeded size or ratio limits")
                if decoder.eof:
                    pending = decoder.unused_data
                    complete = not pending and f.tell() == path.stat().st_size
                    if complete:
                        break
                    decoder = zstd.ZstdDecompressor(options={zstd.DecompressionParameter.window_log_max: 23})
        return bytes(result), complete
    with path.open("rb") as f:
        f.seek(offset)
        data = f.read(budget)
    return data, offset + len(data) >= path.stat().st_size


def records_in(data, eof=False, skip=False):
    """Never parse a writer's unterminated last record. Return committed offset."""
    end = data.rfind(b"\n") + 1
    malformed = oversized = 0
    rows = []
    consumed = 0
    stream = io.BytesIO(data[:end])
    for index, line in enumerate(stream):
        if index >= 10000:
            end = consumed
            break
        consumed += len(line)
        if skip:
            skip = False
            continue
        if len(line) > LINE:
            oversized += 1
            continue
        try:
            x = json.loads(line)
            if isinstance(x, dict):
                rows.append(x)
            else:
                malformed += 1
        except (ValueError, UnicodeError, RecursionError):
            malformed += 1
    if end == 0 and len(data) >= CHUNK:
        # Carry a skip flag until newline; advance without retaining giant lines.
        return [], len(data), True, malformed, oversized + (not skip)
    return rows, end, skip, malformed, oversized


def candidate(provider, name):
    if name.lower() in SECRET_NAMES:
        return False
    if provider == "claude":
        return name.endswith(".jsonl") and bool(UUID.fullmatch(name[:-6]))
    if provider == "codex":
        return name.startswith("rollout-") and name.endswith((".jsonl", ".jsonl.zst"))
    if provider == "copilot":
        return name == "events.jsonl"
    if provider == "gemini":
        return name.startswith("session-") and name.endswith((".json", ".jsonl"))
    return provider == "pi" and name.endswith(".jsonl") and bool(UUID.search(name[:-6]))


def enumerate_sources(profile):
    out, problems, seen, visited = [], {}, set(), 0
    for root in profile["roots"]:
        try:
            r = approved_root(root)
            stack = [(r, 0)]
            while stack:
                folder, depth = stack.pop()
                if depth > 8:
                    problems["depthLimit"] = problems.get("depthLimit", 0) + 1
                    continue
                with os.scandir(folder) as entries:
                    for entry in entries:
                        visited += 1
                        if visited > MAX_FILES * 8 or len(out) >= MAX_FILES:
                            problems["enumerationLimit"] = 1
                            return out, problems
                        p = Path(entry.path)
                        if entry.name.startswith(".") or entry.name.lower() in {"subagents", "node_modules", "auth", "credentials"}:
                            continue
                        try:
                            if is_link(p):
                                problems["reparseSkipped"] = problems.get("reparseSkipped", 0) + 1
                                continue
                            if entry.is_dir(follow_symlinks=False):
                                stack.append((p, depth + 1))
                            elif candidate(profile["provider"], entry.name):
                                if profile["provider"] == "copilot" and not UUID.fullmatch(p.parent.name):
                                    continue
                                if profile["provider"] == "gemini" and p.parent.name != "chats":
                                    continue
                                p = source_file(p, r)
                                ident = digest(physical(p))
                                if ident not in seen and not any(p.is_relative_to(Path(e)) for e in profile.get("excluded", [])):
                                    seen.add(ident)
                                    out.append((p, root))
                        except (OSError, HubError):
                            problems["unreadable"] = problems.get("unreadable", 0) + 1
        except (OSError, HubError):
            problems["rootUnavailable"] = problems.get("rootUnavailable", 0) + 1
    return sorted(out, key=lambda x: os.path.normcase(str(x[0]))), problems


def profile_validate(p):
    if not isinstance(p, dict) or p.get("provider") not in PROVIDERS or not re.fullmatch(r"[a-zA-Z0-9_-]{1,60}", p.get("id", "")):
        raise HubError("Invalid provider or profile ID")
    p = dict(p)
    p.pop("resumeDisabled", None)
    roots = p.get("roots", [])
    if not isinstance(roots, list) or not 1 <= len(roots) <= 8:
        raise HubError("Choose one to eight narrow roots")
    for root in roots:
        approved_root(root)
    env = p.get("env", {})
    if not isinstance(env, dict) or not set(env).issubset(ENV_NAMES[p["provider"]]):
        raise HubError("Only provider directory environment mappings are permitted")
    for value in env.values():
        local_path(value, True)
    raw_exe = p.get("executable", "")
    if not isinstance(raw_exe, str) or (raw_exe and not Path(raw_exe).is_absolute()):
        raise HubError("Choose an absolute native executable path")
    # Pin user-selected executable aliases; history roots remain link-free.
    exe = local_path(str(Path(raw_exe).resolve(strict=False))) if raw_exe else None
    if exe and exe.suffix.lower() != ".exe":
        raise HubError("Choose an installed native .exe; shell scripts and command strings are disabled")
    # Prevent accidental cross-profile resume. Config-home ownership is explicit.
    config = local_path(p.get("configHome", ""), True)
    script = p.get("launchScript")
    if script:
        allowed = {"pi": "pi-launcher.js", "gemini": "gemini.js"}.get(p["provider"])
        if not allowed or not exe or exe.name.lower() != "node.exe" or Path(script).name != allowed or not local_path(script).is_file():
            raise HubError("Only a supported provider's explicit native Node launcher is allowed as a script target")
    for root in roots:
        if p["provider"] in ("claude", "codex", "pi"):
            expected = config / ("projects" if p["provider"] == "claude" else "sessions")
            if not Path(root).resolve().is_relative_to(expected.resolve()):
                p["resumeDisabled"] = "Custom root needs explicit native-store mapping; discovery remains available"
    p = dict(p)
    p["executable"] = str(exe) if exe else ""
    p["cliMissing"] = not exe or not exe.is_file()
    p["label"] = clean(p.get("label") or p["id"], 80)
    p["enabled"] = bool(p.get("enabled", True))
    p["content"] = bool(p.get("content", False))
    p["env"] = {**env}
    needed = {"claude": "CLAUDE_CONFIG_DIR", "codex": "CODEX_HOME", "pi": "PI_CODING_AGENT_DIR"}.get(p["provider"])
    if needed:
        if needed in env and Path(env[needed]).resolve() != config.resolve():
            raise HubError("Profile environment does not match its config home")
        p["env"][needed] = str(config)
    if p["provider"] == "pi":
        if len(roots) == 1:
            p["env"]["PI_CODING_AGENT_SESSION_DIR"] = roots[0]
        else:
            p["resumeDisabled"] = "Pi resume requires one explicit session directory per profile"
    if p["provider"] == "opencode":
        if len(roots) == 1 and Path(roots[0]).name == "opencode" and config.name == "opencode":
            expected_env = {"XDG_DATA_HOME": str(Path(roots[0]).parent), "XDG_CONFIG_HOME": str(config.parent)}
            if any(name in env and Path(env[name]).resolve() != Path(value).resolve() for name, value in expected_env.items()):
                raise HubError("OpenCode environment does not match its explicit data/config roots")
            p["env"].update(expected_env)
        else:
            p["resumeDisabled"] = "OpenCode requires explicit opencode data/config folders for isolated resume"
    if p["provider"] == "copilot":
        p["env"]["COPILOT_HOME"] = str(config)
        p["resumeDisabled"] = "History supported; a real Copilot CLI and native continuation have not been verified"
    if p["provider"] == "gemini":
        if config.name != ".gemini" or any(not Path(root).is_relative_to(config / "tmp") for root in roots):
            p["resumeDisabled"] = "Gemini resume requires an explicit .gemini config home and tmp history root"
        if "GEMINI_CLI_HOME" in env and Path(env["GEMINI_CLI_HOME"]).resolve() != config.parent.resolve():
            raise HubError("Gemini environment does not match its explicit config home")
        p["env"]["GEMINI_CLI_HOME"] = str(config.parent)
        if p.get("projectPath"):
            local_path(p["projectPath"], True)
    for exclusion in p.get("excluded", []):
        local_path(exclusion)
        if not any(Path(exclusion).is_relative_to(Path(r)) for r in roots):
            raise HubError("Exclusions must be inside the approved roots")
    return p


def source_records(provider, path, offset=0, skip=False):
    data, eof = read_window(path, offset)
    if provider != "gemini":
        rows, end, skip, bad, big = records_in(data, eof, skip)
        return data, rows, end, skip, bad, big, eof
    # Gemini journals can replace/rewind messages. Never index an incomplete
    # projection or retain removed text from a prior file generation.
    if not eof:
        return data, [], 0, False, 0, 1, False
    try:
        if path.suffix == ".json":
            rows = [json.loads(data)]
        else:
            rows, end, _, bad, big = records_in(data, eof)
            if end != len(data) or bad or big:
                raise ValueError("Incomplete Gemini journal")
        rows = _adapters.gemini.replay(rows)
        return data, rows, len(data), False, 0, 0, True
    except (ValueError, TypeError, AttributeError, KeyError, RecursionError):
        return data, [], 0, False, 1, 0, False


def scan_file(store, profile, path, root, full=False):
    stamp = file_stamp(path)
    ident = digest([profile["provider"], physical(path)])
    cachekey = "file:" + ident
    cache = store.get(cachekey, {})
    changed = cache.get("stamp") != stamp or cache.get("parser") != PARSER
    if changed:
        # Restart on replacement, shrink or same-size rewrite; append preserves cursor.
        old = cache.get("stamp", [])
        if profile["provider"] == "gemini" or not old or old[:2] != stamp[:2] or stamp[2] <= old[2] or old[4] != stamp[4]:
            cache = {}
            store.db.execute("DELETE FROM content WHERE k=?", (ident,))
        cache.update(stamp=stamp, parser=PARSER)
        cache["complete"] = False
    meta = cache.get("meta", {"title": "", "formatSupported": False})
    if changed or not meta.get("nativeId"):
        data, rows, end, _, bad, big, eof = source_records(profile["provider"], path)
        for x in rows:
            parse_record(profile["provider"], x, meta)
        cache["malformed"] = bad
        cache["oversized"] = big
        if profile["provider"] != "gemini" and path.suffix != ".zst" and stamp[2] > CHUNK:
            with path.open("rb") as f:
                f.seek(max(0, stamp[2] - CHUNK))
                tail = f.read(CHUNK)
            tail = tail.partition(b"\n")[2]
            for x in records_in(tail)[0]:
                parse_record(profile["provider"], x, meta)
        meta["timestampCoverage"] = "complete" if eof and end == len(data) and not bad and not big else "partial head/tail"
        if profile["provider"] == "gemini" and not eof:
            meta["formatSupported"] = False
            meta["contentWarning"] = "Gemini history exceeds the complete replay budget or is malformed; metadata only"
    offset = cache.get("offset", 0)
    if full and profile.get("content") and not cache.get("complete"):
        data, rows, end, skip, bad, big, eof = source_records(profile["provider"], path, offset, cache.get("skip", False))
        texts = []
        for x in rows:
            msg = parse_record(profile["provider"], x, meta)
            if msg:
                texts.append(msg["text"])
        if texts:
            store.db.execute("INSERT INTO content VALUES (?,?)", (ident, "\n".join(texts)))
        cache.update(offset=offset + end, skip=skip, complete=eof and end == len(data),
                     malformed=cache.get("malformed", 0) + bad, oversized=cache.get("oversized", 0) + big)
        meta["timestampCoverage"] = "complete" if cache["complete"] and not cache["malformed"] and not cache["oversized"] else "partial incremental"
    if profile["provider"] == "gemini":
        project = profile.get("projectPath", "")
        # Gemini stores a hash, not cwd. Only an explicit exact user mapping
        # with matching upstream SHA-256 can establish the original project.
        meta["cwd"] = project if project and hashlib.sha256(project.encode()).hexdigest() == meta.get("projectHash") else ""
    cache["meta"] = meta
    store.set(cachekey, cache)
    native = meta.get("nativeId")
    if not native:
        # Preserve a metadata-only row for unknown/oversized headers, never omit silently.
        native = "unknown:" + ident[:12]
    key = digest([profile["provider"], ident, native])
    return {**meta, "key": key, "provider": profile["provider"], "nativeId": native,
            "canonicalSourceIdentity": ident, "sourcePath": str(path), "root": root,
            "sourceKind": "file", "fileModifiedAt": timestamp(stamp[3] / 1000000),
            "fingerprint": stamp, "parserVersion": PARSER, "sourceBytes": stamp[2],
            "indexBytes": cache.get("offset", 0), "indexComplete": cache.get("complete", False) and not cache.get("malformed") and not cache.get("oversized"),
            "malformed": cache.get("malformed", 0), "oversized": cache.get("oversized", 0),
            "targets": [profile["id"]], "stale": False}


def opencode_fingerprint(path, root):
    wal = path.with_name(path.name + "-wal")
    return [file_stamp(path), file_stamp(source_file(wal, root)) if wal.exists() else None]


def offline_source(path):
    """Windows share-deny-write handle, including checkpoint/rename protection."""
    if os.name != "nt":
        raise HubError("Offline database snapshots require Windows in this build")
    import msvcrt
    k = ctypes.WinDLL("kernel32", use_last_error=True)
    k.CreateFileW.argtypes = [wintypes.LPCWSTR, wintypes.DWORD, wintypes.DWORD, ctypes.c_void_p, wintypes.DWORD, wintypes.DWORD, wintypes.HANDLE]
    k.CreateFileW.restype = wintypes.HANDLE
    k.CloseHandle.argtypes = [wintypes.HANDLE]
    handle = k.CreateFileW(str(path), 0x80000000, 1, None, 3, 0x80, None)
    if handle == ctypes.c_void_p(-1).value:
        raise HubError("OpenCode is open for writing or inaccessible; close it before refreshing")
    try:
        descriptor = msvcrt.open_osfhandle(handle, os.O_RDONLY | os.O_BINARY)
    except Exception:
        k.CloseHandle(handle)
        raise
    return os.fdopen(descriptor, "rb")


def opencode_snapshot(path, root):
    # Stat timestamps alone are insufficient on Windows while a writer holds
    # handles. Hold DB and WAL share-deny-write handles together before reading.
    # Existing writers fail this acquisition; new writers/checkpoints cannot open.
    with contextlib.ExitStack() as stack:
        source = stack.enter_context(offline_source(path))
        wal = path.with_name(path.name + "-wal")
        wal_source = stack.enter_context(offline_source(source_file(wal, root))) if wal.exists() else None
        before = opencode_fingerprint(path, root)
        if sum(stamp[2] for stamp in before if stamp) > _adapters.sqlite_snapshot.LIMIT:
            raise HubError("OpenCode database/WAL exceeds the 128 MiB snapshot budget")
        data = source.read(_adapters.sqlite_snapshot.LIMIT + 1)
        if len(data) > _adapters.sqlite_snapshot.LIMIT:
            raise HubError("OpenCode snapshot grew beyond its read budget")
        remaining = _adapters.sqlite_snapshot.LIMIT - len(data)
        journal = wal_source.read(remaining + 1) if wal_source else b""
        if len(journal) > remaining:
            raise HubError("OpenCode WAL grew beyond its read budget")
        if opencode_fingerprint(path, root) != before:
            raise HubError("OpenCode changed during snapshot; refresh and retry")
    return _adapters.sqlite_snapshot.connect(data, journal), before


def opencode_rows(profile):
    """Query only a validated in-memory committed DB/WAL image."""
    records = []
    for root in profile["roots"]:
        path = source_file(Path(root) / "opencode.db", root)
        db, before = opencode_snapshot(path, root)
        try:
            db.execute("PRAGMA query_only=ON")
            db.set_progress_handler(lambda: 1 if time.monotonic() > deadline else 0, 1000)
            deadline = time.monotonic() + 3
            rows = db.execute('SELECT id,title,directory,time_created,time_updated,version FROM session WHERE parent_id IS NULL LIMIT ?', (MAX_FILES + 1,)).fetchall()
            if len(rows) > MAX_FILES:
                raise HubError("OpenCode session count exceeds enumeration limit")
            for native, title, cwd, created, updated, version in rows:
                ident = digest(["opencode", physical(path), native])
                records.append({"key": digest(["opencode", ident, native]), "provider": "opencode",
                                "nativeId": clean(native, 100), "title": redact(clean(title, 160)),
                                "cwd": clean(cwd, 32000), "createdAt": timestamp(created),
                                "lastConversationAt": None, "providerUpdatedAt": timestamp(updated),
                                "timestampCoverage": "provider metadata; conversation time unknown",
                                "sourceVersion": clean(version, 30), "formatSupported": str(version).startswith("1.3."),
                                "sourcePath": str(path), "root": root, "sourceKind": "database",
                                "canonicalSourceIdentity": ident, "fingerprint": before, "parserVersion": PARSER,
                                "targets": [profile["id"]], "stale": False, "indexComplete": False})
        finally:
            db.close()
        if opencode_fingerprint(path, root) != before:
            raise HubError("OpenCode changed while reading; previous results retained")
    return records


def opencode_messages(record, cursor=None, limit=30):
    path = source_file(record["sourcePath"], record["root"])
    db, before = opencode_snapshot(path, record["root"])
    if before != record["fingerprint"]:
        db.close()
        raise HubError("OpenCode database changed; refresh before preview")
    messages, malformed = [], 0
    cursor = cursor or [-1, ""]
    try:
        deadline = time.monotonic() + 3
        db.set_progress_handler(lambda: int(time.monotonic() > deadline), 1000)
        db.execute("PRAGMA query_only=ON")
        rows = db.execute('''SELECT p.time_created,p.id,substr(p.data,1,65537),substr(m.data,1,65537)
            FROM part AS p JOIN message AS m ON m.id=p.message_id
            WHERE p.session_id=? AND m.session_id=? AND
            (p.time_created>? OR (p.time_created=? AND p.id>?))
            ORDER BY p.time_created,p.id LIMIT ?''',
            (record["nativeId"], record["nativeId"], cursor[0], cursor[0], cursor[1], limit)).fetchall()
        for at, part_id, part_raw, message_raw in rows:
            cursor = [at, part_id]
            if len(part_raw) > 65536 or len(message_raw) > 65536:
                malformed += 1
                continue
            try:
                part, message = json.loads(part_raw), json.loads(message_raw)
                if message.get("role") in ("user", "assistant") and part.get("type") == "text":
                    messages.append({"role": message["role"], "text": redact(clean(part.get("text"), 65536)), "at": timestamp(at)})
            except (ValueError, AttributeError, RecursionError):
                malformed += 1
    finally:
        db.close()
    if opencode_fingerprint(path, record["root"]) != before:
        raise HubError("OpenCode changed during content read")
    return {"messages": messages, "cursor": cursor, "partial": len(rows) >= limit, "malformed": malformed, "oversized": 0, "branch": "root session; text parts only"}


def index_opencode(store, profile, row):
    ident = row["canonicalSourceIdentity"]
    cachekey = "file:" + ident
    cache = store.get(cachekey, {})
    if cache.get("stamp") != row["fingerprint"]:
        cache = {"stamp": row["fingerprint"]}
        store.db.execute("DELETE FROM content WHERE k=?", (ident,))
    if profile.get("content") and not cache.get("complete"):
        result = opencode_messages(row, cache.get("cursor"), 32)
        text = "\n".join(m["text"] for m in result["messages"])
        if text:
            store.db.execute("INSERT INTO content VALUES (?,?)", (ident, text))
        cache.update(cursor=result["cursor"], complete=not result["partial"],
                     offset=cache.get("offset", 0) + len(text.encode("utf-8")))
        store.set(cachekey, cache)
    row.update(indexComplete=cache.get("complete", False), indexBytes=cache.get("offset", 0))


def refresh(store, full=False, profile_id=None):
    profiles = store.get("profiles", [])
    previous = {r["key"]: r for r in store.get("records", [])}
    output, statuses, examined, advanced = {}, [], 0, 0
    # A requested profile refresh retains every other profile's previous records.
    for p in profiles:
        old = [r for r in previous.values() if p["id"] in r["targets"]]
        status = {"profile": p["id"], "provider": p["provider"], "counts": {}, "state": "ready"}
        if not p.get("enabled") or (profile_id and p["id"] != profile_id):
            for r in old:
                r = {**r, "targets": [p["id"]], "stale": True}
                merge_record(output, r)
            continue
        try:
            p = profile_validate(p)
            status["cliInstalled"] = not p["cliMissing"]
            if p["provider"] == "opencode":
                found = opencode_rows(p)
                if full:
                    # Round-robin for more than sixteen conversations.
                    cursor = store.get("opencodeCursor:" + p["id"], 0) % max(1, len(found))
                    for row in found[cursor:cursor + 16]:
                        index_opencode(store, p, row)
                    store.set("opencodeCursor:" + p["id"], (cursor + 16) % max(1, len(found)))
            else:
                candidates, problems = enumerate_sources(p)
                status["counts"] = problems
                found = []
                cursor = store.get("cursor:" + p["id"], 0) % max(1, len(candidates))
                rotated = candidates[cursor:cursor + (16 if full else 128)]
                old_by_source = {r["canonicalSourceIdentity"]: r for r in old}
                live_paths = {str(path) for path, _ in candidates}
                failed_paths = set()
                # 32 MiB decoded work per RPC, then continue on next explicit batch.
                count = 0
                for path, root in rotated:
                    examined += 1
                    try:
                        before = store.get("file:" + digest([p["provider"], physical(path)]), {})
                        if p["provider"] != "gemini" and not full and before.get("stamp") == file_stamp(path) and before.get("parser") == PARSER:
                            ident = digest([p["provider"], physical(path)])
                            match = old_by_source.get(ident)
                            if match:
                                found.append({**match, "targets": [p["id"]], "stale": False})
                                continue
                        r = scan_file(store, p, path, root, full)
                        found.append(r)
                        count += 1
                        advanced += 1
                    except (OSError, ValueError, sqlite3.Error, HubError, zstd.ZstdError):
                        failed_paths.add(str(path))
                        problems["parseFailed"] = problems.get("parseFailed", 0) + 1
                        count += 1
                # Keep unprocessed records, marked stale; never erase on a partial batch.
                found_keys = {r["key"] for r in found}
                found_sources = {r["canonicalSourceIdentity"] for r in found}
                for r in old:
                    if r["key"] not in found_keys:
                        found.append({**r, "targets": [p["id"]], "stale": r.get("stale", False) or r["canonicalSourceIdentity"] in found_sources or r["sourcePath"] not in live_paths or r["sourcePath"] in failed_paths})
                remaining = max(0, len(candidates) - cursor - examined)
                status["remaining"] = remaining
                store.set("cursor:" + p["id"], (cursor + examined) % max(1, len(candidates)))
                examined = 0
                if problems or remaining:
                    status["state"] = "partial"
            for r in found:
                merge_record(output, r)
            status["sessions"] = len(found)
        except (HubError, OSError, ValueError, sqlite3.Error):
            for r in old:
                merge_record(output, {**r, "targets": [p["id"]], "stale": True})
            status.update(state="unavailable", reason="Profile/root/schema unavailable or live WAL; prior results retained")
        statuses.append(status)
    # Same native ID within one config home is ambiguous to the native CLI.
    bindings = {}
    by_profile = {p["id"]: p for p in profiles}
    for row in output.values():
        row["collision"] = False
        for target in row["targets"]:
            p = by_profile[target]
            binding = (row["provider"], os.path.normcase(p["configHome"]), row["nativeId"])
            bindings.setdefault(binding, []).append(row)
    for rows in bindings.values():
        if len({r["canonicalSourceIdentity"] for r in rows}) > 1:
            for row in rows:
                row["collision"] = True
    store.set("records", list(output.values()))
    store.set("statuses", statuses)
    store.set("lastScan", dt.datetime.now(dt.timezone.utc).isoformat())
    return {"advanced": advanced, "statuses": statuses, "lastScan": store.get("lastScan")}


def merge_record(output, row):
    if row["key"] in output:
        old = output[row["key"]]
        row = {**old, "targets": sorted(set(old["targets"] + row["targets"])), "stale": old["stale"] and row["stale"]}
    output[row["key"]] = row


def find_record(store, key):
    if not isinstance(key, str) or not KEY.fullmatch(key):
        raise HubError("Invalid record key")
    row = next((r for r in store.get("records", []) if r["key"] == key), None)
    if row is None:
        raise HubError("Session no longer indexed; refresh")
    return row


def list_records(store, request):
    query = unicodedata.normalize("NFKC", clean(request.get("query", ""), 300)).casefold()
    content_keys = set()
    if request.get("fullText") and query:
        # Literal terms only. No arbitrary MATCH grammar or SQL from input.
        terms = re.findall(r"\w+", query, re.UNICODE)[:12]
        if terms:
            # A conversation spans multiple indexed chunks. Intersect identities,
            # not chunk rows, so query results do not depend on chunk boundaries.
            matches = None
            for term in dict.fromkeys(terms):
                literal = '"' + term.replace('"', '""') + '"'
                keys = {x[0] for x in store.db.execute("SELECT DISTINCT k FROM content WHERE content MATCH ? LIMIT 20000", (literal,))}
                matches = keys if matches is None else matches & keys
                if not matches:
                    break
            content_keys = matches or set()
    profiles = {profile["id"]: profile for profile in store.get("profiles", [])}
    rows = []
    for record in store.get("records", []):
        annotation = store.get("annotation:" + record["key"], {})
        if annotation.get("removed") and not request.get("removed"):
            continue
        if bool(annotation.get("archived")) != bool(request.get("archived")):
            continue
        if request.get("provider") in PROVIDERS and record["provider"] != request["provider"]:
            continue
        if request.get("profile") and request["profile"] not in record["targets"]:
            continue
        hay = " ".join(str(record.get(x) or "") for x in ("title", "cwd", "nativeId")) + " " + annotation.get("alias", "")
        content_match = record["canonicalSourceIdentity"] in content_keys and content_search_allowed(record, request, profiles)
        if query and query not in unicodedata.normalize("NFKC", hay).casefold() and not content_match:
            continue
        rows.append({**record, **annotation, "receipt": store.get("receipt:" + record["key"]),
                     "title": annotation.get("alias") or record.get("title") or "Untitled session"})
    rows.sort(key=lambda r: (r.get("lastConversationAt") or "", r["key"]), reverse=not request.get("oldest"))
    offset = max(0, int(request.get("offset", 0)))
    return {"rows": rows[offset:offset + 60], "total": len(rows), "offset": offset,
            "profiles": store.get("profiles", []), "statuses": store.get("statuses", []),
            "lastScan": store.get("lastScan"), "schema": SCHEMA}


def content_search_allowed(record, request, profiles):
    """Authorize shared physical-source hits per explicit target's opt-in."""
    source = Path(record["sourcePath"])
    for target in record["targets"]:
        if request.get("profile") and target != request["profile"]:
            continue
        profile = profiles.get(target, {})
        if not profile.get("enabled") or not profile.get("content") or profile.get("provider") != record["provider"]:
            continue
        if any(source.is_relative_to(Path(exclusion)) for exclusion in profile.get("excluded", [])):
            continue
        if any(source.is_relative_to(Path(root)) for root in profile.get("roots", [])):
            return True
    return False


def preview(store, key):
    r = find_record(store, key)
    p = source_file(r["sourcePath"], r["root"])
    before = file_stamp(p)
    if r["sourceKind"] == "database":
        result = opencode_messages(r)
        for msg in result["messages"]:
            msg["text"] = msg["text"][:2000]
        return result
    data, rows, consumed, _, malformed, oversized, eof = source_records(r["provider"], p)
    complete = eof and consumed == len(data) and not malformed and not oversized
    messages, meta = [], {}
    # Pi previews follow active ancestry only when the whole file fits the budget.
    if r["provider"] == "pi" and complete and r.get("sourceVersion") != "1":
        entries = [x for x in rows if x.get("type") != "session" and x.get("id")]
        by_id = {x["id"]: x for x in entries}
        branch, seen = [], set()
        leaf = entries[-1] if entries else None
        while leaf and leaf.get("id") not in seen and len(seen) < 10000:
            seen.add(leaf["id"])
            branch.append(leaf)
            leaf = by_id.get(leaf.get("parentId"))
        if leaf or (branch and branch[-1].get("parentId")):
            raise HubError("Pi branch ancestry is incomplete or cyclic")
        rows = [x for x in rows if x.get("type") == "session"] + list(reversed(branch))
    for x in rows:
        msg = parse_record(r["provider"], x, meta)
        if msg and (not messages or (messages[-1]["role"], messages[-1]["text"]) != (msg["role"], msg["text"])):
            msg["text"] = msg["text"][:2000]
            messages.append(msg)
            if len(messages) >= 30:
                break
    if before != file_stamp(p):
        raise HubError("Session changed during preview; refresh and retry")
    return {"messages": messages, "partial": not complete or len(messages) >= 30 or bool(r.get("historyBase")),
            "branch": "active" if r["provider"] == "pi" and complete else "bounded file excerpt; branch coverage unknown",
            "malformed": malformed, "oversized": oversized}


def running_provider(provider, executable=None):
    """Privacy preserving: enumerate executable names, never other command lines."""
    if os.name != "nt":
        return None
    class Process(ctypes.Structure):
        _fields_ = [("dwSize", wintypes.DWORD), ("cntUsage", wintypes.DWORD),
                    ("th32ProcessID", wintypes.DWORD), ("th32DefaultHeapID", ctypes.c_size_t),
                    ("th32ModuleID", wintypes.DWORD), ("cntThreads", wintypes.DWORD),
                    ("th32ParentProcessID", wintypes.DWORD), ("pcPriClassBase", wintypes.LONG),
                    ("dwFlags", wintypes.DWORD), ("szExeFile", wintypes.WCHAR * 260)]
    k = ctypes.WinDLL("kernel32", use_last_error=True)
    k.CreateToolhelp32Snapshot.restype = wintypes.HANDLE
    k.Process32FirstW.argtypes = [wintypes.HANDLE, ctypes.POINTER(Process)]
    k.Process32NextW.argtypes = [wintypes.HANDLE, ctypes.POINTER(Process)]
    k.CloseHandle.argtypes = [wintypes.HANDLE]
    k.OpenProcess.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.DWORD]
    k.OpenProcess.restype = wintypes.HANDLE
    k.QueryFullProcessImageNameW.argtypes = [wintypes.HANDLE, wintypes.DWORD, wintypes.LPWSTR, ctypes.POINTER(wintypes.DWORD)]
    handle = k.CreateToolhelp32Snapshot(2, 0)
    if handle == ctypes.c_void_p(-1).value:
        return None
    try:
        entry = Process()
        entry.dwSize = ctypes.sizeof(entry)
        ok = k.Process32FirstW(handle, ctypes.byref(entry))
        if not ok:
            return None
        names = {"claude": {"claude.exe"}, "codex": {"codex.exe"},
                 "opencode": {"opencode.exe"}, "pi": {"node.exe", "pi.exe"},
                 "copilot": {"copilot.exe"}, "gemini": {"node.exe", "gemini.exe"}}[provider]
        if executable:
            names.add(Path(executable).name.casefold())
        def advance():
            ctypes.set_last_error(0)
            result = k.Process32NextW(handle, ctypes.byref(entry))
            if not result and ctypes.get_last_error() != 18:
                raise OSError("Process enumeration unavailable")
            return result
        node_seen = False
        while ok:
            if entry.szExeFile.casefold() in names:
                if entry.szExeFile.casefold() == "node.exe":
                    node_seen = True
                else:
                    if executable:
                        process = k.OpenProcess(0x1000, False, entry.th32ProcessID)
                        if not process:
                            return None
                        try:
                            size = wintypes.DWORD(32768)
                            buffer = ctypes.create_unicode_buffer(size.value)
                            if not k.QueryFullProcessImageNameW(process, 0, buffer, ctypes.byref(size)):
                                return None
                            # The Claude desktop app also calls itself Claude.exe.
                            # Compare the selected verified CLI image, not its label.
                            if not os.path.samefile(buffer.value, executable):
                                ok = advance()
                                continue
                        except OSError:
                            return None
                        finally:
                            k.CloseHandle(process)
                    return True
            ok = advance()
        if not node_seen:
            return False
        # Ask WMI for PIDs only; unrelated Node command lines never enter Hub.
        # The fixed WQL patterns recognize the audited installed CLI launchers.
        patterns = {"pi": "(CommandLine LIKE '%pi-launcher.js%' OR CommandLine LIKE '%pi-coding-agent%')",
                    "gemini": "(CommandLine LIKE '%gemini.js%' OR CommandLine LIKE '%gemini-cli%')"}
        query = "Name='node.exe' AND (" + patterns[provider] + " OR CommandLine IS NULL OR CommandLine='')"
        script = 'Get-CimInstance -ClassName Win32_Process -Filter "' + query + '" -ErrorAction Stop | ForEach-Object { if ([string]::IsNullOrEmpty($_.CommandLine)) { "unknown" } else { $_.ProcessId } } | Select-Object -First 1'
        powershell = Path(os.environ.get("SystemRoot", "C:/Windows")) / "System32/WindowsPowerShell/v1.0/powershell.exe"
        try:
            answer = subprocess.run([str(local_path(str(powershell))), "-NoProfile", "-NonInteractive", "-Command", script],
                                    stdin=subprocess.DEVNULL, capture_output=True, timeout=6, shell=False)
            if answer.returncode != 0:
                return None
            result = answer.stdout.strip()
            return bool(result) if not result or result.isdigit() else None
        except (OSError, subprocess.TimeoutExpired, HubError):
            return None
    except OSError:
        return None
    finally:
        k.CloseHandle(handle)


def codex_writer_owned(profile, native):
    """Read-only probe of Codex 0.164's own cooperative per-thread lock."""
    directory = local_path(str(Path(profile["configHome"]) / "thread-writer-locks"))
    if not directory.is_dir():
        return running_provider("codex", profile["executable"])
    path = local_path(str(directory / (native + ".lock")))
    if not path.exists():
        return False
    if not path.is_file() or path.stat().st_nlink != 1:
        return None
    class Overlapped(ctypes.Structure):
        _fields_ = [("Internal", ctypes.c_size_t), ("InternalHigh", ctypes.c_size_t),
                    ("Offset", wintypes.DWORD), ("OffsetHigh", wintypes.DWORD), ("hEvent", wintypes.HANDLE)]
    k = ctypes.WinDLL("kernel32", use_last_error=True)
    k.CreateFileW.argtypes = [wintypes.LPCWSTR, wintypes.DWORD, wintypes.DWORD, ctypes.c_void_p, wintypes.DWORD, wintypes.DWORD, wintypes.HANDLE]
    k.CreateFileW.restype = wintypes.HANDLE
    k.LockFileEx.argtypes = [wintypes.HANDLE, wintypes.DWORD, wintypes.DWORD, wintypes.DWORD, wintypes.DWORD, ctypes.POINTER(Overlapped)]
    k.UnlockFileEx.argtypes = [wintypes.HANDLE, wintypes.DWORD, wintypes.DWORD, wintypes.DWORD, ctypes.POINTER(Overlapped)]
    k.CloseHandle.argtypes = [wintypes.HANDLE]
    handle = k.CreateFileW(str(path), 0x80000000, 7, None, 3, 0x80, None)
    if handle == ctypes.c_void_p(-1).value:
        return None
    try:
        overlap = Overlapped()
        if not k.LockFileEx(handle, 3, 0, 0xffffffff, 0xffffffff, ctypes.byref(overlap)):
            return True if ctypes.get_last_error() in (32, 33) else None
        k.UnlockFileEx(handle, 0, 0xffffffff, 0xffffffff, ctypes.byref(overlap))
        return False
    finally:
        k.CloseHandle(handle)


def resume_spec(store, key, profile_id, active_probe=None):
    r = find_record(store, key)
    if profile_id not in r["targets"]:
        raise HubError("Choose an explicit source profile")
    p = next((p for p in store.get("profiles", []) if p["id"] == profile_id), None)
    if not p:
        raise HubError("Profile is missing")
    p = profile_validate(p)
    if p["provider"] != r["provider"] or not p["enabled"] or p.get("cliMissing") or p.get("resumeDisabled") or not p.get("versionVerified"):
        raise HubError("Profile launch is disabled or its CLI version has not been verified")
    if p.get("verifiedExecutableStamp") != file_stamp(Path(p["executable"])):
        raise HubError("Provider executable changed; check its version again")
    if p.get("launchScript") and p.get("verifiedScriptStamp") != file_stamp(Path(p["launchScript"])):
        raise HubError("Provider launcher changed; check its version again")
    if r.get("stale") or not r.get("formatSupported") or r.get("identityConflict") or r.get("subagent") or r.get("collision"):
        raise HubError("Source is stale, unsupported, ambiguous, or a subagent session")
    native = r["nativeId"]
    if not (UUID.fullmatch(native) if r["provider"] != "opencode" else re.fullmatch(r"ses_[A-Za-z0-9]{8,80}", native)):
        raise HubError("Native session identity is invalid")
    path = source_file(r["sourcePath"], r["root"])
    current = opencode_fingerprint(path, r["root"]) if r["sourceKind"] == "database" else file_stamp(path)
    if current != r["fingerprint"]:
        raise HubError("Source changed since refresh")
    cwd = local_path(r.get("cwd", ""), True)
    if str(cwd) not in p.get("trustedProjects", []):
        raise HubError("Trust this recorded project before launching; provider project hooks may execute")
    if active_probe is not None:
        active = active_probe(r["provider"])
    elif r["provider"] == "codex" and r.get("sourceVersion") == "0.164.0":
        active = codex_writer_owned(p, native)
    else:
        active = running_provider(r["provider"], p["executable"])
    if active is not False:
        raise HubError("A provider process may own this session; close it before resuming. Ownership is conservative")
    receipt = store.get("receipt:" + key, {})
    if receipt.get("state") in ("launching", "unverified") and time.time() - receipt.get("epoch", 0) < 60:
        raise HubError("This session was just requested; duplicate launch refused")
    args = {"claude": ["--resume", native], "codex": ["--no-daemon", "resume", native],
            "opencode": ["--session", native], "pi": ["--session", str(path)],
            "gemini": ["--session-file", str(path)]}[r["provider"]]
    prefix = [p["launchScript"]] if p.get("launchScript") else []
    return {"argv": [p["executable"], *prefix, *args], "cwd": str(cwd), "env": p["env"], "profile": p["id"]}


def launch(root, key, profile_id):
    with Store(root) as store:
        spec = resume_spec(store, key, profile_id)
        store.set("receipt:" + key, {"state": "launching", "epoch": time.time(), "profile": profile_id})
    code = 1
    try:
        env = profile_environment(spec["env"])
        print("Session Hub: requesting native resume. Verify the session ID and previous context in the agent.", flush=True)
        child = subprocess.Popen(spec["argv"], cwd=spec["cwd"], env=env, shell=False)
        with Store(root) as store:
            store.set("receipt:" + key, {"state": "unverified", "epoch": time.time(), "profile": profile_id})
        code = child.wait()
    finally:
        with Store(root) as store:
            store.set("receipt:" + key, {"state": "unverified" if code == 0 else "failed", "epoch": time.time(), "profile": profile_id, "exitCode": code})
    return code


def profile_environment(overrides):
    # Do not inspect or log credential values. Drop inherited account selection,
    # auth and provider routing; only explicit directory mappings are restored.
    prefixes = ("ANTHROPIC_", "CLAUDE_", "CODEX_", "OPENAI_", "OPENCODE_", "PI_", "AZURE_OPENAI_", "AWS_", "GEMINI_", "GOOGLE_", "COPILOT_", "GITHUB_", "GH_")
    env = {name: value for name, value in os.environ.items()
           if name not in set().union(*ENV_NAMES.values())
           and not name.upper().startswith(prefixes)
           and not re.search(r"(?:API_KEY|AUTH_TOKEN|OAUTH_TOKEN|ACCESS_TOKEN|SECRET_KEY|BEARER_TOKEN)$", name.upper())}
    env.update(overrides)
    return env


def probe():
    versions = {}
    for name in PROVIDERS:
        exe = shutil.which(name + ".exe")
        # Pi's PowerShell shim is not accepted as an executable. User may configure
        # a native launcher; do not run arbitrary .cmd/.ps1 scripts automatically.
        script = Path.home() / ".pi/agent/bin/pi-launcher.js" if name == "pi" else None
        if name == "pi" and not exe and script.is_file():
            exe = shutil.which("node.exe")
        if name == "gemini" and not exe:
            script = Path(os.environ.get("APPDATA", "")) / "npm/node_modules/@google/gemini-cli/bundle/gemini.js"
            if script.is_file():
                exe = shutil.which("node.exe")
        versions[name] = {"installed": bool(exe), "executable": str(Path(exe).resolve()) if exe else None,
                          "launchScript": str(script) if script and script.is_file() else None,
                          "state": "native executable found" if exe else "native .exe missing; shell shims are disabled"}
    return {"providers": versions, "python": sys.version.split()[0], "sqlite": sqlite3.sqlite_version,
            "platform": sys.platform, "schema": SCHEMA}


def rpc(store, req):
    action = req.get("action")
    if action == "list":
        return list_records(store, req)
    if action == "probe":
        return probe()
    if action == "refresh":
        return refresh(store, bool(req.get("content")), req.get("profile"))
    if action == "preview":
        return preview(store, req.get("key"))
    if action == "profile-save":
        p = profile_validate(req.get("profile"))
        profiles = store.get("profiles", [])
        old = next((x for x in profiles if x["id"] == p["id"]), None)
        # Configuration edits invalidate verification and project trust.
        if not old or any(old.get(x) != p.get(x) for x in ("executable", "launchScript", "configHome", "roots", "env", "projectPath")):
            p["versionVerified"] = False
            p["trustedProjects"] = []
        else:
            # Verification is an observed result, not a writable form flag.
            for name in ("versionVerified", "verifiedExecutableStamp", "verifiedScriptStamp", "cliVersion"):
                if name in old:
                    p[name] = old[name]
                else:
                    p.pop(name, None)
        profiles = [x for x in profiles if x["id"] != p["id"]] + [p]
        if len(profiles) > 32:
            raise HubError("Maximum 32 profiles")
        store.set("profiles", profiles)
        if old and (not p["content"] or any(old.get(k) != p.get(k) for k in ("roots", "provider", "excluded", "configHome", "enabled"))):
            clear_content(store)
        if old and any(old.get(k) != p.get(k) for k in ("roots", "provider", "excluded", "configHome")):
            records = []
            for row in store.get("records", []):
                targets = [t for t in row["targets"] if t != p["id"]]
                if targets:
                    records.append({**row, "targets": targets})
            store.set("records", records)
        return {"saved": p["id"]}
    if action == "verify-version":
        profiles = store.get("profiles", [])
        p = next((p for p in profiles if p["id"] == req.get("profile")), None)
        if not p:
            raise HubError("Profile missing")
        p = profile_validate(p)
        if p["cliMissing"]:
            raise HubError("Native provider CLI is missing; discovery remains available")
        # Version only: no config/plugin discovery, no provider transcript access.
        prefix = [p["launchScript"]] if p.get("launchScript") else []
        result = subprocess.run([p["executable"], *prefix, "--version"], stdin=subprocess.DEVNULL,
                                capture_output=True, timeout=8, shell=False, cwd=str(store.root), env=profile_environment(p["env"]))
        version = clean(result.stdout.decode("utf-8", "replace"), 100).strip()
        expected = {"claude": r"2\.1\.322", "codex": r"0\.164\.0", "opencode": r"1\.3\.17", "pi": r"1\.1\.0", "gemini": r"0\.49\.0", "copilot": r"(?!)"}[p["provider"]]
        verified = result.returncode == 0 and bool(re.search(r"(?<![\d.])" + expected + r"(?![\d.])", version))
        for item in profiles:
            if item["id"] == p["id"]:
                item.update(versionVerified=verified, cliVersion=version,
                            verifiedExecutableStamp=file_stamp(Path(p["executable"])),
                            verifiedScriptStamp=file_stamp(Path(p["launchScript"])) if p.get("launchScript") else None)
        store.set("profiles", profiles)
        return {"verified": verified, "version": version, "reason": "Only the researched installed versions are enabled"}
    if action == "trust-project":
        r = find_record(store, req.get("key"))
        profiles = store.get("profiles", [])
        p = next((p for p in profiles if p["id"] == req.get("profile") and p["id"] in r["targets"]), None)
        if not p or req.get("confirmation") != r.get("cwd"):
            raise HubError("Explicit confirmation of the exact recorded cwd is required")
        cwd = str(local_path(r["cwd"], True))
        p["trustedProjects"] = sorted(set(p.get("trustedProjects", []) + [cwd]))
        store.set("profiles", profiles)
        return {"trusted": True}
    if action == "resume":
        spec = resume_spec(store, req.get("key"), req.get("profile"))
        # The terminal wrapper revalidates before launch. No success claim here.
        return {"folder": spec["cwd"], "argv": [sys.executable, "-I", str(Path(__file__).resolve()), "--state", str(store.root),
                                                "launch", req["key"], req["profile"]], "state": "unverified"}
    if action == "annotate":
        r = find_record(store, req.get("key"))
        value = store.get("annotation:" + r["key"], {})
        for name in ("archived", "removed"):
            if name in req:
                value[name] = bool(req[name])
        if "alias" in req:
            value["alias"] = redact(clean(req["alias"], 160))
        value["updatedAt"] = dt.datetime.now(dt.timezone.utc).isoformat()
        store.set("annotation:" + r["key"], value)
        return {"saved": True}
    if action == "clear-content":
        clear_content(store)
        return {"cleared": True}
    if action == "portable-list":
        result = {"foreign": [], "conflicts": []}
        for prefix, field in (("foreign:", "foreign"), ("conflict:", "conflicts")):
            for key, value in store.db.execute("SELECT k,v FROM kv WHERE k LIKE ? LIMIT 60", (prefix + "%",)):
                item = json.loads(value)
                result[field].append({"key": key, "provider": item.get("provider"),
                                      "nativeId": clean(item.get("nativeId"), 100), "alias": clean(item.get("annotation", {}).get("alias"), 160)})
        return result
    if action == "portable-apply":
        # Linking only changes Hub metadata. It can never create a native source
        # or restore a launch configuration from another computer.
        target = find_record(store, req.get("key"))
        portable_key = req.get("portableKey", "")
        if not re.fullmatch(r"(?:foreign|conflict):[a-f0-9]{64}", portable_key):
            raise HubError("Invalid portable metadata key")
        item = store.get(portable_key)
        if not item or item["provider"] != target["provider"] or item["nativeId"] != target["nativeId"]:
            raise HubError("Explicit matching provider and native ID required for metadata linking")
        local_key = "annotation:" + target["key"]
        old = store.get(local_key)
        if old and old != item["annotation"] and req.get("conflictChoice") not in ("keep-local", "use-imported"):
            raise HubError("Choose keep-local or use-imported explicitly; no annotation was overwritten")
        if req.get("conflictChoice") != "keep-local" and (not old or req.get("conflictChoice") == "use-imported"):
            if old:
                store.set("annotation-backup:" + digest([local_key, old]), old)
            store.set(local_key, item["annotation"])
        store.set("portable-receipt:" + digest([portable_key, target["key"]]), {"target": target["key"], "choice": req.get("conflictChoice", "new")})
        return {"linked": True, "nativeSourceChanged": False}
    if action == "recover":
        raise HubError("Use the offline recover command with the app closed")
    if action in ("delete-original", "native-import", "remote-sync"):
        raise HubError("Unavailable: no audited provider restore/delete or remote sync implementation")
    raise HubError("Unsupported action")


def clear_content(store):
    store.db.execute("DELETE FROM content")
    # Secure deletion in the in-memory DB, then serialize a compact fresh image.
    for key, value in store.db.execute("SELECT k,v FROM kv WHERE k LIKE 'file:%'").fetchall():
        cache = json.loads(value)
        cache.update(offset=0, complete=False, skip=False, cursor=None)
        store.set(key, cache)
    store.db.commit()
    store.db.execute("VACUUM")
    store.set("records", [{**r, "indexBytes": 0, "indexComplete": False} for r in store.get("records", [])])
    store.dirty = True
    store.purge_backup = True


def metadata_manifest(store):
    entries = []
    for key, value in store.db.execute("SELECT k,v FROM kv WHERE k LIKE 'annotation:%'"):
        r = next((r for r in store.get("records", []) if r["key"] == key[11:]), None)
        if r:
            entries.append({"origin": key[11:], "provider": r["provider"], "nativeId": r["nativeId"], "annotation": json.loads(value)})
    body = {"schema": 1, "kind": "hub-metadata-only", "createdAt": dt.datetime.now(dt.timezone.utc).isoformat(), "entries": entries}
    return {"body": body, "sha256": digest(body)}


def portable_encrypt(manifest, password):
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM
    from cryptography.hazmat.primitives.kdf.scrypt import Scrypt
    if len(password) < 12 or len(password) > 1024:
        raise HubError("Use a passphrase of at least 12 characters")
    salt, nonce = os.urandom(16), os.urandom(12)
    key = Scrypt(salt=salt, length=32, n=2**17, r=8, p=1).derive(password.encode("utf-8"))
    header = b"HSH1" + salt + nonce
    data = json.dumps(manifest, ensure_ascii=True, separators=(",", ":")).encode()
    return header + AESGCM(key).encrypt(nonce, data, header)


def portable_decrypt(data, password):
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM
    from cryptography.hazmat.primitives.kdf.scrypt import Scrypt
    if not 48 <= len(data) <= 8 * CHUNK or data[:4] != b"HSH1" or len(password) > 1024:
        raise HubError("Unsupported or truncated encrypted bundle")
    try:
        key = Scrypt(salt=data[4:20], length=32, n=2**17, r=8, p=1).derive(password.encode("utf-8"))
        manifest = json.loads(AESGCM(key).decrypt(data[20:32], data[32:], data[:32]))
    except Exception:
        raise HubError("Wrong passphrase or damaged encrypted bundle") from None
    body = manifest.get("body", {})
    if not isinstance(body, dict) or set(manifest) != {"body", "sha256"} or set(body) != {"schema", "kind", "createdAt", "entries"} or body.get("schema") != 1 or body.get("kind") != "hub-metadata-only" or manifest.get("sha256") != digest(body):
        raise HubError("Bundle schema or checksum mismatch")
    if not isinstance(body.get("entries"), list) or len(body["entries"]) > MAX_FILES:
        raise HubError("Bundle entry limit")
    for e in body["entries"]:
        if not isinstance(e, dict) or set(e) != {"origin", "provider", "nativeId", "annotation"} or not KEY.fullmatch(str(e.get("origin", ""))) or e.get("provider") not in PROVIDERS or not isinstance(e.get("nativeId"), str) or len(e["nativeId"]) > 100:
            raise HubError("Invalid portable identity")
        annotation = e.get("annotation")
        if not isinstance(annotation, dict) or not set(annotation).issubset({"alias", "archived", "removed", "updatedAt"}):
            raise HubError("Bundle contains unsupported metadata")
        if not isinstance(annotation.get("alias", ""), str) or len(annotation.get("alias", "")) > 160:
            raise HubError("Invalid alias")
        if any(name in annotation and not isinstance(annotation[name], bool) for name in ("removed", "archived")):
            raise HubError("Invalid archive/removal flags")
    return manifest


def merge_manifest(store, manifest, apply=False):
    result = {"matched": 0, "foreign": 0, "conflicts": 0, "applied": apply}
    # Exact origin only. Same UUID on another machine/profile must never auto-bind.
    keys = {r["key"] for r in store.get("records", [])}
    for item in manifest["body"]["entries"]:
        origin = item["origin"]
        key = "annotation:" + origin if origin in keys else "foreign:" + digest(item)
        old = store.get(key)
        value = item["annotation"] if origin in keys else item
        result["matched" if origin in keys else "foreign"] += 1
        if old is not None and old != value:
            result["conflicts"] += 1
            if apply:
                store.set("conflict:" + digest(item), item)
        elif apply:
            store.set(key, value)
    return result


def recover(root):
    # Acquire the same byte-range lock as normal helpers, even when state itself
    # cannot be decoded. No parallel writer can race the recovery replacement.
    import msvcrt
    lockpath = root / "state.lock"
    if lockpath.exists() and is_link(lockpath):
        raise HubError("Linked recovery lock refused")
    with lockpath.open("a+b") as lock:
        lock.seek(0)
        try:
            msvcrt.locking(lock.fileno(), msvcrt.LK_NBLCK, 1)
        except OSError:
            raise HubError("Another helper is active; recovery refused") from None
        try:
            backup = root / "state.hub.bak"
            if is_link(backup) or backup.stat().st_size > MAX_STATE:
                raise HubError("Unsafe recovery file")
            image = protect(backup.read_bytes(), True)
            db = sqlite3.connect(":memory:")
            try:
                db.deserialize(image)
                if db.execute("PRAGMA integrity_check").fetchone()[0] != "ok":
                    raise HubError("Backup integrity failed")
                version = json.loads(db.execute("SELECT v FROM kv WHERE k='schema'").fetchone()[0])
                if version not in (1, SCHEMA):
                    raise HubError("Unsupported backup schema")
            finally:
                db.close()
            current = root / "state.hub"
            if current.exists():
                if is_link(current):
                    raise HubError("Linked recovery target refused")
                if current.stat().st_size > MAX_STATE:
                    raise HubError("Current state exceeds recovery evidence budget")
                # Persist evidence without removing current. A failed replacement
                # must leave the original authoritative state at its normal path.
                atomic(root / ("damaged-" + uuid.uuid4().hex + ".hub"), current.read_bytes())
            atomic(current, protect(image))
        finally:
            lock.seek(0)
            msvcrt.locking(lock.fileno(), msvcrt.LK_UNLCK, 1)


def main():
    parser = argparse.ArgumentParser(description="Session Hub offline helper; no provider history writes")
    parser.add_argument("--state", required=True)
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("rpc").add_argument("request")
    p = sub.add_parser("launch")
    p.add_argument("key")
    p.add_argument("profile")
    for name in ("export", "import"):
        p = sub.add_parser(name)
        p.add_argument("file")
        if name == "import":
            p.add_argument("--apply", action="store_true")
    sub.add_parser("recover")
    args = parser.parse_args()
    try:
        if args.command == "launch":
            return launch(args.state, args.key, args.profile)
        if args.command == "recover":
            root = local_path(args.state, True)
            recover(root)
            print(json.dumps({"recovered": True}))
            return 0
        if args.command == "rpc":
            if len(args.request) > 64000:
                raise HubError("Request too large")
            req = json.loads(args.request)
            if not isinstance(req, dict):
                raise HubError("Invalid request")
            with Store(args.state) as store:
                result = rpc(store, req)
            print(json.dumps({"ok": True, "result": result}, ensure_ascii=True))
            return 0
        file = local_path(args.file)
        password = getpass.getpass("Bundle passphrase (never stored): ")
        if args.command == "export":
            if file.exists():
                raise HubError("Destination exists; choose a new filename")
            if getpass.getpass("Confirm passphrase: ") != password:
                raise HubError("Passphrases do not match")
            with Store(args.state) as store:
                blob = portable_encrypt(metadata_manifest(store), password)
            # Exclusive creation, no accidental overwrite of histories/settings.
            with file.open("xb") as f:
                f.write(blob)
                f.flush()
                os.fsync(f.fileno())
            print(json.dumps({"exported": True, "kind": "metadata only; no profiles, paths, credentials or transcripts"}))
        else:
            if is_link(file) or file.stat().st_size > 8 * CHUNK:
                raise HubError("Unsafe bundle path or size")
            manifest = portable_decrypt(file.read_bytes(), password)
            with Store(args.state) as store:
                result = merge_manifest(store, manifest, args.apply)
            print(json.dumps(result))
        return 0
    except (HubError, OSError, ValueError, sqlite3.Error, subprocess.SubprocessError, ImportError, zstd.ZstdError) as error:
        message = str(error) if isinstance(error, HubError) else "Operation failed safely; check paths, permissions, dependency versions and source format"
        print(json.dumps({"ok": False, "error": message}, ensure_ascii=True))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
