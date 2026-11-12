# Security

Session Hub is trusted native-mod code, not a sandbox. Review source before
installing it. Report a vulnerability privately to the repository maintainer;
do not attach real transcripts, credentials or diagnostic screenshots. Use the
repository's private vulnerability reporting channel if enabled; never post
sensitive evidence in a public issue.

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

Experimental POSIX ports use PyCA AES-GCM and a random Hub-only key held in macOS
Keychain or Linux Secret Service. No plaintext-key file, environment-secret or
unencrypted fallback exists. Missing keys never initialize over existing state.
New state directories/files use 0700/0600, state writes fsync both data and parent,
and flock serializes operations. POSIX local-mount checks reject network/unknown
filesystems. Native continuation remains disabled there pending GUI/context tests.

Native launch uses argument vectors, verified original cwd, explicit config-home
environment mappings and exact researched versions. It strips inherited provider
credential/routing variables without logging values. Environment-only enterprise
authentication is therefore unsupported. Native CLIs can still run their own
hooks, extensions and network operations after an explicit resume request. Trust
the project and authenticate the intended profile through its native tool first.
No settings, permissions or approval flags are weakened by the launcher.

OpenCode captures bounded DB/WAL bytes under simultaneous Windows deny-write/delete
handles, validates committed WAL frames and projects them in memory. Open writers
are refused; no SQLite connection or SHM write targets the source. A future schema
or corrupt DB can disable the adapter. DPAPI
state is Windows-account-bound. Portable metadata uses PyCA AES-256-GCM, fixed
scrypt parameters (N=131072, r=8, p=1), fresh salt/nonce, authenticated header,
size limits, strict schemas, checksum and explicit conflict handling. There is
no remote sync, native transcript migration, credential export or original delete.

POSIX snapshots use cooperative SQLite DB/WAL/SHM byte-range locks and the SHM
deadman-switch reader lock. Missing SHM is refused, never created. An unrelated
non-cooperating process can still mutate a source; these advisory locks are not
Windows mandatory sharing or a local-user adversary sandbox. Source fingerprints,
WAL checksums and generation checks remain in force. Process checks use names,
not other processes' full command lines; Node ownership intentionally over-blocks.

Native continuity passed for the five tested CLIs; distinct company-identity
isolation remains unverified. Active checks can over-block, especially Pi/Node;
uncertainty disables continuation. Path checks have the usual same-user filesystem
TOCTOU boundary. Manual review and fixes are documented; no independent human
audit is claimed. Redaction is heuristic, not a promise that arbitrary text
contains no secrets. No project-built signed executable is shipped.

Installation verifies complete manifest-listed payloads before target writes,
uses hash-locked offline wheels and prepares separate runtimes for rollback.
Ordinary failed final swaps restore the old mod; unresolved interrupted-install
receipts block another install. SHA-256 checks are integrity checks, not publisher
authentication: obtain the ZIP and expected hash from a trusted maintainer channel.

See [the security review](docs/SECURITY_REVIEW.md),
[the feature status](docs/FEATURE_STATUS.md), [current readiness](docs/PRODUCTION_READINESS.md)
and [the user guide](docs/USER_GUIDE.md).
