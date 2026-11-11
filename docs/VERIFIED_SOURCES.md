# Verified primary-source references (research snapshot: 2026-11-11)

This is a **link map**, not a guarantee that a newer version retains every behavior. Links were checked against public sources on the snapshot date. Codex must open them again and compare to installed versions. **Never treat GitHub HEAD as a substitute for the installed `herdr.d.ts`, `gpui-kit.d.ts`, CLI `--help` or active Windows installation.**

## Herdr GUI — authoritative

| What to read | Link | What it establishes |
|---|---|---|
| Herdr Desktop GUI repository | https://github.com/herdrdev/herdr-app | Actual GUI project, Windows install, user-owned mods, updater behavior and privacy notices. **Do not confuse with the earlier terminal/TUI project.** |
| Installed-guide source | https://github.com/herdrdev/herdr-app/blob/master/defaults/AGENTS.md | Native `View`, `main.js`, `mod.json`, `gpui-kit`, `gpui-base`, `herdr`, `cx.spawn`, `cx.timer`, `exec`, `run`, `tab.new`, mod installation/validation/gallery recipe. |
| Mods documentation | https://github.com/herdrdev/herdr-app/blob/master/docs/mods.md | Personal mod locations, installed `.d.ts` as version-specific API authority, app check and security warning. |
| GUI changelog | https://github.com/herdrdev/herdr-app/blob/master/CHANGELOG.md | 2026-11-10 v0.1.15, API and lifecycle changes; recheck on each new Herdr release. |
| GUI repo developer instructions | https://github.com/herdrdev/herdr-app/blob/master/AGENTS.md | When a feature belongs in mods vs core; compatibility principles. |
| Security/privacy | https://github.com/herdrdev/herdr-app/blob/master/docs/security.md | Mods are trusted code; read before installation. |
| Gallery requirements | https://herdr.dev/gallery/ | Mod-only repo uses `mods/<name>/`, `RECIPE.md`, `preview.png`, optional `keys.json`, GitHub topic `herdr-mod`; gallery not code security review. |

**Installed Windows API probe**: `~/.config/herdr-app/AGENTS.md`, `~/.config/herdr-app/herdr.d.ts`, `~/.config/herdr-app/gpui-kit.d.ts`; `herdr-app commands`; `herdr-app check <mod-directory>`. Find .d.ts if nesting differs. **Do not** use `herdr` TUI guide. **Do not** blindly run `irm ... | iex`; review any installer before execution.

**Upstream signatures documented as of snapshot**:

- `run("tab.new", { name?, space?, folder?, argv?, task? })` and `run("tab.new", {mod, props?})` — create normal terminal tab or mod-only tab. **Confirm installed version & supported args.**
- `exec(cmd, args, { cwd?, on?, timeout? })` — argument vector; use for safe program invocation; explicit timeout.
- Native JS mod `mods/<name>/main.js` + `mod.json`, GPUI rendering without DOM/Node; `cx.spawn`, `cx.timer.every`, `cx.notify`.
- `herdr-app check` tests load/one render only; it is *not* an end-to-end integration test.

## Claude Code

| What to read | Link | Notes |
|---|---|---|
| CLI reference | https://code.claude.com/docs/en/cli-reference | Official `claude --resume <session>`/`claude -r` behavior, `claude auth status` and version help. |
| Claude Code upstream code | https://github.com/anthropics/claude-code | May be incomplete vs closed-source distribution; installed CLI is authoritative for behavior. |
| Claude Code settings | https://code.claude.com/docs/en/settings | Confirm config-directory override and safe profile configuration against installed version. |

**Candidate** metadata source `~/.claude/projects/` (Windows `%USERPROFILE%\.claude\projects`); custom `CLAUDE_CONFIG_DIR`. Source schemas must be discovered and tested, especially project/cwd mapping. Do not read actual auth files.

## OpenAI Codex CLI

| What to read | Link | Notes |
|---|---|---|
| CLI reference | https://learn.chatgpt.com/docs/cli/reference | `codex resume [SESSION_ID]`, `--last`, `--all`, cwd handling; version-dependent. |
| CLI documentation | https://learn.chatgpt.com/docs/codex/cli | User workflows. |
| Codex source | https://github.com/openai/codex | Read actual rollout/session parsing code when defining adapter and tests. |

**Candidate** history root `$CODEX_HOME/sessions` (default under `~/.codex/`); confirm installed version. Do not edit any local Codex thread database. `codex resume <id>` resumes a same-provider session, not a cross-provider conversion.

## OpenCode

| What to read | Link | Notes |
|---|---|---|
| Current CLI reference | https://opencode.ai/docs/cli/commands | Documented `opencode session list --format json`, `session export <id> --sanitize`, `opencode mini --session <id>` and `opencode run --session <id> <prompt>`. |
| Source repository | https://github.com/anomalyco/opencode | Use to check session model/CLI output, changes, platform storage. |

Prefer supported CLI JSON output over database peeking. Use `opencode mini --session <id>` or an installed interactive command if verified; `opencode run --session` with no follow-up message is **not** the same as opening an interactive conversation. Avoid `opencode auth export`: it exports secrets and is irrelevant.

## Pi coding agent

| What to read | Link | Notes |
|---|---|---|
| Maintained source repository | https://github.com/earendil-works/pi | Current destination of the old `badlogic/pi-mono` link at snapshot date. |
| CLI documentation | https://github.com/earendil-works/pi/blob/main/packages/coding-agent/docs/cli.md | `pi --session <path|id>`, `pi --resume`, `pi --session-dir`, `PI_CODING_AGENT_SESSION_DIR`. |
| Coding agent usage | https://github.com/earendil-works/pi/blob/main/packages/coding-agent/docs/usage.md | Session files and per-project semantics, fork/tree caveats. |

**Candidate** root `~/.pi/agent/sessions/` unless changed by CLI flags, env or settings. Session ID lookup can be project-scoped; prefer exact path when safe.

## Key facts vs implementation hypotheses

| Item | Status |
|---|---|
| Herdr native mod structure, app-side command arrays, `tab.new`, user-mod persistence | Documented upstream; must be checked against installed version |
| Four agents' resume/list command patterns above | Documented upstream; must be checked against installed versions |
| Raw transcript layouts and metadata fields | **Not stable APIs**; must be researched/tested with synthetic fixtures |
| Herdr packaged ZIP working on user's PC | **Not verified** — starter contains no functional mod |
| Automatic cross-computer native conversation sync | **Not guaranteed**; optional and gated by explicit, audited implementation |
| Work and personal credentials fully isolated | Design requirement; needs real validation per configured profile |

Keep original source URLs (not bare tool citations) inside code comments/README where decisions rely on them. Pin a tested release/commit SHA when implementation is validated.

## Additional engineering references (verified 2026-11-11)

- Pane: https://github.com/greenfield-inc/Pane ; migration behavior https://github.com/greenfield-inc/Pane/blob/main/docs/SESSIONS.md ; **AGPL-3.0** (read-only/adoption/continuity ideas, not copy-paste code).
- T3: https://github.com/pingdotgg/t3code ; scanner https://github.com/pingdotgg/t3code/blob/main/apps/server/src/project/AgentSessionScanner.ts ; importer https://github.com/pingdotgg/t3code/blob/main/apps/server/src/project/AgentSessionImporter.ts ; source contracts https://github.com/pingdotgg/t3code/blob/main/packages/contracts/src/agentSessions.ts ; **MIT**. Current contracts include Claude, Codex and Pi; OpenCode requires its own primary reference.
- T3 import documentation: https://github.com/pingdotgg/t3code/blob/main/docs/user/welcome-wizard.md (30-day/200-message/size limits); https://github.com/pingdotgg/t3code/blob/main/docs/user/thread-migration.md (copy-once V1→V2 version migration, not live sync).
- T3 known edge cases: https://github.com/pingdotgg/t3code/issues/21755 (compressed Codex), https://github.com/pingdotgg/t3code/issues/29153 (oversized Claude), https://github.com/pingdotgg/t3code/issues/10961 (import UI post-onboarding, fixed Nov 9), https://github.com/pingdotgg/t3code/issues/17236 (native provider identity collision), https://github.com/pingdotgg/t3code/discussions/21764 (mtime vs last conversation timestamp; proposal, not confirmation of a merged fix).
- Details, copy restrictions, acceptance criteria: `docs/REFERENCE_IMPLEMENTATIONS.md` and `docs/MIGRATION_AND_REFRESH_DESIGN.md`.
