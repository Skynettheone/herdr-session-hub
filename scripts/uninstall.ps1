[CmdletBinding(SupportsShouldProcess=$true)]
param([Parameter(Mandatory=$true)][string]$AppHome, [switch]$PurgeHubData)
$ErrorActionPreference='Stop'
$targetHome=[IO.Path]::GetFullPath($AppHome)
if (-not (Test-Path -LiteralPath $targetHome -PathType Container)) { throw 'App home is missing' }
$names=@('mods/session-hub')
if ($PurgeHubData) { $names += @('data/session-hub','data/session-hub-runtime','data/session-hub-mod-backups','data/session-hub-install') }
foreach($name in $names) {
    $target=[IO.Path]::GetFullPath((Join-Path $targetHome $name))
    if (-not $target.StartsWith(($targetHome+[IO.Path]::DirectorySeparatorChar),[StringComparison]::OrdinalIgnoreCase)) { throw 'Target escaped selected app home' }
    $part=$target
    while($part) {
        if ((Test-Path -LiteralPath $part) -and ((Get-Item -LiteralPath $part -Force).Attributes -band [IO.FileAttributes]::ReparsePoint)) { throw 'Linked uninstall target refused' }
        $parent=[IO.Path]::GetDirectoryName($part)
        if($parent -eq $part){break}
        $part=$parent
    }
    if ((Test-Path -LiteralPath $target) -and $PSCmdlet.ShouldProcess($target,'Remove only Session Hub owned files (close Herdr first)')) {
        Remove-Item -LiteralPath $target -Recurse -Force
    }
}
Write-Output 'Provider histories, credentials, Herdr layouts and hotkeys were not targeted. State remains unless -PurgeHubData was specified.'
