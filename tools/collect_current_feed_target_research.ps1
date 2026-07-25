$ErrorActionPreference = "Stop"
$projectRoot = Split-Path -Parent $PSScriptRoot
$python = Join-Path $projectRoot "training\.venv\Scripts\python.exe"
$root = Join-Path $projectRoot "training\output\current_feed_xauusd_real_ticks_202001_202606"
$research = Join-Path $root "research\current_feed_target_ladder"
$request = Join-Path $research "XAU_AI_CURRENT_FEED_TARGET_REQUESTS.csv"
$manifest = Join-Path $research "current_feed_target_request_manifest.json"
$export = Join-Path $research "XAU_AI_CURRENT_FEED_TARGET_LADDERS.csv"
$decisions = Join-Path $root "source_artifacts\XAU_AI_SHADOW_BACKTEST_OBJECTIVE_DECISIONS_V4.csv"
$report = Join-Path $research "current_feed_target_replay.json"

foreach ($required in @($python, $request, $manifest, $export, $decisions)) {
    if (-not (Test-Path -LiteralPath $required)) {
        throw "Current-feed Target collection input not found: $required"
    }
}
& $python (Join-Path $projectRoot "training\test_current_feed_target_replay.py")
if ($LASTEXITCODE -ne 0) { throw "Current-feed Target replay test failed." }
& $python (Join-Path $projectRoot "training\replay_current_feed_targets.py") `
    --request $request --request-manifest $manifest --export $export `
    --decisions $decisions --output $report
if ($LASTEXITCODE -ne 0) { throw "Current-feed Target replay failed." }
Write-Output "Current-feed Target export validated and replayed successfully."
