$ErrorActionPreference = "Stop"
$projectRoot = Split-Path -Parent $PSScriptRoot
$python = Join-Path $projectRoot "training\.venv\Scripts\python.exe"
$train = Join-Path $projectRoot "training\output\cr015_pretrain_20200101_20210630\XAU_AI_SETUP_OUTCOME_AUGMENTED_TRAIN.csv"
$audit = Join-Path $projectRoot "training\output\effective_sample_audit_imp082\effective_sample_audit.json"
$imp084 = Join-Path $projectRoot "training\output\lifecycle_m5_replay_imp084"
$request = Join-Path $imp084 "XAU_AI_LIFECYCLE_PATH_REQUESTS.csv"
$manifest = Join-Path $imp084 "lifecycle_path_request_manifest.json"
$export = Join-Path $imp084 "source_artifacts\XAU_AI_LIFECYCLE_M5_PATHS.csv"
$imp085 = Join-Path $projectRoot "training\output\lifecycle_differential_attribution_imp085\lifecycle_differential_attribution.json"
$outputRoot = Join-Path $projectRoot "training\output\canonical_setup_response_attribution_imp086"
$output = Join-Path $outputRoot "canonical_setup_response_attribution.json"

foreach ($required in @($python, $train, $audit, $request, $manifest, $export, $imp085)) {
    if (-not (Test-Path -LiteralPath $required)) {
        throw "Canonical Setup response attribution required path not found: $required"
    }
}

& $python (Join-Path $projectRoot "training\test_canonical_setup_response_attribution.py")
if ($LASTEXITCODE -ne 0) {
    throw "Canonical Setup response attribution focused test failed."
}

& $python (Join-Path $projectRoot "training\canonical_setup_response_attribution.py") `
    --train $train `
    --expected-train-sha256 "F31E6DED4E0AC3B20FDD7964D3E634902736C8AD3316AA15A4E63D5C3C7E9A7E" `
    --effective-sample-audit $audit `
    --expected-audit-sha256 "2646BBD8E881B6BB7F8621E27D1933BE1376711C75558E046B9EA964A1393414" `
    --request $request `
    --request-manifest $manifest `
    --m5-path-export $export `
    --imp085-attribution $imp085 `
    --expected-imp085-sha256 "67DD536BC9C56C3E971EF4E349872AB6C59AE335AF39BE479BB27E811005CA52" `
    --output $output
if ($LASTEXITCODE -ne 0) {
    throw "Canonical Setup response attribution failed."
}

Write-Output "Canonical Setup response attribution written: $output"

