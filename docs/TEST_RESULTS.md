# Test results — 2026-11-12

This is a Windows development candidate. The following evidence supersedes
previous pending-continuation/updater notes. Production configuration was not an
installation target; no real user transcript was used or deleted.

- Python regression suite: 46 tests passed in 25.339 seconds; the subsequently
  added persisted-WAL writer-exclusion regression also passed (47 total tests).
  The final bundle build repeats the full suite.
- Native-host panel suite: 10 groups passed, including async search/refresh races,
  error paths, separate panes, focused shortcuts, catalog artwork and safe sidebar
  layout creation/reveal.
- Ruff 0.17.4 correctness checks (`F`, `E9`): passed.
- Native GUI: real search, filters, preview, settings, multiple panes, 420px narrow
  navigation and dark/light/custom-community themes passed the recorded smoke
  checks. Exhaustive controls in every theme remain unverified.
- Four primary native CLIs: actual Hub-button continuation restored original
  native IDs/cwd/selected profiles and prior context, followed by a new
  `CONTINUITY_OK` response. Active ownership was detected for all four.
- Real Herdr updater: 0.1.14→0.1.15, backup rollback to 0.1.14 and re-update passed.
  39 mod/config/layout hashes survived update; 42 including encrypted Hub state
  survived rollback. Unknown-SDK continuation was disabled while browsing worked.
  Native status reported `errors: []` on restored and re-updated versions.

See [NATIVE_ACCEPTANCE.md](NATIVE_ACCEPTANCE.md) for versions, isolation, method,
archive checksums, native screenshots and limitations. The model backend was a
loopback fixture; cloud-account personal/company isolation was not tested.
Gemini continuation remains unverified; Copilot has no usable installed CLI.

Regression coverage includes 10k records, Unicode/long paths, sparse >1 GiB files,
malformed/partial JSONL, compressed/concatenated/corrupt Codex rollouts, duplicate
identities, shared-profile FTS privacy, cross-chunk AND, explicit trust, executable
version drift, source hashes, WAL checksums/commits/locking, atomic state recovery,
interrupted schema updates, metadata encryption/tampering/conflicts and disabled
dangerous operations. A 10k-record list/search page took 0.183 seconds in the local
46-test run; this is a sample, not a performance guarantee.

## Hosted CI

On pushed commit `57e2c4c918a2544db5bdfa37b1ed68d9d3fb9d02`:

- [Windows tests](https://github.com/Skynettheone/herdr-session-hub/actions/runs/43134090322): success.
- [Combined CodeQL](https://github.com/Skynettheone/herdr-session-hub/actions/runs/43134094615): success.

Two earlier queued runs had zero jobs and no downloadable logs. Fresh manual
dispatches completed successfully. These results cover that exact commit;
final-change CI results are recorded below after the source push. CodeQL job
completion is not a claim of no alerts or an independent security audit.

CI remains one relevant-change Windows fixture/lint/panel job and one main-branch
combined CodeQL job, with cancellation of stale runs. No deployment or publication
job exists. Installed-SDK/GUI, packaging and install smoke are local release checks.

## Remaining release gates

Cloud-account isolation, Gemini continuation, exhaustive real-GUI controls,
mixed-build active ownership, future Herdr versions and independent security
review remain open. Original deletion, native transcript migration and remote
sync are deliberately unavailable. macOS/Linux, UNC and WSL are unsupported.
`releaseReady=false`; source tests and a checked development bundle do not imply
a production release or authorize installation/publication.
