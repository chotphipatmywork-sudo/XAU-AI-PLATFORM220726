param([string]$MetaEditor="C:\Program Files\MetaTrader 5\MetaEditor64.exe")
$ErrorActionPreference = "Stop"
$projectRoot = Split-Path -Parent $PSScriptRoot
$sync = Join-Path $projectRoot "tools\sync_current_feed_lifecycle_research_to_mt5.ps1"
powershell.exe -NoProfile -ExecutionPolicy Bypass -File $sync
$terminalRoot = Join-Path $env:APPDATA "MetaQuotes\Terminal\D0E8209F77C8CF37AD8BF550E51FF075"
$platform = Join-Path $terminalRoot "MQL5\Experts\XAU-AI-PLATFORM"
Copy-Item -LiteralPath (Join-Path $projectRoot "tests\TestCurrentFeedJointGeometryM5Exporter.mq5") -Destination (Join-Path $platform "tests\TestCurrentFeedJointGeometryM5Exporter.mq5") -Force
$log = Join-Path $projectRoot "outputs\compile\current_feed_joint_m5\TestCurrentFeedJointGeometryM5Exporter.log"
New-Item -ItemType Directory -Force -Path (Split-Path $log) | Out-Null
if (Test-Path -LiteralPath $log) { Remove-Item -LiteralPath $log -Force }
$source = Join-Path $platform "tests\TestCurrentFeedJointGeometryM5Exporter.mq5"
Start-Process -FilePath $MetaEditor `
    -ArgumentList ('/compile:"{0}"' -f $source),('/log:"{0}"' -f $log) `
    -WindowStyle Hidden -Wait
if (-not (Test-Path -LiteralPath $log)) {
    throw "MetaEditor did not create joint M5 compile log."
}
$text=Get-Content -Raw -LiteralPath $log
if($text -notmatch 'Result: 0 errors, 0 warnings'){ throw "Joint M5 compile failed: $log" }
Write-Output "Joint M5 compile passed: 0 errors, 0 warnings."
