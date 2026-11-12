"""Actual POSIX locks and read-only SQLite concurrency; no provider programs."""
import importlib.util
import os
from pathlib import Path
import sqlite3
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("posix_hub", ROOT / "mods/session-hub/helper/hub.py")
hub = importlib.util.module_from_spec(spec)
spec.loader.exec_module(hub)


@unittest.skipIf(os.name == "nt", "Native POSIX locking acceptance")
class PosixTests(unittest.TestCase):
    def setUp(self):
        (ROOT / ".dev/tests").mkdir(parents=True, exist_ok=True)
        self.tmp = tempfile.TemporaryDirectory(dir=ROOT / ".dev/tests", prefix="posix-")
        self.root = Path(self.tmp.name)
        self.path = self.root / "opencode.db"

    def tearDown(self):
        self.tmp.cleanup()

    def test_rollback_snapshot_blocks_another_process_writer(self):
        database = sqlite3.connect(self.path)
        database.execute("CREATE TABLE sample(value TEXT)")
        database.commit()
        database.close()
        original = self.path.read_bytes()
        with hub._adapters.platform_io.sqlite_sources(self.path, lambda p: hub.source_file(p, self.root)):
            code = "import sqlite3,sys\nd=sqlite3.connect(sys.argv[1],timeout=.1)\ntry:\n d.execute(\"INSERT INTO sample VALUES ('racing')\");d.commit()\nexcept sqlite3.OperationalError:\n sys.exit(12)\n"
            result = subprocess.run([sys.executable, "-I", "-c", code, str(self.path)], capture_output=True, timeout=10)
            self.assertEqual(result.returncode, 12, result.stderr)
        snapshot, _ = hub.opencode_snapshot(self.path, str(self.root))
        self.assertEqual(snapshot.execute("SELECT count(*) FROM sample").fetchone()[0], 0)
        snapshot.close()
        self.assertEqual(self.path.read_bytes(), original)

    def test_wal_snapshot_refuses_active_transaction_and_preserves_source_bytes(self):
        code = """import sqlite3,sys
d=sqlite3.connect(sys.argv[1],timeout=.1)
d.execute('PRAGMA journal_mode=WAL');d.execute('PRAGMA wal_autocheckpoint=0')
d.execute('CREATE TABLE sample(value TEXT)');d.execute("INSERT INTO sample VALUES ('committed')");d.commit()
print('idle',flush=True)
sys.stdin.readline();d.execute('BEGIN IMMEDIATE');d.execute("INSERT INTO sample VALUES ('uncommitted')")
print('writing',flush=True)
sys.stdin.readline();d.rollback();d.close()
"""
        writer = subprocess.Popen([sys.executable, "-I", "-c", code, str(self.path)], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        try:
            self.assertEqual(writer.stdout.readline().strip(), "idle")
            files = [self.path, self.path.with_name("opencode.db-wal"), self.path.with_name("opencode.db-shm")]
            original = {p: p.read_bytes() for p in files}
            snapshot, _ = hub.opencode_snapshot(self.path, str(self.root))
            self.assertEqual(snapshot.execute("SELECT * FROM sample").fetchall(), [("committed",)])
            snapshot.close()
            self.assertTrue(all(p.read_bytes() == raw for p, raw in original.items()))
            writer.stdin.write("begin\n");writer.stdin.flush()
            self.assertEqual(writer.stdout.readline().strip(), "writing")
            with self.assertRaises(hub.HubError):
                hub.opencode_snapshot(self.path, str(self.root))
        finally:
            writer.communicate("close\n", timeout=10)
            self.assertEqual(writer.returncode, 0)

    def test_missing_wal_shared_memory_is_refused_without_creating_it(self):
        database = sqlite3.connect(self.path)
        database.execute("PRAGMA journal_mode=WAL")
        database.execute("CREATE TABLE sample(value TEXT)")
        database.commit()
        wal = self.path.with_name("opencode.db-wal")
        data, frames = self.path.read_bytes(), wal.read_bytes()
        database.close()
        self.path.write_bytes(data);wal.write_bytes(frames)
        with self.assertRaises(hub.HubError):
            hub.opencode_snapshot(self.path, str(self.root))
        self.assertFalse(self.path.with_name("opencode.db-shm").exists())
        self.assertEqual(self.path.read_bytes(), data)
        self.assertEqual(wal.read_bytes(), frames)

    def test_wal_lock_generation_survives_last_provider_connection_close(self):
        code = """import sqlite3,sys
d=sqlite3.connect(sys.argv[1],timeout=.1)
d.execute('PRAGMA journal_mode=WAL');d.execute('CREATE TABLE sample(value TEXT)');d.commit()
print('idle',flush=True);sys.stdin.readline();d.close()
"""
        writer = subprocess.Popen([sys.executable,"-I","-c",code,str(self.path)],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
        try:
            self.assertEqual(writer.stdout.readline().strip(),"idle")
            shared = self.path.with_name("opencode.db-shm")
            identity = (shared.stat().st_dev, shared.stat().st_ino)
            with hub._adapters.platform_io.sqlite_sources(self.path, lambda p: hub.source_file(p,self.root)):
                writer.communicate("close\n",timeout=10)
                self.assertEqual(writer.returncode,0)
                self.assertTrue(shared.exists())
                self.assertEqual((shared.stat().st_dev,shared.stat().st_ino),identity)
        finally:
            if writer.poll() is None:
                writer.communicate("close\n",timeout=10)

    def test_codex_flock_and_unverified_platform_continuation_guard(self):
        import fcntl
        directory = self.root / "thread-writer-locks"
        directory.mkdir()
        native = "11111111-2222-4333-8444-555555555555"
        path = directory / (native + ".lock")
        path.write_bytes(b"")
        profile = dict(configHome=str(self.root), executable=sys.executable)
        with path.open("rb") as source:
            fcntl.flock(source.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
            self.assertTrue(hub.codex_writer_owned(profile, native))
        self.assertFalse(hub.codex_writer_owned(profile, native))
        self.assertFalse(hub.native_continuation_verified())
        config = self.root / "claude"
        history = config / "projects"
        history.mkdir(parents=True)
        with patch.object(hub, "native_continuation_verified", return_value=False):
            result = hub.profile_validate(dict(id="test",provider="claude",configHome=str(config),roots=[str(history)],executable=sys.executable))
        self.assertIn("platform-specific", result["resumeDisabled"])


if __name__ == "__main__":
    unittest.main()
