# Implementation security review — 2026-11-12

## POSIX port assessment

Preserved Windows DPAPI, source-sharing and continuation gates. Reviewed new
boundaries: fixed Hub-only Keychain/Secret Service namespace, key material kept
out of argv/files/logs, missing-key refusal, random AES-GCM nonces/root-bound AAD,
private state modes, fsync/atomic writes, flock, native binary/Node targets,
names-only ownership and cooperative SQLite byte-range locking. No provider
credential, transcript mutation or runtime HTTP client was added.

Review added the SQLite SHM deadman-switch reader lock so the last provider
connection cannot replace/unlink a held generation. A real cross-process Linux
test closes that connection during the snapshot and verifies retained identity.
Keychain creation now verifies exact read-back before saving state. POSIX
installation initially generated verifier bytecode in its source bundle; fixed
loading preserves the verified bundle, with repeat-install regression coverage.
Hosted tests exercised actual macOS Keychain and Linux Secret Service. Shared
fixture vaults exist only in tests; runtime has no test-mode/fallback switch.

This is implementer review, not an independent audit. POSIX source locks are
advisory and version/VFS-specific; missing source SHM and unknown ownership fail
closed. No additional desktops exist for native GUI/context acceptance, so POSIX
continuation and production readiness remain disabled. Intel macOS has no pinned
crypto wheel. CI failures exposed YAML quoting and symlink-alias test expectations;
these were fixed, not hidden with skipped OS jobs. See PORT_ACCEPTANCE.md.

Final privacy review found command detection could resolve a PATH alias to a
credential-named file and inspect its binary header. It now rejects those names
before any open, matching the history-source boundary. A sentinel regression
forbids the open itself. Final platform CI and CodeQL passed on `4b32d18`.

## Package and installer follow-up

Release verification now rejects incomplete/empty/duplicate/unsafe manifests,
missing or altered runtime files, unexpected payloads, reparse/hard links and
private development files, with bounded reads/counts. The builder validates both
staging and extraction; installation validates before target writes. Six new
adversarial package tests passed with actual Windows file/directory links.

Same-version upgrades previously rebuilt the old mod's runtime before validating
the new mod. Unique runtime directories now preserve rollback environments.
An exclusive installer lock serializes upgrades. Failure injection after backing
up the mod proved the final-swap failure restores old runtime.json and a working
old helper. Unresolved power-loss receipts and held installer locks refuse new
installs. Source bundle, layout/key/provider sentinels remained unchanged.
No publisher key or independent human audit is available; hashes do not establish
publisher identity. Review scope remains trusted same-user code, not an adversarial
local-user sandbox. See PRODUCTION_READINESS.md for current claim boundaries.

Scope: local source review and synthetic adversarial tests. This is the
implementer's review, **not an independent audit or a certification**.

## Completed manual follow-up

The user requested manual review instead of Daybreak. Reviewed boundaries: native
process argument construction and environment routing; untrusted JSONL/Gemini
replay/SQLite WAL; path/reparse/hard-link handling; DPAPI/atomic state and recovery;
profile trust/FTS consent; encrypted portability; install/uninstall scope; runtime
network behavior; dependency locks and the licensed native-header adapter.

| Finding | Resolution and evidence |
|---|---|
| P1: backup copy could truncate an unrelated hard-linked file | Backup now atomically replaces its own directory entry. A real hard-link regression proves unrelated source bytes remain unchanged. |
| P2: bundle import accepted arbitrary filenames/hard links | Import/export require `.hsh`; credential names are rejected before reads or passphrase prompts; linked imports are refused. |
| P2: imported aliases could bypass the normal secret filter | Import linking and export use the same alias normalization/redaction; regression proves the synthetic secret does not persist or re-export. |
| P2: uninstall checked links only down to the selected home | Every ancestor is now checked to the drive; an actual directory-link dry-run is refused without modifying the sentinel. |
| P2: profile JSON could add trusted projects or turn the string `false` into content opt-in | Same-config saves preserve recorded trust; changed configurations reset trust; enabled/content require JSON booleans. Regression rejects forged trust/version and malformed consent flags. |
| Reliability: authenticated non-object bundle JSON could raise an uncaught attribute error | Schema/object validation now fails with the normal safe error. |

No unresolved exploitable defect was identified within this reviewed scope after
the fixes and stated regressions. This is not a claim of exhaustive security.
Native providers remain trusted programs and may load their own configuration,
hooks or network after user-requested launch. A trusted mod or compromised Windows
account is outside Hub's security boundary. DPAPI protects disk state, not live
process memory/pagefiles/crash dumps. Native active-owner probes remain conservative.

The [OSV package-version API](https://google.github.io/osv.dev/api/) returned no
listed advisories for cryptography 50.0.2, cffi 2.1.1 and pycparser 3.12 on
2026-11-12. Only those public coordinates were sent. This does not replace review
of bundled native dependencies or establish future safety. Runtime indexing and
browsing have no network client; the loopback/cloud clients exist only in manual
acceptance harnesses or separately installed native provider CLIs.

## Native acceptance review follow-up

Both focused Standards and Spec reviewers found no remaining actionable defect
in the final fixes. A P1 snapshot race was corrected: DB/WAL reads now hold
simultaneous Windows deny-write/delete handles, including actual bounded reads.
Real SQLite fixtures prove existing writers are refused, new writers are blocked,
persisted WAL commits survive projection and source bytes stay unchanged.
Unexpected Toolhelp enumeration termination now means unknown ownership; only
ERROR_NO_MORE_FILES establishes exhaustion. Renamed CLI basenames participate
in image identity checks, while Claude Desktop does not masquerade as the CLI.
Missing Node command-line visibility also means unknown, blocking continuation.

Codex 0.164's cooperative writer lock was observed held by the real resumed CLI.
All four primary native tests detected live ownership. This does not establish
mixed-build ownership or account isolation; selected-image/Node guards remain
conservative. No credential registry is read by Hub. Native context and updater
results are in NATIVE_ACCEPTANCE.md and supersede earlier unverified notes below.
The manual loopback harness serves only allowlisted release/model routes and
logs booleans/counts, never request bodies. It is not part of mod runtime or CI.

Docking uses compare-and-create for a new personal layout and preserves the
existing tree/files. Actual update/rollback retained 42 checked files. No production
installation, original deletion, credential transfer or release publication occurred.
Latest combined CodeQL on `1c104dc` completed successfully; the repository alert
API reported **0 open code-scanning alerts** afterward. That is a point-in-time
scanner result, not proof of absence of vulnerabilities or an independent audit.

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
- Discovery uses read-only file modes. OpenCode uses a private, checksummed read-only snapshot and committed-WAL
  projection under Windows deny-write/delete handles. Active writers are refused;
  no SQL writes run on a source.
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
remain a release gate. Tested native continuation and updater evidence is in
NATIVE_ACCEPTANCE.md and FOLLOWUP_ACCEPTANCE.md; distinct-account identity
separation remains unavailable with the single real account. Imported native transcripts, destructive original
operations and remote endpoints are not implemented. No source data was deleted
or production mod installed. The user later explicitly authorized source commits
and a push to their GitHub origin; no GitHub Release or gallery publication was
performed.

## Follow-up findings and remediation

Review discovered a shared-source FTS privacy bug: an opted-out profile could see
content matches from an opted-in profile sharing the same file. Content hits now
require the current target's enabled state, opt-in, approved root and exclusions;
metadata search remains separately available. Regression verifies both targets.

Recovery previously renamed current state away before replacement was durable.
It now atomically preserves encrypted evidence and keeps current state in place
until replacement succeeds. A missing current file with an existing backup refuses
silent empty initialization. Failure injection and offline recovery tests pass.

Keep-local now leaves absent local annotations absent. Partial record-budget and
oversized coverage is explicit, including old rows whose source identity changed.
Copilot subagent events are rejected before either cwd or text is extracted.
Gemini replay checks total projected messages, not only physical journal records;
full-file replay prevents indexing text that later patches removed. Greater-than-
budget/malformed Gemini sources disable launch and expose metadata-only fallback.

These earlier regression checks alone do not establish native continuity. The
later native acceptance results above are limited to the tested CLIs and profiles. The new source review is separate from CodeQL and is not an
independent third-party security audit. See CODE_REVIEW.md.

## Native-form and search usability follow-up

Source tasks df50a84 and d0b19d5 add draft/UI validation, fixed existing IDs,
provider-switch draft clearing, explicit native field focus and clearer progress.
Filesystem/profile consent validation remains in the helper. Manual review found
no new network, shell, credential or original-history write path. User-controlled
Pi indexing processed only the opted-in synthetic source; six other profiles
stayed Off and all other providers had zero indexed bytes. Original and preserved
native-file hashes remained unchanged. Native form/search evidence and cleanup
status are in FORM_ACCEPTANCE.md. Both Windows CI and combined CodeQL passed on
d0b19d5; no independent audit is claimed.

## Usage follow-up

The Usage change adds no runtime network, credential reader, shell string,
provider launcher or original-history write. Numeric/model/time-only caching
uses the existing DPAPI/atomic state namespace and is excluded from portability.
Current profile roots/exclusions/enablement reauthorize cached hits. Missing or
changed discovery scope cannot silently establish complete zero usage.

Separate standards/security and spec reviewers found six accounting/coverage
issues, including oversized JSON integers, Gemini rewind/budget handling and
upstream model qualification. All were fixed, regression-tested and follow-up
resolutions confirmed. USAGE_REVIEW.md keeps the axes and findings separate.
This is implementer-team manual/agent review, not an external human assessment.
CI, native controls, approved cache/rate removal and unchanged originals are
documented in USAGE_ACCEPTANCE.md. Locked dependencies are unchanged.
