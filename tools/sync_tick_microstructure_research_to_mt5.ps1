param(
    [string]$TerminalId = "D0E8209F77C8CF37AD8BF550E51FF075"
)

$ErrorActionPreference = "Stop"
$projectRoot = Split-Path -Parent $PSScriptRoot
$terminalRoot = Join-Path $env:APPDATA "MetaQuotes\Terminal\$TerminalId\MQL5\Experts\XAU-AI-PLATFORM"

$relativeFiles = @(
    "core\brain\liquidity\models\TickMicrostructureResult.mqh",
    "core\brain\liquidity\engines\TickMicrostructureEngine.mqh",
    "core\ai\HistoricalTickMicrostructureExporter.mqh",
    "tests\TestHistoricalTickMicrostructureExporter.mq5"
)

foreach ($relativeFile in $relativeFiles) {
    $source = Join-Path $projectRoot $relativeFile
    $destination = Join-Path $terminalRoot $relativeFile
    if (-not (Test-Path -LiteralPath $source)) {
        throw "Workspace source not found: $source"
    }
    $destinationDirectory = Split-Path -Parent $destination
    if (-not (Test-Path -LiteralPath $destinationDirectory)) {
        New-Item -ItemType Directory -Path $destinationDirectory | Out-Null
    }
    $sourceHash = (Get-FileHash -LiteralPath $source -Algorithm SHA256).Hash
    if (Test-Path -LiteralPath $destination) {
        $currentHash = (Get-FileHash -LiteralPath $destination -Algorithm SHA256).Hash
        if ($sourceHash -eq $currentHash) {
            Write-Output "CURRENT $relativeFile SHA256=$sourceHash"
            continue
        }
    }
    if (Test-Path -LiteralPath $destination) {
        (Get-Item -LiteralPath $destination).IsReadOnly = $false
    }
    $copied = $false
    for ($attempt = 1; $attempt -le 10; $attempt++) {
        try {
            Copy-Item -LiteralPath $source -Destination $destination -Force
            $copied = $true
            break
        }
        catch [System.IO.IOException] {
            if ($attempt -eq 10) {
                throw
            }
            Start-Sleep -Milliseconds 500
        }
    }
    if (-not $copied) {
        throw "Copy did not complete: $relativeFile"
    }
    $destinationHash = (Get-FileHash -LiteralPath $destination -Algorithm SHA256).Hash
    if ($sourceHash -ne $destinationHash) {
        throw "Hash verification failed: $relativeFile"
    }
    Write-Output "SYNCED $relativeFile SHA256=$sourceHash"
}

Write-Output "Tick microstructure research files synchronized successfully."
