param()

$ErrorActionPreference = "Stop"
$projectRoot = Split-Path -Parent $PSScriptRoot
$python = Join-Path $projectRoot "training\.venv\Scripts\python.exe"
$config = Join-Path $projectRoot "training\config\imp099_geometry_component_experiment_preregistration.json"
$output = Join-Path $projectRoot "training\output\imp099_geometry_component_experiment"

foreach ($required in @($python, $config)) {
    if (-not (Test-Path -LiteralPath $required)) {
        throw "IMP-099 execution required path not found: $required"
    }
}

New-Item -ItemType Directory -Force -Path $output | Out-Null
& $python (Join-Path $projectRoot "training\execute_imp099_geometry_component_experiment.py") `
    --config $config `
    --repository $projectRoot `
    --output (Join-Path $output "experiment_metrics.json") `
    --raw (Join-Path $output "raw_experiment_records.csv") `
    --validation (Join-Path $output "validation_results.json") `
    --gate (Join-Path $output "gate_result.json")
if ($LASTEXITCODE -ne 0) {
    throw "IMP-099 locked experiment execution failed."
}
Write-Output "IMP-099 execution evidence written: $output"
