# Release and gallery checklist

## GitHub repository settings
- Name `herdr-session-hub`
- Description: `A unified session manager for Herdr. Discover, search, preview, organize, and resume Claude Code, Codex, OpenCode, and Pi conversations.`
- Public; MIT; Issues and Discussions on; private vulnerability reporting on.
- Topics: `herdr-mod`, `herdr`, `claude-code`, `codex`, `opencode`, `pi-coding-agent`, `session-manager`, `developer-tools`, `ai-agents`, `open-source`.

## Before listing
1. Implement `mods/session-hub/main.js`, `mod.json` and optional helper with documented install path.
2. Add production-ready `RECIPE.md` (describe ACTUAL working implementation, not proposed architecture).
3. Capture real UI screenshot `preview.png` from `herdr-app shot` (remove personal content/paths).
4. Do not include `layouts/` folder in mod-only repo.
5. Run Windows and provider acceptance suite; publish test report and release tag with checksums.
6. Publish by pushing public repo with `herdr-mod` topic; Herdr gallery picks up eligible repos. Listing is not an independent security audit.

## Update resilience
- Keep user-installed mod in `~/.config/herdr-app/mods/session-hub/` separate from shipped Herdr mods.
- Don't write to Herdr `defaults`, `settings.json`, or built-in layout without explicit user action.
- On future Herdr API changes, run CI with new declarations, update compatibility matrix; ship mod updates via GitHub releases with backup/rollback.
