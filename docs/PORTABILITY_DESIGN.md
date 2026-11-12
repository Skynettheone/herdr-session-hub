# macOS and Linux port checkpoint — 2026-11-12

The user requires both native ports before production readiness. Windows-only
scope was explicitly declined. Keep `releaseReady=false` until the required
native acceptance exists; do not equate Herdr OS support with Hub acceptance.

## Confirmed boundaries before implementation

- Windows DPAPI, byte-range locks, process enumeration and source share modes are
  platform-specific. Preserve those paths rather than replacing working guards.
- macOS can keep a Hub-only AES key in Keychain using documented generic-password
  APIs. Linux needs an unlocked Secret Service and `secret-tool`; no plaintext
  key file, environment-secret or fallback to unencrypted state is acceptable.
- POSIX `flock` supports Hub-owned state/install serialization. SQLite database
  byte-range locking uses `fcntl` instead; these mechanisms are not equivalent.
  A missing source SHM cannot be created by this read-only extension. Unsupported
  snapshot conditions must remain unavailable instead of using unlocked copies.
- Native POSIX executable files and explicit Node launchers need argv/fingerprint
  validation. Other process command lines and provider credentials remain private.
- This host has Windows GUI acceptance and an existing Ubuntu WSL environment
  with Python 3.12.3, but no discovered Python 3.14 or Secret Service client.
  Docker is not running. macOS native GUI testing is not available locally.

## Primary interfaces studied

- [Apple generic-password function declarations](https://github.com/apple-oss-distributions/Security/blob/main/OSX/libsecurity_keychain/lib/SecKeychain.cpp)
- [GNOME secret-tool argument/stdin interface](https://github.com/GNOME/libsecret/blob/main/tool/secret-tool.c)
- [Python POSIX locking](https://docs.python.org/3.14/library/fcntl.html)
- [SQLite rollback locking](https://sqlite.org/lockingv3.html)
- [SQLite WAL lock offsets](https://sqlite.org/walformat.html#wal_locks)
- [Codex writer-lock protocol](https://github.com/openai/codex/blob/main/codex-rs/rollout/src/writer_lock.rs)

Implementations are independent adapters, not copies of Apple/GNOME source.
Research concerns interfaces, not a review of all upstream security. Native
key-store denial, unavailable desktop bus, permissions and missing APIs must
produce safe errors without exposing key material. Local state is OS/user bound;
encrypted metadata exchange remains the portable route. No original histories
or production configuration are port/test targets.
