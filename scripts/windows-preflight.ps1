# Herdr Session Hub Windows preflight: read-only diagnostics.
# Does not read transcript contents, credentials or send data to network.
# Run: pwsh -NoProfile -File .\scripts\windows-preflight.ps1

$ErrorActionPreference = 'Continue'
Write-Output '=== Herdr Session Hub Windows preflight ==='
Write-Output "PowerShell: $($PSVersionTable.PSVersion)"
Write-Output "Windows: $([System.Environment]::OSVersion.VersionString)"

foreach ($exe in @('herdr-app','claude','codex','opencode','pi')) {
    $cmd = Get-Command $exe -ErrorAction SilentlyContinue
    if (-not $cmd) {
        Write-Output ("{0}: NOT FOUND" -f $exe)
        continue
    }
    Write-Output ("{0}: FOUND (path not shown to avoid leaking username)" -f $exe)
    try {
        if ($exe -in @('claude','codex','opencode')) {
            $version = & $exe --version 2>&1 | Select-Object -First 1
            Write-Output ("  version: {0}" -f $version)
        } elseif ($exe -eq 'herdr-app') {
            # Some releases may not expose --version; do not assume.
            Write-Output '  inspect the installed GUI version in Settings > About / changelog'
        } else {
            Write-Output '  version: check pi --help manually (flag varies by release)'
        }
    } catch {
        Write-Output ("  version probe failed: {0}" -f $_.Exception.GetType().Name)
    }
}

$roots = [ordered]@{
    'Claude default' = (Join-Path $HOME '.claude\projects')
    'Claude work candidate' = (Join-Path $HOME '.claude-work\projects')
    'Codex default' = (Join-Path $HOME '.codex\sessions')
    'Pi default' = (Join-Path $HOME '.pi\agent\sessions')
}
if ($env:CODEX_HOME) { $roots['Codex configured'] = (Join-Path $env:CODEX_HOME 'sessions') }
if ($env:CLAUDE_CONFIG_DIR) { $roots['Claude configured'] = (Join-Path $env:CLAUDE_CONFIG_DIR 'projects') }
if ($env:PI_CODING_AGENT_SESSION_DIR) { $roots['Pi configured'] = $env:PI_CODING_AGENT_SESSION_DIR }

Write-Output '=== Local candidate session directories (only counts, not content) ==='
foreach ($r in $roots.GetEnumerator()) {
    if (Test-Path -LiteralPath $r.Value -PathType Container) {
        $n = @(Get-ChildItem -LiteralPath $r.Value -File -Filter '*.jsonl' -Recurse -ErrorAction SilentlyContinue).Count
        Write-Output ("{0}: EXISTS; jsonl count: {1}" -f $r.Key,$n)
    } else {
        Write-Output ("{0}: NOT PRESENT" -f $r.Key)
    }
}

$herdrHome = Join-Path $HOME '.config\herdr-app'
Write-Output ("Herdr personal config: {0}" -f $(if (Test-Path -LiteralPath $herdrHome) {'FOUND'} else {'NOT FOUND'}))
if (Test-Path -LiteralPath $herdrHome) {
    foreach ($name in @('AGENTS.md','herdr.d.ts','gpui-kit.d.ts')) {
        $found = @(Get-ChildItem -LiteralPath $herdrHome -Filter $name -File -Recurse -ErrorAction SilentlyContinue).Count
        Write-Output ("  {0}: {1}" -f $name,$(if ($found -gt 0) {'FOUND'} else {'NOT FOUND'}))
    }
}
Write-Output '=== Done. Do not paste private paths or raw session contents into public issues. ==='
