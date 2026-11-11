# Test and acceptance plan

## Mandatory validation
1. Pin/report actual installed Herdr GUI version, OS, provider CLI versions, config paths (not tokens).
2. Use synthetic sanitized JSONL fixtures for Claude, Codex and Pi; fixture/mock OpenCode CLI responses for schema changes. Never commit real user history.
3. Unit tests: stable session identity; project metadata; sorting; filters; aliases/archive; locale timestamps; pagination; partial/truncated JSONL; UTF-8 and Unicode; duplicate IDs across profiles; exclusion rules; broken symlinks/junction loops; invalid cwd.
4. Integration tests: all four agents detected; missing agent state; custom roots; profiles; refresh updates; read-only previews; full-text index opt-in, clear and rebuild; no source changes (hash checks).
5. Resume: Herdr `run('tab.new', {folder, argv, name})` using supported command shape; exact args, new tab, original cwd, same provider/profile, no command injection. Test spaces and Unicode cwd.
6. Session management: Hub alias/rename; archive/unarchive; index removal vs original deletion; confirmation, backup, failure rollback, active-session refuse.
7. Export/import/sync: encryption at rest for portable bundle; wrong key; missing/untrusted dest; conflicts; checksum errors; truncated archive; restore capability correctly indicated. No credentials synced.
8. Security: scan dependencies, misuse of exec, injection fixtures, file ACL, no network for index/search, test hidden malicious transcript.
9. Performance: 10,000 synthetic sessions; paginate UI, avoid blocking UI or rescanning on render. Record real metrics; set sustainable thresholds based on test machine and workload.
10. Upgrade: personal mod survives Herdr update; version drift degrades gracefully; reinstall idempotent, uninstall deletes only Hub state; rollback.
11. `herdr-app check <mod-folder>` must pass; manually test deferred UI actions, refresh and dialogs (check alone isn't sufficient).
12. Test on real Windows 11 with installed Herdr GUI and installed CLIs; optional CI on Windows/macOS/Linux. Do not claim cross-platform runtime support until tested.

## Release check
- `README` truthfully states tested providers/versions/OS and what remains experimental.
- `RECIPE.md` accurately documents actual implementation.
- `preview.png` is a real screenshot from running GUI, not a mock.
- Source includes `mods/session-hub/main.js` and `mod.json`, with no `layouts/` directory in gallery submission.
- GitHub repo topic `herdr-mod` set; LICENSE/SECURITY/CHANGELOG included; release checksum included.
- No actual user secret data in source, tests or assets.

## Pane/T3-inspired regression gates (must add synthetic fixtures)

1. **Windows Codex compressed rollouts**: old `.jsonl.zst` sessions are discoverable when installed Codex supports them; corrupt files fail safely; decompression is capped.
2. **Big Claude transcripts**: metadata discovery remains responsive on 50 MB, 100 MB, and synthetic >1 GB histories; preview stays bounded; no silent omission.
3. **Timestamp correctness**: distinguish last conversational message from file mtime; file appended with only bookkeeping must not become falsely recent.
4. **Repeated imports and refresh**: same source scanned 3 times produces one normalized record; source records unchanged; newly created session appears after user-triggered refresh.
5. **Provider-instance separation**: identical session UUIDs across two account profiles remain distinct; a physically shared transcript can expose multiple explicit resume targets without transcript copying.
6. **Native continuity**: process launch alone is insufficient; report `continued`, `unverified`, `failed` accurately and check last context on disposable test sessions.
7. **Migration/versioning**: versioned index upgrades recover from interruption; original source formats untouched and backed up only when explicit authorized native migration is requested.
8. **License provenance**: record imported third-party code/files, source commit, license and notices; no accidental use of Pane AGPL-3.0 code in MIT-only distribution.
9. **Partial discovery**: malformed/too-large/locked provider sources display skipped counts and diagnostics, not `No sessions found`.
10. **Active sessions**: never automatically launch concurrent writer for the same native conversation; preserve running sessions in other tools.
