$ErrorActionPreference = "Stop"
$projectRoot = Split-Path -Parent $PSScriptRoot
$python = Join-Path $projectRoot "training\.venv\Scripts\python.exe"
$root = Join-Path $projectRoot "training\output\current_feed_xauusd_real_ticks_202001_202606\research\current_feed_lifecycle"
$request = Join-Path $root "XAU_AI_CURRENT_FEED_LIFECYCLE_REQUESTS.csv"
$manifest = Join-Path $root "current_feed_lifecycle_request_manifest.json"
$paths = Join-Path $root "XAU_AI_CURRENT_FEED_LIFECYCLE_M5_PATHS.csv"
$report = Join-Path $root "current_feed_lifecycle_replay.json"
foreach ($required in @($python, $request, $manifest, $paths)) {
    if (-not (Test-Path -LiteralPath $required)) {
        throw "Current-feed lifecycle collection input not found: $required"
    }
}
& $python (Join-Path $projectRoot "training\test_lifecycle_management_replay.py")
if ($LASTEXITCODE -ne 0) { throw "Lifecycle management replay test failed." }
& $python (Join-Path $projectRoot "training\replay_lifecycle_management.py") `
    --request $request --request-manifest $manifest `
    --m5-path-export $paths --output $report
if ($LASTEXITCODE -ne 0) { throw "Current-feed lifecycle replay failed." }
Write-Output "Current-feed lifecycle export validated and replayed successfully."
