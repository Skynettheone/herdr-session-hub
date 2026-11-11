[CmdletBinding()]
param([string]$Python)
$ErrorActionPreference='Stop'
$repo=[IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..'))
if(-not $Python){$Python=Join-Path $repo '.venv/Scripts/python.exe'}
$package=Join-Path $repo ('.dev/install-smoke-'+[guid]::NewGuid().ToString('N'))
$testHome=Join-Path $package '.dev/app'
New-Item -ItemType Directory -Force -Path (Join-Path $package 'scripts'),(Join-Path $package 'wheelhouse'),(Join-Path $package 'mods/session-hub/helper'),(Join-Path $testHome 'layouts')|Out-Null
foreach($name in @('version.json','requirements-windows.lock')){Copy-Item -LiteralPath (Join-Path $repo $name) -Destination $package}
foreach($name in @('install.ps1','uninstall.ps1','verify-package.py','check-native.ps1')){Copy-Item -LiteralPath (Join-Path $repo "scripts/$name") -Destination (Join-Path $package 'scripts')}
foreach($name in @('main.js','model.js','ui.js','mod.json')){Copy-Item -LiteralPath (Join-Path $repo "mods/session-hub/$name") -Destination (Join-Path $package 'mods/session-hub')}
Copy-Item -LiteralPath (Join-Path $repo 'mods/session-hub/helper/hub.py') -Destination (Join-Path $package 'mods/session-hub/helper')
Copy-Item -LiteralPath (Join-Path $repo 'mods/session-hub/helper/adapters') -Destination (Join-Path $package 'mods/session-hub/helper') -Recurse
Copy-Item -LiteralPath (Join-Path $repo 'mods/session-hub/icons') -Destination (Join-Path $package 'mods/session-hub') -Recurse
Copy-Item -LiteralPath (Join-Path $repo 'mods/session-hub/assets') -Destination (Join-Path $package 'mods/session-hub') -Recurse
Get-ChildItem -LiteralPath (Join-Path $repo '.research/wheels') -Filter '*.whl' -File | ForEach-Object {Copy-Item -LiteralPath $_.FullName -Destination (Join-Path $package 'wheelhouse')}
$layout=Join-Path $testHome 'layouts/keep.json'
$keys=Join-Path $testHome 'keys.json'
$original=Join-Path $package 'synthetic-provider-original.jsonl'
'{"test":"layout sentinel"}'|Set-Content -LiteralPath $layout
'{"test":"key sentinel"}'|Set-Content -LiteralPath $keys
'{"type":"synthetic original"}'|Set-Content -LiteralPath $original
$hashes=@($layout,$keys,$original)|ForEach-Object {(Get-FileHash -LiteralPath $_ -Algorithm SHA256).Hash}
$installer=Join-Path $package 'scripts/install.ps1'
$uninstaller=Join-Path $package 'scripts/uninstall.ps1'
& $installer -AppHome $testHome -Python $Python
if(-not(Test-Path -LiteralPath (Join-Path $testHome 'mods/session-hub/runtime.json'))){throw 'Runtime was not configured'}
$runtime=Get-Content -LiteralPath (Join-Path $testHome 'mods/session-hub/runtime.json') -Raw|ConvertFrom-Json
& $runtime.python -I $runtime.helper --state $runtime.state rpc '{"action":"list"}'
if($LASTEXITCODE -ne 0){throw 'Installed isolated helper failed to import its adapters'}
if(-not(Test-Path -LiteralPath (Join-Path $testHome 'mods/session-hub/assets/HERDR-LICENSE.txt'))){throw 'Official artwork license missing'}
New-Item -ItemType Directory -Force -Path (Join-Path $testHome 'data/session-hub')|Out-Null
'kept'|Set-Content -LiteralPath (Join-Path $testHome 'data/session-hub/keep.txt')
& $installer -AppHome $testHome -Python $Python
if(-not(Test-Path -LiteralPath (Join-Path $testHome 'data/session-hub-mod-backups'))){throw 'Upgrade backup missing'}
& $uninstaller -AppHome $testHome -WhatIf
if(-not(Test-Path -LiteralPath (Join-Path $testHome 'mods/session-hub/main.js'))){throw 'WhatIf mutated installation'}
& $uninstaller -AppHome $testHome
if(Test-Path -LiteralPath (Join-Path $testHome 'mods/session-hub')){throw 'Uninstall left the mod'}
if(-not(Test-Path -LiteralPath (Join-Path $testHome 'data/session-hub/keep.txt'))){throw 'Default uninstall erased state'}
& $uninstaller -AppHome $testHome -PurgeHubData
if(Test-Path -LiteralPath (Join-Path $testHome 'data/session-hub')){throw 'Explicit Hub purge failed'}
$after=@($layout,$keys,$original)|ForEach-Object {(Get-FileHash -LiteralPath $_ -Algorithm SHA256).Hash}
if(Compare-Object $hashes $after){throw 'Layout, keys or synthetic provider original changed'}
Write-Output 'PASS: offline install, upgrade backup, uninstall WhatIf, state retention, explicit Hub purge and layout/key/original hash preservation'
