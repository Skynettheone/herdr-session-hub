# Provider adapter research checklist

All commands are **starting candidates**, not a substitute for probing installed versions and validating actual session IDs and directories.

| Provider | Common local roots (per user) | Official/known resume approach | Discovery and risks |
|---|---|---|---|
| Claude Code | `~/.claude/projects/`, custom `CLAUDE_CONFIG_DIR` for alternate profiles | `claude --resume <session-id>` (from original cwd) | JSONL per project; avoid token/settings files; validate IDs, cwd, profile, nested/subagent transcripts. |
| Codex CLI | `~/.codex/sessions/`, custom `CODEX_HOME` | `codex resume <session-id>` | JSONL rollout paths and optional SQLite index; read-only parse; changing/symlinking CODEX_HOME can cause index inconsistencies. |
| OpenCode | OpenCode-maintained local database; `opencode debug paths` | `opencode mini --session <id>` documented; verify if full-screen `opencode --session <id>` supported in installed CLI | Prefer `opencode session list --format json` and supported export APIs; do not edit DB. |
| Pi coding agent | `~/.pi/agent/sessions/`, configurable by installed Pi version | `pi --session <path-or-id>` | JSONL sessions can branch; preserve full source path and original cwd. |

## Required probes
- `claude --version`, `claude --help`.
- `codex --version`, `codex resume --help`.
- `opencode --version`, `opencode session list --help`, `opencode debug paths`.
- `pi --version` / `pi --help`.
- `herdr-app commands`, `herdr-app status`, `herdr-app check <mod-folder>`.

## Known important caveats
- Different provider CLIs use different session formats and may need different working directories. 'Resume' means continue with **same provider**, not transfer between providers.
- Some provider versions may not expose a stable read-only preview API. Use bounded parsing or show metadata-only.
- Do not assume GUI-sidebars of different vendors automatically import CLI history even when shared local files exist.
- Windows project paths may contain Unicode, spaces, junctions, or access restrictions. Never blindly recurse all directories.

## Source documentation
- Herdr API: https://github.com/herdrdev/herdr-app/blob/master/defaults/AGENTS.md
- Claude CLI: https://code.claude.com/docs/en/cli-reference
- Codex CLI source: https://learn.chatgpt.com/docs/cli/reference
- Codex config: https://github.com/openai/codex/blob/main/codex-rs/core/src/config/mod.rs
- OpenCode: https://opencode.ai/docs/cli/commands
- Pi: https://github.com/earendil-works/pi

## Verified expansion — 2026-11-12

| Provider | Read-only history | Native continuation status |
|---|---|---|
| Claude / Codex / Pi / OpenCode | Fixture-tested adapters plus real disposable native stores; OpenCode committed WAL supported only without open writers | Native Herdr context continuation passed with a loopback model fixture; cloud-account isolation unverified |
| Gemini 0.49.0 | `tmp/<project>/chats/session-*.json` and `.jsonl`; complete replay ≤2 MiB / 10k projected messages; partial/malformed journals stay metadata-only | `--session-file <absolute-path>`; installed help verified; explicit .gemini home, Node launcher, projectPath hash match, CLI stamp and trust required; actual continuity unverified |
| Copilot | `session-state/<UUID>/events.jsonl`; user/assistant content, root context, no subagent/tool content | Disabled: installed VS Code shim returns 127; no real CLI verified |
| Cursor / Amp | Recognized through Herdr; no verified offline reader | No Hub continuation claim; CLIs absent |
| Other built-in or custom Herdr agents | Dynamic catalog with native name/icon/installed state and explicit unavailable-history explanation | No guessed generic resume command |

Root selection remains explicit for every profile. Gemini's config home must be
`.gemini`; its `GEMINI_CLI_HOME` is that folder's parent. `directories` are added
workspace paths and never treated as original cwd. `projectPath` is user supplied
and must hash exactly to recorded `projectHash`; a mismatch leaves cwd unknown.
Copilot rewind/truncation produces a partial raw-log excerpt; no exact canonical
branch reconstruction is claimed. Large Gemini replay is deliberately disabled
rather than indexing obsolete text that later patches might remove.
