# Session Hub — native history panel (development candidate)

Native GPUI mod for Herdr Desktop 0.1.15 on Windows x64. Explicit profiles discover
Claude Code, Codex, Pi and quiescent OpenCode histories without moving transcripts.
Search/filter/group, read bounded previews, create aliases, archive or hide entries.
Opt in to encrypted local content indexing. Request native resume in a local
Herdr tab with explicit profile and cwd; continuity is not automatically verified.

Requires CPython 3.14 and offline dependency installation through
`scripts/install.ps1`. Copying the mod alone is insufficient. `mod.json` uses
`place=none` so installation does not alter the current layout or hotkeys. Open
with `herdr-app do mod.open --name session-hub` after approving installation.

The accompanying preview is a real installed-Herdr initial loading render of
the refined layout. A populated gallery capture remains pending after GUI testing
was stopped. It does not establish native provider continuity. Original deletion,
native transcript migration and remote sync are unavailable. See README.md and
docs/FEATURE_STATUS.md for the release blockers. Do not list this candidate as a
production gallery release before those gates pass.
