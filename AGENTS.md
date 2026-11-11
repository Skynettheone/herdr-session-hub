> BEFORE IMPLEMENTING PROVIDER SCANNING/IMPORT, read `docs/REFERENCE_IMPLEMENTATIONS.md` and `docs/MIGRATION_AND_REFRESH_DESIGN.md`. Check Pane/T3 source at current pinned SHAs; study but do not copy incompatible AGPL code. Distinguish discovery/index from native session migration, and do not claim resumption without continuity verification.

# Codex instructions — Herdr Session Hub

You are implementing **Herdr Session Hub**, a native GPUI mod for **Herdr Desktop GUI** (`herdr-app`), NOT Herdr TUI.

READ `CODEX_HANDOVER.md` AND `docs/VERIFIED_SOURCES.md` FIRST. Then read the documents in `docs/`, especially `PRODUCT_REQUIREMENTS.md`, `ARCHITECTURE.md`, `SECURITY_AND_PRIVACY.md` and `TEST_PLAN.md`, before coding. Honor the full requested scope, including advanced features, with guarded destructive/sync options.

## Critical source of truth
1. The direct source links and evidence level are in `docs/VERIFIED_SOURCES.md`. The locally installed `~/.config/herdr-app/AGENTS.md`, `herdr.d.ts`, `gpui-kit.d.ts` and `herdr-app commands` (if available) take precedence over examples from web/docs. Herdr's native mod code must not use Node, React, Electron, DOM, HTML or setTimeout.
2. Herdr upstream: https://github.com/herdrdev/herdr-app ; gallery: https://herdr.dev/gallery/.
3. Official provider documentation and upstream source govern CLI flags and session schemas. Probe installed versions. Do not invent APIs.
4. Before implementation, write a short `docs/RESEARCH_FINDINGS.md` with confirmed capabilities, unknowns, tested versions, and blockers. Then proceed implementing all feasible features; mark unavailable features explicitly and implement safe fallback behavior rather than pretending success.

## Non-negotiable safety
- Read-only access to original provider transcripts for discovery, preview and search.
- No reading credential files (`auth.json`, tokens, keys, config secrets); exact-scoped search roots, no arbitrary home traversal.
- Paths and session IDs are untrusted data. No string-interpolated shells; spawn with argument vectors and verified cwd using supported Herdr APIs.
- Don't allow mutation of original transcripts for custom alias/archive; store metadata in Session Hub's own namespace.
- Original-session deletion only when specifically requested, confirmed, backed up, and implemented using a supported per-provider API or audited transactional process; never delete live sessions. Export/import and sync must be opt-in, encrypted where contents leave the machine, and conflict-safe.
- The mod must never overwrite shipped Herdr mods, user layouts, keys or other settings. Keep existing layouts unchanged and isolate all Hub state.
- No telemetry, no network use for browsing/indexing. If optional sync is implemented, connect only on the user's explicit action and document destination and privacy.
- Never push/publish or install in the production Herdr directory automatically. Build/test locally; request explicit user approval for external publishing and production install.

## Implementation discipline
- Deliver small working slices without stopping at architecture-only planning.
- Implement adapters independently, with fixture tests and integration smoke tests.
- Use no unsafe command execution and no silent fallback from one profile to another.
- Each UI action must be tested, including async error states and multiple panes.
- `herdr-app check` is required but insufficient: interactive behavior must be verified against an installed Herdr GUI.
- Include an uninstaller and migration plan for Hub-owned data.
- If a feature depends on an unavailable API/OS capability, don't forge it: provide a specific blocker, graceful disabled state and test proving the fallback.
- Build release and gallery assets only from completed features. Do not use fabricated UI screenshots.
