"""Real POSIX install transactions; external venv/pip/SDK calls are mocked.

This does not claim native Herdr acceptance. Actual platform smoke tests use
the same installer separately on disposable hosts.
"""
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]


def loaded(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


installer = loaded("posix_installer", ROOT / "scripts/install.py")
package = loaded("install_package", ROOT / "scripts/verify-package.py")


@unittest.skipIf(os.name == "nt", "Native POSIX installer transactions")
class InstallTests(unittest.TestCase):
    def setUp(self):
        (ROOT / ".dev/tests").mkdir(parents=True, exist_ok=True)
        self.tmp = tempfile.TemporaryDirectory(dir=ROOT / ".dev/tests", prefix="install-")
        self.base = Path(self.tmp.name).resolve()
        self.bundle = self.base / "package"
        for name in package.target_files(installer.target()):
            path = self.bundle / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(b"synthetic package")
        (self.bundle / "scripts/verify-package.py").write_bytes((ROOT / "scripts/verify-package.py").read_bytes())
        (self.bundle / "version.json").write_text(json.dumps(dict(version="0.1.0-experimental.1", platform=installer.target(),
            channel="experimental", releaseReady=False, stablePlatforms=["windows-x64"],
            nativeContinuationVerified=False, payload="install")))
        self.manifest()
        self.home = self.base / ".dev/app"
        self.herdr = self.base / "herdr-app"
        self.herdr.write_bytes(b"synthetic SDK mock")
        self.herdr.chmod(0o700)
        self.commands = []
        self.mocked_repo = patch.object(installer, "REPO", self.bundle)
        self.mocked_repo.start()
        self.addCleanup(self.mocked_repo.stop)
        self.mocked_run = patch.object(installer, "run", self.external_run)
        self.mocked_run.start()
        self.addCleanup(self.mocked_run.stop)

    def tearDown(self):
        self.tmp.cleanup()

    def manifest(self):
        path = self.bundle / "SHA256SUMS.txt"
        path.write_text("".join(f"{hashlib.sha256(p.read_bytes()).hexdigest()}  {p.relative_to(self.bundle).as_posix()}\n"
                               for p in sorted(self.bundle.rglob("*")) if p.is_file() and p != path))

    def external_run(self, argv, **options):
        self.commands.append([str(a) for a in argv])
        if "venv" in argv:
            python = Path(argv[-1]) / "bin/python"
            python.parent.mkdir(parents=True)
            python.write_text("synthetic interpreter")
        if str(argv[0]) == str(self.herdr):
            self.assertTrue(Path(options["env"]["HERDR_APP_HOME"]).is_relative_to(self.home))
            self.assertTrue(Path(options["env"]["HOME"]).is_relative_to(self.home))

    def runtime(self):
        return json.loads((self.home / "mods/session-hub/runtime.json").read_text())

    def test_tamper_and_wrong_platform_refused_before_target_writes(self):
        (self.bundle / "mods/session-hub/main.js").write_bytes(b"tampered")
        with self.assertRaises(ValueError):
            installer.install(self.home, str(self.herdr))
        self.assertFalse(self.home.exists())
        self.assertFalse(self.commands)
        self.manifest()
        wrong = "macos-arm64" if installer.target() == "linux-x64" else "linux-x64"
        with patch.object(installer, "target", return_value=wrong), self.assertRaisesRegex(ValueError, "platform"):
            installer.install(self.home, str(self.herdr))
        self.assertFalse(self.home.exists())

    def test_upgrade_keeps_old_runtime_and_source_bundle(self):
        before = (self.bundle / "SHA256SUMS.txt").read_bytes()
        installer.install(self.home, str(self.herdr))
        first = self.runtime()
        original = Path(first["python"]).read_bytes()
        installer.install(self.home, str(self.herdr))
        second = self.runtime()
        self.assertNotEqual(first["python"], second["python"])
        self.assertEqual(Path(first["python"]).read_bytes(), original)
        self.assertEqual((self.bundle / "SHA256SUMS.txt").read_bytes(), before)
        package.verify(self.bundle)
        pip = next(args for args in self.commands if "pip" in args)
        self.assertIn("--no-index", pip)
        self.assertIn("--require-hashes", pip)
        self.assertEqual((self.home / "data/session-hub").stat().st_mode & 0o777, 0o700)

    def test_failed_final_swap_restores_previous_mod_and_runtime(self):
        installer.install(self.home, str(self.herdr))
        previous = self.runtime()
        replace = os.replace
        def failed(source, destination):
            if Path(source).name.startswith(".session-hub-stage-"):
                raise OSError("Synthetic interrupted swap")
            replace(source, destination)
        with patch.object(installer.os, "replace", side_effect=failed), self.assertRaises(OSError):
            installer.install(self.home, str(self.herdr))
        self.assertEqual(self.runtime(), previous)
        self.assertTrue(Path(previous["python"]).is_file())
        self.assertFalse((self.home / "data/session-hub-install/pending.json").exists())

    def test_pending_receipt_and_concurrent_installer_are_refused(self):
        import fcntl
        installer.install(self.home, str(self.herdr))
        transaction = self.home / "data/session-hub-install"
        pending = transaction / "pending.json"
        pending.write_text("{}")
        with self.assertRaisesRegex(ValueError, "Interrupted"):
            installer.install(self.home, str(self.herdr))
        pending.unlink()
        with (transaction / "install.lock").open("rb") as source:
            fcntl.flock(source.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
            with self.assertRaisesRegex(ValueError, "Another installer"):
                installer.install(self.home, str(self.herdr))

    def test_uninstall_preserves_state_layout_keys_and_originals(self):
        installer.install(self.home, str(self.herdr))
        layout = self.home / "layouts/keep.json"
        layout.parent.mkdir()
        layout.write_text("layout sentinel")
        keys = self.home / "keys.json"
        keys.write_text("keys sentinel")
        original = self.base / "synthetic-provider.jsonl"
        original.write_text("original sentinel")
        state = self.home / "data/session-hub/keep.txt"
        state.write_text("retained state")
        before = {p:p.read_bytes() for p in (layout, keys, original)}
        installer.uninstall(self.home, dry_run=True)
        self.assertTrue((self.home / "mods/session-hub").exists())
        installer.uninstall(self.home)
        self.assertTrue(state.exists())
        installer.uninstall(self.home, purge=True)
        self.assertFalse(state.exists())
        self.assertTrue(all(p.read_bytes() == raw for p,raw in before.items()))


if __name__ == "__main__":
    unittest.main()
