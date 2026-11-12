# F01–F16 implementation status — 2026-11-12

“Implemented” below means code and stated tests exist. It does not mean all native
provider acceptance gates passed. This is **0.1.0-dev**, not a production release.

Usage is an additional view in the same History panel: native themed graphs,
numeric breakdowns, profile/provider/UTC filters, encrypted bounded numeric
refresh, exact local rates, recorded limits and explicit partial coverage.
Five provider usage formats have fixtures; Copilot's persisted log omits usage.
See [USAGE_ACCEPTANCE.md](USAGE_ACCEPTANCE.md) for GUI/arithmetic evidence and
[USAGE_DESIGN.md](USAGE_DESIGN.md) for pricing/deduplication boundaries. Existing
release gates remain in force.

| ID | Implementation and verified scope | Remaining limits |
|---|---|---|
| F01 | User-invoked native command detection; explicit profiles; missing CLI does not hide history | Help/version verified locally; no default home scan |
| F02 | Six read-only adapters; native IDs, cwd, source/profile, times, titles; four real disposable native stores | No user histories used; OpenCode refuses open writers, supports quiescent committed WAL |
| F03 | Normalized metadata substring search, debounced UI, literal FTS token option | Query work bounded; old subprocess may finish before newer query replaces it |
| F04 | All/six history provider chips, profile filtering, live Herdr agent catalog | Native Codex/Pi/Gemini filters exercised; other actions have host coverage |
| F05 | Four primary CLIs plus Gemini passed native Herdr context checks with a loopback backend; original ID/cwd/wrapper verified; native active ownership observed | Gemini 0.49 duplicate snapshots fail closed; real-cloud Claude continuation passed after user-handled startup notice; non-Codex ownership remains conservative |
| F06 | Manual refresh beyond onboarding, incremental fingerprints/cache, bounded batches, visible counts/status, cooperative cancel | Enumeration per batch bounded at 20k files/160k entries; large content requires repeated passes |
| F07 | Dock creates a personal layout copy with one collapsible History tab beside Files/Changes; shipped files/previous layouts untouched; update/rollback passed | Standard panel structure required for header integration; exact 0.1.15 SDK; future updates require review |
| F08 | Guided root/config/executable form, pickers, advanced multi-root/exclusions JSON | Reparse, hard-link, UNC and WSL sources refused; unsupported custom-store resume disabled |
| F09 | Read-only plain GPUI text, 30 turns × 2k chars, redaction, no tool payloads; Pi ancestry | Head budget partial; attachments omitted; Pi full-text covers all branches |
| F10 | Compact collapsible project groups, page of 60; responsive master/detail or sidebar navigation; full cwd in Details | Group counts are per visible page; unknown conversation times remain unknown |
| F11 | Explicit profiles/targets, same-store collision guard, directory env mapping; two isolated stores authenticated by the user and created real-cloud marker sessions; unsigned profile has no auth fallback | Both sign-ins use one identity; user has no separate company account, so distinct-company identity behavior remains unverified |
| F12 | OFF by default; per-profile opt-in, local FTS5, chunk progress, clear/rebuild, DPAPI encrypted disk state | 256 MiB encrypted state limit; zstd replay capped at 128 MiB decoded / ratio 200 / 8 MiB window; no complete huge-compressed indexing claim |
| F13 | Archive/unarchive only in Hub metadata | No provider-native archive mutation |
| F14 | Display aliases and reset to original title | No native rename mutation |
| F15 | Removal tombstone + restore view, originals untouched | Original deletion deliberately unavailable; disabled operation tested |
| F16 | Encrypted metadata export/import, passphrase terminal, schema/checksum, wrong-key/corrupt handling, dry-run, foreign records/conflicts, explicit annotation linking | No native transcript export/restore, remote transport or continuous sync; unavailable operations tested |

## Release scope and remaining gates

[PRODUCTION_READINESS.md](PRODUCTION_READINESS.md) is the current inventory.
Native continuation, representative GUI controls, user-controlled privacy tests,
manual security review and the isolated updater/rollback are completed within
their recorded scope. They are no longer blanket unfinished tasks.

Distinct company identity, other OS/provider builds and additional native agents
still require external acceptance environments. Conservative ownership checks,
bounded replay, unavailable deletion/native restore/remote sync and offline
recorded-only Usage are deliberate guarded limits. No independent human audit or
publisher signature is claimed. The maintainer must choose and accept an explicit
supported release scope before clearing the release gate; production installation
and publication also need separate approval. Source commits and pushing to the
requested origin were explicitly authorized.

`version.json` keeps `releaseReady=false`. `build-release.ps1` refuses normal
release mode until changed after evidence is recorded. `-AllowUnverified` builds
only an accurately named development bundle.

## Expanded agent support

Claude, Codex, OpenCode, Pi, Gemini and Copilot have fixture-tested local history
readers. Gemini requires complete bounded replay and an exact project-hash mapping
for resume. Copilot native launch stays disabled because the installed shim has
no real CLI. Cursor, Amp and every other native/custom Herdr catalog entry appear
in Settings → Agents with truthful capability status; no undocumented disk reader
or silent generic launch is used. This is catalog parity, not universal history
or native-continuation acceptance. See PROVIDER_MATRIX.md.
