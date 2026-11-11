# Architecture and data model

## Preferred design
- `mods/session-hub/main.js`: native Herdr GPUI view (`gpui-kit`, `gpui-base`, `herdr`), not DOM/React/Node.
- Provider adapters: Claude Code / Codex / OpenCode / Pi. Use documented CLI discovery APIs when available, otherwise bounded read-only parsing. No direct mutations of source databases.
- A **small, audited local indexing helper** may be useful for fast cross-provider full-text search. Prefer Rust CLI with embedded SQLite FTS5, invoked via Herdr's `exec(command, args, {cwd,timeout})` API. Verify native packaging, helper integrity, and CLI availability. A helper is optional and must be justified vs. Herdr-only implementation.
- Store Hub-owned metadata, alias/archive flags, index and preferences in the mod's own user data area, never in provider source dirs.
- Use canonical paths, bounded file enumeration, stable provider-specific IDs; support multiple configured profiles. No junction/symlink loops or accidental scanning of entire profile.
- Resume via `run('tab.new', {name, folder, argv})` after checking the installed Herdr command contract and provider CLI flags. Do not shell-interpolate user content. No invocation before user click.
- Background jobs use Herdr's `cx.spawn` and timers, not setInterval. Keep per-view state within View instance, not module scope.

## Normalized SessionRecord (conceptual; validate per adapter)
```
{
  key: string,            // stable namespace: provider/profile/native-id
  provider: 'claude'|'codex'|'opencode'|'pi',
  profileId: string,
  nativeId: string,
  sourcePath?: string,    // bounded allowed source
  cwd?: string,           // verified original project directory
  title: string,
  alias?: string,         // Hub-only
  createdAt?: string,
  updatedAt?: string,
  summary?: string,
  archived: boolean,      // Hub-only
  canResume: boolean,
  resumeUnavailableReason?: string,
  sourceKind: 'file'|'cli'|'database',
  fingerprint?: string,
  schemaVersion?: string
}
```

## Interface abstraction
- `discover(profile, options): Promise<SessionRecord[]>`
- `preview(record, {maxBytes,maxTurns}): Promise<Preview>`
- `resumeSpec(record, profile): Promise<{argv:string[],cwd:string}>`
- `refresh(profile, sinceCursor): Promise<DiscoveryResult>`
- `canDeleteOriginal(record): Promise<SafeDeleteCapability>` (default false)
- `deleteOriginal(record, verifiedConsent): Promise<Result>` (never enabled by default)

## Privacy boundaries
- `discovery`: read approved session roots ONLY.
- `index`: local metadata and opt-in content index; clear/delete index command.
- `sync`: separate optional module, encrypted export/import; no auth/key file export.
- `profile`: labels, roots and launch executable, NOT saved OAuth secrets.

## Safe encrypted sync strategy
1. Build offline export/import with manifest, schema version, checksums, timestamps, redaction options.
2. Implement encryption using an audited existing cryptographic library/tool (e.g. verified age-compatible implementation), never custom crypto. Document key recovery and where keys live.
3. User chooses destination and initiates transfer. No silently enabled remote endpoints.
4. Sync Hub metadata and content separately; support preview before applying, detect conflicts and never overwrite a live session or overwrite provider auth.
5. Imported session becomes directly resumable only after a verified provider-native import/restore path for that agent/version. Otherwise it is a read-only archived preview.

## Installation updates
- Personal mod lives at `~/.config/herdr-app/mods/session-hub/`. Shipped Herdr mods may change during Herdr upgrades; personal copies persist.
- On startup check expected API capabilities, display diagnostic and disable affected actions on incompatibility.
- Run `herdr-app check` and interactive smoke tests after upgrading the app; support rollback to last tagged working release.

## Implemented reader boundary

`helper/adapters/` contains independent Claude/Codex/Pi/Copilot/Gemini readers and
shared conversation-only normalization. A fixed local package loader preserves
Python `-I` isolation without adding cwd or provider paths to imports. The helper
retains bounded file/SQLite I/O, DPAPI store, profile validation and launch policy.
Gemini projection runs only on complete bounded input; its append operations can
remove text, so every file generation replaces indexed text. OpenCode's immutable
reader refuses WAL and has its own fixture coverage. Live native catalog artwork
is display metadata only; no agent-provided `run` vector becomes a guessed resume
command. Each resumed session still uses its audited provider-specific contract.
