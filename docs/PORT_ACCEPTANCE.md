# Platform ports and release scope — 2026-11-12

The user now approves the first stable release for Windows x64 only. This
supersedes the earlier requirement for macOS/Linux acceptance before any stable
release. Version 0.1.0 is stable only on Windows; Linux/macOS artifacts are
0.1.0-experimental.1 with releaseReady=false and continuation disabled. No
production installation, release tag or publication is authorized.

## Implemented port boundary

| Target | State / filesystem / process / installation | Native desktop continuation |
|---|---|---|
| Windows x64 | Existing DPAPI, mandatory source sharing, process/lock guards and offline installer retained | Five tested provider/version combinations; previous real GUI and continuity evidence retained |
| Linux x64 | Secret Service key via fixed `secret-tool` interface; PyCA AES-GCM, 0700 state and 0600 writes, flock, local-mount guard, cooperative SQLite DB/WAL/SHM locks, native binary/Node validation, offline transactional installer | Disabled pending native Herdr/provider acceptance |
| Apple Silicon macOS | Hub-only Keychain generic-password item; same authenticated state/permissions/transaction boundary, native local-filesystem and process interfaces, offline installer | Disabled pending native Herdr/provider acceptance |
| Intel macOS / other architectures | No claimed binary bundle: pinned cryptography 50.0.2 supplies no Intel macOS wheel; other architectures are not accepted targets | Unavailable |

The Windows continuation scope is Claude 2.1.322, Codex 0.164.0, Pi 1.1.0,
OpenCode 1.3.17 and Gemini 0.49.0 with Herdr GUI 0.1.15/core 0.1.20. Copilot
continuation, Cursor/Amp/unknown readers, original deletion, transcript restore,
remote sync and live account-wide billing/quotas remain disabled/unavailable.
Distinct company identities remain unverified; the available real account tests
use one identity in separate stores plus an unsigned negative control.

## Actual validation and its limits

Windows continues to exercise real DPAPI. Shared POSIX parser/index/Usage tests
use an in-memory fixture vault so hundreds of synthetic state roots do not add
keys to a person's OS key store. Runtime has no fixture flag, environment-key or
plaintext fallback. A separate opt-in hosted test uses **actual macOS Keychain
and Linux Secret Service**, creates only Hub-namespace random synthetic entries,
verifies read-back/encryption/decryption and an unsigned scope, and discards the
test VM afterward. No provider credentials or cloud account is queried.

Local Linux testing uses a checksum-verified official standalone Python 3.14.10
archive, explicit hash-locked wheels and fresh `/tmp/herdr-session-hub-port-*`
directories inside the existing Ubuntu WSL environment. HOME/PATH are isolated;
system Python and WSL user settings are not changed. This validates Linux helper
behavior, not WSL history traversal or a Linux GUI. Native CI uses Ubuntu 24.04
and Apple Silicon macOS 15. Final counts, CI and archive receipts are maintained
in RELEASE_REPORT.md; earlier failed CI runs are not represented as passes.

Real POSIX tests cover writer/checkpoint exclusion, preserving DB/WAL/SHM bytes,
missing-SHM refusal, Codex flock ownership, source-lock generation survival after
the last provider connection closes, state transactions, encryption failure and
installer rollback. Installer unit tests mock venv/pip/Herdr processes; they do
not establish a native GUI check. The standalone package verifier checks target
architecture and matching locked wheels. No library downgrade or source build
is silently substituted for the missing Intel macOS dependency wheel.

## Native acceptance still required

On each target desktop, use a fresh disposable home/core, genuine Herdr 0.1.15,
the exact provider versions and loopback synthetic histories. Verify the real
History/Usage panel, docking, focus/input/keyboard behavior, theme/width changes,
project trust and native context continuation, plus install/upgrade/uninstall
and app update/rollback. User-owned authentication/privacy notices must be handled
by the user. Do not enable `native_continuation_verified()` for a target until
that evidence is recorded and reviewed. Hosted unit/key-store checks alone do
not authorize lifting this guard.

Those native desktop checks are required before promoting either port to stable.
Port source and local experimental bundles are prepared for that next acceptance
step. They do not inherit Windows readiness, and their remaining acceptance does
not block the user-approved Windows-only stable scope. Nothing is published.
