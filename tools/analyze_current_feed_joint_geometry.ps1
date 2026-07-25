$ErrorActionPreference = "Stop"
$projectRoot = Split-Path -Parent $PSScriptRoot
$python = Join-Path $projectRoot "training\.venv\Scripts\python.exe"
$root = Join-Path $projectRoot "training\output\current_feed_xauusd_real_ticks_202001_202606"
$target = Join-Path $root "research\current_feed_target_ladder"
$stop = Join-Path $root "research\current_feed_stop_ladder"
$outputDirectory = Join-Path $root "research\current_feed_joint_geometry"
$output = Join-Path $outputDirectory "current_feed_joint_geometry.json"
& $python (Join-Path $projectRoot "training\test_current_feed_joint_geometry.py")
if ($LASTEXITCODE -ne 0) { throw "Joint-geometry focused test failed." }
& $python (Join-Path $projectRoot "training\analyze_current_feed_joint_geometry.py") `
    --request (Join-Path $target "XAU_AI_CURRENT_FEED_TARGET_REQUESTS.csv") `
    --request-manifest (Join-Path $target "current_feed_target_request_manifest.json") `
    --stop-export (Join-Path $stop "XAU_AI_CURRENT_FEED_STOP_LADDERS.csv") `
    --target-export (Join-Path $target "XAU_AI_CURRENT_FEED_TARGET_LADDERS.csv") `
    --decisions (Join-Path $root "source_artifacts\XAU_AI_SHADOW_BACKTEST_OBJECTIVE_DECISIONS_V4.csv") `
    --output $output
if ($LASTEXITCODE -ne 0) { throw "Joint-geometry analysis failed." }
Write-Output "Current-feed joint-geometry frontier completed."
