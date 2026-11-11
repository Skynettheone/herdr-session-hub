# Session discovery, update, and migration — implementation contract

Read `REFERENCE_IMPLEMENTATIONS.md` first. This document resolves the ambiguous word "migration": ordinary discovery should **not move a user's conversation to another app or rewrite the original**.

## Core model and identities

Each record should contain at least `provider`, `profileId`, `nativeSessionId`, `sourcePath/sourceDbIdentity`, `canonicalSourceIdentity`, `cwd`, `projectKey`, `title`, `createdAt`, `lastConversationAt`, `fileModifiedAt`, `status`, `resumeCapability`, `contentCapability`, `parserVersion`, and `fingerprint`. Keep secrets/credentials out of all records.

- `profileId`: locally defined user-facing identity, not an OAuth key. Preserve which account/profile launches a session, with explicit user selection.
- `canonicalSourceIdentity`: NTFS file ID when safely obtainable or normalized real path + stable source-native ID; track WSL filesystem separately. Duplicate profiles can reference the same physical transcript, so show one history entry with multiple resume targets where appropriate.
- Unique identity must include provider AND profile/native source; never identify a session solely by its title or native UUID.
- `projectKey`: derived from trustworthy recorded cwd / repository identity, not just encoded directory name. If ambiguous, mark `Unknown project`.
- Separate `lastConversationAt` from `fileModifiedAt`. Avoid claiming metadata bookkeeping marks a session as active work.

## Discovery pipeline

1. Enumerate explicitly approved roots and configured provider instances. Do not follow arbitrary junctions outside those roots.
2. Locate candidate sessions using provider-approved indexes/CLI list APIs where possible, else bounded JSONL scans. Detect compressed rollouts when supported.
3. Read minimal metadata first. Schedule expensive preview/full-text indexing separately. Use file identity, size, mtime and parser version to avoid repeat work.
4. Parse partial/live JSONL safely. Malformed/truncated records should not hide the entire provider; return partial results with diagnostic counts.
5. De-dupe by physical transcript identity and provider-specific native identity. Detect collisions and show selectable resume profiles.
6. Save atomic, versioned *Hub-owned* index. Never append to original provider transcripts or alter provider DB schemas.
7. UI: initial loading, progress, cancel, refresh, source counts, last scan, errors, stale/unavailable resumes, and a per-provider status.
8. Incremental or user-triggered refresh must work after onboarding and after Herdr restarts; no mandatory background polling to expose old history.

## Resume pipeline

1. User explicitly chooses a specific history record and profile/agent.
2. Validate source exists, trusted cwd, current CLI is installed, session not known active elsewhere, path within expected limits, and provider-specific ID syntax.
3. Build a command **argv array**, not a shell interpolation. Launch Herdr tab with original cwd; only pass approved environment mappings.
4. Label `Launching`, then `Continued`, `Not verified`, or `Failed`. A successful process start alone is NOT continuity verification. Verify native resume where possible without leaking conversation content or submitting test prompts to a real session.
5. Never accidentally start a new empty agent and claim it resumed the old one. If verification cannot be done safely, show `Unverified` with guidance.
6. Explicitly disable or require separate confirmation for a session currently active in another agent/terminal; don't use Pane's copy/fork workflow without a separate provider-specific audited implementation.

## Indexed full-text search

- Opt-in for full conversation content, with per-profile inclusion/exclusion. Metadata-only is the privacy-safe default.
- Stream/chunk input with bounded memory. For huge transcripts, continue indexing in batches and report incomplete coverage; no blanket 30-day cutoff.
- Ignore and never index credential files, environment exports or non-conversation agent artifacts. Embedded transcript text is untrusted data.
- Hub-owned cache must be clearable, encrypted at rest if sensitive content is persisted, and excluded from Git repositories/backups unless intended.
- Search does not mean export: no server/network calls. Never log searchable phrases or raw extracted text.

## Versioned upgrades

- Source parsers have version tags; detect installed provider version/format, opt into stable versions, and downgrade to metadata-only on unknown format rather than guessing.
- Hub index migrations are versioned and transactional: copy current state, validate new schema, atomically swap, and keep rollback path.
- Update of Herdr's app should not overwrite user-owned mod. API changes may require a mod update; test compatibility with the installed `.d.ts` and `herdr-app check` plus GUI smoke tests.
- New source files appear on user refresh; existing indexed records remain available during failed refresh, marked stale rather than erased.

## Optional native migration / sync

- Keep it separate from browsing. Document precisely whether a bundle contains **metadata only**, **sanitized excerpt**, or **complete native transcripts**.
- Portable bundles must have version, source profile/provider, integrity manifest, encryption via vetted library, preview/dry-run, conflict resolution, recovery path, and no secrets.
- Native transcript migration to another machine/account needs provenance checks, verified provider-supported restore, source/target CLI version compatibility and permission to touch company files. If not safely supported, disable it and report `unsupported`, not a fake success.
- A remote sync implementation must require explicit opt-in, endpoint authorization, safe transport and encryption, independent security review, and tests. No automatic copying between personal and company accounts.

## Acceptance tests inspired by real upstream bug reports

- Stale file mtime vs most recent conversational message timestamp.
- Codex `.jsonl.zst` files, missing decompressor, corrupted compressed input, excessive decompression ratio.
- Claude histories 50 MB, 100 MB and synthetic >1 GB: metadata visible, bounded preview, index progress and safe cancellations.
- Two different profiles with same native UUID: never combine; same physical session referenced by two profiles: one list item, two resume options.
- First scan, subsequent scan after new external session, repeated scan, interrupted scan; no duplicates and no silent missing history.
- Incomplete transcript while agent actively writes: no mistaken import/resume/mutation, no hard crash.
- Hub index schema v1→v2 upgrade with simulated power failure: old data recoverable.
- Profile-specific cwd with spaces, non-ASCII characters, drive letter/UNC, WSL root, symlink/junction loop.
- End-to-end one original session resume per provider with session ID and last user-visible context checked; run only on synthetic/disposable sessions.
