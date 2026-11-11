[CmdletBinding()]
param([Parameter(Mandatory=$true)][string]$ModPath)
$ErrorActionPreference='Stop'
$resolved=[IO.Path]::GetFullPath($ModPath)
if(-not(Test-Path -LiteralPath $resolved -PathType Container)){throw 'Native check target is missing'}
# herdr-app.exe is a Windows GUI-subsystem executable. PowerShell can return
# immediately when invoked directly. Start it through Process and await the real
# exit code; ArgumentList preserves paths as arguments without shell quoting.
$info=[Diagnostics.ProcessStartInfo]::new()
$info.FileName=(Get-Command herdr-app.exe -ErrorAction Stop).Source
$info.UseShellExecute=$false
$info.CreateNoWindow=$true
$info.RedirectStandardOutput=$true
$info.RedirectStandardError=$true
$info.ArgumentList.Add('check')
$info.ArgumentList.Add($resolved)
$process=[Diagnostics.Process]::Start($info)
try {
    $stdout=$process.StandardOutput.ReadToEndAsync()
    $stderr=$process.StandardError.ReadToEndAsync()
    if(-not $process.WaitForExit(60000)){$process.Kill();throw 'Native check timed out'}
    if($stdout.Result){Write-Output $stdout.Result.TrimEnd()}
    if($stderr.Result){Write-Output $stderr.Result.TrimEnd()}
    exit $process.ExitCode
} finally {$process.Dispose()}
