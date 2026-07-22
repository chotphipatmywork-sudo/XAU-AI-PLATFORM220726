param(
    [string]$OutputName = "stage_d_setup_quality"
)

$ErrorActionPreference = "Stop"
$projectRoot = Split-Path -Parent $PSScriptRoot
$python = Join-Path $projectRoot "training\.venv\Scripts\python.exe"
$outputRoot = Join-Path $projectRoot "training\output\$OutputName"
$train = Join-Path $outputRoot "XAU_AI_SETUP_OUTCOME_TRAIN.csv"
$splitSummary = Join-Path $outputRoot "setup_outcome_split_summary.json"
$researchOutput = Join-Path $outputRoot "research"

foreach ($required in @($python, $train, $splitSummary)) {
    if (-not (Test-Path -LiteralPath $required)) {
        throw "Stage D research input not found: $required"
    }
}
$split = Get-Content -LiteralPath $splitSummary -Raw | ConvertFrom-Json
if (-not $split.ready_for_train_only_ranking) {
    Write-Output "Stage D Train readiness gate is not met. No model was trained."
    exit 0
}

& $python (Join-Path $projectRoot "training\setup_quality_walk_forward.py") `
    --train $train `
    --output-dir $researchOutput
if ($LASTEXITCODE -ne 0) {
    throw "Stage D Train-only Setup-quality research failed."
}
Write-Output "Stage D Train-only research completed. Deployment remains unauthorized."
