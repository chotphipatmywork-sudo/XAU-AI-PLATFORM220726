param(
    [string]$TerminalId = "D0E8209F77C8CF37AD8BF550E51FF075"
)

$ErrorActionPreference = "Stop"
$projectRoot = Split-Path -Parent $PSScriptRoot
$python = Join-Path $projectRoot "training\.venv\Scripts\python.exe"
$outputRoot = Join-Path $projectRoot "training\output\past_only_target_replay_train_202001_202507"
$sourceRoot = Join-Path $outputRoot "source_artifacts"
$request = Join-Path $outputRoot "XAU_AI_PAST_ONLY_TARGET_REQUESTS.csv"
$manifest = Join-Path $outputRoot "past_only_target_request_manifest.json"
$terminalFiles = Join-Path $env:APPDATA "MetaQuotes\Terminal\$TerminalId\MQL5\Files"
$terminalExport = Join-Path $terminalFiles "XAU_AI_PAST_ONLY_TARGET_LADDERS.csv"
$export = Join-Path $sourceRoot "XAU_AI_PAST_ONLY_TARGET_LADDERS.csv"
$report = Join-Path $outputRoot "past_only_target_replay.json"

foreach ($required in @($python, $request, $manifest, $terminalExport)) {
    if (-not (Test-Path -LiteralPath $required)) {
        throw "Past-only Target collection required path not found: $required"
    }
}
New-Item -ItemType Directory -Path $sourceRoot -Force | Out-Null
Copy-Item -LiteralPath $terminalExport -Destination $export -Force

& $python (Join-Path $projectRoot "training\replay_past_only_targets.py") `
    --request $request `
    --request-manifest $manifest `
    --export $export `
    --pretrain-decisions (Join-Path $projectRoot "training\output\cr015_pretrain_20200101_20210630\source_artifacts\XAU_AI_SHADOW_BACKTEST_OBJECTIVE_DECISIONS_V4.csv") `
    --main-decisions (Join-Path $projectRoot "training\output\objective_minimum_reclaim_finalized_202107_202606\source_artifacts\XAU_AI_SHADOW_BACKTEST_OBJECTIVE_DECISIONS_V4.csv") `
    --pretrain-exclusions (Join-Path $projectRoot "training\config\cr015_real_tick_quality_exclusions_202001_202106.json") `
    --main-exclusions (Join-Path $projectRoot "training\config\stage_d_real_tick_quality_exclusions_202107_202606.json") `
    --split-summary (Join-Path $projectRoot "training\output\objective_minimum_reclaim_finalized_202107_202606\setup_outcome_split_summary.json") `
    --output $report
if ($LASTEXITCODE -ne 0) {
    throw "Past-only Target Train-only replay failed."
}

Write-Output "Past-only Target export collected and replayed successfully."
Write-Output $report

