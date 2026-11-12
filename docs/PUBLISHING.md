# Release and gallery checklist

Current status: **[Windows 0.1.0 is published](https://github.com/Skynettheone/herdr-session-hub/releases/tag/v0.1.0)**
under the user's explicit approval. Linux/macOS remain **0.1.0-experimental.1**,
releaseReady=false, with continuation disabled and no attached stable-release
assets. Production installation and repository About/topic changes were not
performed. Future releases, gallery-setting changes and production installation
need separate authorization.

## Prepared release inputs

- README, RECIPE, genuine sanitized screenshots, licensed artwork and user guide.
- [Release notes](RELEASE_NOTES.md), changelog, compatibility and security policies.
- Exact source commit, passing relevant CI/CodeQL and Windows acceptance evidence.
- Windows stable offline ZIP, manifest and external SHA-256 sidecar; separately
  labeled experimental POSIX ZIPs are excluded from stable assets by default.
- [Release report](RELEASE_REPORT.md) with immutable artifact receipts and checks.

The installer uses a separate runtime, checks before replacing the mod, retains
upgrade backups and leaves original histories/layouts/keys intact. Tests and
build/audit material remain in source, outside the install ZIP. There is no
deployment workflow or automatic release publisher.

## Procedure for future authorized publications

1. Recheck the approved commit against the release receipts and current CI. If
   executable/runtime/installer bytes change, repeat the relevant checks and build
   new artifacts; do not overwrite receipts for old ZIPs.
2. Create the approved v0.1.0 tag and GitHub release using the reviewed notes and
   Windows stable ZIP/sidecar. Experimental assets need explicit inclusion with
   their experimental names and limitations; never rename them as stable.
3. Compare downloaded release assets with the approved receipts before advertising
   them. Update the README's unpublished status only after observing publication.
4. Add the herdr-mod topic/gallery listing only if separately authorized. Preserve
   the native mod-only repository shape, with no root layouts/ directory. A gallery
   listing is not an independent security audit or publisher signature.

Suggested repository description: A native Herdr History/Usage panel for local
agent sessions, safe continuation and recorded token/cost graphs.
Suggested topics after listing approval: herdr-mod, herdr, claude-code, codex,
opencode, pi-coding-agent, session-manager, developer-tools.

## Future compatibility

User mods remain separate from shipped Herdr files. New Herdr/provider versions
require installed SDK/help/source review and disposable acceptance before their
launch gates expand. macOS/Linux stable promotion requires native desktop tests
in PORT_ACCEPTANCE.md. Distinct enterprise identities, live billing, deletion,
native restore and remote sync do not become supported through a release label.
