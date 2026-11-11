[CmdletBinding()]
param(
    [Parameter(Mandatory=$true)][string]$AppHome,
    [string]$Python = 'python',
    [switch]$InstallProduction
)
$ErrorActionPreference = 'Stop'
$repo = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..'))
$targetHome = [IO.Path]::GetFullPath($AppHome)
$production = [IO.Path]::GetFullPath((Join-Path $HOME '.config/herdr-app'))
if ($targetHome -eq $production -and -not $InstallProduction) {
    throw 'Production install requires an explicit -InstallProduction argument. Close Herdr and approve installation first.'
}
if (-not $InstallProduction -and -not $targetHome.StartsWith(($repo + [IO.Path]::DirectorySeparatorChar), [StringComparison]::OrdinalIgnoreCase)) {
    throw 'Without -InstallProduction, select an isolated app home inside this repository.'
}
function Assert-NoReparse([string]$Path) {
    $item = $Path
    while ($item) {
        if (Test-Path -LiteralPath $item) {
            if ((Get-Item -LiteralPath $item -Force).Attributes -band [IO.FileAttributes]::ReparsePoint) { throw 'Linked installation path refused' }
        }
        $parent = [IO.Path]::GetDirectoryName($item)
        if ($parent -eq $item) { break }
        $item = $parent
    }
}
Assert-NoReparse $targetHome
& $Python -I -c 'import sys; assert sys.version_info[:2] == (3,14), "Python 3.14 required"'
if ($LASTEXITCODE -ne 0) { throw 'Python 3.14 is required' }
$version = (Get-Content -LiteralPath (Join-Path $repo 'version.json') -Raw | ConvertFrom-Json).version
$modRoot = Join-Path $targetHome 'mods'
$destination = Join-Path $modRoot 'session-hub'
$runtimeRoot = Join-Path $targetHome "data/session-hub-runtime/$version"
Assert-NoReparse $destination
Assert-NoReparse $runtimeRoot
New-Item -ItemType Directory -Force -Path $modRoot,$runtimeRoot | Out-Null
$venv = Join-Path $runtimeRoot 'venv'
& $Python -I -m venv $venv
if ($LASTEXITCODE -ne 0) { throw 'Virtual environment creation failed' }
$runtimePython = Join-Path $venv 'Scripts/python.exe'
$wheelhouse = Join-Path $repo 'wheelhouse'
if (-not (Test-Path -LiteralPath $wheelhouse -PathType Container)) { throw 'Missing offline wheelhouse. Build a local bundle first (scripts/build-release.ps1).' }
& $runtimePython -I -m pip install --no-index --find-links $wheelhouse --require-hashes -r (Join-Path $repo 'requirements-windows.lock')
if ($LASTEXITCODE -ne 0) { throw 'Pinned offline dependency installation failed' }
$staging = Join-Path $modRoot ('.session-hub-stage-' + [guid]::NewGuid().ToString('N'))
New-Item -ItemType Directory -Path $staging | Out-Null
foreach ($name in @('main.js','model.js','ui.js','mod.json')) { Copy-Item -LiteralPath (Join-Path $repo "mods/session-hub/$name") -Destination $staging }
Copy-Item -LiteralPath (Join-Path $repo 'mods/session-hub/icons') -Destination $staging -Recurse
Copy-Item -LiteralPath (Join-Path $repo 'mods/session-hub/helper') -Destination $staging -Recurse
Get-ChildItem -LiteralPath (Join-Path $staging 'helper') -Filter '*.pyc' -Recurse | ForEach-Object { Remove-Item -LiteralPath $_.FullName }
@{schema=1;python=$runtimePython;helper=(Join-Path $destination 'helper/hub.py');state=(Join-Path $targetHome 'data/session-hub');base=$destination} | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $staging 'runtime.json') -Encoding utf8NoBOM
& (Join-Path $PSScriptRoot 'check-native.ps1') -ModPath $staging
if ($LASTEXITCODE -ne 0) { throw 'Native mod check failed; installation has not replaced the current mod' }
if (Test-Path -LiteralPath $destination) {
    $backupRoot = Join-Path $targetHome 'data/session-hub-mod-backups'
    Assert-NoReparse $backupRoot
    New-Item -ItemType Directory -Force -Path $backupRoot | Out-Null
    $backup = Join-Path $backupRoot ([DateTime]::UtcNow.ToString('yyyyMMddHHmmss') + '-' + [guid]::NewGuid().ToString('N'))
    Move-Item -LiteralPath $destination -Destination $backup
}
Move-Item -LiteralPath $staging -Destination $destination
Write-Output 'Session Hub installed with place=none. No layout or hotkey was edited. Open it with: herdr-app do mod.open --name session-hub'
