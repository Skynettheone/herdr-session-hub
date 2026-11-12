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
$testRoot=Join-Path ([IO.Path]::GetDirectoryName($repo)) '.dev'
if (-not $InstallProduction -and -not $targetHome.StartsWith(($testRoot + [IO.Path]::DirectorySeparatorChar), [StringComparison]::OrdinalIgnoreCase)) {
    throw 'Without -InstallProduction, select a disposable app home below the bundle parent .dev directory.'
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
& $Python -I -B (Join-Path $PSScriptRoot 'verify-package.py') $repo
if ($LASTEXITCODE -ne 0) { throw 'Package integrity verification failed; no installation files were changed' }
$version = (Get-Content -LiteralPath (Join-Path $repo 'version.json') -Raw | ConvertFrom-Json).version
if ($version -notmatch '^[0-9]+\.[0-9]+\.[0-9]+(?:-[a-zA-Z0-9.-]+)?$') { throw 'Invalid package version' }
$modRoot = Join-Path $targetHome 'mods'
$destination = Join-Path $modRoot 'session-hub'
# Never rebuild a runtime already referenced by the current mod or its backup.
$runtimeRoot = Join-Path $targetHome ("data/session-hub-runtime/"+$version+'-'+[guid]::NewGuid().ToString('N'))
Assert-NoReparse $destination
Assert-NoReparse $runtimeRoot
$transactionRoot=Join-Path $targetHome 'data/session-hub-install'
Assert-NoReparse $transactionRoot
New-Item -ItemType Directory -Force -Path $transactionRoot | Out-Null
$lockPath=Join-Path $transactionRoot 'install.lock'
Assert-NoReparse $lockPath
try {
    $installLock=[IO.File]::Open($lockPath,[IO.FileMode]::OpenOrCreate,[IO.FileAccess]::ReadWrite,[IO.FileShare]::None)
} catch { throw 'Another installer is active or its lock is unavailable. No current mod was replaced.' }
try {
$receipt=Join-Path $transactionRoot 'pending.json'
Assert-NoReparse $receipt
if(Test-Path -LiteralPath $receipt) { throw 'Interrupted installation receipt found. Restore the recorded mod backup before retrying; see USER_GUIDE.md.' }
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
foreach ($name in @('main.js','model.js','ui.js','usage.js','tabs.js','mod.json')) { Copy-Item -LiteralPath (Join-Path $repo "mods/session-hub/$name") -Destination $staging }
Copy-Item -LiteralPath (Join-Path $repo 'mods/session-hub/icons') -Destination $staging -Recurse
Copy-Item -LiteralPath (Join-Path $repo 'mods/session-hub/assets') -Destination $staging -Recurse
Copy-Item -LiteralPath (Join-Path $repo 'mods/session-hub/helper') -Destination $staging -Recurse
Get-ChildItem -LiteralPath (Join-Path $staging 'helper') -Filter '*.pyc' -Recurse | ForEach-Object { Remove-Item -LiteralPath $_.FullName }
@{schema=1;python=$runtimePython;helper=(Join-Path $destination 'helper/hub.py');state=(Join-Path $targetHome 'data/session-hub');base=$destination} | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $staging 'runtime.json') -Encoding utf8NoBOM
& (Join-Path $PSScriptRoot 'check-native.ps1') -ModPath $staging -CheckHome (Join-Path $runtimeRoot 'sdk-check')
if ($LASTEXITCODE -ne 0) { throw 'Native mod check failed; installation has not replaced the current mod' }
$backup=$null
if (Test-Path -LiteralPath $destination) {
    $backupRoot = Join-Path $targetHome 'data/session-hub-mod-backups'
    Assert-NoReparse $backupRoot
    New-Item -ItemType Directory -Force -Path $backupRoot | Out-Null
    $backup = Join-Path $backupRoot ([DateTime]::UtcNow.ToString('yyyyMMddHHmmss') + '-' + [guid]::NewGuid().ToString('N'))
}
@{schema=1;destination=$destination;backup=$backup;staging=$staging;runtime=$runtimeRoot} | ConvertTo-Json | Set-Content -LiteralPath $receipt -Encoding utf8NoBOM
try {
    if($backup) { Move-Item -LiteralPath $destination -Destination $backup }
    Move-Item -LiteralPath $staging -Destination $destination
} catch {
    # Ordinary swap failures restore the previous complete mod and its untouched
    # runtime. A power loss retains the receipt and backup for explicit recovery.
    if($backup -and -not(Test-Path -LiteralPath $destination) -and (Test-Path -LiteralPath $backup)) {
        Move-Item -LiteralPath $backup -Destination $destination
    }
    if(-not $backup -or (Test-Path -LiteralPath $destination)) { Remove-Item -LiteralPath $receipt }
    throw
}
Remove-Item -LiteralPath $receipt
Write-Output 'Session Hub installed with place=none. No layout or hotkey was edited. Open it with: herdr-app do mod.open --name session-hub'
} finally { $installLock.Dispose() }
