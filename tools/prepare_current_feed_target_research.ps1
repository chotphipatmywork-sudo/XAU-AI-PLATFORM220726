param(
    [string]$TerminalId = "D0E8209F77C8CF37AD8BF550E51FF075"
)

$ErrorActionPreference = "Stop"
$projectRoot = Split-Path -Parent $PSScriptRoot
$python = Join-Path $projectRoot "training\.venv\Scripts\python.exe"
$evidenceRoot = Join-Path $projectRoot "training\output\current_feed_xauusd_real_ticks_202001_202606"
$setupAudit = Join-Path $evidenceRoot "source_artifacts\XAU_AI_SHADOW_BACKTEST_OBJECTIVE_SETUP_AUDIT.csv"
$outputRoot = Join-Path $evidenceRoot "research\current_feed_target_ladder"
$request = Join-Path $outputRoot "XAU_AI_CURRENT_FEED_TARGET_REQUESTS.csv"
$manifest = Join-Path $outputRoot "current_feed_target_request_manifest.json"
$terminalFiles = Join-Path $env:APPDATA "MetaQuotes\Terminal\$TerminalId\MQL5\Files"

foreach ($required in @($python, $setupAudit)) {
    if (-not (Test-Path -LiteralPath $required)) {
        throw "Current-feed Target research input not found: $required"
    }
}

New-Item -ItemType Directory -Path $outputRoot -Force | Out-Null
New-Item -ItemType Directory -Path $terminalFiles -Force | Out-Null
& $python (Join-Path $projectRoot "training\test_current_feed_target_requests.py")
if ($LASTEXITCODE -ne 0) { throw "Current-feed Target request test failed." }
& $python (Join-Path $projectRoot "training\build_current_feed_target_requests.py") `
    --setup-audit $setupAudit --output $request --manifest $manifest
if ($LASTEXITCODE -ne 0) { throw "Current-feed Target request build failed." }

$destination = Join-Path $terminalFiles "XAU_AI_CURRENT_FEED_TARGET_REQUESTS.csv"
Copy-Item -LiteralPath $request -Destination $destination -Force
if ((Get-FileHash -LiteralPath $request -Algorithm SHA256).Hash -ne
    (Get-FileHash -LiteralPath $destination -Algorithm SHA256).Hash) {
    throw "Current-feed Target request MT5 copy hash mismatch."
}
Write-Output "Current-feed Target requests prepared and copied by verified hash."
