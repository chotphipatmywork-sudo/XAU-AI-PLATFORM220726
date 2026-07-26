param()

$ErrorActionPreference = "Stop"
$projectRoot = Split-Path -Parent $PSScriptRoot
$python = Join-Path $projectRoot "training\.venv\Scripts\python.exe"
$config = Join-Path $projectRoot "training\config\imp099_geometry_component_experiment_preregistration.json"
$output = Join-Path $projectRoot "training\output\imp099_preregistration\preregistration_validation.json"

foreach ($required in @($python, $config)) {
    if (-not (Test-Path -LiteralPath $required)) {
        throw "IMP-099 required path not found: $required"
    }
}

& $python (Join-Path $projectRoot "training\validate_imp099_preregistration.py") `
    --config $config `
    --repository $projectRoot `
    --output $output
if ($LASTEXITCODE -ne 0) {
    throw "IMP-099 preregistration validation failed."
}
Write-Output "IMP-099 preregistration validation written: $output"
