param(
    [string]$MetricsPath = "training\config\research_scorecard_imp080_current.json",
    [string]$ScorecardPath = "training\output\research_scorecard_current\research_scorecard.json",
    [string]$ReferencePath = ""
)

$ErrorActionPreference = "Stop"
$projectRoot = Split-Path -Parent $PSScriptRoot
$python = Join-Path $projectRoot "training\.venv\Scripts\python.exe"
$resolvedMetrics = if ([System.IO.Path]::IsPathRooted($MetricsPath)) {
    $MetricsPath
} else {
    Join-Path $projectRoot $MetricsPath
}
$resolvedScorecard = if ([System.IO.Path]::IsPathRooted($ScorecardPath)) {
    $ScorecardPath
} else {
    Join-Path $projectRoot $ScorecardPath
}

foreach ($required in @($python, $resolvedMetrics)) {
    if (-not (Test-Path -LiteralPath $required)) {
        throw "Research Scorecard required path not found: $required"
    }
}

$scorecardScript = Join-Path $projectRoot "training\research_scorecard.py"
$scorecardCliArgs = @(
    '--input', $resolvedMetrics,
    '--output', $resolvedScorecard
)
if ($ReferencePath) {
    $resolvedReference = if ([System.IO.Path]::IsPathRooted($ReferencePath)) {
        $ReferencePath
    } else {
        Join-Path $projectRoot $ReferencePath
    }
    if (-not (Test-Path -LiteralPath $resolvedReference)) {
        throw "Research Scorecard reference not found: $resolvedReference"
    }
    $scorecardCliArgs += @('--reference', $resolvedReference)
}
& $python $scorecardScript @scorecardCliArgs
if ($LASTEXITCODE -ne 0) {
    throw "Research Scorecard build failed."
}
Write-Output "Research Scorecard written: $resolvedScorecard"
