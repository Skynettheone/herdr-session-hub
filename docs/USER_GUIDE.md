# Using Session Hub

This build is a development candidate. Four primary CLIs passed native Herdr
continuation with disposable histories and a loopback model fixture. Herdr
update/rollback passed in an isolated installation. Cloud-account isolation and
independent security review remain unverified. Keep a separate metadata backup.

The follow-up manual assessment and fixes are in SECURITY_REVIEW.md. Two
separately configured profiles were signed into the same real account; distinct
company-account identity behavior remains unverified because no second account
is available. Gemini native continuation passed with a loopback model fixture.

## Setup and opening

Python 3.14 x64, Herdr 0.1.15 and the provider CLIs must be installed separately.
The offline development bundle contains pinned Windows encryption wheels.
After approving a production installation, close Herdr and run from the bundle:

```powershell
pwsh -NoProfile -File scripts/install.ps1 -AppHome "$HOME/.config/herdr-app" -InstallProduction
herdr-app do mod.open --name session-hub
```

The installer uses `place=none`: it does not dock automatically or edit layouts,
keys, agent definitions or settings. Opening the panel is an explicit Herdr action.
Click **Dock** to add History to the native Files/Changes panel in a new
`session-hub-workspace` personal layout copy. A small History tab appears beside
Files and Changes: click it to open/collapse the same panel. History's own collapse
button also hides it. No duplicate scanner/view is added to the header.
Existing layout files and shipped header code are preserved; select the original
layout to return. Older Hub-generated left wrappers are upgraded only in the new
copy. Custom layouts without the standard panel structure receive a clear fallback
and can still open the 440px History dialog. Repeated docking reveals an existing
Hub, including hidden ancestors, instead of adding another panel.
To try it without production installation, see CONTRIBUTING.md. Do not copy only
the mod directory: `runtime.json` must point at the configured Python helper.

## Profiles

Open Settings. Choose provider, a unique profile ID, label, explicit session root,
config home and native command. **Detect installed command** resolves a CLI; it
does not scan any histories. Folder pickers choose the two directories. Save,
check the installed version, then Refresh. There is no implicit personal profile.
Create personal and company profiles separately. Never copy authentication files.

| Provider | Config home | Session root |
|---|---|---|
| Claude | approved `.claude` / `.claude-work` | its `projects` directory (or a subtree) |
| Codex | approved CODEX_HOME | its `sessions` directory (or subtree) |
| Pi | approved Pi agent directory | its `sessions` directory |
| OpenCode | explicit `opencode` config folder | explicit `opencode` data folder containing `opencode.db` |

Custom roots can be discovered, but roots outside the native config store disable
resume when the CLI cannot be shown to find them. Shared physical files appear once
with explicit profile targets. Different physical histories never merge solely
because their native UUID matches. Same UUID twice inside one native store blocks
launch because provider selection would be ambiguous.

Pi's installed PowerShell shim is not executed. Configure `node.exe` plus the
audited installed `bin/pi-launcher.js` in its launcher field. This is a provider
process, not Node inside the GPUI mod.

Advanced JSON accepts `excluded` (absolute paths within roots), up to eight
`roots`, `enabled`, `content`, and directory-only `env`. Account credentials and
arbitrary shell arguments are not accepted. Example, replacing these local paths:

```json
{
  "id": "work-claude",
  "label": "Company",
  "provider": "claude",
  "roots": ["C:/Users/you/.claude-work/projects"],
  "configHome": "C:/Users/you/.claude-work",
  "executable": "C:/Users/you/.local/bin/claude.exe",
  "content": false,
  "enabled": true,
  "excluded": []
}
```

Provider versions outside the researched exact CLI versions disable native launch.
Updating the executable invalidates its stored version check. Updating Herdr outside
0.1.15 disables launch while allowing browsing if the native APIs still load.

## Browsing and search

Refresh scans explicit roots in bounded batches and shows per-profile status.
**Stop after this batch** cooperatively cancels at the next commit boundary; it
does not terminate a provider. Failed scans preserve old records marked stale.
F5 refreshes. Ctrl+F focuses search. Up/Down and Enter select a history entry;
Escape returns from detail/settings. Collapse a project by clicking its heading.
The list renders at most 60 sessions per page; group counts are for that page.
Recent sorting uses observed conversation timestamps, never filesystem mtime.
Unknown timestamps stay explicitly unknown.

Wide views use a history column and conversation detail side by side. A narrow
sidebar opens the detail in place, with a Back button. Conversation previews load
when selected; Details contains IDs/source information, and Organize contains
aliases/archive/removal and portable metadata. The continuation action stays at
the bottom. The profile picker and View options keep secondary filters compact.
All surfaces, text, borders, selection and primary actions use the current
Herdr theme's semantic colors, including community themes; no fixed light/dark
palette is layered over them.

Metadata search matches title, alias, native ID and recorded project path. Full text
adds literal token queries to the local FTS5 index (no regular expressions or SQL).
Content indexing defaults off. Opt in per profile and save, then **Index content
batch**. Each pass advances plain JSONL histories in 2 MiB chunks; repeat passes
until coverage is sufficient. Discovery still sees metadata from huge histories
without indexing the entire file. Content, titles and state are encrypted with
Windows DPAPI; they are decrypted in helper memory during use. Clearing the content
index also replaces its prior accessible encrypted backup. It does not securely
erase old filesystem/OneDrive snapshots or clear first-prompt titles.

Previews are plain native text, at most 30 turns of 2,000 characters each; tool
events and attachments are omitted. Redaction is best effort. A partial preview is
not the provider's complete restored context. Pi's active ancestry is used only
when it fits the read budget; otherwise coverage is explicitly unknown. Full-text
Pi indexing includes abandoned branches as historical text.

OpenCode uses a read-only immutable SQLite connection and never starts the CLI
for discovery. Non-empty WAL data blocks scanning rather than silently hiding
recent conversations. Close OpenCode and use its own supported maintenance to
checkpoint; Hub never checkpoints, copies, writes or changes the source DB.

## Resume

Choose the exact profile in detail. Verify its CLI version in Settings. Type the
exact recorded project path to trust it; starting a provider there can load project
hooks/configuration. Select a **local** Herdr space before Resume. The helper
checks source fingerprint, version, cwd and possible active ownership again when
the terminal wrapper runs. Directory environment overrides are replaced per
profile. Missing/renamed projects are blocked; no silent fallback cwd or account.

Active checks currently enumerate executable names without inspecting other process
command lines. A running same-provider process blocks resume even if it might own
a different session. Pi conservatively treats any Node process as possible
ownership. This can over-block on development machines. Provider-specific precise
ownership and end-to-end continuity need further validation before production.

The outcome is **unverified** after launch. Check the provider's session ID and
previous visible conversation yourself. No test prompts are sent automatically.
No fresh-session fallback, transcript copying or restart-resume promise exists.

## Organizing and portability

Aliases, archive flags and removal tombstones live only in Hub state. An empty
alias restores the provider title. Archived switches between active and archived
entries. Removed includes hidden entries so they can be restored. Original
deletion, native transcript restoration and remote synchronization are unavailable.

Encrypted offline metadata export/import uses a terminal passphrase prompt, never
an argv password or environment variable. Run with the configured Python/helper
paths from `mods/session-hub/runtime.json`:

```powershell
$runtime = Get-Content "$HOME/.config/herdr-app/mods/session-hub/runtime.json" -Raw | ConvertFrom-Json
& $runtime.python -I $runtime.helper --state $runtime.state export C:/ApprovedDestination/metadata.hsh
& $runtime.python -I $runtime.helper --state $runtime.state import C:/ApprovedDestination/metadata.hsh
# Review the counts, then explicitly apply:
& $runtime.python -I $runtime.helper --state $runtime.state import C:/ApprovedDestination/metadata.hsh --apply
```

Export refuses existing destinations. Bundles contain annotations and opaque source
identities, provider and native ID, not transcripts, titles, project paths,
profiles, executables or credentials. User-entered aliases may themselves contain
sensitive information: use a strong unique passphrase (minimum 12 characters).
The format uses PyCA AES-256-GCM and scrypt with fixed parameters and authenticated
version header. Losing the passphrase loses the bundle.

Import defaults to dry-run. Exact local source identities can restore annotations;
foreign identities are retained as foreign metadata, never attached to a same-UUID
local account. Conflicting values are retained separately, never overwritten.
Review imported metadata in Settings. In a matching local session's detail, review
portable metadata and explicitly choose **Keep local annotation** or **Use imported
annotation**. This linking never changes a native source or launch profile; an old
annotation is backed up before replacement. Retain the original bundle. This is
encrypted file exchange, not continuous sync or native migration.

## Upgrade, rollback and uninstall

Close Herdr before replacing the mod. Installer upgrades keep the previous mod
under `data/session-hub-mod-backups/`; Hub state is separate. Before any upgrade,
copy `data/session-hub` to an approved local backup. Local DPAPI state is bound to
your Windows identity; use portable encrypted metadata for another machine.

State writes are atomic with one prior encrypted backup. Schema v1→v2 is additive;
unknown future versions are refused. An interrupted replacement leaves the old
state readable. On corruption, stop Herdr and use the helper's `recover` command;
it validates the backup and keeps damaged evidence under a new `.hub` name. Do not
recover while another helper is active. To roll back code, restore the prior mod
folder and matching runtime; restore matching state from your approved backup if
the previous version cannot read the current schema.

Actual Herdr 0.1.14→0.1.15 update and backup rollback were tested only in a
disposable installation (NATIVE_ACCEPTANCE.md). Back up the complete app binaries
and personal app home before an application upgrade. To roll back, fully exit the
app, restore the matching binary backup and retain the personal home; restore its
state backup only if an older schema requires it. Windows can briefly hold the
executable after window close; wait for that specific app to exit before replacing
its folder. Herdr 0.1.14 still browses Hub but continuation is deliberately disabled.
There is no claimed automatic app downgrade command.

```powershell
pwsh -NoProfile -File scripts/uninstall.ps1 -AppHome "$HOME/.config/herdr-app" -WhatIf
pwsh -NoProfile -File scripts/uninstall.ps1 -AppHome "$HOME/.config/herdr-app"
# Explicitly also erase Hub-owned state/runtime/backups:
pwsh -NoProfile -File scripts/uninstall.ps1 -AppHome "$HOME/.config/herdr-app" -PurgeHubData
```

The uninstaller targets only named Hub namespaces. Provider originals, auth,
Herdr layouts and keys are untouched. Close any Hub pane through Herdr itself.
Before uninstalling, select your original layout or remove the Hub pane in Herdr.
The personal sidebar layout copy is retained because it also contains your
workspace; remove that optional copy yourself only after choosing another layout.

## Herdr agent catalog, Gemini and Copilot

Settings → Agents follows Herdr's current names, icons and installed detection,
including custom agents. A detected command does not imply history support.
Cursor/Amp/other agents with no verified reader show an unavailable explanation.

Gemini profiles select the explicit `.gemini` config folder and a narrow `tmp`
chat-history subtree. Detect command can select `node.exe` plus the installed
`@google/gemini-cli/bundle/gemini.js`; shell shims are not executed. The optional
Original project path must exactly match the recorded SHA-256 project hash. A
missing/mismatched path leaves the project unknown and Continue disabled. Legacy
JSON and current JSONL replay is complete only within 2 MiB and 10k messages;
larger or malformed files stay metadata-only.

Gemini continuation uses `--resume UUID`, preserving native identity. The
`--session-file` option imports/forks and is deliberately not used. Gemini 0.49
can leave multiple files with the same ID after resuming; Hub refuses ambiguous
copies rather than guessing a source. Close live agents and inspect native Gemini
history using its own supported UI when this fallback occurs. Hub never deletes,
rewrites or silently coalesces those originals.

Copilot profiles select the explicit Copilot home and `session-state` subtree.
`events.jsonl` beneath UUID directories is read without starting Copilot. The
installed VS Code shim is not a usable CLI, so Continue remains disabled. No
auto-install or cloud API fallback runs. Rewind/truncation preview is partial.

## Profile form shortcuts

Add profile and Edit profile open a dedicated editor. Save and Cancel stay visible
at the bottom while fields scroll. Escape cancels the draft and returns to the
profile list. Invalid IDs or missing required folders are highlighted before a
save is sent to the helper; filesystem checks still run in the helper. Existing
profile IDs/providers stay fixed, so creating a different account requires Add
profile. Switching agents in a new draft clears old folders and commands.

Advanced JSON opens a separate multiline editor with its own Save profile JSON
action. It saves that JSON instead of guided-field edits. Cancel discards the
unsaved JSON. The existing ID must remain unchanged; a new draft cannot overwrite
another saved profile. No credential values belong in either editor.

Organize → Use original name clears only the Hub alias. Agent names appear once;
a single profile named after its agent is omitted as redundant. Distinct profile
labels remain visible. Multiple profiles always remain selectable, with IDs added
when their labels would otherwise look identical.
