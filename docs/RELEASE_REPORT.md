# Release preparation report — 2026-11-12

Version **0.1.0-dev**, Windows x64, Python 3.14, Herdr GUI 0.1.15/core 0.1.20.
The source tasks are committed conventionally on main at the user-authorized
origin. No production install, original-history deletion, GitHub Release or
gallery publication was performed.

The candidate includes the collapsible History tab beside native Files/Changes,
six read-only history adapters, explicit profiles, incremental local indexing,
Hub-only organization and encrypted metadata portability. FEATURE_STATUS.md
maps every F01–F16 requirement to implementation, tested scope and limits.

## Validation and release status

53 Python tests, 11 host groups, correctness lint, isolated installed SDK check,
offline wheel verification and disposable install/upgrade/uninstall passed.
Hosted final-source Windows CI and final Python/JS CodeQL succeeded; links are in
TEST_RESULTS.md. Native continuity/updater evidence is in NATIVE_ACCEPTANCE.md
and FOLLOWUP_ACCEPTANCE.md. Manual security findings and fixes are documented;
no independent audit or certification is claimed.

`releaseReady=false` is intentional. A distinct company identity is unavailable;
several native form actions still need a human pass because automation focus was
unreliable. Gemini 0.49 duplicate snapshots refuse continuation. Mixed-build live
ownership and future Herdr SDKs require further acceptance. Native transcript
migration, original deletion and remote sync are unavailable. This candidate is
not an unqualified production release.

## Local packaging

`scripts/build-release.ps1 -AllowUnverified` prepares a clearly named development
ZIP containing source, native assets/licenses, tests, scripts, docs, genuine
screenshots and three hash-locked Windows encryption wheels. No local environment,
authentication stores, provider histories, runtime.json or SDK/research downloads
are package inputs. The builder repeats the required checks; the SDK check's own
configuration/state is isolated even when using the installed binary.

Every payload file is listed in SHA256SUMS.txt. Both staged payload and fresh ZIP
extraction must pass `python scripts/verify-package.py <directory>`. ZIP SHA-256 is
an integrity check, not a signature. All older ZIPs are superseded by the latest
verified candidate listed below. Filename/hash/final test output are appended
outside the ZIP after verification to avoid a checksum/report cycle.
