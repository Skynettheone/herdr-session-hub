# Security and privacy design requirements

> Threat model: local agent transcripts can include passwords, token values, private code, customer data, prompt injections and executable strings. Herdr GUI mods are trusted (not sandboxed), so they are high-impact local code.

## Must-haves
- No telemetry, tracking, automatic network requests, or data export by default.
- Explicit, narrow roots for each provider/profile; never scan `auth.json`, credentials, token caches, `config.toml`, OAuth artifacts, or unrelated files.
- Escape control characters and markup in transcripts; display them as untrusted text, never evaluate or execute them.
- No shell interpolation for resuming; use argv arrays and verified executable/cwd. Handle Windows quoting, path traversal, reparse loops, UNC paths, hardlinks and symlinks.
- Read-only original transcripts for indexing and preview.
- Bounded IO and file sizes; incremental parser tolerates partially written JSONL without corrupting it.
- Privacy-aware full-text index: opt-in, local-only, file permissions, exclusion rules, clear/rebuild, no silent raw transcript logging.
- Custom aliases, archive flags and user preferences stay in Hub-owned metadata, not in source transcripts.
- Deletion of originals requires supported adapter operation, backup snapshot, explicit typed confirmation, active-session guard, complete audit of intended targets, recovery test and undo where feasible. Default disabled.
- Export/import requires clear preview, user selection, encryption when data leave machine, signature/integrity checking, versioned manifests, secret-exclusion filters and no credentials.
- Sync preserves source versions and conflicts (never overwrite one user's live transcript with another's); cannot promise universal native resumption of imported transcripts.
- No remote network access unless user explicitly configures sync destination and authorizes operation. Secret keys are not stored in public repo.
- Provide release hashes, reproducible builds or documented verification commands where practical; dependency/license scanning and GitHub code scanning CI.
- Normal-user install, no admin requirement, no modification to Herdr executable.

## Test attacks
- malicious transcript containing `; rm -rf`, PowerShell metacharacters, `$(...)`, newline, U+202E, enormous JSON line, binary file and symlink to secret outside roots.
- `.claude-work` with different account; show profile label and don't fall back to personal when work missing.
- active CLI writing to JSONL, simultaneous refresh, missing project directory, deleted CLI binary, stale cwd.
- damaged index and crash during backup/export/import; clear cache and rebuild preserving originals.
- encrypted export with wrong key, truncated data, conflicting session native IDs and profile mismatches.

## Reviewer checklist
- Check subprocess APIs and arguments; network code locations; dependency lockfile; ignore paths; what is persisted; whether private content leaks into logs, screenshots, GitHub issues, or previews.
- Disclose that this is a trusted mod and users should review source before installation.
