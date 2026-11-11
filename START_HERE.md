# Herdr Session Hub — GitHub setup

**Implementation update (2026-11-12):** the native mod, helper, tests and local
development packaging now exist. Read README.md and docs/FEATURE_STATUS.md for
current evidence and open release gates. The original starter instructions below
are historical setup context, not a claim that publication is authorized.

- **Repository:** `herdr-session-hub`
- **Display name:** Herdr Session Hub
- **Description:** A unified session manager for Herdr. Discover, search, preview, organize, and resume Claude Code, Codex, OpenCode, and Pi conversations.
- **Tagline:** Every agent. Every session. One place.
- **Website (ecosystem; not your listing yet):** https://herdr.dev/gallery/
- **Topics:** `herdr-mod`, `herdr`, `claude-code`, `codex`, `opencode`, `pi-coding-agent`, `session-manager`, `developer-tools`, `ai-agents`, `open-source`
- **License:** MIT
- **Visibility:** Public
- **Primary language:** JavaScript (Herdr GPUI native mod) plus optional Rust helper for local indexing.
- **Platform:** Windows first; macOS and Linux after successful verification.

## Start building with Codex

1. Create an empty GitHub repository called `herdr-session-hub`. Do not initialize with a second README/license when uploading these files.
2. Extract this starter pack into the repository root.
3. Open Codex with that folder as the working directory. Give it **`CODEX_HANDOVER.md`** as the main implementation brief, and review `docs/REFERENCE_IMPLEMENTATIONS.md` and `docs/MIGRATION_AND_REFRESH_DESIGN.md` for Pane/T3 integration guidance; it links to the full master prompt, verified documentation and acceptance tests. For a short copy-paste, use `COPY_INTO_CODEX.txt`.
4. Codex must first verify APIs from installed `~/.config/herdr-app/AGENTS.md`, `herdr.d.ts`, `gpui-kit.d.ts`, and local `herdr-app commands` if available.
5. Build the features and run tests. Publish only after genuine end-to-end validation, not merely a passing syntax check.

This archive is an **implementation specification**, NOT a completed Herdr mod. Do not install it into Herdr.

## Read-first files
- `CODEX_HANDOVER.md` — complete instruction and links.
- `docs/VERIFIED_SOURCES.md` — official Herdr and provider documentation, with verified vs uncertain notes.
- `docs/WINDOWS_PREFLIGHT.md` and `scripts/windows-preflight.ps1` — read-only local environment checks.
- `docs/IMPLEMENTATION_SEQUENCE.md` — ordered milestones and release gates.

## References
- Herdr GUI: https://github.com/herdrdev/herdr-app
- Herdr gallery: https://herdr.dev/gallery/
- Claude Code CLI: https://code.claude.com/docs/en/cli-reference
- Codex source: https://github.com/openai/codex
- OpenCode CLI: https://opencode.ai/docs/cli/commands
- Pi coding agent: https://github.com/earendil-works/pi

## New upstream research references
- Pane migration/continuity: https://github.com/greenfield-inc/Pane/blob/main/docs/SESSIONS.md
- T3 scanner: https://github.com/pingdotgg/t3code/blob/main/apps/server/src/project/AgentSessionScanner.ts
- T3 importer: https://github.com/pingdotgg/t3code/blob/main/apps/server/src/project/AgentSessionImporter.ts
- T3 import contracts: https://github.com/pingdotgg/t3code/blob/main/packages/contracts/src/agentSessions.ts
- Read both new docs before implementing scanning, refresh, profile identity, resume, or migration.
