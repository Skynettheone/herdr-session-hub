# Session Hub — native history panel (development candidate)

Native GPUI mod for Herdr Desktop 0.1.15 on Windows x64. Explicit profiles discover
Claude Code, Codex, Pi, quiescent OpenCode, Gemini and Copilot histories without
moving transcripts. Native catalog artwork follows the installed Herdr.
Linux x64 and Apple Silicon macOS ports have native helper/key-store CI and
offline installers, but native Herdr GUI/context acceptance is pending and
provider continuation stays disabled there. See docs/PORT_ACCEPTANCE.md.
Search/filter/group, read bounded previews, create aliases, archive or hide entries.
Opt in to encrypted local content indexing. Request native resume in a local
Herdr tab with explicit profile and cwd; continuity is not automatically verified.

Requires CPython 3.14 and offline dependency installation through
`scripts/install.ps1`. Copying the mod alone is insufficient. `mod.json` uses
`place=none` so installation does not alter the current layout or hotkeys. Open
with `herdr-app do mod.open --name session-hub` after approving installation.
Use Dock for a collapsible History tab beside Files and Changes in a new personal
layout copy. The original layout and shipped header files remain untouched.

The accompanying preview is a real populated isolated-Herdr capture of the
refined layout. Dark, paper and a custom community-format theme were checked.
Four primary providers and Gemini passed native Herdr context continuation with a
local model fixture; isolated Herdr update and rollback passed. Original deletion,
native transcript migration and remote sync are unavailable. See README.md and
docs/FEATURE_STATUS.md for the release blockers. Do not list this candidate as a
production gallery release before those gates pass.
