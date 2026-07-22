$ErrorActionPreference = "Stop"
$projectRoot = Split-Path -Parent $PSScriptRoot
$entry = Join-Path $projectRoot "XAU-AI-PLATFORM.mq5"
$visited = New-Object "System.Collections.Generic.HashSet[string]"

function Visit-Include([string]$Path) {
    $full = [IO.Path]::GetFullPath($Path)
    if (-not $visited.Add($full)) {
        return
    }
    $directory = Split-Path -Parent $full
    foreach ($line in Get-Content -LiteralPath $full) {
        if ($line -match '^\s*#include\s+"([^"]+)"') {
            $include = [IO.Path]::GetFullPath((Join-Path $directory $matches[1]))
            if (-not (Test-Path -LiteralPath $include)) {
                throw "Missing include: $include"
            }
            Visit-Include $include
        }
    }
}

Visit-Include $entry
$forbiddenFiles = $visited | Where-Object {
    $_ -match 'TradeExecutor|PositionCloser|ExecutionPipeline|TradeManager|TradeLifecycle'
}
if ($forbiddenFiles) {
    throw "Broker-capable file entered the canonical Shadow closure: $forbiddenFiles"
}

$source = ($visited | ForEach-Object {
    Get-Content -LiteralPath $_ -Raw
}) -join "`n"
$forbiddenTokens = @(
    "<Trade/Trade.mqh>",
    "OrderSend",
    "PositionClose(",
    "m_trade.Buy(",
    "m_trade.Sell("
)
foreach ($token in $forbiddenTokens) {
    if ($source.Contains($token)) {
        throw "Broker mutation token entered the canonical Shadow closure: $token"
    }
}

Write-Output "Canonical Shadow include files: $($visited.Count)"
Write-Output "Broker-capable files in canonical closure: 0"
Write-Output "Broker mutation tokens in canonical closure: 0"
Write-Output "Shadow no-broker validation passed"
