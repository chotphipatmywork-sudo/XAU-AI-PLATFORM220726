param([string]$TerminalId="D0E8209F77C8CF37AD8BF550E51FF075",
      [string]$MetaEditor="C:\Program Files\MetaTrader 5\MetaEditor64.exe")
$ErrorActionPreference="Stop"
$root=Split-Path -Parent $PSScriptRoot
& (Join-Path $PSScriptRoot "sync_current_feed_stop_research_to_mt5.ps1") -TerminalId $TerminalId
$terminal=Join-Path $env:APPDATA "MetaQuotes\Terminal\$TerminalId\MQL5\Experts\XAU-AI-PLATFORM"
$source=Join-Path $terminal "tests\TestCurrentFeedStructuralStopExporter.mq5"
$dir=Join-Path $root "outputs\compile\current_feed_stop";New-Item -ItemType Directory -Path $dir -Force|Out-Null
$log=Join-Path $dir "TestCurrentFeedStructuralStopExporter.log"
if(Test-Path $log){Remove-Item $log -Force}
Start-Process -FilePath $MetaEditor -ArgumentList ('/compile:"{0}"'-f $source),('/log:"{0}"'-f $log) -WindowStyle Hidden -Wait
if(-not(Test-Path $log) -or (Get-Content $log -Raw)-notmatch '0 errors, 0 warnings'){throw "Stop compile failed"}
Write-Output "Current-feed Stop compile passed: 0 errors, 0 warnings."
