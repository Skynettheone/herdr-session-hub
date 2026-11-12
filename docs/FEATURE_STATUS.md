# F01–F16 implementation status — 2026-11-12

“Implemented” below means code and stated tests exist. It does not mean all native
provider acceptance gates passed. This is **0.1.0-dev**, not a production release.

| ID | Implementation and verified scope | Remaining limits |
|---|---|---|
| F01 | User-invoked native command detection; explicit profiles; missing CLI does not hide history | Help/version verified locally; no default home scan |
| F02 | Six read-only adapters; native IDs, cwd, source/profile, times, titles; four real disposable native stores | No user histories used; OpenCode refuses open writers, supports quiescent committed WAL |
| F03 | Normalized metadata substring search, debounced UI, literal FTS token option | Query work bounded; old subprocess may finish before newer query replaces it |
| F04 | All/six history provider chips, profile filtering, live Herdr agent catalog | Native Codex filter exercised; other actions have host-mock coverage |
| F05 | Four primary CLIs passed native Herdr continuation with prior context, original cwd and selected profile; Codex native writer lock; exact CLI image checks | Loopback model fixture, no cloud-account isolation proof; Gemini continuation unverified; non-Codex ownership remains conservative |
| F06 | Manual refresh beyond onboarding, incremental fingerprints/cache, bounded batches, visible counts/status, cooperative cancel | Enumeration per batch bounded at 20k files/160k entries; large content requires repeated passes |
| F07 | Explicit Dock creates a personal sidebar layout copy; originals untouched; real 0.1.14→0.1.15 update, rollback and re-update passed | Resume enabled only on tested 0.1.15; API-breaking future updates require review |
| F08 | Guided root/config/executable form, pickers, advanced multi-root/exclusions JSON | Reparse, hard-link, UNC and WSL sources refused; unsupported custom-store resume disabled |
| F09 | Read-only plain GPUI text, 30 turns × 2k chars, redaction, no tool payloads; Pi ancestry | Head budget partial; attachments omitted; Pi full-text covers all branches |
| F10 | Compact collapsible project groups, page of 60; responsive master/detail or sidebar navigation; full cwd in Details | Group counts are per visible page; unknown conversation times remain unknown |
| F11 | Explicit labeled profiles, physical de-duplication, separate targets, same-store ID collision guard, directory env mappings | Actual personal/company credential separation not runtime-verified; inherited provider credential env is stripped |
| F12 | OFF by default; per-profile opt-in, local FTS5, chunk progress, clear/rebuild, DPAPI encrypted disk state | 256 MiB encrypted state limit; zstd replay capped at 128 MiB decoded / ratio 200 / 8 MiB window; no complete huge-compressed indexing claim |
| F13 | Archive/unarchive only in Hub metadata | No provider-native archive mutation |
| F14 | Display aliases and reset to original title | No native rename mutation |
| F15 | Removal tombstone + restore view, originals untouched | Original deletion deliberately unavailable; disabled operation tested |
| F16 | Encrypted metadata export/import, passphrase terminal, schema/checksum, wrong-key/corrupt handling, dry-run, foreign records/conflicts, explicit annotation linking | No native transcript export/restore, remote transport or continuous sync; unavailable operations tested |

## Release gates still open

1. Cloud-account personal/company isolation remains unverified. Four primary
   providers passed native continuation with a loopback backend; Gemini has not.
2. Broader active ownership across mixed CLI builds/profiles remains unverified.
   Actual live detection passed for all four tested CLIs. Codex 0.164 uses its
   per-thread lock; other adapters conservatively block their selected CLI image
   or recognized Node provider. This may block unrelated sessions.
3. Interactive coverage of every control in real Herdr, multiple panes and both
   themes/narrow widths; host mocks do not establish all native interactions.
   The renewed pass verified search/filter/preview/settings, dark/light/custom-theme
   rendering, multiple panes and captures. Four primary native launch controls
   passed; exhaustive native controls remain open.
4. Future Herdr versions and unsupported OSes require new acceptance. Actual
   0.1.14→0.1.15 update, backup rollback and re-update passed in isolation.
5. Independent security review of the helper, crypto envelope, dependency pipeline
   and Windows executable/launch behavior; signed build strategy if binaries ship.
6. User approval before production installation or gallery/release publication. Source
   commits and pushing to the requested origin were explicitly authorized.

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
