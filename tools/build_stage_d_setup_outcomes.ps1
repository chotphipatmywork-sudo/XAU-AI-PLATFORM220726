param(
    [string]$TerminalId = "D0E8209F77C8CF37AD8BF550E51FF075",
    [string]$AgentName = "Agent-127.0.0.1-3000",
    [string]$OutputName = "stage_d_setup_quality",
    [string]$QualityExclusions = "",
    [string]$SetupAuditPath = "",
    [string]$DecisionsPath = ""
)

$ErrorActionPreference = "Stop"
$projectRoot = Split-Path -Parent $PSScriptRoot
$python = Join-Path $projectRoot "training\.venv\Scripts\python.exe"
$testerFiles = Join-Path $env:APPDATA "MetaQuotes\Tester\$TerminalId\$AgentName\MQL5\Files"
$setupAudit = if ($SetupAuditPath) { $SetupAuditPath } else {
    Join-Path $testerFiles "XAU_AI_SHADOW_BACKTEST_OBJECTIVE_SETUP_AUDIT.csv"
}
$decisions = if ($DecisionsPath) { $DecisionsPath } else {
    Join-Path $testerFiles "XAU_AI_SHADOW_BACKTEST_OBJECTIVE_DECISIONS_V4.csv"
}
if (-not [System.IO.Path]::IsPathRooted($setupAudit)) {
    $setupAudit = Join-Path $projectRoot $setupAudit
}
if (-not [System.IO.Path]::IsPathRooted($decisions)) {
    $decisions = Join-Path $projectRoot $decisions
}
$outputRoot = Join-Path $projectRoot "training\output\$OutputName"
$dataset = Join-Path $outputRoot "XAU_AI_SETUP_OUTCOME_DATASET.csv"
$buildSummary = Join-Path $outputRoot "setup_outcome_build_summary.json"

foreach ($required in @($python, $setupAudit, $decisions)) {
    if (-not (Test-Path -LiteralPath $required)) {
        throw "Stage D required file not found: $required"
    }
}
if (-not (Test-Path -LiteralPath $outputRoot)) {
    New-Item -ItemType Directory -Path $outputRoot | Out-Null
}

$buildArguments = @(
    (Join-Path $projectRoot "training\build_setup_outcome_dataset.py"),
    "--setup-audit", $setupAudit,
    "--decisions", $decisions,
    "--output", $dataset,
    "--summary", $buildSummary
)
if ($QualityExclusions) {
    $qualityPath = $QualityExclusions
    if (-not [System.IO.Path]::IsPathRooted($qualityPath)) {
        $qualityPath = Join-Path $projectRoot $qualityPath
    }
    if (-not (Test-Path -LiteralPath $qualityPath)) {
        throw "Stage D quality-exclusion file not found: $qualityPath"
    }
    $buildArguments += @("--quality-exclusions", $qualityPath)
}
& $python @buildArguments
if ($LASTEXITCODE -ne 0) {
    throw "Stage D Setup Outcome build failed."
}

$build = Get-Content -LiteralPath $buildSummary -Raw | ConvertFrom-Json
if (-not $build.ready_for_train_split) {
    Write-Output "Stage D Dataset built safely, but training remains blocked."
    Write-Output ("Plans/trainable/target/non-target: {0}/{1}/{2}/{3}" -f `
        $build.structural_plans, $build.trainable_rows, `
        $build.outcome_distribution.TARGET_FIRST, `
        ($build.outcome_distribution.STOP_FIRST + $build.outcome_distribution.TIMEOUT))
    Write-Output ("Required trainable/target/non-target: {0}/{1}/{2}" -f `
        $build.minimum_trainable_rows, $build.minimum_target_rows, `
        $build.minimum_non_target_rows)
    Write-Output "Run a longer Objective Strategy Tester interval before Stage D splitting."
    exit 0
}

$train = Join-Path $outputRoot "XAU_AI_SETUP_OUTCOME_TRAIN.csv"
$validation = Join-Path $outputRoot "XAU_AI_SETUP_OUTCOME_VALIDATION.csv"
$test = Join-Path $outputRoot "XAU_AI_SETUP_OUTCOME_TEST.csv"
$splitSummary = Join-Path $outputRoot "setup_outcome_split_summary.json"
& $python (Join-Path $projectRoot "training\split_setup_outcome_dataset.py") `
    --dataset $dataset `
    --train $train `
    --validation $validation `
    --test $test `
    --summary $splitSummary
if ($LASTEXITCODE -ne 0) {
    throw "Stage D Setup Outcome split failed."
}

$split = Get-Content -LiteralPath $splitSummary -Raw | ConvertFrom-Json
if ($split.ready_for_train_only_ranking) {
    Write-Output "Stage D Setup Outcome Dataset and temporal split are ready."
    Write-Output "Validation and Test remain sealed; run the separate Train-only research tool."
} else {
    Write-Output "Stage D split completed, but Train readiness remains blocked."
}
