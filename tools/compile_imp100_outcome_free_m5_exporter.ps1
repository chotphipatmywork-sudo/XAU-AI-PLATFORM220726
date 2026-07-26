param(
    [string]$TerminalId = "D0E8209F77C8CF37AD8BF550E51FF075",
    [string]$MetaEditor = "C:\Program Files\MetaTrader 5\MetaEditor64.exe"
)
$ErrorActionPreference = "Stop"
$projectRoot = Split-Path -Parent $PSScriptRoot
$sync = Join-Path $projectRoot "tools\sync_imp100_outcome_free_m5_exporter_to_mt5.ps1"
powershell.exe -NoProfile -ExecutionPolicy Bypass -File $sync -TerminalId $TerminalId
$platform = Join-Path $env:APPDATA "MetaQuotes\Terminal\$TerminalId\MQL5\Experts\XAU-AI-PLATFORM"
$source = Join-Path $platform "tests\TestCurrentFeedJointGeometryM5Exporter.mq5"
$executable = [System.IO.Path]::ChangeExtension($source, ".ex5")
$log = Join-Path $projectRoot "outputs\compile\imp100_outcome_free_m5\TestCurrentFeedJointGeometryM5Exporter.log"
New-Item -ItemType Directory -Force -Path (Split-Path $log) | Out-Null
if (Test-Path -LiteralPath $log) { Remove-Item -LiteralPath $log -Force }
Start-Process -FilePath $MetaEditor `
    -ArgumentList ('/compile:"{0}"' -f $source),('/log:"{0}"' -f $log) `
    -WindowStyle Hidden -Wait
if (-not (Test-Path -LiteralPath $log)) { throw "MetaEditor did not create IMP-100 outcome-free compile log." }
$text = Get-Content -Raw -LiteralPath $log
if ($text -notmatch 'Result: 0 errors, 0 warnings') {
    Write-Output $text
    throw "IMP-100 outcome-free M5 compile failed or warned: $log"
}
if (-not (Test-Path -LiteralPath $executable)) { throw "IMP-100 outcome-free exporter EX5 was not generated." }
Write-Output "IMP-100 outcome-free M5 compile passed: 0 errors, 0 warnings."
Write-Output "EX5=$executable"