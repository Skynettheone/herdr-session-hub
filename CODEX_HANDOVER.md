# Codex handover — Herdr Session Hub

**Project**: `herdr-session-hub` | **Target**: native Herdr Desktop GUI (`herdr-app`) on Windows | **Snapshot**: 2026-11-11

This is a **complete implementation handover**, not working mod code. Read every named project document before editing. The user wants a high-quality, open-source standalone **mod**, not the Herdr TUI, a fork, or an alternative full layout.

## 0. What the user wants

A minimal, polished **History** panel in the **current Herdr Desktop GUI**, without replacing its present layout. It should discover, search, preview, manage and resume past sessions — even ones launched outside Herdr — from four independent agents: **Claude Code, OpenAI Codex CLI, OpenCode, Pi coding agent**. Windows 11 is the first required environment, with support for long paths, Unicode, spaces and real Windows launch behavior. Future macOS/Linux portability. It must survive normal Herdr application updates via personal mod installation (API breakage still possible).

Full requirements: `docs/PRODUCT_REQUIREMENTS.md` (F01-F16). Multi-profile support, full-text search, reversible alias/archive, cautious original deletion, and optional encrypted portability/sync are in the requested scope. Do **not** implement cross-agent transcript conversion or merge credentials. Personal/company Claude profiles may use different config locations and even shared transcript directories; deduplicate by underlying source while preserving the profile-specific resume target.

## 1. Sources to open — do not rely on memory

**Authoritative source directory**: `docs/VERIFIED_SOURCES.md` (includes direct links, purpose, confidence and caveats). Also read `docs/REFERENCE_IMPLEMENTATIONS.md` and `docs/MIGRATION_AND_REFRESH_DESIGN.md` **before writing any discovery or migration code**. First look at:

- https://github.com/herdrdev/herdr-app — **current native GUI**, not the older `herdrdev/herdr` TUI.
- https://github.com/herdrdev/herdr-app/blob/master/defaults/AGENTS.md — official native mod/command guide. Exact mod shape, GPUI syntax, `tab.new`, `exec`, async lifecycle, security cautions and gallery spec.
- https://github.com/herdrdev/herdr-app/blob/master/docs/mods.md — documentation and installed `.d.ts` priority.
- https://github.com/herdrdev/herdr-app/blob/master/CHANGELOG.md — detect changes before implementation; as of 2026-11-11 release 0.1.15 exists.
- https://herdr.dev/gallery/ — community mod packaging and `herdr-mod` GitHub topic.
- https://code.claude.com/docs/en/cli-reference — Claude Code CLI resume semantics.
- https://learn.chatgpt.com/docs/cli/reference — OpenAI Codex CLI resume semantics.
- https://opencode.ai/docs/cli/commands — OpenCode session JSON listing, safe metadata exports, and interactive resume.
- https://github.com/earendil-works/pi/blob/main/packages/coding-agent/docs/cli.md — Pi's `--session` and `--session-dir` behavior.

**Installed SDK is decisive**. On the user PC inspect `~/.config/herdr-app/AGENTS.md`, `herdr.d.ts`, `gpui-kit.d.ts`, `herdr-app commands`, and `herdr-app --version` or version reported by the installed binary. These may differ from GitHub HEAD. Do not invent undocumented JS or process APIs.

## 2. Reality-checked Herdr integration

- Native mods are JS using `gpui-kit`, `gpui-base`, `herdr`; **no Node globals, React, DOM, Electron, browser webview or `setTimeout`** in a mod.
- `mods/session-hub/main.js` must default-export a `View`; `mod.json` controls initial placement. Personal mod folder is `~/.config/herdr-app/mods/session-hub/`.
- For dynamic work: `cx.spawn`; for periodic refresh use a moderate `cx.timer.every` interval, with cancellation/overlap guards, never continuous redraw. `herdr` exports `exec(command,args,{cwd,on,timeout})` for explicit child process argument arrays.
- `run("tab.new", {name, folder, argv})` is documented; verify the **installed** command argument schema via `herdr-app commands` before implementing. It is a new Herdr terminal in the chosen source project's folder; no destructive session transfer.
- `herdr-app check <mod-dir>` validates module load + one render. It does **NOT** validate async discovery, clicks, providers or native running sessions. Test those in a real Herdr GUI.
- First use of `mod.json` with `place` may dock a new panel. Respect existing layout: default right/none according to user preferences, never rewrite shipped layouts or overwrite existing mod names.
- Personal copied mods remain owned by the user on normal updates, but updates can change APIs. A supported-version matrix, smoke tests, and rollback belong in release process.

See upstream guide for exact API and signatures: https://github.com/herdrdev/herdr-app/blob/master/defaults/AGENTS.md

## 3. Native agent resume and discovery — verify installed versions

| Provider | Discovery plan | Resume plan | Caveats |
|---|---|---|---|
| Claude Code | Bounded read-only JSONL scan under approved config root's `projects/` | `claude --resume <session-id>` | Correct `CLAUDE_CONFIG_DIR` per profile. Verify cwd from trustworthy metadata, not encoded folder name alone. Skip subagent/transient files that aren't resumable. |
| Codex CLI | Bounded metadata scan `CODEX_HOME/sessions/` and/or documented local store; verify rollout versions | `codex resume <session-id>` | Don't edit SQLite/thread indexes; Codex may prompt on cwd mismatch. |
| OpenCode | Prefer `opencode session list --format json`, optional `opencode session export <id> --sanitize` for preview | `opencode --session <id>` OR `opencode mini --session <id>` (verify interactive installed CLI help and desired UX) | `opencode run --session` without a prompt is not a safe GUI resume choice. Don't query/modify its DB without verifying a stable API. |
| Pi coding agent | Bounded scan of supported JSONL roots, `PI_CODING_AGENT_SESSION_DIR`, `--session-dir` | `pi --session <path-or-id>` | Session tree/branches and cross-project fork prompts; path may be safer than ambiguous ID. |

Do not assume file schemas from guides alone. Read current upstream source and build **synthetic** fixtures for each provider, including corrupt/partial files. Never put live transcripts or tokens into the repo.

For multiple accounts, do **not** copy OAuth tokens or use a single global account switch. Profiles declare approved history roots + launch executable/flags + optional safe environment mappings. If native Herdr argv API cannot set subprocess env safely, use an audited helper wrapper or explain the limitation and disable that profile's resume. Never invoke a shell string containing untrusted names, ids or paths.

## 3A. References and requirements added after Pane / T3 source review

- **Pane**: https://github.com/greenfield-inc/Pane and https://github.com/greenfield-inc/Pane/blob/main/docs/SESSIONS.md — study native adoption, idempotent migration records, live-session guards and verifiable continuation; **do not copy AGPL-3.0 source into this MIT repository** without compatible licensing analysis.
- **T3 Code**: https://github.com/pingdotgg/t3code, especially [`AgentSessionScanner.ts`](https://github.com/pingdotgg/t3code/blob/main/apps/server/src/project/AgentSessionScanner.ts), [`AgentSessionImporter.ts`](https://github.com/pingdotgg/t3code/blob/main/apps/server/src/project/AgentSessionImporter.ts), [`agentSessions.ts`](https://github.com/pingdotgg/t3code/blob/main/packages/contracts/src/agentSessions.ts). T3 currently covers Claude, Codex **and Pi** in its source import contract; verify release. MIT code is reusable only with appropriate notices and assessment.
- **Known bugs to avoid**: compressed Codex `.jsonl.zst` misses (#21755), huge Claude sessions (#29153), misleading file mtime (discussion #21764), CLI sessions imported only during onboarding (fixed November 9 in #10961), and provider-instance identity collisions (#17236). Links and implementation criteria are in `docs/REFERENCE_IMPLEMENTATIONS.md`.
- **Do not conflate** `discover`, `preview`, `import`, `resume`, `migrate`, `sync`. A read-only history browser should not relocate transcripts. Index refresh must be user-invocable indefinitely, not onboarding-only. Successful launch is not proof of resumed context. See `docs/MIGRATION_AND_REFRESH_DESIGN.md`.
- **Security constraint**: no copying or exposing personal/company OAuth tokens, no unsanctioned file/network access, no silent originals mutation. Do not assume upstream snippets or components have undergone a full security audit.

## 4. Order of execution — implement, don't just write a plan

**Gate A — local environment and research**
1. Run `scripts/windows-preflight.ps1` *locally* on Windows; inspect actual binaries and SDK. Do not commit the output if it has private paths or account details.
2. Inspect the sources listed above, plus Pane/T3 actual history implementations and licenses; record current Herdr version, supported APIs, four CLI versions, commit SHAs, and reference findings in `docs/RESEARCH_FINDINGS.md` / `docs/UPSTREAM_REVIEW.md`, marking each point confirmed/assumed/blocked.
3. Build documented commands and a provider capability matrix. Confirm how the current Herdr UI docks a mod without rewriting current layout.

**Gate B — native working vertical slice**
4. Implement a valid `mods/session-hub/` module with clean, responsive native UI. Show list, tabs, search, provider chips, project group, error/empty/loading states.
5. Implement read-only Claude and Codex adapters and click-to-resume in a real Herdr tab. Assert the cwd and exact argument vector.
6. Add OpenCode and Pi adapters and native resume. Run end-to-end against disposable test projects (never mutate real source sessions).

**Gate C — complete features**
7. Custom paths/profiles, de-duplication, refresh/cancellation, safe previews, sorting/filtering, persistent local metadata.
8. Full-text search: opt-in content indexing; bounded incremental extraction; local-only index; clear/reset; correct filesystem permissions. If Herdr-only implementation is too slow, ship a minimal auditable helper with documented build, signing/checksum and safe invocation, not arbitrary script execution.
9. Aliases and archive in **Hub-owned metadata only**. 'Remove from Hub' must be separate from 'Delete original'. Provide precise provider/active-session checks, backup and typed confirmation; if unsafe or unverified, visibly disable original deletion. No pretending it works.
10. Portable, versioned offline export/import with checksum and secret filters; encrypted export if contents leave the machine. Optional remote sync MUST be opt-in, conflict-safe and backed by a reviewed cryptographic library, not homegrown encryption. Begin with Hub metadata sync and be explicit where native transcript restoration is unsupported.

**Gate D — hardening and open source release**
11. Run tests for 10k synthetic session records, corrupt JSONL, partial writer files, Unicode/long/UNC paths, junction loops, malicious transcript text, CLI missing, profile mismatch, stale cwd, index corruption, wrong decryption key, session conflicts.
12. `herdr-app check` and **real interactive GUI smoke test** (search, refresh, actual resume of each provider). Upgrade test: personal mod persists and only supported APIs used; rollback test with backup.
13. Document true tested coverage and limitations; produce `SECURITY.md`, `CONTRIBUTING.md`, `CHANGELOG.md`, version/compatibility matrix, working uninstall instructions, `RECIPE.md`, **real sanitized screenshot** `preview.png`.
14. No publishing, remote deployment, app installation, copying real chat data, or destructive operations until user explicitly approves. Ready the repo and give a test report.

At every gate keep moving. If blocked, implement the safe mock/adapter and note **not runtime verified**. Do not claim end-to-end success without real GUI and original provider CLI tests.

## 5. Must-pass acceptance

The full F01–F16 matrix is in `docs/PRODUCT_REQUIREMENTS.md`; use `docs/TEST_PLAN.md` for tests. Also require:
- Both user-owned `.claude` personal/work histories are discoverable as **separate profiles** without copying credentials and are never silently mixed.
- Existing Herdr layout/shortcuts/agents remain untouched, and uninstall leaves originals intact.
- All four providers show old history created outside Herdr; all four resume safely on a single Windows machine after actual verification.
- No transcript text leaks to logging, public builds, telemetry or diagnostic screenshots.
- App update keeps the mod on disk; compatibility breaking changes have a recorded fallback and a way to roll back.

## 6. At final Codex handback

Provide:
- What is implemented, by F01–F16 ID; tested vs untested vs deliberately disabled.
- Exact files/commit(s), commands run, environment & CLI versions, real test output and Herdr GUI screenshots.
- Security audit summary (dependencies, network, credential scope, shell launch, original file hashes, exports), known risks and mitigations.
- Clean install, upgrade, uninstall, backup and rollback instructions for Windows.
- Exact next actions necessary to publish on GitHub and appear in Herdr Gallery. Never claim gallery publication until observed.
