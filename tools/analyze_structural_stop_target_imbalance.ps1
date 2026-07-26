param()

$ErrorActionPreference = "Stop"
$projectRoot = Split-Path -Parent $PSScriptRoot
$python = Join-Path $projectRoot "training\.venv\Scripts\python.exe"
$base = Join-Path $projectRoot "training\output\current_feed_xauusd_real_ticks_202001_202606"
$research = Join-Path $base "research"
$imp097 = Join-Path $research "current_feed_rr_rejection"
$output = Join-Path $research "structural_stop_target_imbalance"

$arguments = @{
    "imp097-details" = Join-Path $imp097 "current_feed_rr_rejection_records.csv"
    "imp097-root" = Join-Path $imp097 "current_feed_rr_rejection_root_cause.json"
    "stop-export" = Join-Path $research "current_feed_stop_ladder\XAU_AI_CURRENT_FEED_STOP_LADDERS.csv"
    "target-export" = Join-Path $research "current_feed_target_ladder\XAU_AI_CURRENT_FEED_TARGET_LADDERS.csv"
    "decisions" = Join-Path $base "source_artifacts\XAU_AI_SHADOW_BACKTEST_OBJECTIVE_DECISIONS_V4.csv"
}

foreach ($required in @($python) + $arguments.Values) {
    if (-not (Test-Path -LiteralPath $required)) {
        throw "IMP-098 required path not found: $required"
    }
}

New-Item -ItemType Directory -Force -Path $output | Out-Null
& $python (Join-Path $projectRoot "training\analyze_structural_stop_target_imbalance.py") `
    --imp097-details $arguments["imp097-details"] `
    --imp097-root $arguments["imp097-root"] `
    --stop-export $arguments["stop-export"] `
    --target-export $arguments["target-export"] `
    --decisions $arguments["decisions"] `
    --output (Join-Path $output "structural_stop_target_imbalance_root_cause.json") `
    --details (Join-Path $output "structural_stop_target_imbalance_records.csv")
if ($LASTEXITCODE -ne 0) {
    throw "IMP-098 structural imbalance analysis failed."
}
Write-Output "IMP-098 structural imbalance evidence written: $output"
