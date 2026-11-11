# Test evidence — 2026-11-12

## Environment

Windows 11 (PowerShell reports Windows NT 10.0.26300.0), Herdr 0.1.15,
isolated herdr-core 0.1.20, CPython 3.14.3, SQLite 3.50.4, Node 24.14.1.
Provider version/help probes: Claude Code 2.1.322, Codex CLI 0.164.0,
OpenCode 1.3.17, Pi 1.1.0. No credentials or actual history text were inspected.

## Executed tests

`python -m unittest discover -s tests -v`: **33 tests passed**, 8.224 seconds
in the final development-bundle run, including a >260-character Unicode source
path. Restricted-sandbox hard-link creation
was denied; rerun outside that sandbox with ordinary-user permissions passed.
This is not an administrator requirement.

Coverage includes four synthetic adapters, exact resume argv/cwd/profile, missing
CLI, unknown versions, changed executable, cwd trust, active/unknown refusal,
source-hash invariance, malformed and partial JSONL, skipped huge lines,
incremental append/search, credentials excluded, distinct/shared identities,
same-store native collisions, FTS opt-in/clear, live OpenCode WAL refusal,
actual DPAPI encryption, concurrent writers, corruption refusal, transactional
schema upgrade, interrupted replacement, locked recovery, real authenticated
portable encryption, wrong keys/tampering/truncation, foreign metadata and conflicts.

50 MiB, 100 MiB and **1 GiB + 1 byte** synthetic sparse histories stayed visible
with bounded previews. Traced helper allocations stayed under the asserted
25 MiB bound in those tests. These are sparse-file parser tests, not a claim of
full >1 GiB indexing throughput. Actual zstd concatenated frames, corruption,
truncation and decompression-ratio safeguards were exercised.

10,000 synthetic normalized session records: sorting/filtering/pagination took
**0.111 seconds** in that run (threshold 5 seconds). A separate 270-file test
verified 128/128/14 refresh batches, eventual complete enumeration and stale
missing-source retention. This does not establish 10k-file cold-scan latency.

`node --experimental-vm-modules --test tests/panel.test.mjs`: **5 test groups
passed**. These cover deferred search/filter/profile/grouping/pagination behavior,
detail previews, aliases/archive/removal, copy, trust, exact `tab.new` requests,
guided settings, picker/profile JSON failures, index controls, offline export/import
terminal arguments, error recovery and independent pane state. Native host calls
are mocked; this is not full native interactive acceptance.

The native UX was subsequently refined: native accessible buttons, compact rows,
automatic bounded previews, a master/detail layout above 760 logical pixels,
sidebar navigation below that width, and separate settings sections. Theme tests
verify that dark, light and partial community palettes resolve only through Herdr
semantic tokens, with no fixed palette overrides. An actual initial native render
of the redesigned layout passed. The user stopped Computer Use with Escape before
the remaining redesigned interaction and community-theme visual checks; those
checks were not resumed or claimed complete.

`herdr-app check mods/session-hub`: **passed** on the installed 0.1.15 SDK after
implementation changes. An earlier restricted check warned about unavailable
gpui-shell storage; checks exited successfully. Passing check is only one render.

## Actual GUI observations

An isolated app home under `.dev/herdr-app`, dedicated
`HC_SESSION=test-session-hub` and scratch XDG paths were used. The real installed
Herdr GUI rendered all four synthetic records with no reported mod errors. Windows
computer-use observations verified provider filtering (Codex leaves one record),
opening detail, scrolling, and loading/rendering the synthetic user/assistant
preview. The helper ran asynchronously via Herdr's real `exec` API.

`preview.png` is an unmodified real capture of the redesigned native layout's
initial loading state. GUI automation was stopped before the revised gallery
capture and visual theme matrix were complete. It contains no private histories
and is not a fabricated mockup; a final populated gallery screenshot remains a
release gate.

## Not established

- Same-native-session continuity and last context after real resume for any of
  the four providers. Only command help, vectors, cwd and safety guards are tested.
- Runtime personal/company authentication isolation, Windows quoting across every
  provider launcher, all controls in real native UI, native multi-pane interactions,
  light-theme and narrow-width acceptance.
- Actual Herdr updater persistence, full rollback through a real app upgrade,
  macOS/Linux, WSL/UNC, signed helper distribution or independent security audit.

## Hosted validation after the authorized push

On commit `b320575`, [Windows tests](https://github.com/Skynettheone/herdr-session-hub/actions/runs/43084706399)
completed successfully. [CodeQL](https://github.com/Skynettheone/herdr-session-hub/actions/runs/43084706351)
completed successfully for Python and JavaScript/TypeScript. This records job
completion, not an assertion that no security alerts exist or an independent audit.
The first Windows workflow was rejected before tests because a YAML plain scalar
contained the pip `--only-binary=:all:` flag; a focused CI commit changed it to a
block scalar, and the corrected workflow passed.

Local package/install/uninstall verification is recorded in RELEASE_REPORT.md.
No production installation or original deletion was performed. The folder was not
a Git checkout at the start; the user later explicitly requested initialization,
logical commits and a push to their origin. Release publication remains separate.
