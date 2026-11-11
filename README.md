# Herdr Session Hub

A native Herdr Desktop history panel for Claude Code, Codex, OpenCode, Pi, Gemini
and Copilot, with a live capability catalog for every Herdr agent.

**Development candidate — not production-ready.** The implementation and local
test suite are present. Native GUI rendering/filtering/preview were exercised on
Windows; actual restored provider context has not been verified. Production installation and publication have not been performed.

Session Hub discovers explicit local roots, searches metadata and opted-in text,
groups projects, previews plain conversation text, and stores aliases/archive
flags separately from originals. Hub state is encrypted with Windows DPAPI.
The native layout uses compact rows, responsive master/detail navigation and
Herdr semantic colors and official icons for built-in and community themes. Dark,
light and a custom community-format theme were checked in the native GUI.
Portable encrypted metadata bundles have dry-run import and conflict handling.
Native resume requests use explicit profile directories, original cwd and argv
arrays. OpenCode reads its installed-version SQLite schema without starting the
CLI and refuses nonempty WAL data. Oversized and compressed histories have
bounded reads and visible partial coverage.

| Capability | Status |
|---|---|
| F01–F04 discovery, history, metadata search, filters | Implemented; six history adapters fixture-tested |
| F05 native continuation | Guarded launch implemented; actual continuity unverified; active checks conservative |
| F06–F11 refresh, layout preservation, roots, preview, grouping, profiles | Implemented; native smoke and synthetic tests; update persistence not runtime-tested |
| F12 full-text search | Opt-in encrypted local FTS5; bounded incremental coverage |
| F13–F14 archive and aliases | Hub-only, reversible |
| F15 removal / original delete | Hub removal implemented; original deletion unavailable |
| F16 portability / sync | Encrypted metadata file exchange implemented; native restore and remote sync unavailable |

See the full [F01–F16 status and release gates](docs/FEATURE_STATUS.md),
[test evidence](docs/TEST_RESULTS.md), [security findings](docs/SECURITY_REVIEW.md),
[pinned upstream review](docs/UPSTREAM_REVIEW.md) and [user guide](docs/USER_GUIDE.md).

Tested environment: Windows 11, Herdr 0.1.15, herdr-core 0.1.20, CPython 3.14.3,
SQLite 3.50.4, Node 24.14.1 (tests only). CLI help/version probes: Claude 2.1.322,
Codex 0.164.0, OpenCode 1.3.17, Pi 1.1.0, Gemini 0.49.0. Copilot is a missing-CLI shim; its native continuation
is disabled. Cursor, Amp and other Herdr/custom agents are recognized with honest
unavailable-history status when no verified offline adapter exists. This does not
imply native resume acceptance. macOS/Linux, UNC and WSL are unsupported in this build.

For a synthetic isolated demo or a local development bundle, follow
[CONTRIBUTING.md](CONTRIBUTING.md). Install/uninstall/upgrade/rollback instructions
are in the [user guide](docs/USER_GUIDE.md). The installer requires an explicit
production-install switch and uses `place=none`; it does not replace layouts.

This is a trusted mod. There is no runtime telemetry or network client. A native
provider may use its own hooks and network after a user requests resume. Read
[SECURITY.md](SECURITY.md) before installing. No credentials are read, copied,
merged or exported by Hub. MIT license; dependency notices are included separately.
