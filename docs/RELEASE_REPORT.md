# Release preparation — 2026-11-12

Classification: **0.1.0-dev, Windows x64 development candidate**.
`releaseReady=false`; this is not an approved production/gallery release.

## Local validation

- Python helper and native panel behavior tests pass; see TEST_RESULTS.md.
- Native `check` is awaited with its actual Windows process exit code.
- Offline installer smoke passed after correcting GUI-subsystem process waiting:
  first install, second-install backup, uninstall dry-run, normal uninstall with
  state retained, explicit Hub purge, and unchanged hashes for layout/key/provider
  sentinels. All targets were disposable directories under this repository.
- Provider originals and production Herdr configuration were not installation
  targets. No GitHub Release or gallery listing was created.
- GUI automation was stopped by the user. Remaining native visual/theme and
  continuation acceptance gates are explicit in FEATURE_STATUS.md.

## Bundle contents and verification

`scripts/build-release.ps1 -AllowUnverified` produces an explicitly named local
development ZIP and SHA-256 sidecar under `dist/`. It includes mod/helper source,
native SVG assets, tests, scripts, documentation, the genuine initial-render
preview and the three locked offline dependency wheels. Each payload file has a
SHA-256 entry in `SHA256SUMS.txt`. Source state, user paths/runtime.json, research
repositories, environments, SDK-generated declarations and provider histories
are excluded. No `layouts/` directory is submitted as a mod.

The completed local bundle is
`herdr-session-hub-0.1.0-dev-windows-x64-20261111190747.zip` (UTC build suffix),
4,220,075 bytes. Both the staged payload and a fresh ZIP extraction passed the
manifest verifier: **67 files**, no development state/auth/runtime config.
SHA-256: `6e49ebf0faf1299f64f0ff29540f93ebb2a4aa020d4df97a3645b09ca0000dee`.
The sidecar and this final verification entry are external to the ZIP to avoid
a checksum/report cycle. Bundles remain local; they were not published as releases.

Run `python scripts/verify-package.py <unpacked-directory>` before installation.
The sidecar detects accidental damage; it is not an independently signed release.
Full native update/rollback acceptance and a signing strategy remain open.

Git is initialized on `main` with the user-specified origin. Logical conventional
commits are authored with the existing Git identity, without assistant names or
authorship trailers. The user subsequently authorized pushing `main`; this does
not authorize a production installation or a GitHub/gallery release.

The authorized source push succeeded. Windows CI and both CodeQL language jobs
passed on the corrected CI commit; direct run links are in TEST_RESULTS.md.
