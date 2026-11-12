# Test results — 2026-11-12

## Windows 0.1.0 stable preparation

The user approves Windows x64-only stable scope. Source policy and tests are
committed at `cd30b9a`, with release documentation at
`61884d12e9f38836b2cc8b385d535f63830eb003`. Three new package regressions prove
that stable source derives only experimental POSIX artifacts, regenerated
manifests cannot promote a port/enable continuation, and source readiness cannot
silently expand stable scope. Runtime/native provider and UI code is unchanged.

The normal local Windows build, without AllowUnverified, passed **110 Python
tests in 61.377 seconds** (98 passed, 12 platform skips), **17 UI host groups**,
Ruff, the isolated installed Herdr SDK check, offline wheel hashes and staged/
fresh ZIP verification. The 10k list/search sample took 0.369 seconds. Private
Linux Python 3.14.10 ran **110 tests in 35.977 seconds** (106 passed, three
Windows-only plus one unavailable local native key-store check skipped).

Final hosted CI, disposable installer checks and immutable release/experimental
artifact receipts are in [RELEASE_REPORT.md](RELEASE_REPORT.md). Windows native
acceptance evidence remains valid for its recorded exact versions; experimental
macOS/Linux still require native GUI/context/updater acceptance before promotion.

Final hosted source `61884d1` passed all three jobs: 110 tests each, Windows
98 passed / 12 platform skips, Linux/macOS each 107 passed / 3 Windows-only skips.
Native Secret Service/Keychain checks and Windows Ruff/17 UI groups passed;
CodeQL passed with zero open alerts returned afterward. Real Windows installer
checks passed through default state retention; its interrupted final explicit
purge was resumed and independently verified against fixed original/layout/key
fixture hashes and package integrity. The first Linux package smoke's 60-second
offline-pip timeout was not counted as a pass; the fresh 180-second retry passed
packaged helper startup, missing-vault refusal/no plaintext and extraction integrity.

## Release-candidate payload checkpoint

Source `1b90fa48106e733923c1b4a86eadb425ef7b9adb` adds the install-only
allowlist and a regression proving that manifested development files are refused.
The local Windows build ran **107 Python tests in 53.854 seconds**, with 12
platform skips, plus **17 UI host groups**, Ruff and the isolated installed
Herdr SDK check. Its 10k list/search sample took 0.485 seconds. A fresh private
Linux Python 3.14.10 environment ran **107 tests in 22.289 seconds**, with three
Windows-only checks and the unavailable local native key-store check skipped.

Windows/macOS/Linux hosted results, fresh candidate archive receipts and real
installer checks are recorded in [RELEASE_REPORT.md](RELEASE_REPORT.md).
All three hosted platform jobs passed 107 tests: Windows 95 passed / 12 platform
skips, Linux/macOS each 104 passed / 3 Windows-only skips. Actual native key-store
checks passed, CodeQL passed and the repository returned zero open alerts.
The documentation/payload changes do not change native UI, accounting or provider
launcher implementation; existing GUI/Usage/continuation evidence retains its
recorded scope. No extra macOS/Linux desktop acceptance is inferred.

## Earlier platform-port checkpoint

On exact source `4b32d18e15d8d3858a37060ccb8fec4eaf35d0ae`, the essential
[platform matrix](https://github.com/Skynettheone/herdr-session-hub/actions/runs/43202496160)
and [CodeQL](https://github.com/Skynettheone/herdr-session-hub/actions/runs/43202496031)
passed. Windows ran 106 Python tests: 94 passed, 12 POSIX-only checks skipped,
plus 17 UI host groups and Ruff. Linux x64 ran 106: 103 passed, three Windows-only
checks skipped. Apple Silicon macOS ran 106: 103 passed, three Windows-only checks
skipped. Actual Linux Secret Service and macOS Keychain tests passed; Windows
retains actual DPAPI coverage. The repository reported zero open code-scanning
alerts afterward. Native GUI/context acceptance for the new ports remains pending.

The preceding local Ubuntu WSL stage with a private checksum-verified Python 3.14.10 environment ran
105 tests in 15.989 seconds: 101 passed, three Windows-only plus the unavailable
local desktop-key-store check skipped. This is helper coverage, not WSL history
support or a Linux GUI pass. POSIX tests verify real cross-process writer locks,
WAL generation lifetime, private state, and install transactions. Installer unit
tests mock pip/venv/SDK commands; no native desktop acceptance is inferred.
The user's requirement includes those desktops, which are unavailable, so the
production gate remains closed. PORT_ACCEPTANCE.md records the remaining work.

The final Windows build ran 106 tests in 37.368 seconds (12 platform skips),
17 host groups, Ruff, the isolated installed SDK check and offline wheel hashes.
Its 10k list/search sample took 0.457 seconds. Renewed real Windows install smoke
passed tamper refusal, failed-swap rollback/working old helper, receipt/lock
refusal, separate runtimes, immutable package, uninstall/state retention/Hub purge
and unchanged layout/key/original hashes. The final privacy regression proves
executable detection refuses credential-named alias targets before opening them.

## Release-hardening follow-up

**82 Python tests** passed in 33.884 seconds (76 previous + six adversarial
package groups), along with **17 native-host groups** and Ruff. The 10k-record
sample took 0.238 seconds. The renewed disposable install smoke passed checksum
tamper refusal before target writes, first install, injected final-swap failure
and old-helper recovery, unresolved receipt refusal, exclusive-lock refusal,
separate-runtime upgrade, unchanged source bundle, uninstall WhatIf, retained
state, explicit Hub purge and layout/key/original hashes. No mod/launcher/parser
code changed; existing native GUI/continuity evidence remains scoped below.
Final build/hosted CI/artifact receipts are recorded in RELEASE_REPORT.md.

This is a checked **0.1.0-dev Windows candidate**, not an unqualified production
release. The F01–F16 implementation/limits are in FEATURE_STATUS.md. Native checks
used disposable installations, histories and config homes; production config was
not an installation target. Real cloud checks used only new synthetic prompts.

## Automated checks

- **53 Python tests** and **12 native-host panel groups** passed locally and in
  hosted Windows CI. Ruff correctness checks passed. Coverage includes oversized
  and malformed histories, bounded compressed Codex rollouts, duplicate identity,
  active-writer refusal, SQLite WAL snapshot consistency, shared-profile FTS
  consent, argument/environment routing, interrupted state migration, hard links,
  encrypted portability/tampering/conflicts and safe unavailable operations.
- Installed Herdr SDK check passed with every checker home/config variable now
  explicitly isolated under `.dev/native-sdk-check`. It is a load/render check,
  not a substitute for native GUI interaction.
- Offline wheel hashes and disposable install/upgrade-backup/uninstall checks
  passed. The final bundle build/extraction results are in RELEASE_REPORT.md.
- A 10k-record list/search sample took 0.483 seconds in the preceding build;
  performance samples are machine/workload-specific, not guarantees.

## Native acceptance

- Claude Code 2.1.322, Codex 0.164.0, OpenCode 1.3.17 and Pi 1.1.0 resumed through
  the actual Hub button, retained native ID/profile/cwd and answered a fresh
  context-dependent prompt. Real CLIs/stores used a deterministic loopback model.
- Gemini 0.49.0 also passed native `--resume UUID` context/identity verification.
  Its repeated-resume duplicate snapshots deliberately fail closed. This was not
  a Google cloud-account test. See FOLLOWUP_ACCEPTANCE.md.
- User-controlled Claude sign-ins authenticated two isolated stores with one
  real identity. Both created separate real-cloud marker conversations; the
  personal Hub launch returned its prior marker on a fresh prompt. An unsigned
  third store had no auth fallback. A distinct company identity is unavailable.
- Herdr 0.1.14→0.1.15 update, verified backup rollback and re-update passed.
  Update retained 39 checked files; rollback retained 42 including encrypted Hub
  state. This is the tested version pair, not future-API compatibility assurance.
- Native History shares the right Files/Changes stack in a new personal layout;
  both its header chip and internal collapse control worked. Old layouts,
  shipped header, settings and keys remained unchanged. Removal/restore and
  archive/unarchive passed on synthetic Pi; the original hash stayed unchanged.
  Details, copy notices, filtering and narrow settings rendering were observed.
- Earlier native smoke covers search/debounce, preview, settings/catalog, multiple
  views, dark/light/community-format themes and a 420px pane. Unmodified new
  captures are `screenshots/history-tab.jpg` and `history-collapsed.jpg`.
- Final native status: `errors: []`. The follow-up test terminal was closed.

## CI and security

- [Windows tests on d0b19d5](https://github.com/Skynettheone/herdr-session-hub/actions/runs/43172531932): **success**.
- [Combined CodeQL on d0b19d5](https://github.com/Skynettheone/herdr-session-hub/actions/runs/43172531856): **success**.
  This covers the latest form/label implementation and regression tests. Code-scanning API reported zero open alerts after the scan.
- Manual assessment and six corrected findings are in SECURITY_REVIEW.md.
  The user declined Daybreak. No independent human audit is claimed.

CI stays limited to one relevant-change Windows test/lint/panel job and one
combined CodeQL job, with stale-run cancellation. No deployment/publication job.

## Coverage gaps and release gates

The earlier scrolled-form gaps are closed by the native pass in
FORM_ACCEPTANCE.md: alias save/reset, guided typing/save, empty-field validation,
malformed JSON, picker cancellation and Cancel passed after the usability fixes.
User-controlled synthetic-only opt-in, native index/search, clear and Off cleanup
passed; all profiles ended Off with zero indexed rows and unchanged originals.
Native privacy/trust/authentication controls require user handling. Exhaustive
GUI acceptance is not claimed. See FOLLOWUP_ACCEPTANCE.md for exact outcomes.

Distinct company-account identity, mixed-build ownership, future SDKs and
macOS/Linux/UNC/WSL remain unverified or unsupported. Original deletion, native
transcript migration and remote sync remain explicitly unavailable. The current
port checkpoint above supersedes the older blanket macOS/Linux status. Native
desktop acceptance is still required; no production installation or release
publication was performed.

## Usage follow-up — 2026-11-12

The Usage addition has 23 accounting/integration regressions, bringing the
Python suite to 76 tests, plus 17 native-host behavior groups. Recorded counters
and estimates matched an independent synthetic oracle for all four presets.
The actual GUI pass covered default dark, Paper light and Atom One Dark themes,
wide/narrow layouts, filters, UTC forms, charts/breakdowns, pricing and approved
rate/cache removal-restoration. Original hashes matched; every conversation
search flag remained Off. A real 0.1.14 SDK check found a missing optional scroll
export; guarded fallback now passes 0.1.14 and 0.1.15 SDK checks and cannot enable
older-host continuation just because a newer executable appears on PATH.

USAGE_ACCEPTANCE.md gives the exact native scope and oracle numbers;
USAGE_REVIEW.md records all six review findings and confirmed fixes. Final
runtime CI and package extraction evidence are in RELEASE_REPORT.md. CI remains
the essential Windows job and combined CodeQL job, with no publishing workflow.
