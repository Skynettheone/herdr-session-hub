"""Opt-in real OS-key-store acceptance, only on disposable CI desktops.

No provider item is queried. The CI VM is discarded afterward. Runtime code has
no corresponding test-mode/unencrypted fallback.
"""
import importlib.util
import os
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("native_vault", ROOT / "mods/session-hub/helper/adapters/platform_io.py")
platform_io = importlib.util.module_from_spec(spec)
spec.loader.exec_module(platform_io)


@unittest.skipUnless(os.name != "nt" and os.environ.get("HUB_TEST_NATIVE_VAULT") == "1", "Requires a disposable native Keychain/Secret Service test session")
class NativeVaultTests(unittest.TestCase):
    def test_real_vault_roundtrip_and_missing_key_refusal(self):
        (ROOT / ".dev/tests").mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(dir=ROOT / ".dev/tests", prefix="native-vault-") as scratch:
            root = Path(scratch).resolve()
            platform_io.private_directory(root)
            key = platform_io.state_key(root, create=True)
            self.assertEqual(len(key), 32)
            self.assertEqual(platform_io.state_key(root), key)
            encrypted = platform_io.protect(b"synthetic native vault marker", root)
            (root / "state.hub").write_bytes(encrypted)
            self.assertEqual(platform_io.protect(encrypted, root, True), b"synthetic native vault marker")
            self.assertNotIn(b"synthetic native vault marker", encrypted)
            other = root / "unsigned-profile"
            other.mkdir(mode=0o700)
            with self.assertRaises(platform_io.PlatformError):
                platform_io.state_key(other)


if __name__ == "__main__":
    unittest.main()
