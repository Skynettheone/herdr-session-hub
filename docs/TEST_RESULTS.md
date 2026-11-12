# Test results — 2026-11-12

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
transcript migration and remote sync remain explicitly unavailable. These limits
keep `releaseReady=false`; no production installation or release publication
was performed.

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
