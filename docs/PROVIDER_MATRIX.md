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
