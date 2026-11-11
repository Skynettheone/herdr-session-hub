# Product Requirements Document — Herdr Session Hub

## Product scope
Native Herdr GUI mod for Windows with later macOS/Linux support. Four providers: Claude Code, Codex CLI, OpenCode, Pi coding agent. No cross-provider transcript conversion. Preserve current Herdr layout and provider auth.

## Full required feature matrix (all in development scope)
| ID | Feature | Required behavior and acceptance |
|---|---|---|
| F01 | Discover four agents | Detect installed commands and indexed session stores; missing agent displays actionable status. |
| F02 | List old sessions | Include sessions created outside Herdr, title/first prompt, provider, profile, project, timestamps and stable id. |
| F03 | Search | Search titles, original project paths, aliases, ids; normalized, cancellable. |
| F04 | Provider filter | All/Claude/Codex/OpenCode/Pi, with combined filters. |
| F05 | Resume in Herdr | Explicit click invokes verified provider resume command in new Herdr tab and original cwd; report missing cwd, active lock, unsupported. |
| F06 | Refresh | Manual refresh with progress; incremental refresh without restarting Herdr; handle partial writer files. |
| F07 | Preserve layouts | Personal mod directory, no replacement of shipped layouts or hotkeys, install/removal reversible. |
| F08 | Custom history paths | Per provider/profile root(s), validation, preview, permission errors, safe disable. |
| F09 | Read-only previews | Bounded excerpts of user/assistant turns, escaped text, no tool execution, optional redaction. |
| F10 | Project grouping | Collapsible group, stable working directory, counts and sort by recency. |
| F11 | Multiple provider profiles | Explicit personal/work labels, isolated credentials, independently configured roots and launch commands, never silently choose wrong account. |
| F12 | Full-text search | OFFLINE, local FTS index with opt-in content indexing, privacy UI, ignore credential and excluded paths, clear/rebuild control. |
| F13 | Archive | Hub-only archive flag/hide state by default, reversible; do not mutate provider originals. |
| F14 | Rename | Hub-only display alias initially, reversible. Native rename only if safe documented support. |
| F15 | Delete | Separate 'Remove from Hub' (index only) from 'Delete original' (dangerous). Native source deletion disabled unless provider-supported, backed up, explicit typed confirmation, tested recovery. |
| F16 | Cross-computer sync | Optional, explicit, encrypted backup/export/import and conflict-safe sync. Never raw Dropbox/Git/HTTP upload of transcripts or credentials; no background/cloud default. Support portable metadata sync first, content only with verified compatible source-import process and user approval. |

## UI details
- Sidebar-sized panel dock left/right by default, responsive on narrow widths; light/dark via `theme()`.
- Header with refresh, search, settings, status, counts; provider chips; profile multi-select; project grouping; sortable list; empty/permission/invalid-format states; keyboard navigation.
- Session detail shows title, origin, project path, profile, resume status, timestamps, metadata, read-only preview, resume in tab, copy ID, alias, archive, export, and guarded delete.
- Distinguish `session exists`, `CLI installed`, `can resume`, and `source writable` as independent signals.
- Show a visible warning for unknown cwd, version drift, or account mismatch.

## User journeys
1. User has old Claude transcripts, never opened Herdr before. Install mod, select Claude filter, see historical sessions, open one in new tab, conversation resumes.
2. User has two Claude Code profiles. Choose profile explicitly and resume the same eligible source using the intended credentials without merging auth.
3. User starts session in Codex externally. Refresh Herdr, see it, full-text search and resume.
4. User adds OpenCode or Pi profile. Adapter probes the environment and lists sessions or explains absence/unsupported version.
5. User archives an entry and later unarchives; provider transcript stays unchanged.
6. User requests deletion. Safe confirmation/backup flow or clear unavailable warning; no silent source delete.
7. User chooses encrypted export, moves file to another computer, imports metadata and optional sessions if provider compatibility allows; no credential transfer.
8. User updates Herdr. Personal mod files, settings, and cache persist and panel passes compatibility checks, or gracefully reports unsupported API.

## Out of scope (unless later separately approved)
- Automatic mixing of personal/company auth tokens.
- Converting Claude Code JSONL into Codex/Pi/OpenCode native formats.
- Remote multiuser session collaboration or sharing private session contents publicly.
- Uploading transcript content as telemetry or diagnostic logs.

## Release gates
A release is complete only when F01–F16 are either implemented and tested or clearly documented as a deliberate guarded/unavailable subfeature with precise reason. Never call v1 production-ready if unsafe deletion or end-to-end encrypted sync have not been tested.
