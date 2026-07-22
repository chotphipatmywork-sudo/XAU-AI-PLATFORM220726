param(
    [string]$TerminalId = "D0E8209F77C8CF37AD8BF550E51FF075"
)

$ErrorActionPreference = "Stop"
$projectRoot = Split-Path -Parent $PSScriptRoot
$terminalRoot = Join-Path $env:APPDATA "MetaQuotes\Terminal\$TerminalId\MQL5\Experts\XAU-AI-PLATFORM"

if (-not (Test-Path -LiteralPath $terminalRoot)) {
    throw "MT5 project copy was not found: $terminalRoot"
}

$relativeFiles = @(
    "core\brain\trend\models\ConfirmedSwingStructureResult.mqh",
    "core\brain\trend\engines\ConfirmedSwingStructureEngine.mqh",
    "core\ai\HistoricalSwingStructureExporter.mqh",
    "tests\TestHistoricalSwingStructureExporter.mq5"
)

foreach ($relativeFile in $relativeFiles) {
    $source = Join-Path $projectRoot $relativeFile
    $destination = Join-Path $terminalRoot $relativeFile
    if (-not (Test-Path -LiteralPath $source)) {
        throw "Workspace source was not found: $source"
    }
    $destinationDirectory = Split-Path -Parent $destination
    if (-not (Test-Path -LiteralPath $destinationDirectory)) {
        New-Item -ItemType Directory -Path $destinationDirectory | Out-Null
    }
    if (Test-Path -LiteralPath $destination) {
        (Get-Item -LiteralPath $destination).IsReadOnly = $false
    }
    Copy-Item -LiteralPath $source -Destination $destination -Force
    $sourceHash = (Get-FileHash -LiteralPath $source -Algorithm SHA256).Hash
    $destinationHash = (Get-FileHash -LiteralPath $destination -Algorithm SHA256).Hash
    if ($sourceHash -ne $destinationHash) {
        throw "Hash verification failed: $relativeFile"
    }
    Write-Output "SYNCED $relativeFile SHA256=$sourceHash"
}

Write-Output "Swing structure research files synchronized successfully."
