# XAU AI PLATFORM
# File: run_objective_setup_failure_diagnostic.ps1
# Layer: Tools / Offline Research
# Version: 1.0.0
# Purpose: Run frozen Stage D Train-only Objective Setup failure diagnostics.

$ErrorActionPreference = "Stop"
$projectRoot = Split-Path -Parent $PSScriptRoot
$python = Join-Path $projectRoot "training\.venv\Scripts\python.exe"
$evidenceRoot = Join-Path $projectRoot "training\output\stage_d_setup_quality_real_ticks_202107_202606"
$train = Join-Path $evidenceRoot "XAU_AI_SETUP_OUTCOME_TRAIN.csv"
$setupAudit = Join-Path $evidenceRoot "source_real_ticks_202107_202606\XAU_AI_SHADOW_BACKTEST_OBJECTIVE_SETUP_AUDIT.csv"
$output = Join-Path $evidenceRoot "research\objective_setup_failure\objective_setup_failure_diagnostic.json"

foreach ($required in @($python, $train, $setupAudit)) {
    if (-not (Test-Path -LiteralPath $required)) {
        throw "Objective Setup failure diagnostic input not found: $required"
    }
}

& $python (Join-Path $projectRoot "training\test_objective_setup_failure_diagnostic.py")
if ($LASTEXITCODE -ne 0) {
    throw "Objective Setup failure focused test failed."
}

& $python (Join-Path $projectRoot "training\diagnose_objective_setup_failures.py") `
    --train $train `
    --setup-audit $setupAudit `
    --output $output
if ($LASTEXITCODE -ne 0) {
    throw "Objective Setup Train-only failure diagnostic failed."
}

Write-Output "Objective Setup failure diagnostic completed. Runtime and deployment remain unchanged."
