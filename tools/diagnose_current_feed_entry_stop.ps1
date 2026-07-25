$ErrorActionPreference = "Stop"
$projectRoot = Split-Path -Parent $PSScriptRoot
$python = Join-Path $projectRoot "training\.venv\Scripts\python.exe"
$root = Join-Path $projectRoot "training\output\current_feed_xauusd_real_ticks_202001_202606"
$research = Join-Path $root "research\current_feed_target_ladder"
$report = Join-Path $root "research\current_feed_entry_stop_diagnostic.json"
$arguments = @(
    (Join-Path $projectRoot "training\diagnose_current_feed_entry_stop.py"),
    "--request", (Join-Path $research "XAU_AI_CURRENT_FEED_TARGET_REQUESTS.csv"),
    "--request-manifest", (Join-Path $research "current_feed_target_request_manifest.json"),
    "--export", (Join-Path $research "XAU_AI_CURRENT_FEED_TARGET_LADDERS.csv"),
    "--setup-audit", (Join-Path $root "source_artifacts\XAU_AI_SHADOW_BACKTEST_OBJECTIVE_SETUP_AUDIT.csv"),
    "--decisions", (Join-Path $root "source_artifacts\XAU_AI_SHADOW_BACKTEST_OBJECTIVE_DECISIONS_V4.csv"),
    "--output", $report
)
& $python (Join-Path $projectRoot "training\test_current_feed_entry_stop.py")
if ($LASTEXITCODE -ne 0) { throw "Current-feed Entry/Stop focused test failed." }
& $python @arguments
if ($LASTEXITCODE -ne 0) { throw "Current-feed Entry/Stop diagnostic failed." }
Write-Output "Current-feed Train-only Entry/Stop diagnostic completed."
