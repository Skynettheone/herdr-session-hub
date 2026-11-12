# Native continuation and updater acceptance — 2026-11-12

These checks used real installed provider CLIs and the real Herdr GUI on Windows,
with repository-local histories, configuration, app binaries and a dedicated
`HC_SESSION`. No production installation, real histories or cloud credentials
were test targets. The model server was a deterministic loopback fixture.

## Continuation

Each CLI created its own native session outside Herdr, in a project path containing
spaces and `é`. Its first assistant response contained a synthetic nonce. Hub
discovered that store without copying it. The actual **Continue in Herdr** button
opened a native terminal through Herdr's `tab.new` command and the normal audited
helper, with no injected active-probe bypass. A new `VERIFY_CONTEXT` request
contained no nonce. The fixture returned `CONTINUITY_OK` only when the native
request included the earlier nonce in conversation history.

| CLI | Version | Native ID retained | Original cwd / selected wrapper | Prior context and new response | Live guard |
|---|---|---|---|---|---|
| Claude Code | 2.1.322 | Yes | Yes | Passed | Selected CLI image detected |
| Codex | 0.164.0 | Yes | Yes | Passed | Native thread-writer lock detected |
| Pi | 1.1.0 | Yes | Yes | Passed | Native Node launcher detected |
| OpenCode | 1.3.17 | Yes | Yes | Passed | Selected CLI image detected |

Claude/Pi required their ordinary first-launch project trust; Claude also asked
to use the synthetic loopback API key. These were confined to disposable profiles.
Codex's Windows sandbox setup was dismissed; no Windows sandbox/security setting
was changed. No tools were requested by the fixture. Herdr's terminal API was
used for synthetic prompts and output inspection; GUI automation clicked Hub
controls. Native model requests were observed on the loopback server without
logging their bodies. Provider CLIs may independently check for updates.

OpenCode can leave committed frames in `opencode.db-wal` after the CLI exits.
Hub now captures DB and WAL under simultaneous Windows deny-write/delete handles,
validates SQLite salts/checksums/commits and projects a bounded in-memory image.
It never connects SQLite to the original DB or touches its SHM. Existing writers,
oversized/corrupt snapshots and changed fingerprints fail closed.

These checks establish native file/session continuity, Unicode cwd and the tested
launch chain. They do **not** establish real personal/company cloud-account
isolation, provider service availability, arbitrary hooks/extensions, all versions
or every authentication flow. Gemini continuation remains unverified; Copilot
continuation remains disabled because no working installed CLI was found.

## Real updater and backup rollback

Official archives were checked against their published manifests before execution:

| Version | Official archive SHA-256 |
|---|---|
| 0.1.14 | `c8a9da0e1b7c8ec85e2e131006797ba0fe0fc7793f3ab80e482f7622a5516b01` |
| 0.1.15 | `62ddf27ee9acc13d9b3421389817d1cabdc906c23f9ff1363f6cdbc8af3da39c` |

Sources: [0.1.14 manifest](https://releases.herdr.dev/app/0.1.14/manifest.json),
[current app manifest at test time](https://releases.herdr.dev/app/latest.json).
The [pinned native updater](https://github.com/herdrdev/herdr-app/blob/b22936225403f38f0e6f38dd2f2fe4b444a85988/src/update.rs)
supports `HERDR_RELEASES_URL`; only the disposable app used the loopback mirror.
Archive bytes/checksums were unchanged. Core binaries were physically copied
before testing, so the updater could not replace the production core executable.

1. Opened actual 0.1.14 with Hub in its personal namespace. Browsing worked and
   continuation was disabled with an unsupported-SDK warning.
2. Used actual `app.check_updates` / `app.update` to stage, verify and restart into
   0.1.15. All 39 checked personal mod/runtime/config/layout hashes survived.
3. Completed the four native continuation checks on 0.1.15.
4. Closed only the disposable workspace/app and restored the verified 0.1.14
   installation backup. An initial rename hit a Windows file-handle release
   delay; the harness now stops only its confined copied image and retries.
5. Reopened 0.1.14: selected sidebar layout persisted, browsing/preview/refresh
   worked, continuation was disabled, and native status had `errors: []`.
   All 42 checked files, including three encrypted Hub state files, retained
   their pre-rollback hashes before further user-invoked refresh.
6. Repeated the real updater to return to 0.1.15; selected layout persisted and
   native status again reported `errors: []`.

Backup rollback was tested; Herdr has no claimed automatic downgrade button.
This does not establish compatibility with future API changes. The exact 0.1.15
launch gate remains, and unknown state schemas are refused.

## Sidebar and reproduction

History's Dock button uses supported `layout()`, compare-and-create
`writeTextFile`, `layout.switch/show/select` and `closeOverlay`. It creates a new
personal layout around the complete original tree. Existing layout files and
shipped mods remain unchanged. An existing Hub is revealed rather than duplicated.
The default install remains `place=none`, requiring explicit user docking.

Genuine unmodified captures: [native sidebar](screenshots/sidebar.png) and
[rolled-back disabled continuation](screenshots/rollback-disabled.png). They show
only disposable synthetic histories. Existing light/community-theme captures
remain separate visual evidence; theme coverage is not exhaustive.

Manual harnesses are `tests/native_lab_server.py`, `native_lab_runner.py`,
`native_lab_observe.py` and `herdr_update_lab.py`. They are excluded from ordinary
CI execution. Use a new `.dev` test root, checksum-verified official binaries,
explicit disposable profiles and separate `HERDR_APP_HOME`/`HC_SESSION`/HOME/XDG
directories. The updater harness deliberately refuses an existing prepare target.
It expects the prepared fixture under `.dev/native-lab`; it is an acceptance
harness, not a production installer or turnkey cloud-authentication test.
