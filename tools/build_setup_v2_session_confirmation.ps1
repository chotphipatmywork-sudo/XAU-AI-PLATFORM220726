# XAU AI PLATFORM
# File: build_setup_v2_session_confirmation.ps1
# Layer: Tools / Offline Research
# Version: 1.0.0
# Purpose: Build a fresh post-cutoff Setup Outcome confirmation Dataset.

param(
    [string]$TerminalId = "D0E8209F77C8CF37AD8BF550E51FF075",
    [string]$AgentName = "Agent-127.0.0.1-3000",
    [string]$OutputName = "cr014_session_confirmation_after_20260626",
    [string]$QualityExclusions = ""
)

$ErrorActionPreference = "Stop"
$projectRoot = Split-Path -Parent $PSScriptRoot
$python = Join-Path $projectRoot "training\.venv\Scripts\python.exe"
$testerFiles = Join-Path $env:APPDATA "MetaQuotes\Tester\$TerminalId\$AgentName\MQL5\Files"
$setupAudit = Join-Path $testerFiles "XAU_AI_SHADOW_BACKTEST_OBJECTIVE_SETUP_AUDIT.csv"
$decisions = Join-Path $testerFiles "XAU_AI_SHADOW_BACKTEST_OBJECTIVE_DECISIONS_V4.csv"
$outputRoot = Join-Path $projectRoot "training\output\$OutputName"
$dataset = Join-Path $outputRoot "XAU_AI_SETUP_OUTCOME_CONFIRMATION.csv"
$summary = Join-Path $outputRoot "setup_outcome_confirmation_build_summary.json"

foreach ($required in @($python, $setupAudit, $decisions)) {
    if (-not (Test-Path -LiteralPath $required)) {
        throw "CR-014 confirmation source not found: $required"
    }
}
if (Test-Path -LiteralPath $dataset) {
    throw "CR-014 confirmation Dataset already exists. Do not overwrite untouched evidence: $dataset"
}
if (-not (Test-Path -LiteralPath $outputRoot)) {
    New-Item -ItemType Directory -Path $outputRoot | Out-Null
}

$arguments = @(
    (Join-Path $projectRoot "training\build_setup_outcome_dataset.py"),
    "--setup-audit", $setupAudit,
    "--decisions", $decisions,
    "--output", $dataset,
    "--summary", $summary
)
if ($QualityExclusions) {
    $qualityPath = $QualityExclusions
    if (-not [System.IO.Path]::IsPathRooted($qualityPath)) {
        $qualityPath = Join-Path $projectRoot $qualityPath
    }
    if (-not (Test-Path -LiteralPath $qualityPath)) {
        throw "CR-014 quality-exclusion file not found: $qualityPath"
    }
    $arguments += @("--quality-exclusions", $qualityPath)
}

& $python @arguments
if ($LASTEXITCODE -ne 0) {
    throw "CR-014 fresh Setup Outcome build failed."
}
Write-Output "CR-014 confirmation Dataset built. Run the confirmation tool only after readiness review."
