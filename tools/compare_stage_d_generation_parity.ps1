param(
    [string]$TerminalId = "D0E8209F77C8CF37AD8BF550E51FF075",
    [string]$AgentName = "Agent-127.0.0.1-3000",
    [string]$OutputName = "stage_d_setup_quality"
)

$ErrorActionPreference = "Stop"
$projectRoot = Split-Path -Parent $PSScriptRoot
$python = Join-Path $projectRoot "training\.venv\Scripts\python.exe"
$outputRoot = Join-Path $projectRoot "training\output\$OutputName"
$reference = Join-Path $outputRoot "reference_real_ticks_202606"
$candidate = Join-Path $env:APPDATA "MetaQuotes\Tester\$TerminalId\$AgentName\MQL5\Files"
$report = Join-Path $outputRoot "generation_model_parity.json"

$arguments = @(
    (Join-Path $projectRoot "training\compare_objective_generation_parity.py"),
    "--reference-setup", (Join-Path $reference "XAU_AI_SHADOW_BACKTEST_OBJECTIVE_SETUP_AUDIT.csv"),
    "--reference-decisions", (Join-Path $reference "XAU_AI_SHADOW_BACKTEST_OBJECTIVE_DECISIONS_V4.csv"),
    "--candidate-setup", (Join-Path $candidate "XAU_AI_SHADOW_BACKTEST_OBJECTIVE_SETUP_AUDIT.csv"),
    "--candidate-decisions", (Join-Path $candidate "XAU_AI_SHADOW_BACKTEST_OBJECTIVE_DECISIONS_V4.csv"),
    "--output", $report
)
foreach ($required in @($python, $arguments[2], $arguments[4], $arguments[6], $arguments[8])) {
    if (-not (Test-Path -LiteralPath $required)) {
        throw "Stage D parity file not found: $required"
    }
}
& $python @arguments
if ($LASTEXITCODE -ne 0) {
    throw "Stage D generation parity comparison failed."
}
$result = Get-Content -LiteralPath $report -Raw | ConvertFrom-Json
if ($result.generation_parity_valid) {
    Write-Output "Stage D generation parity passed. Faster historical generation is eligible."
} else {
    Write-Output "Stage D generation parity failed. Use real ticks only."
}
