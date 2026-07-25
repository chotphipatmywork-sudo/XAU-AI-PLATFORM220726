param(
    [string]$TrainPath = "training\output\cr015_pretrain_20200101_20210630\XAU_AI_SETUP_OUTCOME_AUGMENTED_TRAIN.csv",
    [string]$ReportPath = "training\output\effective_sample_audit_imp082\effective_sample_audit.json",
    [string]$ExpectedSha256 = "F31E6DED4E0AC3B20FDD7964D3E634902736C8AD3316AA15A4E63D5C3C7E9A7E"
)

$ErrorActionPreference = "Stop"
$projectRoot = Split-Path -Parent $PSScriptRoot
$python = Join-Path $projectRoot "training\.venv\Scripts\python.exe"
$auditScript = Join-Path $projectRoot "training\audit_effective_setup_sample.py"
$resolvedTrain = if ([System.IO.Path]::IsPathRooted($TrainPath)) {
    $TrainPath
} else {
    Join-Path $projectRoot $TrainPath
}
$resolvedReport = if ([System.IO.Path]::IsPathRooted($ReportPath)) {
    $ReportPath
} else {
    Join-Path $projectRoot $ReportPath
}

foreach ($required in @($python, $auditScript, $resolvedTrain)) {
    if (-not (Test-Path -LiteralPath $required)) {
        throw "Effective Sample audit required path not found: $required"
    }
}

& $python $auditScript `
    --train $resolvedTrain `
    --expected-sha256 $ExpectedSha256 `
    --output $resolvedReport
if ($LASTEXITCODE -ne 0) {
    throw "Effective Sample audit failed."
}
Write-Output "Effective Sample audit written: $resolvedReport"
