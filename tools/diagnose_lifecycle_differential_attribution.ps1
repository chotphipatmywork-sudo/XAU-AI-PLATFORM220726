$ErrorActionPreference = "Stop"
$projectRoot = Split-Path -Parent $PSScriptRoot
$python = Join-Path $projectRoot "training\.venv\Scripts\python.exe"
$imp084 = Join-Path $projectRoot "training\output\lifecycle_m5_replay_imp084"
$request = Join-Path $imp084 "XAU_AI_LIFECYCLE_PATH_REQUESTS.csv"
$manifest = Join-Path $imp084 "lifecycle_path_request_manifest.json"
$export = Join-Path $imp084 "source_artifacts\XAU_AI_LIFECYCLE_M5_PATHS.csv"
$replay = Join-Path $imp084 "lifecycle_management_replay.json"
$outputRoot = Join-Path $projectRoot "training\output\lifecycle_differential_attribution_imp085"
$output = Join-Path $outputRoot "lifecycle_differential_attribution.json"

foreach ($required in @($python, $request, $manifest, $export, $replay)) {
    if (-not (Test-Path -LiteralPath $required)) {
        throw "Lifecycle differential attribution required path not found: $required"
    }
}

& $python (Join-Path $projectRoot "training\test_lifecycle_differential_attribution.py")
if ($LASTEXITCODE -ne 0) {
    throw "Lifecycle differential attribution focused test failed."
}

& $python (Join-Path $projectRoot "training\diagnose_lifecycle_differential_attribution.py") `
    --request $request `
    --request-manifest $manifest `
    --m5-path-export $export `
    --lifecycle-replay $replay `
    --expected-replay-sha256 "97675D0EBDF8ED85A88E6B118A9412F2513477E85DD6C84B38FFE309362D2630" `
    --output $output
if ($LASTEXITCODE -ne 0) {
    throw "Lifecycle differential attribution failed."
}

Write-Output "Lifecycle differential attribution written: $output"

