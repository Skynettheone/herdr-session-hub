# Release preparation report — 2026-11-12

## Current Usage candidate

The final runtime is `25e9dabd841fd119a4ea327c56a326fdf12b803a`;
acceptance documentation/captures are committed at `903528f`. This supersedes
the older History-only artifact entries retained below. Version remains
**0.1.0-dev / releaseReady=false**; no production installation or release/gallery
publication was performed.

The final build passed **76 Python tests in 30.581 seconds**, **17 UI host groups**,
Ruff, installed Herdr SDK validation and offline hashed-wheel verification.
A 10,000-record list/search sample took 0.264 seconds, without a performance
guarantee. The independent Usage oracle matched all four presets, token channels,
event counts, timeline/model sums and known estimated costs. Native dark/light/
community and narrow/wide checks, approved rate removal/restoration and cache
clear/rebuild passed; originals matched and content-search flags stayed Off.
The isolated app/core were stopped with final native `errors: []`.

Exact-runtime hosted CI passed:
[Windows tests](https://github.com/Skynettheone/herdr-session-hub/actions/runs/43187672204)
and [combined CodeQL](https://github.com/Skynettheone/herdr-session-hub/actions/runs/43187672208).
The repository had zero open code-scanning alerts at the final query. Workflow
scope remains one Windows job and one combined CodeQL job; no CD/publication job.

Separate standards/security and spec review found six issues, all fixed and
regression-tested, with follow-up confirmations. This is implementer-team review,
not an external human audit. The actual older 0.1.14 SDK check exposed a missing
scroll export; the guarded fallback passes 0.1.14/0.1.15 checks and preserves the
older-host continuation block. Interactive Usage acceptance is on 0.1.15.
The earlier complete updater/backup rollback evidence remains separately scoped.

Offline disposable installation, upgrade backup, uninstall WhatIf, retained
state, explicit Hub-only purge and unchanged layout/key/original sentinels passed.
The final archive is checked after fresh extraction, including manifest integrity,
source-byte comparisons and an isolated packaged helper invocation. Its sidecar
checksum is external; the post-build artifact receipt below is intentionally
outside the archive to avoid a checksum/report cycle. Runtime code is not changed
by this documentation refresh.

Live account-wide limits, subscription bills, Copilot persisted usage, ambiguous
Codex fork reconstruction and distinct-company account verification remain
documented limits. See USAGE_ACCEPTANCE.md, USAGE_REVIEW.md and USER_GUIDE.md for
the precise verified scope. These checks do not certify every possible history,
community palette, provider version or future Herdr SDK.

## Verified Usage artifact receipt

`herdr-session-hub-0.1.0-dev-windows-x64-20261112090853.zip`, **5,017,879 bytes**.
SHA-256: `2abbb1f2eddcd1e97dc0a007f8ceda948b01dc299b02197cef8e5b735f894ce2`.

Staging and fresh extraction verified **110 manifest files**; all **57**
runtime/script/test/artwork payload files match the tested repository bytes.
The fresh packaged helper passed an isolated numeric-refresh invocation,
and the extracted native mod passed the installed SDK check. No development
state, auth files or local runtime configuration is included. The final
archive and its external `.zip.sha256` sidecar remain local; no release
was published. This receipt was appended after hashing and intentionally
does not change the verified archive.

## Historical History-only candidate evidence

Version **0.1.0-dev**, Windows x64, Python 3.14, Herdr GUI 0.1.15/core 0.1.20.
The source tasks are committed conventionally on main at the user-authorized
origin. No production install, original-history deletion, GitHub Release or
gallery publication was performed.

The candidate includes the collapsible History tab beside native Files/Changes,
six read-only history adapters, explicit profiles, incremental local indexing,
Hub-only organization and encrypted metadata portability. FEATURE_STATUS.md
maps every F01–F16 requirement to implementation, tested scope and limits.

## Validation and release status

53 Python tests, 12 host groups, correctness lint, isolated installed SDK check,
offline wheel verification and disposable install/upgrade/uninstall passed.
Hosted final-source Windows CI and final Python/JS CodeQL succeeded; links are in
TEST_RESULTS.md. Native continuity/updater evidence is in NATIVE_ACCEPTANCE.md
and FOLLOWUP_ACCEPTANCE.md. Manual security findings and fixes are documented;
no independent audit or certification is claimed.

`releaseReady=false` is intentional. A distinct company identity is unavailable;
The previously open native form actions passed after the usability fixes in
FORM_ACCEPTANCE.md; privacy-control handling remains user-owned. Gemini 0.49 duplicate snapshots refuse continuation. Mixed-build live
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

## Previous verified candidate

This ZIP predates the form/duplicate-label fixes in df50a84. It is retained as
historical evidence; the next verified package supersedes it.

`herdr-session-hub-0.1.0-dev-windows-x64-20261112063431.zip`, **4,624,285 bytes**.
SHA-256: `f0839d9b5419f671bfc6a7586d0e8fa96d094b8778ee197c929b0530cd136f4c`.
Staging and a fresh extraction each verified **97 files**, with no development
state, auth stores or runtime configuration. The ZIP remains local/unpublished.

This build passed Ruff, **53 Python tests** in 14.997 seconds, **11 panel groups**,
isolated installed SDK check and offline wheel hashes. Its 10k-record list/search
sample took 0.144 seconds. The final-checker disposable install smoke passed
offline first install, upgrade backup, uninstall WhatIf, retained state, explicit
Hub purge and unchanged layout/key/original sentinels. The final GUI metadata
round-trips preserved the original hash and all four header/settings/old-layout
sentinels. Native status ended with errors=[]. The isolated app/core and loopback
fixture were stopped; private user-created sign-in homes were retained locally,
ignored by Git and excluded from the package, without reading or revoking them.

Source changes through `c55af3b` passed Windows CI; final Python/JS at `1c104dc`
passed combined CodeQL. Acceptance/docs/screenshots are committed at `1a2fc68`.
This post-build result entry is intentionally external to the ZIP, avoiding a
checksum/report cycle. No runtime code changed after validation.

## Completed native form and privacy follow-up

Source commits df50a84 and d0b19d5 fix the dedicated forms, JSON editor, duplicate
labels, search focus and refresh completion. Native alias/reset, guided save,
validation, JSON errors and picker cancellation passed. User-controlled Pi-only
consent, indexing, full-text search, clear and Off cleanup passed. All profiles
ended Off; indexed rows and marker matches were zero; original/native-file hashes
were unchanged and native status had no errors. The disposable app/core are stopped.
See FORM_ACCEPTANCE.md for evidence and the interrupted final screenshot boundary.

The final-code build passed 53 Python tests (28.316 seconds), 12 panel groups,
Ruff, isolated installed SDK validation and offline wheel verification. A 10k
list/search sample took 0.270 seconds, without a performance guarantee. Windows
CI and combined CodeQL passed on d0b19d5. The installer is unchanged from the
previous passed install/upgrade/uninstall smoke; no redundant install was run.

The final artifact refresh changes documentation and genuine captures only. The
already-tested runtime/test/script payload is checked byte-for-byte before
repackaging. New filename/checksum are recorded outside the archive after fresh
extraction verification; no implementation code or dependencies changed.

## Final verified form-acceptance candidate

`herdr-session-hub-0.1.0-dev-windows-x64-20261112071625.zip`, **4,691,854 bytes**.
SHA-256: `b5eae024354ed75fca2bcc6c00e14276d33f553c342b1cf312832ae416ea8acf`.
Staging and fresh extraction both verified **100 files**, with no development
state, credentials, provider histories or local runtime configuration. All **53**
runtime/test/script payload files match the already-tested source byte-for-byte;
only documentation and genuine native screenshots were refreshed after cleanup.
The final report/checksum entry is external to the ZIP to avoid a checksum cycle.

All requested remaining native form and synthetic privacy round-trip checks are
complete. The test app/core are stopped. The package remains a local development
candidate with the previously documented account/provider/platform limits; it
was not installed into production or published as a release.
