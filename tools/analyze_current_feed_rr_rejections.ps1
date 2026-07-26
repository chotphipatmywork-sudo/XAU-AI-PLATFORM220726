param()

$ErrorActionPreference = "Stop"
$projectRoot = Split-Path -Parent $PSScriptRoot
$python = Join-Path $projectRoot "training\.venv\Scripts\python.exe"
$base = Join-Path $projectRoot "training\output\current_feed_xauusd_real_ticks_202001_202606"
$research = Join-Path $base "research"
$target = Join-Path $research "current_feed_target_ladder"
$stop = Join-Path $research "current_feed_stop_ladder"
$joint = Join-Path $research "current_feed_joint_geometry"
$output = Join-Path $research "current_feed_rr_rejection"

foreach ($required in @(
    $python,
    (Join-Path $target "XAU_AI_CURRENT_FEED_TARGET_REQUESTS.csv"),
    (Join-Path $target "current_feed_target_request_manifest.json"),
    (Join-Path $stop "XAU_AI_CURRENT_FEED_STOP_LADDERS.csv"),
    (Join-Path $target "XAU_AI_CURRENT_FEED_TARGET_LADDERS.csv"),
    (Join-Path $base "source_artifacts\XAU_AI_SHADOW_BACKTEST_OBJECTIVE_DECISIONS_V4.csv"),
    (Join-Path $joint "current_feed_joint_geometry.json")
)) {
    if (-not (Test-Path -LiteralPath $required)) {
        throw "IMP-097 required path not found: $required"
    }
}

New-Item -ItemType Directory -Force -Path $output | Out-Null
& $python (Join-Path $projectRoot "training\analyze_current_feed_rr_rejections.py") `
    --request (Join-Path $target "XAU_AI_CURRENT_FEED_TARGET_REQUESTS.csv") `
    --request-manifest (Join-Path $target "current_feed_target_request_manifest.json") `
    --stop-export (Join-Path $stop "XAU_AI_CURRENT_FEED_STOP_LADDERS.csv") `
    --target-export (Join-Path $target "XAU_AI_CURRENT_FEED_TARGET_LADDERS.csv") `
    --decisions (Join-Path $base "source_artifacts\XAU_AI_SHADOW_BACKTEST_OBJECTIVE_DECISIONS_V4.csv") `
    --joint-report (Join-Path $joint "current_feed_joint_geometry.json") `
    --output (Join-Path $output "current_feed_rr_rejection_root_cause.json") `
    --details (Join-Path $output "current_feed_rr_rejection_records.csv")
if ($LASTEXITCODE -ne 0) {
    throw "IMP-097 RR rejection root-cause analysis failed."
}
Write-Output "IMP-097 RR rejection root-cause evidence written: $output"
