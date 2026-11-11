# Implementation security review — 2026-11-12

Scope: local source review and synthetic adversarial tests. This is the
implementer's review, **not an independent audit or a certification**.

## Findings corrected during implementation

- Windows GUI-subsystem native checks are now awaited through ProcessStartInfo
  with ArgumentList and a timeout. Direct PowerShell invocation could otherwise
  continue with a stale exit code and move a staging folder before check finished.

- Cross-process Windows state lock initially touched a byte before acquiring its
  lock; acquisition now locks beyond EOF without reading another holder's byte.
- Corrected stdlib zstd parameter usage and replaced multi-frame replay with a
  streaming, window/ratio/output-capped implementation. Truncated/corrupt input
  fails safely; oversized lines are skipped without retaining them.
- Duplicate native IDs inside one config store now disable launch. Shared physical
  transcripts retain explicit targets; separate stores retain separate identities.
- Provider configuration edits invalidate applicable records/trust/version results;
  a record cannot resume through a different provider's executable.
- Version checks now retain executable/launcher fingerprints; replacing a binary
  requires a new check. Unrecognized Herdr version disables terminal launch.
- Clear-index also clears displayed coverage and replaces the accessible encrypted
  previous backup. DPAPI corruption is never silently reset.
- Recovery validates schema and SQLite integrity, holds the normal state lock,
  and preserves damaged evidence. Interrupted swaps leave old state recoverable.
- Account credential/routing environment variables are dropped before native
  provider launch/version checks. Only explicit directory overrides are restored.
- Portable import validates authenticated schema/size/types. Matching UUID alone
  never binds a foreign source; explicit annotation linking preserves local backups.

## Verified controls

- No network/fetch implementation in shipped mod/helper. Public network requests
  during development were limited to requested upstream research, package wheels
  and package-name/version advisory queries. No history/credential upload.
- Discovery uses read-only file modes. OpenCode uses `mode=ro&immutable=1`, refuses
  WAL and checks before/after metadata; it never runs SQL writes on a source.
- Tests compare synthetic provider source hashes before/after preview, search,
  refresh and metadata changes. OpenCode tests also compare directory listings.
- Credential filenames, arbitrary shells, relative/UNC paths, reparse points,
  hardlinks and invalid native identities are rejected. Text is plain native text.
- No provider auth files are opened by Hub. Test data and screenshot histories
  are synthetic. Runtime paths/state/research are excluded from release inputs.
- DPAPI local state and actual PyCA AES-GCM/scrypt round-trips, wrong passwords,
  tampering/truncation, conflicting metadata and interrupted migration were tested.
- Native process arguments are arrays with `shell=False`; no bypass-permission
  flags are added. Original deletion/native import/remote sync reject explicitly.

## Dependencies

Pinned Windows x64 wheels: cryptography 50.0.2, cffi 2.1.1, pycparser 3.12.
Hashes are in requirements-windows.lock. The OSV batch query returned **no reported
advisories for those exact package versions** on the review date. This is not a
complete audit of Python, SQLite, OpenSSL, Herdr or provider dependencies. Wheel
licenses/notices are retained. Builds/installations verify lockfile hashes offline.

## Residual risks / unavailable operations

All same-user code can replace a trusted mod/helper or race path checks; this is
not a local adversary sandbox. DPAPI does not protect against the logged-in user,
malware in that account or process-memory capture. Redaction is heuristic. Metadata
titles are content too. Local encrypted backups can remain in filesystem/cloud
snapshots after clear/uninstall; no secure erase claim is made.

Active detection intentionally over-blocks and is not proof of ownership absence
for renamed/custom provider builds. Precise native locks/registry integrations
remain a release gate. Actual provider continuation, account separation and update
persistence are not verified. Imported native transcripts, destructive original
operations and remote endpoints are not implemented. No source data was deleted
or production mod installed. The user later explicitly authorized source commits
and a push to their GitHub origin; no GitHub Release or gallery publication was
performed.
