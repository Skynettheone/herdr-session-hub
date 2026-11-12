"""Portable encrypted-state invariants; fake vaults never replace runtime vaults."""
import ctypes
import importlib.util
import os
from pathlib import Path
import secrets
import subprocess
import tempfile
import unittest
from unittest.mock import MagicMock, patch

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("platform_io_test", ROOT / "mods/session-hub/helper/adapters/platform_io.py")
platform_io = importlib.util.module_from_spec(spec)
spec.loader.exec_module(platform_io)


class PortableStateTests(unittest.TestCase):
    def setUp(self):
        (ROOT / ".dev/tests").mkdir(parents=True, exist_ok=True)
        self.tmp = tempfile.TemporaryDirectory(dir=ROOT / ".dev/tests", prefix="platform-")
        self.root = Path(self.tmp.name)
        self.keys = {}

    def tearDown(self):
        self.tmp.cleanup()

    def key(self, root, create=False):
        identity = platform_io.account(root)
        if create:
            self.keys.setdefault(identity, secrets.token_bytes(32))
        if identity not in self.keys:
            raise platform_io.PlatformError("Test key missing")
        return self.keys[identity]

    def test_authenticated_encryption_wrong_key_tamper_and_root_binding(self):
        data = b"SYNTHETIC PRIVATE CONTENT"
        with patch.object(platform_io, "state_key", self.key):
            encrypted = platform_io.protect(data, self.root)
            self.assertNotIn(data, encrypted)
            self.assertNotEqual(encrypted, platform_io.protect(data, self.root))
            self.assertEqual(platform_io.protect(encrypted, self.root, True), data)
            for changed in (encrypted[:-1], encrypted[:-1] + bytes([encrypted[-1] ^ 1]), b"old plaintext"):
                with self.assertRaises(platform_io.PlatformError):
                    platform_io.protect(changed, self.root, True)
            other = self.root / "different-state-home"
            self.keys[platform_io.account(other)] = self.key(self.root)
            with self.assertRaises(platform_io.PlatformError):
                platform_io.protect(encrypted, other, True)
            self.keys[platform_io.account(self.root)] = secrets.token_bytes(32)
            with self.assertRaises(platform_io.PlatformError):
                platform_io.protect(encrypted, self.root, True)

    def test_missing_key_never_reinitializes_existing_or_backup_state(self):
        for name in ("state.hub", "state.hub.bak"):
            path = self.root / name
            path.write_bytes(b"existing encrypted evidence")
            with patch.object(platform_io, "state_key", self.key):
                with self.assertRaisesRegex(platform_io.PlatformError, "Test key missing"):
                    platform_io.protect(b"replacement", self.root)
            self.assertFalse(self.keys)
            self.assertEqual(path.read_bytes(), b"existing encrypted evidence")
            path.unlink()

    def test_unavailable_vault_has_no_plaintext_fallback(self):
        with patch.object(platform_io, "state_key", side_effect=platform_io.PlatformError("Vault unavailable")):
            with self.assertRaisesRegex(platform_io.PlatformError, "Vault unavailable"):
                platform_io.protect(b"private", self.root)
        self.assertEqual(list(self.root.iterdir()), [])

    def test_linux_key_stays_out_of_argv_and_missing_lookup_does_not_create(self):
        saved = []
        def run(argv, **options):
            self.assertFalse(options["shell"])
            self.assertEqual(Path(argv[0]).as_posix(), "/usr/bin/secret-tool")
            if argv[1] == "lookup":
                return subprocess.CompletedProcess(argv, 0 if saved else 1, saved[-1] if saved else b"")
            saved.append(options["input"])
            self.assertNotIn(saved[-1].decode(), argv)
            return subprocess.CompletedProcess(argv, 0)
        with patch.object(Path, "is_file", return_value=True), patch.object(platform_io.subprocess, "run", side_effect=run):
            with self.assertRaises(platform_io.PlatformError):
                platform_io.linux_key(b"synthetic-scope")
            self.assertFalse(saved)
            key = platform_io.linux_key(b"synthetic-scope", create=True)
            self.assertEqual(len(key), 32)
            self.assertEqual(platform_io.linux_key(b"synthetic-scope"), key)

    def test_keychain_denial_cannot_create_or_expose_a_key(self):
        library = MagicMock()
        library.SecKeychainSetUserInteractionAllowed.return_value = 0
        library.SecKeychainFindGenericPassword.return_value = -25308  # interaction not allowed
        with patch.object(platform_io.ctypes, "CDLL", return_value=library):
            with self.assertRaises(platform_io.PlatformError):
                platform_io.mac_key(b"synthetic-scope", create=True)
        library.SecKeychainAddGenericPassword.assert_not_called()

    def test_keychain_existing_key_is_read_and_freed(self):
        library = MagicMock()
        library.SecKeychainSetUserInteractionAllowed.return_value = 0
        secret = ctypes.create_string_buffer(secrets.token_bytes(32))
        def find(*args):
            args[5]._obj.value = 32
            args[6]._obj.value = ctypes.cast(secret, ctypes.c_void_p).value
            return 0
        library.SecKeychainFindGenericPassword.side_effect = find
        with patch.object(platform_io.ctypes, "CDLL", return_value=library):
            self.assertEqual(platform_io.mac_key(b"synthetic-scope"), secret.raw[:32])
        library.SecKeychainItemFreeContent.assert_called_once()
        library.SecKeychainAddGenericPassword.assert_not_called()

    def test_local_filesystem_gate_rejects_network_and_unknown_types(self):
        library = MagicMock()
        def detected(_path, buffer):
            ctypes.c_ulong.from_buffer(buffer).value = 0xef53
            return 0
        library.statfs.side_effect = detected
        with patch.object(platform_io.sys, "platform", "linux"), patch.object(platform_io.ctypes, "CDLL", return_value=library):
            platform_io.local_filesystem(self.root)
            library.statfs.side_effect = lambda _p, buffer: 0
            with self.assertRaises(platform_io.PlatformError):
                platform_io.local_filesystem(self.root)
            library.statfs.side_effect = lambda _p, buffer: -1
            with self.assertRaises(platform_io.PlatformError):
                platform_io.local_filesystem(self.root)

    def test_keychain_creation_reads_back_the_exact_new_key(self):
        library = MagicMock()
        library.SecKeychainSetUserInteractionAllowed.return_value = 0
        saved = []
        def find(*args):
            if not saved:
                return -25300
            args[5]._obj.value = 32
            args[6]._obj.value = ctypes.cast(saved[0], ctypes.c_void_p).value
            return 0
        def added(*args):
            saved.append(ctypes.create_string_buffer(ctypes.string_at(args[6], args[5])))
            return 0
        library.SecKeychainFindGenericPassword.side_effect = find
        library.SecKeychainAddGenericPassword.side_effect = added
        with patch.object(platform_io.ctypes, "CDLL", return_value=library):
            key = platform_io.mac_key(b"synthetic-new-scope", create=True)
        self.assertEqual(len(key), 32)
        self.assertTrue(key == saved[0].raw[:32])
        self.assertEqual(library.SecKeychainFindGenericPassword.call_count, 2)

    def test_process_ownership_is_conservative_without_reading_arguments(self):
        def answer(output, code=0):
            return subprocess.CompletedProcess([], code, output)
        with patch.object(platform_io.subprocess, "run", return_value=answer(b"101 /usr/bin/node\n")) as run, patch.object(platform_io.os, "getpid", return_value=99):
            self.assertTrue(platform_io.process_owned("pi", "/usr/bin/node"))
            self.assertFalse(platform_io.process_owned("claude", "/usr/bin/claude"))
            self.assertEqual(run.call_args.args[0], ["/bin/ps", "-A", "-o", "pid=,comm="])
        for output, code in ((b"malformed", 0), (b"", 0), (b"101 node", 1)):
            with patch.object(platform_io.subprocess, "run", return_value=answer(output, code)):
                self.assertIsNone(platform_io.process_owned("pi"))

    def test_shell_script_is_not_a_native_executable(self):
        script = self.root / "synthetic-cli"
        script.write_bytes(b"#!/bin/sh\necho must-not-run\n")
        script.chmod(0o700)
        self.assertFalse(platform_io.native_executable(script))

    @unittest.skipIf(os.name == "nt", "POSIX ownership/mode acceptance")
    def test_private_directory_rejects_shared_permissions(self):
        self.root.chmod(0o755)
        with self.assertRaises(platform_io.PlatformError):
            platform_io.private_directory(self.root)
        self.assertEqual(self.root.stat().st_mode & 0o777, 0o755)
        self.root.chmod(0o700)
        platform_io.private_directory(self.root)


if __name__ == "__main__":
    unittest.main()
