# Herdr Session Hub 0.1.0

The first stable release for **Windows 11 x64**. Requires **Herdr 0.1.15**, **Python 3.14 x64** and **PowerShell 7**.

## What's included

- A collapsible **History / Usage** panel beside **Files** and **Changes**, using Herdr's icons and theme colors.
- Local history discovery, search and previews for Claude Code, Codex, Pi, OpenCode and Gemini.
- Native continuation with the selected profile and original project folder.
- Token and cache charts, recorded cost estimates, date filters and model/project breakdowns.
- Reversible names, archive and removal stored in Hub metadata. Original histories stay untouched.

## Install on Windows

1. Download the **Windows ZIP** and **SHA256SUMS.txt** from this release's Assets.
2. Check the ZIP's SHA-256, extract it and open PowerShell 7 in the extracted bundle folder.
3. When you are ready to install, close Herdr and run:

```powershell
pwsh -NoProfile -File scripts/install.ps1 -AppHome "$HOME/.config/herdr-app" -InstallProduction
```

4. Reopen Herdr, then open the panel:

```powershell
herdr-app do mod.open --name session-hub
```

Click **Dock** to add History beside Files and Changes in a new personal layout copy. In **Settings > Profiles**, add the history folders you want to browse, then **Refresh**. Switch between **History** and **Usage** in the same panel. Conversation indexing starts Off.

[Full setup, upgrade and uninstall guide](https://github.com/Skynettheone/herdr-session-hub/blob/main/docs/USER_GUIDE.md)

## Support and known limits

- Stable support covers Windows x64 and the [verified provider versions](https://github.com/Skynettheone/herdr-session-hub#compatibility). Unknown versions, active sessions and ambiguous histories cannot continue.
- macOS and Linux remain **experimental**, with native continuation disabled. No macOS/Linux ZIP is included in this release.
- Usage shows recorded local activity and known API-equivalent costs. It does not provide subscription bills or live account quotas; missing data and unknown prices stay visible.
- Duplicate Gemini snapshots cannot continue. Copilot history is experimental, and its continuation and persisted Usage are unavailable.
- Remote sync, native transcript restore, original-history deletion and network/WSL history roots are unavailable. Distinct company-account isolation remains unverified.

[Compatibility and privacy](https://github.com/Skynettheone/herdr-session-hub#compatibility) | [Tests and security review](https://github.com/Skynettheone/herdr-session-hub/blob/main/docs/RELEASE_REPORT.md)

## Verified download

Windows ZIP SHA-256:

```text
bb9bd3e13794165d1fb6d29540f782ff20f00bbe6c8ecf7a2a27f8083c9f2309
```

The ZIP is unchanged from the verified release build. Attached checksum files and downloadable notes preserve the original publication snapshot; this page contains the current wording and installation guidance.
