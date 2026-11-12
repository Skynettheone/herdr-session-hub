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
    if (-not $version.releaseReady -and -not $AllowUnverified) { throw 'Release gates are open. Use -AllowUnverified only for a clearly labeled development bundle.' }
    $dist=Join-Path $repo 'dist'
    New-Item -ItemType Directory -Force -Path $dist|Out-Null
    $name='herdr-session-hub-'+$version.version+'-windows-x64-'+[DateTime]::UtcNow.ToString('yyyyMMddHHmmss')
    $stage=Join-Path $dist $name
    New-Item -ItemType Directory -Path $stage|Out-Null
    foreach($file in @('LICENSE','README.md','RECIPE.md','SECURITY.md','CONTRIBUTING.md','CHANGELOG.md','THIRD_PARTY_NOTICES.md','version.json','requirements-windows.lock','requirements-dev-windows.lock','ruff.toml','preview.png')) {
        if(Test-Path -LiteralPath (Join-Path $repo $file)) { Copy-Item -LiteralPath (Join-Path $repo $file) -Destination $stage }
    }
    foreach($folder in @('docs','scripts','tests')) { Copy-Item -LiteralPath (Join-Path $repo $folder) -Destination $stage -Recurse }
    $mod=Join-Path $stage 'mods/session-hub'
    New-Item -ItemType Directory -Force -Path (Join-Path $mod 'helper')|Out-Null
    foreach($file in @('main.js','model.js','ui.js','tabs.js','mod.json')) { Copy-Item -LiteralPath (Join-Path $repo "mods/session-hub/$file") -Destination $mod }
    Copy-Item -LiteralPath (Join-Path $repo 'mods/session-hub/icons') -Destination $mod -Recurse
    Copy-Item -LiteralPath (Join-Path $repo 'mods/session-hub/assets') -Destination $mod -Recurse
    Copy-Item -LiteralPath (Join-Path $repo 'mods/session-hub/helper/hub.py') -Destination (Join-Path $mod 'helper')
    $adapters=Join-Path $mod 'helper/adapters'
    New-Item -ItemType Directory -Path $adapters|Out-Null
    Get-ChildItem -LiteralPath (Join-Path $repo 'mods/session-hub/helper/adapters') -Filter '*.py' -File | ForEach-Object { Copy-Item -LiteralPath $_.FullName -Destination $adapters }
    # Only explicitly locked third-party wheels. No environment, histories, state,
    # research source files, installed SDKs or local runtime.json are bundled.
    $wheels=Join-Path $stage 'wheelhouse'
    New-Item -ItemType Directory -Path $wheels|Out-Null
    foreach($file in @('cryptography-50.0.2-cp311-abi3-win_amd64.whl','cffi-2.1.1-cp314-cp314-win_amd64.whl','pycparser-3.12-py3-none-any.whl')) {
        $source=Join-Path $repo ".research/wheels/$file"
        if(-not(Test-Path -LiteralPath $source)) { throw 'Missing locked wheel; see CONTRIBUTING.md for preparation' }
        Copy-Item -LiteralPath $source -Destination $wheels
    }
    & $Python -I -m pip download --no-index --find-links $wheels --require-hashes -r (Join-Path $repo 'requirements-windows.lock') --dest $wheels
    if($LASTEXITCODE -ne 0) { throw 'Wheel integrity verification failed' }
    # Bytecode is never release input.
    Get-ChildItem -LiteralPath $stage -Filter '*.pyc' -Recurse | ForEach-Object { Remove-Item -LiteralPath $_.FullName }
    $manifest=Get-ChildItem -LiteralPath $stage -File -Recurse | Sort-Object FullName | ForEach-Object {
        $relative=[IO.Path]::GetRelativePath($stage,$_.FullName).Replace('\','/')
        "$((Get-FileHash -LiteralPath $_.FullName -Algorithm SHA256).Hash.ToLower())  $relative"
    }
    $manifest|Set-Content -LiteralPath (Join-Path $stage 'SHA256SUMS.txt') -Encoding utf8NoBOM
    $zip=$stage+'.zip'
    Compress-Archive -LiteralPath $stage -DestinationPath $zip
    "$((Get-FileHash -LiteralPath $zip -Algorithm SHA256).Hash.ToLower())  $([IO.Path]::GetFileName($zip))" | Set-Content -LiteralPath ($zip+'.sha256') -Encoding utf8NoBOM
    Write-Output "Development bundle prepared: $zip"
} finally { Pop-Location }
