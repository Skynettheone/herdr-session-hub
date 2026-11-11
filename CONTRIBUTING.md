# Contributing

Use Windows x64, CPython 3.14, Node 24 for tests, and Herdr 0.1.15. The mod itself
does not use Node, DOM, React, Electron or browser APIs. No Rust toolchain is needed.
Do not commit personal histories, runtime.json, SDK-generated files or state.

```powershell
python -m venv .venv
./.venv/Scripts/python.exe -m pip install --require-hashes -r requirements-windows.lock
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

For a GUI demo, `pwsh -NoProfile -File scripts/start-demo.ps1` creates only `.dev/`
histories. It sets `HERDR_APP_HOME`, `HC_SESSION=test-session-hub` and scratch XDG
paths. No production config is read or modified. Use the same variables for
`herdr-app status`, `shot`, and commands. Maximize the isolated window if launched
hidden. Native `check` covers one render only; interact with the panel as well.
Stop only this test core/app afterward, never a user's real core.

Prepare the three exact binary wheels under `.research/wheels/`:

```powershell
./.venv/Scripts/python.exe -m pip download --only-binary=:all: --require-hashes -r requirements-windows.lock --dest .research/wheels
pwsh -NoProfile -File scripts/build-release.ps1 -AllowUnverified
```

This deliberately creates a **development** bundle while `releaseReady=false`.
The release builder refuses a normal release until gates in FEATURE_STATUS.md
are closed. It excludes research sources, state, personal runtime config,
environments and transcripts. Windows x64 wheel hashes are not portable to
other Python/platform combinations. Test other targets before adding lockfiles.

Add fixtures for provider schema changes and re-probe native CLI help. Keep
discovery and migration separate. Preserve argument arrays and source-read-only
tests. Never replace unknown capability with invented success. Pane was studied
under AGPL-3.0; no Pane code may be copied into this MIT implementation. T3 ideas
were independently reimplemented, not translated/copied.

Use conventional commit messages, for example:
`fix(index): retain stale sessions after an interrupted refresh`.
Do not add assistant names or assistant-authorship trailers to commit messages.
No push, production install or publication is part of the development workflow.
