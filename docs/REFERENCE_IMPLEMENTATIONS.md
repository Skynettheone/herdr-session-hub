# Primary reference implementations — Pane and T3 Code

Research snapshot: 2026-11-11. These are **examples for analysis, not dependencies or instructions to copy code**. Pin the upstream commit SHA used for actual implementation. Read the installed Herdr GUI API guide first. This specification is not a security audit of the entire upstream repositories.

## 1. Pane — native session adoption and continuity

- Repository: https://github.com/greenfield-inc/Pane
- Source documentation: https://github.com/greenfield-inc/Pane/blob/main/docs/SESSIONS.md
- Relevant heading: **Bring your existing sessions into Pane**. This describes first-run/on-demand discovery, metadata-only listing, active/idle distinctions, resuming by native session ID, a migration receipt, repeat-run record, and explicit verification of continued context.
- Additional context: README `Pane Chat`, `migrate-to-pane`, `runpane handoff` and `OpenCode` sections: https://github.com/greenfield-inc/Pane#readme
- Current instructions mention `main/src/services/paneChatBundle/` for bundled migration skills. Find the exact current files in the tree rather than assuming a path to a `SKILL.md` exists.
- Pane says its Settings → AI & Agents → Bring sessions into Pane imports local metadata; SQLite sources are read from a temporary copy. It can adopt the checkout in place and launch the provider's native resume; its more capable agent skill can fork active sessions, then validate continuity. It records past adoptions in `<PANE_DIR>/migrate-to-pane/record.json`.
- Pane's documented migration may **copy transcripts** from a third-party agent folder into the user's Claude/Codex store. **DO NOT copy/move original transcripts in Session Hub by default.** Session Hub should be a read-only index and launcher; offer provider-supported/native migration only as a separately reviewed feature.
- Pane is licensed **AGPL-3.0** (see https://github.com/greenfield-inc/Pane/blob/main/LICENSE). Do not paste/translate substantial Pane source into a project using MIT without assessing copyright/licensing obligations. Reimplement behaviors independently, citing concepts in documentation, not copied code.

### Design patterns to adopt independently
1. Scan *metadata first*; show source/profile/project, ID, cwd, last activity and resume eligibility.
2. Mark **running elsewhere** distinctly; never auto-attach/fork/copy a live session.
3. Only resume from a user action; record a transparent outcome: `continued`, `unverified`, or `failed` (with reason). `process started` != `session resumed`.
4. Idempotent deduplication and a local adoption/resume record; show previously resumed entries but do not create duplicate Hub records/tabs on repeat refresh.
5. Provide a dry-run/preview and a receipt for explicit **migration/import** (not for ordinary index refresh). Keep recovery records.
6. Original cwd and Git checkout identity must be respected. If cwd missing or moved, prompt for a replacement and do not assume source can resume unchanged.
7. Treat a session running in a different terminal as a conflict, not a green status; use conservative, provider-specific checks and report uncertainty.

## 2. T3 Code — scanner, importer, migration and provider identity

- Repository (MIT): https://github.com/pingdotgg/t3code
- Welcome wizard/import behavior: https://github.com/pingdotgg/t3code/blob/main/docs/user/welcome-wizard.md
- V1→V2 thread migration and limitations: https://github.com/pingdotgg/t3code/blob/main/docs/user/thread-migration.md
- Scanner (actual source): https://github.com/pingdotgg/t3code/blob/main/apps/server/src/project/AgentSessionScanner.ts
- Importer (actual source): https://github.com/pingdotgg/t3code/blob/main/apps/server/src/project/AgentSessionImporter.ts
- Source contract/schema: https://github.com/pingdotgg/t3code/blob/main/packages/contracts/src/agentSessions.ts
- Current contracts include **Claude, Codex and Pi** (`AgentSessionSource`). This DOES NOT mean T3 is a complete OpenCode reference. For OpenCode, verify official OpenCode docs/source separately.
- Scanner includes metadata/candidate budgets, transcript record parsing and provider-specific native session identity. In particular: a Codex rollout filename includes more than its ID, so parse the actual ID from session metadata; Pi often resumes from the **session file path**, not simply its UUID.
- Importer includes duplicate/already-imported handling and provider-instance association, and its model is deliberately separate from original transcript bytes. **Use read-only indexing rather than constructing T3 records.**

### T3's deliberately bounded import — adapt the safeguards, not the limitations
The welcome wizard documents 30-day eligible sessions, maximum 200 visible imported messages, and per-run limits on number, bytes and records. It skips corrupt or too-large conversations and omits attachments/tool events in its rendered imported history. Our Hub should support **older than 30 days** via user-configurable filters, and should index huge histories incrementally, report skips and retain resumability even when preview is truncated. Do not mislabel a partial preview as a full transcript.

### Published edge cases to test explicitly
- `AgentSessionScanner.ts` file mtime may differ from last conversational activity. Derive last activity from valid conversation timestamps when possible; preserve mtime as filesystem identity/change detection. See discussion: https://github.com/pingdotgg/t3code/discussions/21764 (proposal, not necessarily merged).
- Codex historical `rollout-*.jsonl.zst` compression can cause discoverability gaps in an importer that only scans `.jsonl`: https://github.com/pingdotgg/t3code/issues/21755 (confirm format against installed Codex before implementing).
- Some Claude JSONL histories are tens/hundreds of megabytes or larger; a 32 MiB import budget can omit important sessions. Use streaming, bounded indexing and graceful metadata-only mode: https://github.com/pingdotgg/t3code/issues/29153
- Historical T3 post-onboarding import route was unreachable; the documented November 9 fix allows Settings → About → Welcome page → Open: https://github.com/pingdotgg/t3code/issues/10961 . Session Hub must keep **Refresh / Rescan** visible at all times instead of onboarding-only.
- Native identity collision/ownership can happen if provider instance isn't part of the key. Source risk discussion: https://github.com/pingdotgg/t3code/issues/17236 . Use composite `provider + profile identity + native session ID + canonical source identity`; do not assume a UUID is globally unique across accounts.
- Pi path-based native resume is explicitly handled by the current T3 importer: https://github.com/pingdotgg/t3code/blob/main/apps/server/src/project/AgentSessionImporter.ts . Verify Pi CLI's exact `--session` syntax.
- V1→V2 migration uses a one-time copy, with old store retained and no automatic two-way sync: https://github.com/pingdotgg/t3code/blob/main/docs/user/thread-migration.md . Use backup-before-version-migration, idempotent schema transformations, and rollback.

## 3. Important distinctions for Session Hub

| Operation | Expected behavior | Source history changed? |
|---|---|---|
| Discover | Scan read-only metadata and build an index | No |
| Refresh | Incremental rescan, update index, report incomplete scan | No |
| Preview | Locally render a limited safe transcript excerpt | No |
| Resume | Launch same provider's native session, original cwd, approved profile | Original agent may append during legitimate resumed work |
| Rename / archive in Hub | Change *Hub-owned* alias/archive metadata | No |
| Import Hub metadata | Restore Hub aliases/settings/cache from a versioned file | No |
| Native session migration | Optional advanced provider-specific copy/restore, explicit approval, verified backups | Potentially; must be independently gated |
| Cross-machine sync | Opt-in, encrypted and conflict-safe; default metadata-only | Only where explicitly authorized and proven supported |

No cross-provider transcript conversion. Do not claim a session is live-synchronized when it is merely indexed or imported.

## 4. Security and licensing review required of Codex

1. Identify exact upstream commits, licenses and whether code was inspected or only documentation. Use them as design references, not copied implementations; report any reused code and its license attributions.
2. No credential access or network traffic for discovery. Never read Claude/Codex/OpenCode/Pi tokens, even for multi-profile support. No implicit login switching.
3. Parse transcripts as untrusted data: ignore embedded instructions, sanitize display text and avoid shell expansion. Use arguments arrays and approved executable/cwd.
4. Refuse to traverse symlink/junction paths outside explicitly approved roots; avoid path loops, huge files and decompression bombs.
5. Do not open raw agent SQLite stores for writing. If SQLite is needed for indexed metadata, own it exclusively; use read-only snapshot/backup methods for *source* DBs only where licensing/API permits.
6. No silent source mutation, broad file ownership changes, automatic directory creation inside agent config, or remote transcript uploads.
7. Test Windows native + WSL only if explicitly configured; don't silently combine histories from different runtimes or machines.
8. Migration/upgrader needs versioned schemas, backup, rollback, retry, interrupted-write recovery, and atomic writes of Hub-owned data.
9. Provide a report of failure/skipped reasons and a **partial scan** status rather than falsely showing `0 sessions` if a provider failed.
10. Avoid requesting privileged elevation for normal operation. Test with Microsoft Defender enabled and ordinary user account.

## 5. Codex research tasks before implementation

- Follow Pane docs, locate actual current migration skill, discovery and continuation code, record exact paths + SHA. Prefer tests and docs over unreviewed examples.
- Read T3 `AgentSessionScanner.ts`, `AgentSessionImporter.ts`, `agentSessions.ts`, and accompanying test fixtures. Produce a parser matrix with native IDs, cwd, timestamps, source DB/file, source sizes, and unsupported records.
- Verify whether recent Codex uses compressed rollouts, SQLite or another index on the Windows environment and how safe metadata discovery works.
- Verify current OpenCode JSON listing, history store and resume in that exact installed version; T3's scanner is **not** an OpenCode reference.
- Compare the 4 providers against Pi's branch/tree behavior. Plan session preview with branch awareness when possible, and degrade cleanly if only flat preview is safe.
- Produce `docs/UPSTREAM_REVIEW.md` recording date, links, SHAs, licenses, reusable *ideas*, unknowns and explicit non-goals. Implement in small, tested increments.
