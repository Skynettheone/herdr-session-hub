# Release preparation report — 2026-11-12

## Windows 0.1.0 publication

The user explicitly authorized publication. Release
[v0.1.0](https://github.com/Skynettheone/herdr-session-hub/releases/tag/v0.1.0)
was published at **2026-11-12T12:02:01Z** as the latest stable Windows-only release.
The tag targets `e856ecd0b458304b0518e94d686700a21fb93d9d`, adding only the final
test/security/receipt documentation to tested source `61884d1`. Prepublication
checks confirmed the same passing platform CI/CodeQL and zero open alerts,
unchanged runtime/installer/tests, the frozen ZIP hash and 59-file extraction.

Uploaded four assets only: the verified Windows ZIP, its .zip.sha256 sidecar,
SHA256SUMS.txt and RELEASE_NOTES.md. All four were downloaded and compared before
publishing, then downloaded and verified again after publication. The tag target,
non-draft/non-prerelease state and latest-stable status were confirmed through
GitHub. No experimental OS assets, provider data, local state or credentials
were uploaded.

| Published asset | SHA-256 |
|---|---|
| herdr-session-hub-0.1.0-windows-x64-20261112112444.zip | `bb9bd3e13794165d1fb6d29540f782ff20f00bbe6c8ecf7a2a27f8083c9f2309` |
| herdr-session-hub-0.1.0-windows-x64-20261112112444.zip.sha256 | `150a50dc8c20d13bb3e040d83eb89549d4979f11893dec46c0281b2f9be8061b` |
| SHA256SUMS.txt | `1666157c23c852a4560de879da8a3e4b94f44d181d2d050210e73c1b7142454c` |
| RELEASE_NOTES.md | `3120c6cecd9c6156dc96e12d9ddc7c490477f0933844ca2db34a27de23a2a118` |

The ZIP and individual sidecar are unchanged from the approved frozen build.
Publication notes update the date/status and use absolute installation links;
the published aggregate manifest covers those publication files. Original
preparation receipts and their hashes remain below. GitHub normalizes release
body line endings; downloaded assets match exact bytes.

At the user's request, the release title was shortened to **Herdr Session Hub
0.1.0** and its web-page notes were rewritten with clearer installation steps,
single-line paragraphs, concise limits and no long dashes. Implementation flags
and lengthy test/provenance detail stay in this report. Published ZIP, downloadable
notes and checksum assets remain frozen; the editable release page is the current
presentation. Repository download links are updated only after observing publication.
No production configuration was installed or changed. Released assets remain
unchanged after the documentation refinements.

## Current Windows 0.1.0 stable preparation

The user explicitly approves **Windows 11 x64-only stable scope**, superseding
the earlier cross-platform-first gate. Source policy/tests are at `cd30b9a`,
with release documentation at `61884d12e9f38836b2cc8b385d535f63830eb003`.
Windows metadata is version=0.1.0, channel=stable, releaseReady=true and
stablePlatforms=[windows-x64]. Both POSIX artifacts are version=0.1.0-experimental.1,
channel=experimental, releaseReady=false and nativeContinuationVerified=false.
The runtime POSIX continuation guard is unchanged and independently tested.

No native UI, history/Usage parser, encryption or provider-launch implementation
changed in this preparation (`mods/` matches the preceding accepted source).
Windows native GUI, five exact provider versions, real-cloud Claude continuation,
representative themes/forms/Usage and isolated Herdr update/rollback retain their
recorded acceptance scope. Experimental native desktop tests no longer block
Windows-only stable readiness, but remain required before promoting those ports.

### Final checks

On exact source `61884d12e9f38836b2cc8b385d535f63830eb003`, the essential
[three-platform CI](https://github.com/Skynettheone/herdr-session-hub/actions/runs/43209103184)
and [CodeQL](https://github.com/Skynettheone/herdr-session-hub/actions/runs/43209103202)
passed. Each target ran **110 Python tests**: Windows **98 passed / 12 platform
skips**; Linux/macOS each **107 passed / 3 Windows-only skips**. Actual Secret
Service and Keychain checks passed; Windows also passed Ruff and **17 UI host
groups**. The subsequent API query returned **zero open code-scanning alerts**.

The normal local Windows build passed without AllowUnverified: 110 tests in
61.377 seconds, 17 UI groups, Ruff, isolated installed SDK validation, offline
wheel hashes and stage/fresh-extraction checks. Its 10k list/search sample took
0.369 seconds. Local private Linux Python 3.14.10 ran 110 tests in 35.977 seconds,
with four environment/platform skips. Full details are in TEST_RESULTS.md.

The real Windows offline smoke reached checksum-tamper refusal before writes,
first install, failed-swap rollback with a working old helper, pending-receipt and
concurrent-lock refusal, separate-runtime upgrade, immutable package, uninstall
WhatIf and retained state. Its explicit final Hub purge was interrupted after
starting; cleanup was resumed in that same confined test home. The resumed check
completed all Hub-owned removals and independently verified the original fixture,
layout and key bytes plus unchanged source-package integrity. No production
configuration or real provider history was a test/purge target.

Fresh ZIPs verify every included source/wheel byte, with only generated target
version metadata differing from source. The Windows packaged helper passed an
isolated numeric refresh and its extraction remained valid. The first Linux
packaged smoke timed out during offline pip at 60 seconds; a fresh bounded retry
at 180 seconds passed startup, matching wheels, missing-Secret-Service refusal,
no plaintext state and unchanged extraction. The timeout is not counted as a
pass. macOS archive/source integrity and hosted native key-store checks pass;
native GUI/package installation acceptance remains experimental and unverified.

### Frozen artifact receipts

These artifacts supersede the earlier candidates. Windows has **59 manifest
payload files**, experimental ports **57** each, plus their manifest. All have
external `.zip.sha256` sidecars. The release report is outside the ZIPs so recording
these receipts does not change artifact hashes.

| Target / channel | Local ZIP | Bytes | SHA-256 |
|---|---|---:|---|
| Windows x64 stable | `herdr-session-hub-0.1.0-windows-x64-20261112112444.zip` | 4,407,324 | `bb9bd3e13794165d1fb6d29540f782ff20f00bbe6c8ecf7a2a27f8083c9f2309` |
| Linux x64 experimental | `herdr-session-hub-0.1.0-experimental.1-linux-x64-20261112112319.zip` | 5,314,316 | `e40d06970bdc46b6e37b15b390ab890d397de7207f9d52e4fcbbbbbbd2655a02` |
| macOS arm64 experimental | `herdr-session-hub-0.1.0-experimental.1-macos-arm64-20261112112323.zip` | 4,495,592 | `c386e4ff33c8411868e45143969e235419310465409051dc420597b1c6007259` |

`dist/release-0.1.0/` is the curated **Windows-only** publication input directory:
the exact ZIP/sidecar above, RELEASE_NOTES.md, RELEASE-RECEIPT.json with tested
source/CI provenance, and SHA256SUMS.txt covering those four files. Copy equality
and all checksums were verified. Experimental ZIPs remain outside this directory.
No production installation, git tag, GitHub release or gallery change was made.
Publication and production installation still require explicit approval.

## Previous 0.1.0-rc.1 install candidate

Public presentation and agent setup are committed at `d6a825e`; the shared
install-payload policy, builders and regression tests at
`1b90fa48106e733923c1b4a86eadb425ef7b9adb`. README includes the licensed official
logo, genuine synthetic History/Usage captures, compatibility badges, install
snippets and an agent-install prompt. The recipe follows Herdr's native mod
format with explicit helper setup/access and preservation of existing layouts.
Old starter prompts are archived in source; tests, fixtures, build tools and
audit documents remain maintainable source files, excluded from consumer ZIPs.
Private development/account-lab homes were not deleted or used as build inputs.

On that exact source, the essential
[platform matrix](https://github.com/Skynettheone/herdr-session-hub/actions/runs/43206594745)
and [CodeQL](https://github.com/Skynettheone/herdr-session-hub/actions/runs/43206594659)
passed. Each platform ran **107 tests**: Windows **95 passed / 12 platform skips**,
Linux/macOS each **104 passed / 3 Windows-only skips**. Actual Secret Service and
Keychain checks passed; Windows also passed Ruff and 17 UI host groups. Zero open
code-scanning alerts were returned after the scan. Local build times and scope
are in TEST_RESULTS.md.

The renewed real offline Windows install smoke passed tamper refusal before
target writes, failed-swap recovery with a working old helper, interrupted
receipt/concurrent-lock refusal, separate-runtime upgrade, immutable bundle,
uninstall WhatIf, state retention, explicit Hub purge and unchanged
layout/key/synthetic-original sentinels. The new Linux ZIP passed actual isolated
Linux helper startup using only its own offline wheels. Missing Secret Service
correctly refused state writes without plaintext fallback, and extraction still
verified. macOS archive/source integrity and native hosted key-store/dependency
tests passed; native desktop installation/GUI acceptance remains unverified.

The artifacts below supersede the earlier development bundles. They are local,
unpublished candidates with `releaseReady=false`: the user-required macOS/Linux
native GUI/context acceptance still needs unavailable desktops. Native POSIX
continuation remains disabled. Candidate naming and passing helper tests do not
clear that gate. No production installation, tag, release or gallery listing was
performed.

### Install-only candidate receipts

Windows has **58 manifest payload files**, Linux/macOS **56** each (plus the
manifest itself). Every included source/wheel byte matches the reviewed checkout;
only generated target version metadata differs. All three fresh ZIP extractions
and external SHA-256 sidecars verify. The packaged Windows helper passed an
isolated numeric refresh without changing its extracted package.

| Target | Local ZIP | Bytes | SHA-256 |
|---|---|---:|---|
| Windows x64 | `herdr-session-hub-0.1.0-rc.1-windows-x64-20261112110737.zip` | 4,404,895 | `8200abe7aa8f4a77d9df956e73894c2e864f71bced2932b273652cf1c5235e9a` |
| Linux x64 experimental | `herdr-session-hub-0.1.0-rc.1-linux-x64-20261112110815.zip` | 5,310,129 | `974df20fb564454c5a9e5244e589dbf39a755af725ad4195b78f77a52f865ab9` |
| macOS arm64 experimental | `herdr-session-hub-0.1.0-rc.1-macos-arm64-20261112110820.zip` | 4,491,397 | `b6a9dadc39f00ba4f2224210f0d39f6e18960a806aa21ba97e98f12ed050c371` |

## Earlier native-port development candidate

The user requires macOS/Linux ports before production readiness and confirmed
no additional desktops are available. Windows-only production scope was not
accepted. Portable core, native key stores, cooperative writer locks, offline
installers and platform bundles are implemented; POSIX native continuation and
the overall production gate remain disabled pending real Herdr GUI/context tests.
See PORT_ACCEPTANCE.md for the precise scope and follow-up procedure.

Source stages are committed separately: `248b2a8` native state services,
`8d65a29` POSIX filesystem/source guards, `4c904ab` packaging and OS CI,
`720bdc8` YAML correction, `942a40c` WAL lifetime/Keychain read-back and
`930928a` canonical executable test expectations and `4b32d18` credential-target
refusal before executable inspection. Final source
`4b32d18e15d8d3858a37060ccb8fec4eaf35d0ae` passed
[all three platform jobs](https://github.com/Skynettheone/herdr-session-hub/actions/runs/43202496160)
and [combined CodeQL](https://github.com/Skynettheone/herdr-session-hub/actions/runs/43202496031).
Zero open code-scanning alerts were reported afterward.

Each platform ran 106 Python tests: Windows **94 passed / 12 platform skips**,
Linux and Apple Silicon macOS each **103 passed / 3 Windows-only skips**.
Windows also passed Ruff and 17 UI host groups. Actual Keychain and Secret Service
creation/read-back/encryption/decryption/unsigned-scope checks passed. Local
isolated Linux's preceding stage ran 105 with four skips (its actual desktop key store is absent).
Real source-lock tests cover active transactions, checkpoints and the last
provider connection closing while a snapshot holds the SHM deadman switch.

The final local Windows build repeated 106 tests in 37.368 seconds, 17 host groups,
Ruff, isolated installed SDK validation, offline hashes and 123-file stage/fresh
extraction verification. Its 10k sample took 0.457 seconds. The renewed actual
offline Windows install smoke passed tamper/receipt/lock refusal, failed final
swap recovery with a working old helper, distinct retained runtimes, unchanged
source bundle, WhatIf/uninstall/state retention/Hub purge and unchanged sentinels.
Final documentation refresh does not change any tested runtime/script/test byte.

No provider credential, production configuration, original history or remote
endpoint was a port test target. The first CI failures (YAML quoting and raw
Python symlink expectations) were fixed and rerun; they are not counted as passes.
Installer transaction tests mock external processes and do not substitute for
native GUI acceptance. The Windows/native update evidence remains separately
valid for its recorded scope; it is not attributed to macOS/Linux.

Local Windows and experimental Linux x64/macOS arm64 bundles are prepared only
with explicit development labels, matching offline wheels, manifests and fresh
extraction checks. Final artifact/checksum receipts are appended externally to
avoid a checksum cycle. No production install, tag, release or gallery publication
was performed. Intel macOS and other architectures have no accepted bundle.

### Final unpublished port artifact receipts

Each artifact has **123 manifest files** and **66 runtime/script/test/artwork
payload files** that match the tested source. Staging and final fresh extraction
passed verification. Only public Markdown was refreshed after freezing runtime
bytes; this receipt is intentionally appended outside the archives to avoid a
checksum cycle. Each ZIP has a matching external `.zip.sha256` sidecar.

| Target | Local ZIP | Bytes | SHA-256 |
|---|---|---:|---|
| Windows x64 | `herdr-session-hub-0.1.0-dev-windows-x64-20261112104205.zip` | 5,069,145 | `6f28bc62e2a63f72bada1fd8d9ae5b7e389eae41072f9eac39fb012eeee1b5a7` |
| Linux x64 experimental | `herdr-session-hub-0.1.0-dev-linux-x64-20261112104735.zip` | 5,975,629 | `7402a9c6162842674ae39dcb03f2d35d47db254d94bdff66806ca62ef4233a8a` |
| macOS arm64 experimental | `herdr-session-hub-0.1.0-dev-macos-arm64-20261112104735.zip` | 5,157,160 | `bc36997c5740208371a3f88540737e631bda4dbfda6680d72488c6429bcefc67` |

The extracted Windows helper passed an isolated numeric-refresh invocation and
the package still verified afterward. The Linux ZIP was then checksum-verified,
extracted and invoked using an actual isolated Linux Python 3.14.10 interpreter
with only its own hash-locked offline wheels. Packaged helper list/startup passed;
its missing desktop key store correctly refused a write with a single safe error
and no plaintext state. Extraction still verified after both operations. macOS
package integrity/source equality is verified, with actual native dependencies
and key-store behavior covered by hosted tests; no macOS GUI or native package
installation acceptance is claimed. Zero open CodeQL alerts were reported after
the final source scan. All three archives remain local and unpublished.

## Previous release-hardening candidate

Package/installer fixes are committed separately at `556f0aa` and `c235dc9`;
the tested source/docs snapshot is `fce7c5f79b413da8f43fd49cf38a54cf1f7f242c`.
No native mod, provider launcher or accounting implementation changed after
the previous native acceptance. See PRODUCTION_READINESS.md for the reconciled
scope, external evidence limits and deliberately unavailable operations.

The final build passed **82 Python tests in 19.777 seconds**, **17 UI host groups**,
Ruff, installed Herdr 0.1.15 SDK validation and all offline wheel hashes. A 10k
list/search sample took 0.177 seconds. Six new package regression groups include
real Windows hard/directory links. The renewed disposable install smoke passed
pre-write tamper refusal, injected final-swap rollback and a working old helper,
pending-receipt refusal, held-lock refusal, separate-runtime upgrade, unchanged
source bundle, uninstall WhatIf/state retention/Hub purge and unchanged original,
layout and key sentinels. No production configuration was selected.

Hosted [Windows tests](https://github.com/Skynettheone/herdr-session-hub/actions/runs/43193978595)
and [combined CodeQL](https://github.com/Skynettheone/herdr-session-hub/actions/runs/43193978460)
both passed on that exact snapshot. Zero open code-scanning alerts were reported
afterward. CI remains the same two essential jobs, with no publication workflow.

The builder verified staging and a fresh extraction of **112 files**. The packaged
helper also passed an isolated numeric-refresh invocation from extraction, after
which package verification still passed. The independent Usage oracle again
matched all four periods, and the synthetic source hashes/search-Off flags
remained correct. All native/runtime/script/test payload bytes are compared with
the tested source before a final documentation-only archive refresh. Final
filename/hash receipts are appended outside the archive to avoid a checksum cycle.

Version stays **0.1.0-dev / releaseReady=false**. This closes the identified local
package/upgrade gaps; it does not fabricate a second company identity, working
additional CLIs, other OS testing, independent human audit or publisher signature.
No production installation or release/gallery publication was performed.

### Final hardening artifact receipt

`herdr-session-hub-0.1.0-dev-windows-x64-20261112094400.zip`, **5,035,761 bytes**.
SHA-256: `62badf55daba3e7c213fb235a30748eae938826b783baf50f58df05a23af0bfd`.

All **112 manifest files** passed staging and final fresh-extraction checks;
all **58 runtime/script/test/artwork payload files** matched the tested source.
The extracted packaged helper passed with isolated external state, and the
extraction still verified afterward. Only CHANGELOG and this report's preceding
validation section were refreshed after the full build. This final hash receipt
is external to the archive to avoid a checksum cycle. The archive and its
matching `.zip.sha256` sidecar remain local and unpublished. It supersedes all
older artifacts below.

## Previous Usage candidate

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
