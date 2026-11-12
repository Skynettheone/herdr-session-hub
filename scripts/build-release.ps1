[CmdletBinding()]
param([switch]$AllowUnverified, [string]$Python = '.venv/Scripts/python.exe')
$ErrorActionPreference='Stop'
$repo=[IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..'))
Push-Location $repo
try {
    & $Python -m ruff check .
    if ($LASTEXITCODE -ne 0) { throw 'Correctness lint failed; install requirements-dev-windows.lock' }
    & $Python -m unittest discover -s tests -v
    if ($LASTEXITCODE -ne 0) { throw 'Helper tests failed' }
    node --experimental-vm-modules --test tests/panel.test.mjs
    if ($LASTEXITCODE -ne 0) { throw 'Panel behavior tests failed' }
    & (Join-Path $PSScriptRoot 'check-native.ps1') -ModPath (Join-Path $repo 'mods/session-hub')
    if ($LASTEXITCODE -ne 0) { throw 'Native check failed' }
    $version=Get-Content -LiteralPath (Join-Path $repo 'version.json') -Raw|ConvertFrom-Json
    if (-not $version.releaseReady -and -not $AllowUnverified) { throw 'Native acceptance remains open. Use -AllowUnverified only for a clearly labeled local candidate.' }
    $name='herdr-session-hub-'+$version.version+'-windows-x64-'+[DateTime]::UtcNow.ToString('yyyyMMddHHmmss')
    $stage=Join-Path $repo ('dist/'+$name)
    & $Python -I -B (Join-Path $PSScriptRoot 'package_payload.py') --target windows-x64 --stage $stage
    if($LASTEXITCODE -ne 0) { throw 'Install payload preparation failed' }
    $wheels=Join-Path $stage 'wheelhouse'
    & $Python -I -m pip download --no-index --find-links $wheels --require-hashes -r (Join-Path $repo 'requirements-windows.lock') --dest $wheels
    if($LASTEXITCODE -ne 0) { throw 'Offline wheel verification failed' }
    & $Python -I -B (Join-Path $PSScriptRoot 'verify-package.py') $stage
    if($LASTEXITCODE -ne 0) { throw 'Staged package integrity check failed' }
    $zip=$stage+'.zip'
    Compress-Archive -LiteralPath $stage -DestinationPath $zip
    $extract=Join-Path $repo ('.dev/package-extract-'+[guid]::NewGuid().ToString('N'))
    Expand-Archive -LiteralPath $zip -DestinationPath $extract
    & $Python -I -B (Join-Path $PSScriptRoot 'verify-package.py') (Join-Path $extract $name)
    if($LASTEXITCODE -ne 0) { throw 'Fresh extraction integrity check failed' }
    "$((Get-FileHash -LiteralPath $zip -Algorithm SHA256).Hash.ToLower())  $([IO.Path]::GetFileName($zip))" | Set-Content -LiteralPath ($zip+'.sha256') -Encoding utf8NoBOM
    Write-Output "Local install bundle prepared: $zip"
} finally { Pop-Location }
