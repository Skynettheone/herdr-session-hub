# Upstream implementation review

Reviewed 2026-11-11. Downloaded public sources were kept only in ignored
`.research/`; they are excluded from distributable files. No upstream implementation
code was copied or translated into this project.

| Repository | Reviewed commit | License |
|---|---|---|
| [Herdr](https://github.com/herdrdev/herdr-app) | b22936225403f38f0e6f38dd2f2fe4b444a85988 | SDK documentation reference |
| [Pane](https://github.com/greenfield-inc/Pane) | 6fdb44e6dca750e5a8e96b701d8c169a304452cb | AGPL-3.0 with additional attribution terms; no copied code |
| [T3](https://github.com/pingdotgg/t3code) | 7e565c510d6dfaef2e1fd97bf9d89a97ce9cece7 | MIT; no copied code |
| [Codex](https://github.com/openai/codex) | e58bf8f5233b51e7cd1679d947e3028c1ed91b06 | provider-format reference |
| [Pi](https://github.com/earendil-works/pi) | b22e525b325ff1934b4110f7fc60426fd6f0a8f3 | provider-format reference |
| [OpenCode v1.3.17](https://github.com/anomalyco/opencode/tree/517e6c9aa4c61dbc125e7654fc596f1d529f20d9) | 517e6c9aa4c61dbc125e7654fc596f1d529f20d9 | provider-format reference |

OpenCode HEAD 609ee05a23c0cf4f0d26deafcb737dbc343bac6e has a different
source tree; installed v1.3.17 governs this implementation.

## Actual files studied

Pane: `main/src/services/sessionImport/{scan,place,record}.ts`,
`sources/{claudeCode,codex}.ts`, `docs/SESSIONS.md`, and
`main/src/services/paneChatBundle/skills/migrate-to-pane/` including
`references/continuity.md`. Ideas: independent source failures, live ownership,
transparent receipts, rerun safety. Avoid its UUID-only cross-source merging,
30-day cutoff and source-copy behavior for this product.

T3: `apps/server/src/project/AgentSessionScanner.ts`,
`AgentSessionImporter.ts`, `AgentSessionScanner.test.ts`,
`packages/contracts/src/agentSessions.ts`, `docs/user/thread-migration.md`.
Ideas: budget separate phases, Pi active-branch ancestry, provider-instance keys,
exact native IDs, bounded retention. `docs/user/welcome-wizard.md` at the pinned
commit returned 404; the handover's description is not treated as current evidence.

Provider sources: Codex `codex-rs/rollout/src/{list_files.rs,
compression/blocking_reader.rs}`; Pi
`packages/coding-agent/src/core/session-manager.ts` and CLI/usage docs;
OpenCode `packages/opencode/src/cli/cmd/{session,export}.ts` and
`session/index.ts` at the installed-version commit. OpenCode JSON list has
`id,title,updated,created,projectId,directory`; export has `info,messages`.

Herdr: installed guide and declarations, upstream `defaults/AGENTS.md`,
`docs/mods.md`, `docs/security.md`, `CHANGELOG.md`, developer guide. Native
mods are trusted code. An app home alone does not isolate the core document.

Official Claude CLI/settings, Codex CLI, OpenCode CLI and gallery pages were
retrieved. Documentation can be ahead of installed commands. Known issue links
in REFERENCE_IMPLEMENTATIONS.md are regression motivation, not schema authority.

## Parser contract

| Provider | Identity/cwd | Content | Limits/fallback |
|---|---|---|---|
| Claude | `sessionId`, `cwd` on valid primary records | user/assistant text; ignore sidechain/meta/tool payloads | oversized lines skipped; incremental prefix + sampled tail |
| Codex | `session_meta.payload.id`, `cwd` | response message text; event user fallback | zstd capped; history-base indirection marked partial |
| Pi | `session.id`, `cwd`, version 1–3 | message user/assistant; tree parent links | incomplete ancestry reported; no fabricated linear continuity |
| OpenCode | documented offline list/export JSON | `messages[].parts` text with user/assistant role | no automatic CLI startup or source DB writes |

No schema is assumed stable across future major releases. Unsupported version,
missing native ID, stale source and uncertain active ownership disable launch.

## Expanded providers and branding — 2026-11-12

- Gemini source inspected at `cde401adeae75c3dd470dfbf1a6ef389f89a48f9`
  (Apache-2.0): `packages/core/src/services/chatRecordingService.ts`,
  `chatRecordingTypes.ts`, `config/storage.ts`, `utils/paths.ts`, and session
  utilities. [Recording source](https://github.com/google-gemini/gemini-cli/blob/cde401adeae75c3dd470dfbf1a6ef389f89a48f9/packages/core/src/services/chatRecordingService.ts),
  [official session docs](https://geminicli.com/docs/cli/session-management/).
  The bounded replay is independently implemented; no upstream implementation
  was copied or translated. Legacy JSON and append JSONL are fixture-tested;
  `$set`, content patches, ordering, removals and rewind exclude obsolete text.
- Copilot SDK source inspected at `233b07cbfac596121ca4a8f0ff9c02163a7c34d8`:
  [event schema](https://github.com/github/copilot-sdk/blob/233b07cbfac596121ca4a8f0ff9c02163a7c34d8/nodejs/src/generated/session-events.ts),
  [persistence](https://github.com/github/copilot-sdk/blob/233b07cbfac596121ca4a8f0ff9c02163a7c34d8/docs/features/session-persistence.md),
  [official CLI reference](https://docs.github.com/en/copilot/reference/copilot-cli-reference/cli-command-reference).
  Only independently written field readers are shipped. `agentId` and
  `parentToolCallId` subagent events are excluded before metadata/content.
  Rewind/truncation is a partial raw-log excerpt, not canonical reconstruction.
- [Cursor parameters](https://cursor.com/docs/cli/reference/parameters) and
  [Amp threads](https://ampcode.com/docs/threads) establish native CLI behavior,
  not verified offline history readers in this environment. No reverse-engineered
  third-party parser or network history API was added.
- Herdr's GUI catalog source at `b22936225403f38f0e6f38dd2f2fe4b444a85988`
  and installed `Program`/`knownAgents` signatures establish dynamic recognition.
  Actual icon paths and tint rules come from the installed app, not this snapshot.
- Official sheep artwork from `herdrdev/herdr` commit
  `ee5bfb5041bb3e4a49d591c72308aae3c81ecdde`, `assets/logo.svg`, reused
  unmodified with Apache-2.0 license retained. See THIRD_PARTY_NOTICES.md.
