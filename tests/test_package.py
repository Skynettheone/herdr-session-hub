"""Adversarial release inputs, without executing bundled code or provider CLIs."""
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("package_verifier", ROOT / "scripts/verify-package.py")
package = importlib.util.module_from_spec(spec)
spec.loader.exec_module(package)


class PackageTests(unittest.TestCase):
    def setUp(self):
        (ROOT / ".dev/tests").mkdir(parents=True, exist_ok=True)
        self.tmp = tempfile.TemporaryDirectory(dir=ROOT / ".dev/tests", prefix="package-")
        self.root = Path(self.tmp.name)
        for name in package.REQUIRED:
            path = self.root / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(b"synthetic package payload")
        (self.root / "version.json").write_text(json.dumps(dict(platform="windows-x64",version="0.1.0-dev")))
        self.manifest()

    def tearDown(self):
        self.tmp.cleanup()

    def manifest(self):
        lines = [f"{hashlib.sha256(p.read_bytes()).hexdigest()}  {p.relative_to(self.root).as_posix()}"
                 for p in sorted(self.root.rglob("*")) if p.is_file() and p.name != "SHA256SUMS.txt"]
        (self.root / "SHA256SUMS.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")

    def test_complete_bundle_and_tampered_file(self):
        self.assertEqual(package.verify(self.root), len(package.REQUIRED))
        (self.root / "mods/session-hub/main.js").write_bytes(b"changed")
        with self.assertRaisesRegex(ValueError, "checksum"):
            package.verify(self.root)

    def test_empty_missing_and_unlisted_payloads(self):
        path = self.root / "mods/session-hub/main.js"
        original = path.read_bytes()
        path.unlink()
        with self.assertRaisesRegex(ValueError, "missing"):
            package.verify(self.root)
        path.write_bytes(original)
        (self.root / "unexpected.txt").write_text("extra")
        with self.assertRaisesRegex(ValueError, "Unexpected"):
            package.verify(self.root)
        (self.root / "SHA256SUMS.txt").write_text("")
        with self.assertRaisesRegex(ValueError, "Incomplete"):
            package.verify(self.root)

    def test_unsafe_duplicate_and_windows_alias_paths(self):
        manifest = self.root / "SHA256SUMS.txt"
        valid = manifest.read_text()
        checksum = "0" * 64
        for name in ("../outside", "/absolute", "C:/absolute", "a\\b", "a/../b", "a//b", "a/./b", "README.md."):
            manifest.write_text(valid + f"{checksum}  {name}\n")
            with self.subTest(name=name), self.assertRaisesRegex(ValueError, "Unsafe"):
                package.verify(self.root)
        for name in ("README.md", "readme.md"):
            manifest.write_text(valid + f"{checksum}  {name}\n")
            with self.assertRaisesRegex(ValueError, "Duplicate"):
                package.verify(self.root)

    def test_private_and_hardlinked_files_are_refused(self):
        private = self.root / "auth.json"
        private.write_text("synthetic, not a credential")
        self.manifest()
        with self.assertRaisesRegex(ValueError, "Private"):
            package.verify(self.root)
        private.unlink()
        source = self.root / "README.md"
        linked = self.root / "linked.md"
        os.link(source, linked)
        self.manifest()
        with self.assertRaisesRegex(ValueError, "Hard-linked"):
            package.verify(self.root)

    def test_package_size_budget_is_bounded(self):
        from unittest.mock import patch
        with patch.object(package, "MAX_BYTES", 1), self.assertRaisesRegex(ValueError, "size budget"):
            package.verify(self.root)

    def test_linked_payload_directory_and_root_are_refused(self):
        payload = self.root / "payload-alias"
        os.symlink(self.root / "scripts", payload, target_is_directory=True)
        with self.assertRaisesRegex(ValueError, "Linked"):
            package.verify(self.root)
        payload.unlink()
        alias = self.root / "bundle-alias"
        os.symlink(self.root, alias, target_is_directory=True)
        with self.assertRaisesRegex(ValueError, "Linked"):
            package.verify(alias)

    def test_declared_platform_requires_its_own_offline_wheels(self):
        (self.root / "version.json").write_text(json.dumps(dict(platform="linux-x64",version="0.1.0-dev")))
        self.manifest()
        with self.assertRaisesRegex(ValueError, "Incomplete"):
            package.verify(self.root)
        for name in package.target_files("linux-x64"):
            path = self.root / name
            if not path.exists():
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(b"synthetic Linux payload")
        for name in package.REQUIRED - package.target_files("linux-x64"):
            (self.root / name).unlink()
        self.manifest()
        self.assertEqual(package.verify(self.root), len(package.target_files("linux-x64")))
        (self.root / "version.json").write_text(json.dumps(dict(platform="unverified-os")))
        self.manifest()
        with self.assertRaisesRegex(ValueError, "Unsupported"):
            package.verify(self.root)

    def test_install_payload_rejects_development_files_even_when_manifested(self):
        source = self.root / "tests/test_synthetic.py"
        source.parent.mkdir()
        source.write_text("synthetic source test, not part of an install payload")
        self.manifest()
        with self.assertRaisesRegex(ValueError, "Unexpected"):
            package.verify(self.root)


if __name__ == "__main__":
    unittest.main()
