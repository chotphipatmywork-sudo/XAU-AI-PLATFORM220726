param([string]$TerminalId = "D0E8209F77C8CF37AD8BF550E51FF075")
$ErrorActionPreference = "Stop"
$projectRoot = Split-Path -Parent $PSScriptRoot
$python = Join-Path $projectRoot "training\.venv\Scripts\python.exe"
$root = Join-Path $projectRoot "training\output\current_feed_xauusd_real_ticks_202001_202606"
$target = Join-Path $root "research\current_feed_target_ladder"
$stop = Join-Path $root "research\current_feed_stop_ladder"
$joint = Join-Path $root "research\current_feed_joint_m5"
$request = Join-Path $joint "XAU_AI_CURRENT_FEED_JOINT_M5_REQUESTS.csv"
$manifest = Join-Path $joint "current_feed_joint_m5_request_manifest.json"
$terminalFiles = Join-Path $env:APPDATA "MetaQuotes\Terminal\$TerminalId\MQL5\Files"
New-Item -ItemType Directory -Force -Path $joint,$terminalFiles | Out-Null
& $python (Join-Path $projectRoot "training\build_current_feed_joint_m5_requests.py") `
 --request (Join-Path $target "XAU_AI_CURRENT_FEED_TARGET_REQUESTS.csv") `
 --request-manifest (Join-Path $target "current_feed_target_request_manifest.json") `
 --stop-export (Join-Path $stop "XAU_AI_CURRENT_FEED_STOP_LADDERS.csv") `
 --target-export (Join-Path $target "XAU_AI_CURRENT_FEED_TARGET_LADDERS.csv") `
 --decisions (Join-Path $root "source_artifacts\XAU_AI_SHADOW_BACKTEST_OBJECTIVE_DECISIONS_V4.csv") `
 --output $request --manifest $manifest
if ($LASTEXITCODE -ne 0) { throw "Joint M5 request build failed." }
$destination = Join-Path $terminalFiles "XAU_AI_CURRENT_FEED_JOINT_M5_REQUESTS.csv"
Copy-Item -LiteralPath $request -Destination $destination -Force
if ((Get-FileHash $request -Algorithm SHA256).Hash -ne (Get-FileHash $destination -Algorithm SHA256).Hash) {
 throw "Joint M5 request copy hash mismatch."
}
Write-Output "Joint M5 requests prepared and copied: 76."
