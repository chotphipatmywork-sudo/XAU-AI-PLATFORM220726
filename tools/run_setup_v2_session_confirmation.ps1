# XAU AI PLATFORM
# File: run_setup_v2_session_confirmation.ps1
# Layer: Tools / Offline Research
# Version: 1.0.0
# Purpose: Run the one-shot frozen CR-014 Session confirmation.

param(
    [string]$OutputName = "cr014_session_confirmation_after_20260626"
)

$ErrorActionPreference = "Stop"
$projectRoot = Split-Path -Parent $PSScriptRoot
$python = Join-Path $projectRoot "training\.venv\Scripts\python.exe"
$confirmationRoot = Join-Path $projectRoot "training\output\$OutputName"
$dataset = Join-Path $confirmationRoot "XAU_AI_SETUP_OUTCOME_CONFIRMATION.csv"
$output = Join-Path $confirmationRoot "setup_v2_session_confirmation.json"

foreach ($required in @($python, $dataset)) {
    if (-not (Test-Path -LiteralPath $required)) {
        throw "CR-014 Stage 1B input not found: $required"
    }
}
if (Test-Path -LiteralPath $output) {
    throw "CR-014 Stage 1B output already exists; this period is no longer untouched: $output"
}

& $python (Join-Path $projectRoot "training\test_setup_v2_session_confirmation.py")
if ($LASTEXITCODE -ne 0) {
    throw "CR-014 Stage 1B focused confirmation test failed."
}

& $python (Join-Path $projectRoot "training\confirm_setup_v2_session_hypotheses.py") `
    --confirmation $dataset `
    --output $output
if ($LASTEXITCODE -ne 0) {
    throw "CR-014 Stage 1B fresh Session confirmation failed."
}

Write-Output "CR-014 Stage 1B evaluated once. Stage 2, Runtime, and deployment remain unauthorized."
