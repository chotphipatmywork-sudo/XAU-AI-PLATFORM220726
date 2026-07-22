# XAU AI PLATFORM
# File: run_setup_v2_hypothesis_diagnostic.ps1
# Layer: Tools / Offline Research
# Version: 1.0.0
# Purpose: Run the focused CR-014 Stage 1 test and Train-only diagnostic.

param(
    [string]$OutputName = "stage_d_setup_quality_real_ticks_202107_202606"
)

$ErrorActionPreference = "Stop"
$projectRoot = Split-Path -Parent $PSScriptRoot
$python = Join-Path $projectRoot "training\.venv\Scripts\python.exe"
$stageDRoot = Join-Path $projectRoot "training\output\$OutputName"
$train = Join-Path $stageDRoot "XAU_AI_SETUP_OUTCOME_TRAIN.csv"
$output = Join-Path $stageDRoot "research\cr014_stage1\setup_v2_hypothesis_diagnostic.json"

foreach ($required in @($python, $train)) {
    if (-not (Test-Path -LiteralPath $required)) {
        throw "CR-014 Stage 1 input not found: $required"
    }
}

& $python (Join-Path $projectRoot "training\test_setup_v2_hypothesis_diagnostic.py")
if ($LASTEXITCODE -ne 0) {
    throw "CR-014 Stage 1 focused diagnostic test failed."
}

& $python (Join-Path $projectRoot "training\diagnose_setup_v2_hypotheses.py") `
    --train $train `
    --output $output
if ($LASTEXITCODE -ne 0) {
    throw "CR-014 Stage 1 Train-only diagnostic failed."
}

Write-Output "CR-014 Stage 1 diagnostic completed. Stage 2, Runtime, and deployment remain unauthorized."
