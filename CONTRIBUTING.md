# Contributing

Use Windows x64, CPython 3.14, Node 24 for tests, and Herdr 0.1.15. The mod itself
does not use Node, DOM, React, Electron or browser APIs. No Rust toolchain is needed.
Do not commit personal histories, runtime.json, SDK-generated files or state.

```powershell
python -m venv .venv
./.venv/Scripts/python.exe -m pip install --require-hashes -r requirements-windows.lock -r requirements-dev-windows.lock
./.venv/Scripts/python.exe -m ruff check .
./.venv/Scripts/python.exe -m unittest discover -s tests -v
node --experimental-vm-modules --test tests/panel.test.mjs
herdr-app check mods/session-hub
# Reliable synchronous exit status on Windows:
pwsh -NoProfile -File scripts/check-native.ps1 -ModPath mods/session-hub
```

Windows hard-link tests require an ordinary desktop process outside restricted
agent sandboxes; they require no administrator account. Synthetic sparse files
exercise 50 MiB, 100 MiB and over 1 GiB histories without allocating their full
logical size. Tests also exercise actual DPAPI and authenticated encryption.

For a GUI demo, `pwsh -NoProfile -File scripts/start-demo.ps1 -Visible` creates only `.dev/`
histories. It sets `HERDR_APP_HOME`, `HC_SESSION=test-session-hub` and scratch XDG
paths. No production config is read or modified. Use the same variables for
`herdr-app status`, `shot`, and commands. Use `-Visible` for interactive tests; the default starts a hidden test window. Native `check` covers one render only; interact with the panel as well.
Stop only this test core/app afterward, never a user's real core.

Prepare the three exact binary wheels under `.research/wheels/`:

```powershell
./.venv/Scripts/python.exe -m pip download --only-binary=:all: --require-hashes -r requirements-windows.lock --dest .research/wheels
pwsh -NoProfile -File scripts/build-release.ps1 -AllowUnverified
```

This creates a **candidate install** bundle while `releaseReady=false`.
The release builder refuses a normal release until gates in FEATURE_STATUS.md
are closed. It excludes research sources, state, personal runtime config,
environments and transcripts. Windows x64 wheel hashes are not portable to
other Python/platform combinations. Test other targets before adding lockfiles.

Install payloads use a shared explicit allowlist: runtime, matching offline wheels,
platform installers, licenses, README/recipe and user guides. Tests, build tools,
audit documents, extra captures, starter prompts and development dependencies stay
in the source repository. The verifier rejects even manifested extra files.
The builder verifies staging and a fresh ZIP extraction. Install only from the
verified extracted bundle; the source checkout has no release manifest/wheelhouse.
For a disposable installation, choose an app home below the **bundle parent's**
`.dev` directory (for example `../.dev/session-hub-test`). Keep the bundle itself
unchanged so repeated verification succeeds. `tests/install-smoke.ps1` creates
its own disposable package and home, tests tamper refusal and upgrade rollback,
and never selects production. Installer SDK checks use the new runtime's own
scratch home. Power-loss recovery is documented in USER_GUIDE.md.

For POSIX development, use CPython 3.14 and the target's `requirements-linux-x64.lock`
or `requirements-macos-arm64.lock`. Only explicit target-matching binary wheels
are accepted. Prepare those exact wheels under `.research/ports/wheels/<target>`
using `pip download --only-binary=:all: --require-hashes -r <lock> --dest <folder>`
on that target (or pass pip's explicit platform/ABI options when cross-downloading).
Then prepare an **experimental** install bundle from the checkout:

```sh
python -I -B scripts/build-port-bundle.py --target linux-x64 --allow-unverified
python -I -B scripts/build-port-bundle.py --target macos-arm64 --allow-unverified
```

No production bundle is emitted by that script while native acceptance is pending.
The shared POSIX fixture suites inject memory-only keys through test code; runtime
does not have such a switch. `HUB_TEST_NATIVE_VAULT=1` enables the separate real
OS-key-store test only on a disposable desktop/CI account. It creates Hub-owned
synthetic entries; do not enable it casually on a person's normal desktop.
PORT_ACCEPTANCE.md records the remaining native acceptance and architecture limits.

Add fixtures for provider schema changes and re-probe native CLI help. Keep
discovery and migration separate. Preserve argument arrays and source-read-only
tests. Never replace unknown capability with invented success. Pane was studied
under AGPL-3.0; no Pane code may be copied into this MIT implementation. T3 ideas
were independently reimplemented, not translated/copied.

Use conventional commit messages, for example:
`fix(index): retain stale sessions after an interrupted refresh`.
Do not add assistant names or assistant-authorship trailers to commit messages.
No push, production install or publication is part of the development workflow.

CI runs one relevant-change job per port target: Windows x64, Ubuntu 24.04 x64
and macOS 15 arm64, with hash-locked runtime wheels. Shared lint and native-host
JS mocks run once on Windows. POSIX jobs run actual filesystem, process-lock,
installer and native Keychain/Secret Service checks.
Documentation-only pushes do not run it. CodeQL runs both languages in one job
on relevant main pushes or manually, avoiding duplicate PR/main security scans.
Stale runs are cancelled. Native SDK/GUI, install smoke and packaging are local
release checks; no automatic deployment/publication workflow exists.

Manual real-provider/updater acceptance is documented in
`docs/NATIVE_ACCEPTANCE.md`. Its loopback fixture, observer and updater harnesses
live under `tests/native_lab_*.py` / `tests/herdr_update_lab.py` and never run in CI.
Use disposable homes, explicit profiles and a separate core; never copy real
credentials. Keep the harness's serving routes allowlisted. Native requests may
contain synthetic history, so the fixture logs only booleans and counts.
