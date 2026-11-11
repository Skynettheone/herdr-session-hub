# Master Codex task — implement Herdr Session Hub now

Work in this repository to **complete a production-grade, open-source Herdr Desktop GUI mod**, not a TUI plugin. I want all features specified in `docs/PRODUCT_REQUIREMENTS.md`, including advanced profile/full-text features and **secure, explicitly opted-in management/export/sync**. Do not stop at generating a plan; implement and test as much as the environment genuinely supports in this execution. Prioritize a working GUI for four agents over speculative features.

## Read first
Read `CODEX_HANDOVER.md`, `AGENTS.md`, `docs/VERIFIED_SOURCES.md`, `docs/WINDOWS_PREFLIGHT.md`, `docs/IMPLEMENTATION_SEQUENCE.md`, `docs/PRODUCT_REQUIREMENTS.md`, `docs/ARCHITECTURE.md`, `docs/PROVIDER_MATRIX.md`, `docs/SECURITY_AND_PRIVACY.md`, `docs/TEST_PLAN.md`, and upstream Herdr's `defaults/AGENTS.md`. On my Windows PC also inspect my installed Herdr `~/.config/herdr-app/AGENTS.md`, `herdr.d.ts`, `gpui-kit.d.ts` and `herdr-app commands`. Open each primary-source URL in `docs/VERIFIED_SOURCES.md` (links have already been researched; reverify). Consult upstream provider official docs/source for actual installed CLI versions. Record source links, primary-source snippets or file references, versions and unsupported assumptions in `docs/RESEARCH_FINDINGS.md`.

## Build end to end
A. Create native GPUI mod at `mods/session-hub/` with `main.js`, `mod.json`, UI modules, controls, search, filters, project grouping, profile chips, detail view, and explicit resume buttons. No Electron, React, Node globals or webview inside mod runtime. Preserve all existing Herdr layouts.
B. Implement provider adapters Claude Code, Codex, OpenCode, Pi for detection, read-only listing, title/preview, timestamps, stable IDs and resuming in a new Herdr tab under original cwd. Probe exact CLI flags; handle missing, stale and corrupt data.
C. Implement manual and incremental refresh with bounded IO, caching and robust error UI; do not block rendering. Implement custom provider roots and multi-profile labeling and launch selection without touching credentials.
D. Add read-only bounded previews and local full-text search across messages via opted-in local index. A minimal audited Rust helper + SQLite FTS5 is acceptable if needed for performance; justify, lock dependencies, provide Windows build and test scripts. No network access for discovery or indexing.
E. Implement Hub-only aliases, archive/unarchive and removal from index. For original deletion, require verified provider support, backup, typed confirmation and reversible process; leave unavailable on any unverified provider instead of destructive hacks.
F. Implement an offline versioned export/import format with optional redaction, checksums, and encrypted portable bundles through audited crypto. Optional cross-device sync must be disabled by default, user-configured, conflict-safe, secret-excluding and fully tested. Explicitly distinguish archived preview from native resumability after import.
G. Verify installer/uninstaller and user mod directory persistence across normal Herdr updates, add diagnostics, rollback and compatibility tests.
H. Produce README, SECURITY, CONTRIBUTING, CHANGELOG, accurate RECIPE.md and a real sanitized preview.png only after rendering in GUI. Make public-gallery layout `mods/session-hub/` + recipe + preview, NO `layouts/` folder. Never fake screenshot or test results.

## Test and finish
- Build fixtures/tests for every provider and dangerous paths; test search, UI interactions, resume, refresh, profile selection, alias, archive, delete-disabled behavior, export/import/sync encryption and conflicts.
- Run `herdr-app check <mod-folder>` when Herdr installed, then test the actual GUI. Document environment-bound tests separately from those run.
- Run dependency/security scans; ensure no secrets or real history in source or logs.
- Build release artifacts with checksums. Keep feature matrix in README accurate.
- Provide a final report: files created, tests actually run and passed/failed, exact Herdr/CLI versions, security findings, what still can't be verified, commands to install and uninstall, and what requires approval.
- Do not publish to GitHub, install into my production config, or transfer any real transcripts externally without my approval.

If Herdr or any provider CLI is absent, still implement using upstream API declarations and synthetic fixtures, record the limitation, and avoid claiming a successful real Windows integration test.
