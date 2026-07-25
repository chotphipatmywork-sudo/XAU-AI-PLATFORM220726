# XAU AI PLATFORM
# File: diagnose_current_feed_setup_funnel.ps1
# Layer: Tools / Offline Research
# Version: 1.0.0
# Purpose: Run the hash-locked current-feed Train-only Setup funnel diagnostic.

$ErrorActionPreference = "Stop"
$projectRoot = Split-Path -Parent $PSScriptRoot
$python = Join-Path $projectRoot "training\.venv\Scripts\python.exe"
$evidenceRoot = Join-Path $projectRoot "training\output\current_feed_xauusd_real_ticks_202001_202606"
$setupAudit = Join-Path $evidenceRoot "source_artifacts\XAU_AI_SHADOW_BACKTEST_OBJECTIVE_SETUP_AUDIT.csv"
$output = Join-Path $evidenceRoot "research\current_feed_setup_funnel.json"

foreach ($required in @($python, $setupAudit)) {
    if (-not (Test-Path -LiteralPath $required)) {
        throw "Current-feed Setup funnel input not found: $required"
    }
}

& $python (Join-Path $projectRoot "training\test_current_feed_setup_funnel.py")
if ($LASTEXITCODE -ne 0) {
    throw "Current-feed Setup funnel focused test failed."
}

& $python (Join-Path $projectRoot "training\diagnose_current_feed_setup_funnel.py") `
    --setup-audit $setupAudit --output $output
if ($LASTEXITCODE -ne 0) {
    throw "Current-feed Setup funnel diagnostic failed."
}

Write-Output "Current-feed Train-only Setup funnel diagnostic completed."
Write-Output "Validation/Test remain sealed; Runtime and deployment are unchanged."
