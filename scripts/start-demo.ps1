# Starts only an isolated app home and isolated core. No production mods/layouts.
param([switch]$Visible)
$ErrorActionPreference = 'Stop'
$repo = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..'))
$dev = Join-Path $repo '.dev'
$env:HERDR_APP_HOME = Join-Path $dev 'herdr-app'
$env:HC_SESSION = 'test-session-hub'
$env:XDG_CONFIG_HOME = Join-Path $dev 'xdg/config'
$env:XDG_STATE_HOME = Join-Path $dev 'xdg/state'
$env:XDG_DATA_HOME = Join-Path $dev 'xdg/data'
$env:XDG_CACHE_HOME = Join-Path $dev 'xdg/cache'
$env:HERDR_TELEMETRY = '0'
$env:DO_NOT_TRACK = '1'
& (Join-Path $repo '.venv/Scripts/python.exe') (Join-Path $PSScriptRoot 'seed-demo.py')
if ($LASTEXITCODE -ne 0) { throw 'Demo preparation failed' }
hc server start
if ($LASTEXITCODE -ne 0) { throw 'Isolated core failed to start' }
if($Visible){Start-Process -FilePath (Get-Command herdr-app).Source -WindowStyle Normal}
else{Start-Process -FilePath (Get-Command herdr-app).Source -WindowStyle Hidden}
Write-Output 'Started isolated Herdr demo (HC_SESSION=test-session-hub). Use this same environment for status/shot/commands.'
