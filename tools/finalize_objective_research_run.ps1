param(
    [string]$TerminalId = "D0E8209F77C8CF37AD8BF550E51FF075",
    [string]$AgentName = "Agent-127.0.0.1-3000",
    [string]$OutputName = "",
    [string]$QualityExclusions = "training\config\stage_d_real_tick_quality_exclusions_202107_202606.json",
    [string]$ReferenceRoot = "training\output\stage_d_setup_quality_real_ticks_202107_202606",
    [string]$LogPath = ""
)

$ErrorActionPreference = "Stop"
$projectRoot = Split-Path -Parent $PSScriptRoot
$python = Join-Path $projectRoot "training\.venv\Scripts\python.exe"
if (-not $OutputName) {
    $OutputName = "objective_research_" + (Get-Date -Format "yyyyMMdd_HHmmss")
}
$outputRoot = Join-Path $projectRoot "training\output\$OutputName"
$sourceRoot = Join-Path $outputRoot "source_artifacts"
$agentRoot = Join-Path $env:APPDATA "MetaQuotes\Tester\$TerminalId\$AgentName"
$testerFiles = Join-Path $agentRoot "MQL5\Files"
$qualityPath = if ([System.IO.Path]::IsPathRooted($QualityExclusions)) {
    $QualityExclusions
} else { Join-Path $projectRoot $QualityExclusions }
$referencePath = if ([System.IO.Path]::IsPathRooted($ReferenceRoot)) {
    $ReferenceRoot
} else { Join-Path $projectRoot $ReferenceRoot }
if (-not $LogPath) {
    $latestLog = Get-ChildItem (Join-Path $agentRoot "logs") -File -Filter "*.log" |
        Sort-Object LastWriteTime -Descending | Select-Object -First 1
    if (-not $latestLog) { throw "No MT5 Tester log was found." }
    $LogPath = $latestLog.FullName
} elseif (-not [System.IO.Path]::IsPathRooted($LogPath)) {
    $LogPath = Join-Path $projectRoot $LogPath
}

foreach ($required in @($python, $qualityPath, $referencePath, $LogPath)) {
    if (-not (Test-Path -LiteralPath $required)) {
        throw "Objective research finalizer required path not found: $required"
    }
}

New-Item -ItemType Directory -Path $sourceRoot -Force | Out-Null
$artifactNames = @(
    "XAU_AI_SHADOW_BACKTEST_OBJECTIVE_REPORT.csv",
    "XAU_AI_SHADOW_BACKTEST_OBJECTIVE_SETUP_AUDIT.csv",
    "XAU_AI_SHADOW_BACKTEST_OBJECTIVE_DECISIONS_V4.csv",
    "XAU_AI_SHADOW_BACKTEST_OBJECTIVE_EXECUTION_AUDIT.csv"
)
$manifestArtifacts = @()
foreach ($name in $artifactNames) {
    $source = Join-Path $testerFiles $name
    if (-not (Test-Path -LiteralPath $source)) {
        throw "Objective Tester artifact not found: $source"
    }
    $destination = Join-Path $sourceRoot $name
    Copy-Item -LiteralPath $source -Destination $destination -Force
    $item = Get-Item -LiteralPath $destination
    $manifestArtifacts += [ordered]@{
        name = $name
        bytes = $item.Length
        sha256 = (Get-FileHash -LiteralPath $destination -Algorithm SHA256).Hash
    }
}
$manifest = [ordered]@{
    manifest_version = "1.0.0"
    created_at = (Get-Date).ToString("s")
    terminal_id = $TerminalId
    agent_name = $AgentName
    output_name = $OutputName
    source_log = $LogPath
    artifacts = $manifestArtifacts
    deployment_authorized = $false
}
$manifest | ConvertTo-Json -Depth 5 | Set-Content `
    -LiteralPath (Join-Path $outputRoot "objective_run_manifest.json") `
    -Encoding UTF8

$qualityReport = Join-Path $outputRoot "real_tick_quality_audit.json"
& $python (Join-Path $projectRoot "training\audit_real_tick_quality.py") `
    --log $LogPath --quality-exclusions $qualityPath --output $qualityReport
if ($LASTEXITCODE -ne 0) { throw "Real-tick quality warning coverage failed." }

$setupAudit = Join-Path $sourceRoot "XAU_AI_SHADOW_BACKTEST_OBJECTIVE_SETUP_AUDIT.csv"
$decisions = Join-Path $sourceRoot "XAU_AI_SHADOW_BACKTEST_OBJECTIVE_DECISIONS_V4.csv"
& powershell.exe -NoProfile -ExecutionPolicy Bypass `
    -File (Join-Path $projectRoot "tools\build_stage_d_setup_outcomes.ps1") `
    -OutputName $OutputName -QualityExclusions $qualityPath `
    -SetupAuditPath $setupAudit -DecisionsPath $decisions
if ($LASTEXITCODE -ne 0) { throw "Objective Setup Outcome build failed." }

$candidateTrain = Join-Path $outputRoot "XAU_AI_SETUP_OUTCOME_TRAIN.csv"
$referenceTrain = Join-Path $referencePath "XAU_AI_SETUP_OUTCOME_TRAIN.csv"
if (Test-Path -LiteralPath $candidateTrain) {
    & $python (Join-Path $projectRoot "training\compare_objective_contract_train.py") `
        --reference-train $referenceTrain --candidate-train $candidateTrain `
        --output (Join-Path $outputRoot "objective_contract_train_comparison.json")
    if ($LASTEXITCODE -ne 0) { throw "Objective Train-only comparison failed." }

    & $python (Join-Path $projectRoot "training\diagnose_objective_reclaim_residuals.py") `
        --train $candidateTrain --setup-audit $setupAudit `
        --output (Join-Path $outputRoot "objective_reclaim_residual_diagnostic.json")
    if ($LASTEXITCODE -ne 0) { throw "Objective residual diagnostic failed." }
}

Write-Output "Objective research run finalized successfully."
Write-Output "Artifacts, quality audit, Dataset, split, comparison, and residual diagnostic are in:"
Write-Output $outputRoot
