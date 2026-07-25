param(
    [string]$TrainPath = "training\output\cr015_pretrain_20200101_20210630\XAU_AI_SETUP_OUTCOME_AUGMENTED_TRAIN.csv",
    [string]$EffectiveSampleAuditPath = "training\output\effective_sample_audit_imp082\effective_sample_audit.json",
    [string]$ReportPath = "training\output\entry_stop_expectancy_imp083\entry_stop_expectancy_diagnostic.json",
    [string]$ExpectedTrainSha256 = "F31E6DED4E0AC3B20FDD7964D3E634902736C8AD3316AA15A4E63D5C3C7E9A7E",
    [string]$ExpectedAuditSha256 = "2646BBD8E881B6BB7F8621E27D1933BE1376711C75558E046B9EA964A1393414"
)

$ErrorActionPreference = "Stop"
$projectRoot = Split-Path -Parent $PSScriptRoot
$python = Join-Path $projectRoot "training\.venv\Scripts\python.exe"
$diagnosticScript = Join-Path $projectRoot "training\diagnose_entry_stop_expectancy.py"

function Resolve-ProjectPath([string]$PathValue) {
    if ([System.IO.Path]::IsPathRooted($PathValue)) {
        return $PathValue
    }
    return Join-Path $projectRoot $PathValue
}

$resolvedTrain = Resolve-ProjectPath $TrainPath
$resolvedAudit = Resolve-ProjectPath $EffectiveSampleAuditPath
$resolvedReport = Resolve-ProjectPath $ReportPath
foreach ($required in @($python, $diagnosticScript, $resolvedTrain, $resolvedAudit)) {
    if (-not (Test-Path -LiteralPath $required)) {
        throw "Entry/Stop diagnostic required path not found: $required"
    }
}

& $python $diagnosticScript `
    --train $resolvedTrain `
    --expected-train-sha256 $ExpectedTrainSha256 `
    --effective-sample-audit $resolvedAudit `
    --expected-audit-sha256 $ExpectedAuditSha256 `
    --output $resolvedReport
if ($LASTEXITCODE -ne 0) {
    throw "Entry/Stop expectancy diagnostic failed."
}
Write-Output "Entry/Stop expectancy diagnostic written: $resolvedReport"
