$ErrorActionPreference = "Stop"
$projectRoot = Split-Path -Parent $PSScriptRoot
$python = Join-Path $projectRoot "training\.venv\Scripts\python.exe"
$research = Join-Path $projectRoot "training\output\current_feed_xauusd_real_ticks_202001_202606\research"
$source = Join-Path $research "current_feed_stop_ladder\current_feed_stop_replay.json"
$outputDirectory = Join-Path $research "current_feed_direction_asymmetry"
$output = Join-Path $outputDirectory "current_feed_direction_asymmetry.json"
if (-not (Test-Path -LiteralPath $python)) { throw "Project Python was not found." }
if (-not (Test-Path -LiteralPath $source)) { throw "Stop replay report was not found." }
& $python (Join-Path $projectRoot "training\test_current_feed_direction_asymmetry.py")
if ($LASTEXITCODE -ne 0) { throw "Direction-asymmetry focused test failed." }
& $python (Join-Path $projectRoot "training\analyze_current_feed_direction_asymmetry.py") `
    --stop-replay $source --output $output
if ($LASTEXITCODE -ne 0) { throw "Direction-asymmetry analysis failed." }
Write-Output "Current-feed direction-asymmetry analysis completed."
