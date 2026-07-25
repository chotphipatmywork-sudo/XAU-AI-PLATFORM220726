param(
    [string]$TerminalId = "D0E8209F77C8CF37AD8BF550E51FF075"
)

$ErrorActionPreference = "Stop"
$projectRoot = Split-Path -Parent $PSScriptRoot
$python = Join-Path $projectRoot "training\.venv\Scripts\python.exe"
$outputRoot = Join-Path $projectRoot "training\output\past_only_target_replay_train_202001_202507"
$request = Join-Path $outputRoot "XAU_AI_PAST_ONLY_TARGET_REQUESTS.csv"
$manifest = Join-Path $outputRoot "past_only_target_request_manifest.json"
$terminalFiles = Join-Path $env:APPDATA "MetaQuotes\Terminal\$TerminalId\MQL5\Files"

foreach ($required in @(
    $python,
    (Join-Path $projectRoot "training\output\cr015_pretrain_20200101_20210630\source_artifacts\XAU_AI_SHADOW_BACKTEST_OBJECTIVE_SETUP_AUDIT.csv"),
    (Join-Path $projectRoot "training\output\cr015_pretrain_20200101_20210630\source_artifacts\XAU_AI_SHADOW_BACKTEST_OBJECTIVE_DECISIONS_V4.csv"),
    (Join-Path $projectRoot "training\output\objective_minimum_reclaim_finalized_202107_202606\source_artifacts\XAU_AI_SHADOW_BACKTEST_OBJECTIVE_SETUP_AUDIT.csv"),
    (Join-Path $projectRoot "training\output\objective_minimum_reclaim_finalized_202107_202606\source_artifacts\XAU_AI_SHADOW_BACKTEST_OBJECTIVE_DECISIONS_V4.csv"),
    (Join-Path $projectRoot "training\output\cr015_pretrain_20200101_20210630\XAU_AI_SETUP_OUTCOME_AUGMENTED_TRAIN.csv"),
    (Join-Path $projectRoot "training\config\cr015_real_tick_quality_exclusions_202001_202106.json"),
    (Join-Path $projectRoot "training\config\stage_d_real_tick_quality_exclusions_202107_202606.json"),
    (Join-Path $projectRoot "training\output\objective_minimum_reclaim_finalized_202107_202606\setup_outcome_split_summary.json")
)) {
    if (-not (Test-Path -LiteralPath $required)) {
        throw "Past-only Target research required path not found: $required"
    }
}

New-Item -ItemType Directory -Path $outputRoot -Force | Out-Null
New-Item -ItemType Directory -Path $terminalFiles -Force | Out-Null
& $python (Join-Path $projectRoot "training\build_past_only_target_requests.py") `
    --pretrain-setup (Join-Path $projectRoot "training\output\cr015_pretrain_20200101_20210630\source_artifacts\XAU_AI_SHADOW_BACKTEST_OBJECTIVE_SETUP_AUDIT.csv") `
    --pretrain-decisions (Join-Path $projectRoot "training\output\cr015_pretrain_20200101_20210630\source_artifacts\XAU_AI_SHADOW_BACKTEST_OBJECTIVE_DECISIONS_V4.csv") `
    --main-setup (Join-Path $projectRoot "training\output\objective_minimum_reclaim_finalized_202107_202606\source_artifacts\XAU_AI_SHADOW_BACKTEST_OBJECTIVE_SETUP_AUDIT.csv") `
    --main-decisions (Join-Path $projectRoot "training\output\objective_minimum_reclaim_finalized_202107_202606\source_artifacts\XAU_AI_SHADOW_BACKTEST_OBJECTIVE_DECISIONS_V4.csv") `
    --augmented-train (Join-Path $projectRoot "training\output\cr015_pretrain_20200101_20210630\XAU_AI_SETUP_OUTCOME_AUGMENTED_TRAIN.csv") `
    --pretrain-exclusions (Join-Path $projectRoot "training\config\cr015_real_tick_quality_exclusions_202001_202106.json") `
    --main-exclusions (Join-Path $projectRoot "training\config\stage_d_real_tick_quality_exclusions_202107_202606.json") `
    --split-summary (Join-Path $projectRoot "training\output\objective_minimum_reclaim_finalized_202107_202606\setup_outcome_split_summary.json") `
    --output $request `
    --manifest $manifest
if ($LASTEXITCODE -ne 0) {
    throw "Past-only Target request build failed."
}

$destination = Join-Path $terminalFiles "XAU_AI_PAST_ONLY_TARGET_REQUESTS.csv"
Copy-Item -LiteralPath $request -Destination $destination -Force
if ((Get-FileHash -LiteralPath $request -Algorithm SHA256).Hash -ne
    (Get-FileHash -LiteralPath $destination -Algorithm SHA256).Hash) {
    throw "Past-only Target request MT5 copy hash mismatch."
}

Write-Output "Past-only Target requests prepared and copied to MT5 Files."
Write-Output $destination

