param([string]$TerminalId = "D0E8209F77C8CF37AD8BF550E51FF075")
$ErrorActionPreference = "Stop"
$projectRoot = Split-Path -Parent $PSScriptRoot
$terminalRoot = Join-Path $env:APPDATA "MetaQuotes\Terminal\$TerminalId\MQL5\Experts\XAU-AI-PLATFORM"
$relativeFiles = @(
    "core\ai\PastOnlyLifecyclePathExporter.mqh",
    "tests\TestCurrentFeedLifecyclePathExporter.mq5"
)
foreach ($relativeFile in $relativeFiles) {
    $source = Join-Path $projectRoot $relativeFile
    $destination = Join-Path $terminalRoot $relativeFile
    New-Item -ItemType Directory -Path (Split-Path -Parent $destination) -Force | Out-Null
    if (Test-Path -LiteralPath $destination) {
        (Get-Item -LiteralPath $destination).IsReadOnly = $false
    }
    Copy-Item -LiteralPath $source -Destination $destination -Force
    $sourceHash = (Get-FileHash -LiteralPath $source -Algorithm SHA256).Hash
    if ($sourceHash -ne (Get-FileHash -LiteralPath $destination -Algorithm SHA256).Hash) {
        throw "Current-feed lifecycle sync hash mismatch: $relativeFile"
    }
    Write-Output "SYNCED $relativeFile SHA256=$sourceHash"
}
