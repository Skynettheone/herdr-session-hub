# Windows preflight and environment checklist

Run in **PowerShell 7 on the actual Windows user account** where Herdr is installed. The commands should not modify Claude, Codex, OpenCode or Pi. Avoid uploading raw output to public issues because it can show private usernames, project paths or account labels. The bundled `scripts/windows-preflight.ps1` prints only versions, paths to commands and transcript counts, not transcript contents.

## Before coding

```
herdr-app commands
herdr-app status
claude --version
claude --help
codex --version
codex resume --help
opencode --version
opencode session list --help
opencode mini --help
pi --help
```

Use `Get-Command herdr-app,claude,codex,opencode,pi -ErrorAction SilentlyContinue` to locate actual executables. If a CLI isn't installed, tests must use fixtures and provider must show a missing-agent state; don't assume installed.

Inspect, **do not paste to public GitHub**, the local SDK folder:

```
$h = Join-Path $HOME '.config\herdr-app'
Get-ChildItem -Path $h -Filter '*.d.ts' -File -Recurse -ErrorAction SilentlyContinue |
  Select-Object -ExpandProperty FullName
Get-Content (Join-Path $h 'AGENTS.md') -TotalCount 60
```

Only after Codex has prepared a real mod:

```
herdr-app check "$HOME\.config\herdr-app\mods\session-hub"
```

If checking a development folder outside production config is supported in installed Herdr, prefer it. **Do not copy into production mod directory without approval.**

## History roots: defaults are *candidates*, not guaranteed

- Claude Code: `~/.claude/projects/`; alternate profiles under `CLAUDE_CONFIG_DIR` if configured.
- Codex: `~/.codex/sessions/`, or `$env:CODEX_HOME\sessions`.
- Pi: `~/.pi/agent/sessions/`, or configured directory.
- OpenCode: use `opencode session list --format json` for structured metadata; never inspect credentials or raw auth exports.

When multiple profile directories share the same underlying transcript path/junction, avoid duplicated list items. When their credentials are different, keep separate resume choices even for a single shared physical transcript. Avoid reading any credential data to determine profile name.

## Tests that require real Windows, not just CI mocks

- Actual Herdr panel opens, reloads, refreshes and survives app restart without disturbing current layouts.
- `tab.new` starts *exact* provider executable/argv in the original project folder, on same machine, and resumes old sessions.
- Unicode and spaces in project paths, hidden/renamed folders, moved cwd and offline/project-missing state.
- Provider not installed, unrecognized schema, partial JSONL (actively written), junction cycle or file inside excluded credentials root.
- Updates: installed mod persists and passes `check`; if API changes, error is visible and previous mod version can be restored.
