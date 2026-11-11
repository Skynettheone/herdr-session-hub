# Security

Session Hub is trusted native-mod code, not a sandbox. Review source before
installing it. Report a vulnerability privately to the repository maintainer;
do not attach real transcripts, credentials or diagnostic screenshots. No public
repository or private reporting endpoint has been created by this implementation.

The helper opens only explicitly configured session roots and exact OpenCode
database paths. It skips credential filenames, reparse/symlink paths, hard links,
subagents and unrelated files. UNC/WSL traversal is disabled. Provider originals
are never changed by discovery, preview, search, alias/archive or import. No
provider CLI starts during those operations. CLI version checks are explicit.

All local Hub state, including first-prompt titles and opt-in FTS content, is
serialized from an in-memory SQLite DB and encrypted with Windows DPAPI before
atomic replacement. There is no on-disk plaintext SQLite journal. This does not
protect a compromised logged-in account or decrypted process memory. Clearing
content removes the accessible content index and encrypted prior backup, not old
filesystem snapshots or metadata titles.

Native launch uses argument vectors, verified original cwd, explicit config-home
environment mappings and exact researched versions. It strips inherited provider
credential/routing variables without logging values. Environment-only enterprise
authentication is therefore unsupported. Native CLIs can still run their own
hooks, extensions and network operations after an explicit resume request. Trust
the project and authenticate the intended profile through its native tool first.
No settings, permissions or approval flags are weakened by the launcher.

OpenCode's immutable read-only database mode refuses nonempty WAL data and checks
source stability. A future schema or corrupt DB can disable the adapter. DPAPI
state is Windows-account-bound. Portable metadata uses PyCA AES-256-GCM, fixed
scrypt parameters (N=131072, r=8, p=1), fresh salt/nonce, authenticated header,
size limits, strict schemas, checksum and explicit conflict handling. There is
no remote sync, native transcript migration, credential export or original delete.

Known release-blocking limits: provider context continuation has not been verified
end to end; process-name active checks can over-block (especially Pi/Node);
path checks have the usual same-user filesystem TOCTOU boundary; encrypted state
has not undergone independent security review. Redaction is heuristic, not a
promise that arbitrary text contains no secrets. No signed executable is shipped.

See [the security review](docs/SECURITY_REVIEW.md),
[the feature status](docs/FEATURE_STATUS.md) and [the user guide](docs/USER_GUIDE.md).
