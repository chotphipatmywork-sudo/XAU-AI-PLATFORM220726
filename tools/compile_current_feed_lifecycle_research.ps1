param(
    [string]$TerminalId = "D0E8209F77C8CF37AD8BF550E51FF075",
    [string]$MetaEditor = "C:\Program Files\MetaTrader 5\MetaEditor64.exe"
)
$ErrorActionPreference = "Stop"
$projectRoot = Split-Path -Parent $PSScriptRoot
$terminalRoot = Join-Path $env:APPDATA "MetaQuotes\Terminal\$TerminalId\MQL5\Experts\XAU-AI-PLATFORM"
$relativeFile = "tests\TestCurrentFeedLifecyclePathExporter.mq5"
$logRoot = Join-Path $projectRoot "outputs\compile\current_feed_lifecycle"
$log = Join-Path $logRoot "TestCurrentFeedLifecyclePathExporter.log"
& (Join-Path $PSScriptRoot "sync_current_feed_lifecycle_research_to_mt5.ps1") -TerminalId $TerminalId
New-Item -ItemType Directory -Path $logRoot -Force | Out-Null
if (Test-Path -LiteralPath $log) { Remove-Item -LiteralPath $log -Force }
$source = Join-Path $terminalRoot $relativeFile
$process = Start-Process -FilePath $MetaEditor `
    -ArgumentList ('/compile:"{0}"' -f $source), ('/log:"{0}"' -f $log) `
    -WindowStyle Hidden -Wait -PassThru
if (-not (Test-Path -LiteralPath $log)) {
    throw "MetaEditor did not create current-feed lifecycle compile log."
}
$content = Get-Content -LiteralPath $log -Raw
if ($content -notmatch '0 errors, 0 warnings') {
    Write-Output $content
    throw "Current-feed lifecycle compile failed or warned."
}
Write-Output "Current-feed lifecycle compile passed: 0 errors, 0 warnings."
