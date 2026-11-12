[CmdletBinding()]
param([string]$Python)
$ErrorActionPreference='Stop'
$repo=[IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..'))
if(-not $Python){$Python=Join-Path $repo '.venv/Scripts/python.exe'}
$package=Join-Path $repo ('.dev/install-smoke-'+[guid]::NewGuid().ToString('N'))
$testHome=Join-Path ([IO.Path]::GetDirectoryName($package)) ('.dev/install-home-'+[guid]::NewGuid().ToString('N'))
New-Item -ItemType Directory -Force -Path (Join-Path $package 'scripts'),(Join-Path $package 'wheelhouse'),(Join-Path $package 'mods/session-hub/helper'),(Join-Path $testHome 'layouts')|Out-Null
foreach($name in @('version.json','requirements-windows.lock','LICENSE','README.md','RECIPE.md','SECURITY.md','THIRD_PARTY_NOTICES.md','CHANGELOG.md','preview.png')){Copy-Item -LiteralPath (Join-Path $repo $name) -Destination $package}
New-Item -ItemType Directory -Force -Path (Join-Path $package 'docs/screenshots')|Out-Null
foreach($name in @('USER_GUIDE.md','INSTALL_WITH_AGENT.md')){Copy-Item -LiteralPath (Join-Path $repo "docs/$name") -Destination (Join-Path $package 'docs')}
Copy-Item -LiteralPath (Join-Path $repo 'docs/screenshots/usage-community.png') -Destination (Join-Path $package 'docs/screenshots')
foreach($name in @('install.ps1','uninstall.ps1','verify-package.py','check-native.ps1')){Copy-Item -LiteralPath (Join-Path $repo "scripts/$name") -Destination (Join-Path $package 'scripts')}
foreach($name in @('main.js','model.js','ui.js','usage.js','tabs.js','mod.json')){Copy-Item -LiteralPath (Join-Path $repo "mods/session-hub/$name") -Destination (Join-Path $package 'mods/session-hub')}
Copy-Item -LiteralPath (Join-Path $repo 'mods/session-hub/helper/hub.py') -Destination (Join-Path $package 'mods/session-hub/helper')
$adapters=Join-Path $package 'mods/session-hub/helper/adapters'
New-Item -ItemType Directory -Path $adapters|Out-Null
Get-ChildItem -LiteralPath (Join-Path $repo 'mods/session-hub/helper/adapters') -Filter '*.py' -File | ForEach-Object {Copy-Item -LiteralPath $_.FullName -Destination $adapters}
Copy-Item -LiteralPath (Join-Path $repo 'mods/session-hub/icons') -Destination (Join-Path $package 'mods/session-hub') -Recurse
Copy-Item -LiteralPath (Join-Path $repo 'mods/session-hub/assets') -Destination (Join-Path $package 'mods/session-hub') -Recurse
Get-ChildItem -LiteralPath (Join-Path $repo '.research/wheels') -Filter '*.whl' -File | ForEach-Object {Copy-Item -LiteralPath $_.FullName -Destination (Join-Path $package 'wheelhouse')}
$layout=Join-Path $testHome 'layouts/keep.json'
$keys=Join-Path $testHome 'keys.json'
$original=Join-Path ([IO.Path]::GetDirectoryName($testHome)) (([IO.Path]::GetFileName($testHome))+'-provider-original.jsonl')
'{"test":"layout sentinel"}'|Set-Content -LiteralPath $layout
'{"test":"key sentinel"}'|Set-Content -LiteralPath $keys
'{"type":"synthetic original"}'|Set-Content -LiteralPath $original
$hashes=@($layout,$keys,$original)|ForEach-Object {(Get-FileHash -LiteralPath $_ -Algorithm SHA256).Hash}
$installer=Join-Path $package 'scripts/install.ps1'
$uninstaller=Join-Path $package 'scripts/uninstall.ps1'
$manifest=Get-ChildItem -LiteralPath $package -File -Recurse | Sort-Object FullName | ForEach-Object {
    "$((Get-FileHash -LiteralPath $_.FullName -Algorithm SHA256).Hash.ToLower())  $([IO.Path]::GetRelativePath($package,$_.FullName).Replace('\','/'))"
}
$manifest|Set-Content -LiteralPath (Join-Path $package 'SHA256SUMS.txt') -Encoding utf8NoBOM
$main=Join-Path $package 'mods/session-hub/main.js'
$originalMain=[IO.File]::ReadAllBytes($main)
[IO.File]::AppendAllText($main,'// synthetic checksum tamper')
$rejectedHome=$testHome+'-rejected'
$rejected=$false
try { & $installer -AppHome $rejectedHome -Python $Python } catch { $rejected=$_.Exception.Message -like '*Package integrity*' }
if(-not $rejected -or (Test-Path -LiteralPath $rejectedHome)){throw 'Tampered package was not refused before target writes'}
[IO.File]::WriteAllBytes($main,$originalMain)
& $installer -AppHome $testHome -Python $Python
if(-not(Test-Path -LiteralPath (Join-Path $testHome 'mods/session-hub/runtime.json'))){throw 'Runtime was not configured'}
$runtime=Get-Content -LiteralPath (Join-Path $testHome 'mods/session-hub/runtime.json') -Raw|ConvertFrom-Json
& $runtime.python -I $runtime.helper --state $runtime.state rpc '{"action":"list"}'
if($LASTEXITCODE -ne 0){throw 'Installed isolated helper failed to import its adapters'}
if(-not(Test-Path -LiteralPath (Join-Path $testHome 'mods/session-hub/assets/HERDR-LICENSE.txt'))){throw 'Official artwork license missing'}
New-Item -ItemType Directory -Force -Path (Join-Path $testHome 'data/session-hub')|Out-Null
'kept'|Set-Content -LiteralPath (Join-Path $testHome 'data/session-hub/keep.txt')
$runtimeBefore=[IO.File]::ReadAllBytes((Join-Path $testHome 'mods/session-hub/runtime.json'))
$pythonBefore=(Get-FileHash -LiteralPath $runtime.python -Algorithm SHA256).Hash
# Simulate an ordinary final rename failure after the old mod has been backed up.
# The hook exists only in this disposable smoke-test PowerShell scope.
function Move-Item {
    param([string]$LiteralPath,[string]$Destination)
    if([IO.Path]::GetFileName($LiteralPath) -like '.session-hub-stage-*') { throw 'Synthetic final swap failure' }
    Microsoft.PowerShell.Management\Move-Item -LiteralPath $LiteralPath -Destination $Destination
}
$failed=$false
try { & $installer -AppHome $testHome -Python $Python } catch { $failed=$_.Exception.Message -like '*Synthetic final swap failure*' }
Remove-Item Function:\Move-Item
if(-not $failed){throw 'Failure injection did not reach final swap'}
if([Convert]::ToBase64String($runtimeBefore) -ne [Convert]::ToBase64String([IO.File]::ReadAllBytes((Join-Path $testHome 'mods/session-hub/runtime.json')))){throw 'Failed upgrade did not restore the original mod'}
if((Get-FileHash -LiteralPath $runtime.python -Algorithm SHA256).Hash -ne $pythonBefore){throw 'Failed upgrade modified the old runtime'}
if(Test-Path -LiteralPath (Join-Path $testHome 'data/session-hub-install/pending.json')){throw 'Recovered swap retained a blocking receipt'}
& $runtime.python -I -B $runtime.helper --state $runtime.state rpc '{"action":"list"}'
if($LASTEXITCODE -ne 0){throw 'Old helper no longer works after rollback'}
$receipt=Join-Path $testHome 'data/session-hub-install/pending.json'
'{"synthetic":"interrupted transaction"}'|Set-Content -LiteralPath $receipt
$interrupted=$false
try { & $installer -AppHome $testHome -Python $Python } catch { $interrupted=$_.Exception.Message -like '*Interrupted installation receipt*' }
if(-not $interrupted){throw 'Unresolved interrupted install was silently ignored'}
Remove-Item -LiteralPath $receipt
$held=[IO.File]::Open((Join-Path $testHome 'data/session-hub-install/install.lock'),[IO.FileMode]::Open,[IO.FileAccess]::ReadWrite,[IO.FileShare]::None)
try {
    $blocked=$false
    try { & $installer -AppHome $testHome -Python $Python } catch { $blocked=$_.Exception.Message -like '*Another installer is active*' }
    if(-not $blocked){throw 'Concurrent installer was not refused'}
} finally { $held.Dispose() }
& $installer -AppHome $testHome -Python $Python
if(-not(Test-Path -LiteralPath (Join-Path $testHome 'data/session-hub-mod-backups'))){throw 'Upgrade backup missing'}
$upgraded=Get-Content -LiteralPath (Join-Path $testHome 'mods/session-hub/runtime.json') -Raw|ConvertFrom-Json
if($upgraded.python -eq $runtime.python -or -not(Test-Path -LiteralPath $runtime.python)){throw 'Upgrade did not preserve a separate rollback runtime'}
& $Python -I -B (Join-Path $package 'scripts/verify-package.py') $package
if($LASTEXITCODE -ne 0){throw 'Installer modified the verified source bundle'}
& $uninstaller -AppHome $testHome -WhatIf
if(-not(Test-Path -LiteralPath (Join-Path $testHome 'mods/session-hub/main.js'))){throw 'WhatIf mutated installation'}
& $uninstaller -AppHome $testHome
if(Test-Path -LiteralPath (Join-Path $testHome 'mods/session-hub')){throw 'Uninstall left the mod'}
if(-not(Test-Path -LiteralPath (Join-Path $testHome 'data/session-hub/keep.txt'))){throw 'Default uninstall erased state'}
& $uninstaller -AppHome $testHome -PurgeHubData
if(Test-Path -LiteralPath (Join-Path $testHome 'data/session-hub')){throw 'Explicit Hub purge failed'}
$after=@($layout,$keys,$original)|ForEach-Object {(Get-FileHash -LiteralPath $_ -Algorithm SHA256).Hash}
if(Compare-Object $hashes $after){throw 'Layout, keys or synthetic provider original changed'}
Write-Output 'PASS: tamper refusal before writes, offline install, failed-swap rollback, separate runtime upgrade, immutable source bundle, uninstall WhatIf, state retention, Hub purge and unchanged layout/key/originals'
