param([string]$TerminalId = "D0E8209F77C8CF37AD8BF550E51FF075")
$ErrorActionPreference = "Stop"
$projectRoot = Split-Path -Parent $PSScriptRoot
$python = Join-Path $projectRoot "training\.venv\Scripts\python.exe"
$root = Join-Path $projectRoot "training\output\current_feed_xauusd_real_ticks_202001_202606"
$target = Join-Path $root "research\current_feed_target_ladder"
$outputRoot = Join-Path $root "research\current_feed_lifecycle"
$request = Join-Path $outputRoot "XAU_AI_CURRENT_FEED_LIFECYCLE_REQUESTS.csv"
$manifest = Join-Path $outputRoot "current_feed_lifecycle_request_manifest.json"
$terminalFiles = Join-Path $env:APPDATA "MetaQuotes\Terminal\$TerminalId\MQL5\Files"
New-Item -ItemType Directory -Path $outputRoot -Force | Out-Null
New-Item -ItemType Directory -Path $terminalFiles -Force | Out-Null
& $python (Join-Path $projectRoot "training\test_current_feed_lifecycle_requests.py")
if ($LASTEXITCODE -ne 0) { throw "Current-feed lifecycle request test failed." }
& $python (Join-Path $projectRoot "training\build_current_feed_lifecycle_requests.py") `
    --target-request (Join-Path $target "XAU_AI_CURRENT_FEED_TARGET_REQUESTS.csv") `
    --target-manifest (Join-Path $target "current_feed_target_request_manifest.json") `
    --target-export (Join-Path $target "XAU_AI_CURRENT_FEED_TARGET_LADDERS.csv") `
    --decisions (Join-Path $root "source_artifacts\XAU_AI_SHADOW_BACKTEST_OBJECTIVE_DECISIONS_V4.csv") `
    --output $request --manifest $manifest
if ($LASTEXITCODE -ne 0) { throw "Current-feed lifecycle request build failed." }
$destination = Join-Path $terminalFiles "XAU_AI_CURRENT_FEED_LIFECYCLE_REQUESTS.csv"
Copy-Item -LiteralPath $request -Destination $destination -Force
if ((Get-FileHash -LiteralPath $request -Algorithm SHA256).Hash -ne
    (Get-FileHash -LiteralPath $destination -Algorithm SHA256).Hash) {
    throw "Current-feed lifecycle request copy hash mismatch."
}
Write-Output "Current-feed lifecycle requests prepared and copied by verified hash."
