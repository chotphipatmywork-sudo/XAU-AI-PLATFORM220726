$ErrorActionPreference = "Stop"
$projectRoot = Split-Path -Parent $PSScriptRoot
$python = Join-Path $projectRoot "training\.venv\Scripts\python.exe"
$pretrainRoot = Join-Path $projectRoot "training\output\cr015_pretrain_20200101_20210630"
$mainRoot = Join-Path $projectRoot "training\output\objective_minimum_reclaim_finalized_202107_202606"
$train = Join-Path $pretrainRoot "XAU_AI_SETUP_OUTCOME_AUGMENTED_TRAIN.csv"
$audit = Join-Path $projectRoot "training\output\effective_sample_audit_imp082\effective_sample_audit.json"
$pretrainSetup = Join-Path $pretrainRoot "source_artifacts\XAU_AI_SHADOW_BACKTEST_OBJECTIVE_SETUP_AUDIT.csv"
$mainSetup = Join-Path $mainRoot "source_artifacts\XAU_AI_SHADOW_BACKTEST_OBJECTIVE_SETUP_AUDIT.csv"
$manifest = Join-Path $projectRoot "training\output\past_only_target_replay_train_202001_202507\past_only_target_request_manifest.json"
$imp086 = Join-Path $projectRoot "training\output\canonical_setup_response_attribution_imp086\canonical_setup_response_attribution.json"
$outputRoot = Join-Path $projectRoot "training\output\entry_geometry_outcome_attribution_imp087"
$output = Join-Path $outputRoot "entry_geometry_outcome_attribution.json"

foreach ($required in @(
    $python, $train, $audit, $pretrainSetup, $mainSetup, $manifest, $imp086
)) {
    if (-not (Test-Path -LiteralPath $required)) {
        throw "Entry geometry outcome attribution required path not found: $required"
    }
}

& $python (Join-Path $projectRoot "training\test_entry_geometry_outcome_attribution.py")
if ($LASTEXITCODE -ne 0) {
    throw "Entry geometry outcome attribution focused test failed."
}

& $python (Join-Path $projectRoot "training\entry_geometry_outcome_attribution.py") `
    --train $train `
    --expected-train-sha256 "F31E6DED4E0AC3B20FDD7964D3E634902736C8AD3316AA15A4E63D5C3C7E9A7E" `
    --effective-sample-audit $audit `
    --expected-audit-sha256 "2646BBD8E881B6BB7F8621E27D1933BE1376711C75558E046B9EA964A1393414" `
    --pretrain-setup $pretrainSetup `
    --expected-pretrain-setup-sha256 "A406B7EDADA6CACB5691487341294E5F950FF262D1CE8AE26EF958843338B8B8" `
    --main-setup $mainSetup `
    --expected-main-setup-sha256 "A8463D7F118CB52A7B514099FF8B8839F3C2401ECA5A66F50376C4D87C1C9F7A" `
    --past-only-target-manifest $manifest `
    --expected-manifest-sha256 "2D6A559F03245D40C0CB84ACAC1CC1C97D6F2017875ED3DF513D5C54F9C4C6BF" `
    --imp086-attribution $imp086 `
    --expected-imp086-sha256 "A281F29D0CD25E9DCE894BF03F486BA6F7426014DF4F1BFD31DFA29BAA0DBC27" `
    --output $output
if ($LASTEXITCODE -ne 0) {
    throw "Entry geometry outcome attribution failed."
}

Write-Output "Entry geometry outcome attribution written: $output"
