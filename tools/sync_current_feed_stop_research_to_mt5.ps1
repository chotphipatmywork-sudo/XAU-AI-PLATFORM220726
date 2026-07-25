param([string]$TerminalId = "D0E8209F77C8CF37AD8BF550E51FF075")
$ErrorActionPreference="Stop"
$root=Split-Path -Parent $PSScriptRoot
$terminal=Join-Path $env:APPDATA "MetaQuotes\Terminal\$TerminalId\MQL5\Experts\XAU-AI-PLATFORM"
$files=@("core\ai\PastOnlyStructuralStopExporter.mqh",
         "core\ai\PastOnlyStructuralTargetExporter.mqh",
         "tests\TestCurrentFeedStructuralStopExporter.mq5")
foreach($relative in $files){
 $source=Join-Path $root $relative;$dest=Join-Path $terminal $relative
 New-Item -ItemType Directory -Path (Split-Path -Parent $dest) -Force|Out-Null
 Copy-Item -LiteralPath $source -Destination $dest -Force
 if((Get-FileHash $source).Hash -ne (Get-FileHash $dest).Hash){throw "Hash mismatch $relative"}
 Write-Output "SYNCED $relative"
}
