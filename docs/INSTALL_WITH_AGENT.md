# Install Session Hub with your agent

Paste this into an agent running in Herdr:

```text
Read ~/.config/herdr-app/AGENTS.md, then add this mod:
https://github.com/Skynettheone/herdr-session-hub
Follow its RECIPE.md and preserve my existing layouts, shortcuts and provider histories.
```

## What the agent must do

1. Read the installed Herdr guide/SDK, `RECIPE.md`, this guide, the matching
   platform's installer and all runtime files before changing anything.
2. Explain the access: Hub runs a local Python helper, reads explicitly selected
   session roots, writes its own encrypted state, and can start a verified provider
   only on an explicit continuation request. The mod/helper has no HTTP client;
   native providers may use their own hooks and network. Linux/macOS use the OS
   key store for Hub's own encryption key.
3. Check the compatibility table in README. Keep unsupported continuation,
   original deletion, native restore and remote sync disabled. Do not remove
   guards or experimental labels. Version 0.1.0 stable is Windows x64 only;
   macOS/Linux packages remain experimental with native continuation disabled.
4. Use a matching verified bundle and independently compare its external ZIP
   checksum with a trusted receipt. Windows 0.1.0 assets are published at the
   [pinned release](https://github.com/Skynettheone/herdr-session-hub/releases/tag/v0.1.0).
   Use its Windows ZIP and SHA256SUMS.txt. Experimental POSIX bundles remain
   source-build only; guidance is in CONTRIBUTING.md. Do not invent an asset or
   gallery URL, or pipe an unreviewed network script into a shell.
5. A review/preparation request is not permission to install in production. Use
   an isolated app home for that request. If installation itself was authorized,
   explain the exact target and use the installer; do not copy only the mod.
   Existing unrelated files named `mods/session-hub` are a name conflict: stop
   and resolve it with the user. Do not overwrite them or Herdr's shipped mods.
   An existing genuine Hub install can be upgraded with its backup procedure.
6. Use `scripts/install.ps1` on Windows or `scripts/install.py install` on the
   matching POSIX target. The required production switch is explicit. Dependencies
   install from the bundle's hash-locked offline wheelhouse into a separate runtime.
   The installer runs an isolated `herdr-app check` before replacing the mod.
7. Open `session-hub` in Herdr. Let the user choose profiles/history roots; do not
   search the home directory or sign in on their behalf. Click Dock only when
   requested: it creates a new personal layout copy beside Files/Changes.

The user's existing layouts, settings, shortcuts, provider stores and authentication
must remain intact. Never enable content indexing, accept a project-trust notice
or enter an authentication flow without the user's own instruction/handling.

## Checks and rollback

Verify installed helper import, the native panel and its disabled states. A
one-render SDK check is not full GUI or native session-continuation acceptance.
Do not describe macOS/Linux continuation as verified: those native desktop tests
are still pending. The source repository has tests and the precise evidence.

Upgrade backups, interrupted-install receipts and uninstall instructions are in
[the user guide](USER_GUIDE.md). Default uninstall retains Hub state; explicit
purge targets only Hub-owned data. Provider originals are never uninstall targets.
