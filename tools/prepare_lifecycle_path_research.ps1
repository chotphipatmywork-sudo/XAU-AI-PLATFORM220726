param(
    [string]$TerminalId = "D0E8209F77C8CF37AD8BF550E51FF075"
)

$ErrorActionPreference = "Stop"
$projectRoot = Split-Path -Parent $PSScriptRoot
$python = Join-Path $projectRoot "training\.venv\Scripts\python.exe"
$outputRoot = Join-Path $projectRoot "training\output\lifecycle_m5_replay_imp084"
$train = Join-Path $projectRoot "training\output\cr015_pretrain_20200101_20210630\XAU_AI_SETUP_OUTCOME_AUGMENTED_TRAIN.csv"
$audit = Join-Path $projectRoot "training\output\effective_sample_audit_imp082\effective_sample_audit.json"
$request = Join-Path $outputRoot "XAU_AI_LIFECYCLE_PATH_REQUESTS.csv"
$manifest = Join-Path $outputRoot "lifecycle_path_request_manifest.json"
$terminalFiles = Join-Path $env:APPDATA "MetaQuotes\Terminal\$TerminalId\MQL5\Files"

foreach ($required in @($python, $train, $audit)) {
    if (-not (Test-Path -LiteralPath $required)) {
        throw "Lifecycle path preparation required path not found: $required"
    }
}
New-Item -ItemType Directory -Path $outputRoot -Force | Out-Null
New-Item -ItemType Directory -Path $terminalFiles -Force | Out-Null

& $python (Join-Path $projectRoot "training\build_lifecycle_path_requests.py") `
    --train $train `
    --expected-train-sha256 "F31E6DED4E0AC3B20FDD7964D3E634902736C8AD3316AA15A4E63D5C3C7E9A7E" `
    --effective-sample-audit $audit `
    --expected-audit-sha256 "2646BBD8E881B6BB7F8621E27D1933BE1376711C75558E046B9EA964A1393414" `
    --output $request `
    --manifest $manifest
if ($LASTEXITCODE -ne 0) {
    throw "Lifecycle path request build failed."
}

$destination = Join-Path $terminalFiles "XAU_AI_LIFECYCLE_PATH_REQUESTS.csv"
Copy-Item -LiteralPath $request -Destination $destination -Force
if ((Get-FileHash -LiteralPath $request -Algorithm SHA256).Hash -ne
    (Get-FileHash -LiteralPath $destination -Algorithm SHA256).Hash) {
    throw "Lifecycle path request MT5 copy hash mismatch."
}
Write-Output "Lifecycle M5 path requests prepared and copied to MT5 Files."
Write-Output $destination
