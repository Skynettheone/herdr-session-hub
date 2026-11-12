# Research findings — 2026-11-11

## Form usability follow-up — 2026-11-12

Installed 0.1.15 declarations confirm retained InputState.focus/value and normal
GPUI event handlers. The current edit form is appended below all saved profiles,
has no explicit Cancel, and mixes normal input with advanced JSON. This pass will
separate list/edit views, give validation before RPC, keep native path safety in
the helper, and add explicit name reset. Provider changes must clear stale account
folders/command fields. Native input, picker cancellation and invalid JSON remain
acceptance targets; no discovery/provider behavior or production state is changed.

## Follow-up research and decisions — 2026-11-12

The user authorized personal/company sign-ins performed by the user in disposable
profiles and an external Daybreak assessment. No credential file may be inspected
or copied. Daybreak bootstrap reported no GitHub connection; the user later declined
Daybreak in favor of manual review. No external scan was launched. Gemini 0.49's installed @google/genai bundle supports
GOOGLE_GEMINI_BASE_URL and native Gemini SSE. The planned continuity fixture uses
that loopback endpoint and native-created histories, followed by the normal Hub
launch chain. Native GUI coverage is tracked by control and outcome rather than inferred
from host mocks. Completed results and remaining native form gaps are in
FOLLOWUP_ACCEPTANCE.md.

Follow-up: the user declined Daybreak and requested manual security assessment.
Both user sign-ins report the same native identity; the user confirmed no separate
company account is available. Distinct company-account validation cannot be
claimed. Profile-store routing and an unsigned-profile negative control can still
be checked with the available real account. Gemini --session-file was observed
importing under a new UUID; native continuation must use --resume UUID instead.
Herdr 0.1.15's installed tabs mod hardcodes Files/Changes. A licensed, scoped header
adapter in a new personal layout copy is needed for the requested History toggle;
shipped tabs/layouts must stay untouched. Its source is Apache-2.0, retained with
notices, and exact SDK compatibility remains gated.

## Native acceptance follow-up — 2026-11-12

Installed Codex help and `hc --skill` establish `--no-daemon` for Herdr-hosted
interactive launches. Herdr's pinned `src/update.rs` supports a local
`HERDR_RELEASES_URL` test mirror; official versioned manifests are published at
`app/<version>/manifest.json`. Official 0.1.14 and 0.1.15 archives were verified
against those manifests and run only from repository-local installation copies.
Production installation/configuration and real provider histories remain excluded.
Native continuity tests use deterministic loopback endpoints and disposable homes;
the model backend is a test fixture, while the provider CLI and stored sessions
are real. Completed results are recorded in NATIVE_ACCEPTANCE.md.

Confirmed before implementation on Windows: Herdr **0.1.15**, Claude Code
**2.1.322**, Codex CLI **0.164.0**, OpenCode **1.3.17**, Pi **1.1.0**,
Python **3.14.3**, SQLite **3.50.4**, Node **24.14.1**. No Rust toolchain on PATH.
The installed Herdr AGENTS.md and both declaration files were inspected.
`herdr-app commands` confirms `tab.new {name,space,folder,argv,task,mod,props}`.
`exec` accepts an argument vector and timeout but no environment overrides;
`readTextFile` is capped at 1 MiB. View lifecycle, retained InputState,
focus, clipboard, and native flex builders are available. No production files
have been changed. Git was subsequently initialized and pushed at the user's request.

## Decisions

Use independently written Python 3.14 helper code, not Node in the mod.
Python supplies bounded binary reads, zstd, SQLite FTS5 and safe subprocess
argument vectors. Windows DPAPI protects serialized Hub state, including titles
and opted-in content. PyCA cryptography supplies portable authenticated metadata
bundles; no custom encryption primitives. Secrets never go in subprocess arguments.
Provider configuration is explicit; approved roots and config homes are distinct.
Profile-specific environment selection happens only in the helper launcher.

Claude uses `--resume UUID`; Codex uses `--no-daemon resume UUID`; Pi uses `--session PATH`.
Installed OpenCode uses `session list --format json`, **`export ID`**, and
`--session ID`. It does **not** expose `session export` or `mini` in installed
help. OpenCode CLI startup can initialize stores/load configuration: automatic
discovery must not run it against a user's store. Safe read-only snapshot
support or an explicit offline JSON snapshot is required; otherwise disabled.

## Confirmed source observations

Pane has separate scanning, placement, migration records and continuity checks;
its placement can copy transcripts. Session Hub will not adopt that copy behavior.
T3 bounds metadata and import independently, namespaces provider instances, and
uses Pi's file path as native resume cursor. T3's current version migration may
start a fresh provider session with retained messages: this is not native resume.
Codex metadata supplies the native ID; filename inference alone is insufficient.
Codex source includes zstd rollout readers. Pi version 3 files contain a tree.
Conversation timestamps and source mtime must remain distinct.

## Blockers / verification boundaries

No original history or credentials are needed for tests; synthetic roots only.
Native resume restored context for the four primary CLIs in the isolated GUI
with a loopback model fixture. Active-session detection is conservative; uncertain ownership must block
resume. No audited original deletion or native transcript restore protocol exists
for the four adapters. Both operations remain unavailable. Remote automatic sync
is disabled; explicit encrypted metadata file exchange is the feasible first step.
An isolated Herdr home AND isolated core must be used for GUI testing. A production
installation and gallery publication require separate approval. The user authorized
isolated app update/rollback tests; those passed without production installation.

Pinned sources and licensing observations are in UPSTREAM_REVIEW.md. Test results
and release gates will be recorded separately; these findings are not test passes.

## Expanded catalog and branding — 2026-11-12

The installed 0.1.15 SDK exposes `knownAgents()` plus Program key/name/icon/tint
and installed state. Hub follows this live catalog, including community/custom
entries, without guessing a launch command. Herdr's current upstream catalog
has more entries than the eight in the supplied screenshot. Recognition does
not establish local-history compatibility.

Gemini 0.49.0 was probed through the installed native Node launcher using an
isolated `GEMINI_CLI_HOME`. Public Google source documents legacy JSON and
current JSONL (`$set`, `$patch`, `$rewindTo`). Complete projection is limited
to 2 MiB/10,000 messages; incomplete journals remain metadata-only. A project
hash is not cwd. Resume requires an explicit exact path whose SHA-256 matches
the recorded project hash; added workspace directories are not used as cwd.

Copilot SDK documents persisted events and `COPILOT_HOME/session-state`. The
installed VS Code copilot.exe shim returns 127 and says the real CLI is missing.
Discovery is implemented, including subagent exclusion; native launch stays
disabled. No CLI was installed. Cursor and Amp are absent; their current official
CLI docs establish resume commands but do not establish a verified offline disk
reader here. Other Herdr/custom agents show specific unavailable-history status.

The official sheep SVG comes from the user-requested Herdr TUI repository only
as artwork. The extension continues to use the native desktop GUI SDK. License
and pinned source are retained in THIRD_PARTY_NOTICES.md.

## Usage research checkpoint — 2026-11-12

Before Usage implementation, current T3 source was studied at MIT commit
`3c6864235487147fd5667786152f400a75251fca`. Exact links, accounting semantics,
installed versions and verification gates are in [USAGE_DESIGN.md](USAGE_DESIGN.md).
Confirmed: native SDK path drawing; local token channels for Claude, Codex, Pi,
OpenCode and Gemini; Codex cumulative snapshots require deduplication. Unknown
prices are not zero. Copilot usage events are ephemeral; ordinary history does
not establish usage. Live cloud quotas would require credential/network access
outside this extension's boundary; only recorded local snapshots are feasible.
The new additive numeric cache stays inside encrypted Hub state and does not
turn on conversation indexing. No upstream accounting implementation was copied.

## Release hardening checkpoint — 2026-11-12

Rechecked local source and the official Herdr changelog before this follow-up;
0.1.15 remains its newest listed GUI release. The existing native continuation,
form, privacy and Usage evidence supersedes several historical blocker notes.
Large Gemini conversation replay remains intentionally bounded: lifting that
limit safely requires whole-journal projection, not simply increasing a read size.

Two actionable local release gaps were confirmed: installation did not invoke
the package manifest verifier, and a same-version upgrade rebuilt the runtime
directory already referenced by the old mod before validating its replacement.
Harden verification before target writes and use a unique runtime per installation
with automatic mod rollback on a failed final swap. Test corrupt/missing/linked
package inputs and interrupted swaps using disposable roots only. Hash manifests
establish integrity, not publisher authentication; no signing identity is available.
