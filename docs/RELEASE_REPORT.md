# Release preparation report — 2026-11-12

Version is **0.1.0-dev**, Windows x64 / Python 3.14 / Herdr 0.1.15.
`releaseReady=false` remains intentional. Four primary native continuations and
real Herdr update/rollback have passed; remaining gates are cloud-account
isolation, Gemini continuation, broader ownership/control coverage and independent
security review. Original deletion, native migration and remote sync are unavailable.

The source is on `main` at the user-requested origin, with conventional task
commits using the existing Git identity and no assistant-authorship trailers.
Pushing source was authorized. No production install, GitHub Release, gallery
publication or original-history deletion was performed.

## Validation

- Four real provider CLIs resumed their disposable native session through the
  actual Hub button, retained original cwd/profile/ID and answered a new prompt
  using earlier context. The model backend was a deterministic loopback fixture.
- Real 0.1.14→0.1.15 update preserved 39 mod/config/layout hashes; verified backup
  rollback preserved 42 including encrypted Hub state, with safe version fallback.
  Re-update to 0.1.15 passed. See NATIVE_ACCEPTANCE.md.
- Fixture/panel/correctness checks, native SDK check, install/backup/uninstall
  smoke and offline wheel verification are required by the local release process.
- Hosted Windows and combined CodeQL on `57e2c4c` succeeded. Final-code run links
  are in TEST_RESULTS.md after the next source push.

## Local bundle

`scripts/build-release.ps1 -AllowUnverified` creates a clearly named development
ZIP with source, native assets/licenses, tests, scripts, documentation, real
screenshots and three hash-locked Windows encryption wheels. It repeats Ruff,
Python tests, panel tests and installed SDK check. No environment, runtime.json,
SDK-generated declarations, research downloads, provider histories or credentials
are payload inputs. There is no automatic deployment workflow.

Every payload file is listed in SHA256SUMS.txt. Verify both staged payload and a
fresh ZIP extraction with `python scripts/verify-package.py <directory>`.
The ZIP SHA-256 sidecar is an integrity check, not a signed release. The final
bundle filename/hash and test totals are recorded below after building, outside
that ZIP, to avoid a checksum/report cycle.

The previous bundle `herdr-session-hub-0.1.0-dev-windows-x64-20261111203312.zip`
(82 files, SHA-256 `75dd9ce85597ce28e11b4a2384118bb0bd1ce938d78fdaa282ff9acffa044801`)
is superseded by the native-acceptance bundle when listed below.
