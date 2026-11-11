# Implementation sequence and acceptance gates

The requested scope is all **F01–F16**. Build working, testable vertical slices; never hide a missing capability behind inert UI.

## Gate 0 — research and decisions

- [ ] Read `CODEX_HANDOVER.md`, `AGENTS.md`, all `docs/*.md`, installed Herdr `.d.ts` and official links in `VERIFIED_SOURCES.md`.
- [ ] Run Windows preflight safely; record versions and claims in `docs/RESEARCH_FINDINGS.md`.
- [ ] Confirm `mod.json`, installed UI APIs, launch shape and where the UI panel mounts without layout edits.
- [ ] Choose local-only helper mechanism if required; justify with performance/security, include source and build instructions.

## Gate 1 — a real working GUI

- [ ] Native Herdr session panel; live search, provider filter, project sections; responsive light/dark; keyboard focus.
- [ ] Claude and Codex read-only metadata adapters, no original file writes, privacy-safe titles.
- [ ] Click resume creates new Herdr tab with correct executable, project cwd, profile and native session ID.
- [ ] Test with a test project created outside Herdr, then with a sanitized local real session only with user approval.

## Gate 2 — all four providers and history features

- [ ] OpenCode and Pi adapters; verify help, roots, CLI JSON and resume flags.
- [ ] Previews (bounded, read-only, sanitized); custom directories; profiles and dedup; refresh without restart.
- [ ] Graceful empty/missing/moved/error states; sorted timestamps; large history pagination.

## Gate 3 — full-text, metadata management

- [ ] Local opt-in full-text index; security boundaries; progress, cancel, rebuild and clear.
- [ ] Rename aliases and archive/unarchive stored only in Hub metadata.
- [ ] 'Remove from Hub' must never imply deleting source files. Original delete remains *disabled* until documented, backed up, consented and end-to-end recovery-tested per provider.

## Gate 4 — portability/sync and security

- [ ] Versioned exported metadata manifest; checksums; sanitized optional content.
- [ ] Audited encryption when exporting private content off-device; wrong-key and corrupt-bundle handling; no secrets.
- [ ] Explicit opt-in external sync with conflicts preserved, no background hidden uploads, no unsafe original transcript edits; disable dangerous source-native restore if not supported.
- [ ] Threat model, dependency review, uninstaller, rollback, no telemetry.

## Gate 5 — release and gallery

- [ ] `herdr-app check`; manual real GUI smoke test of all interactive controls.
- [ ] Independent source hashes unchanged after index/search/preview/archive tests.
- [ ] 10,000 synthetic record performance test; Windows CI + manual test notes.
- [ ] Genuine sanitized screenshot, precise `RECIPE.md`, docs, SECURITY/CONTRIBUTING, license, changelog, release checksums.
- [ ] Public GitHub + `herdr-mod` topic **only with user approval**.

Never mark a disabled risky feature as implemented; mark blocked or experimental with why. User asked for complete implementation now, but correctness and safety take precedence over pretending unsupported APIs work. Keep going on independent features when one feature is blocked.
