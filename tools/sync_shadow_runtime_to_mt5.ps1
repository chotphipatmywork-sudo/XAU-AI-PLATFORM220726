param(
    [string]$TerminalId = "D0E8209F77C8CF37AD8BF550E51FF075"
)

$ErrorActionPreference = "Stop"
$projectRoot = Split-Path -Parent $PSScriptRoot
$terminalRoot = Join-Path $env:APPDATA "MetaQuotes\Terminal\$TerminalId\MQL5\Experts\XAU-AI-PLATFORM"

$relativeFiles = @(
    "XAU-AI-PLATFORM.mq5",
    "core\brain\Brain.mqh",
    "core\brain\BrainAnalyzer.mqh",
    "core\brain\ClosedBarObservationTime.mqh",
    "core\brain\BrainContextBuilder.mqh",
    "core\brain\SignalEngine.mqh",
    "core\brain\trend\models\ConfirmedSwingStructureResult.mqh",
    "core\brain\trend\engines\ConfirmedSwingStructureEngine.mqh",
    "core\brain\trend\providers\ClosedBarSwingStructureProvider.mqh",
    "core\ai\BrainFeatureAdapter.mqh",
    "core\ai\features\FeatureExtractor.mqh",
    "core\ai\inference\models\AIInferenceRequest.mqh",
    "core\ai\inference\models\ShadowInferenceProviderMode.mqh",
    "core\ai\inference\IAIInferenceProvider.mqh",
    "core\ai\inference\DevelopmentHeuristicInferenceProvider.mqh",
    "core\ai\inference\DirectionalResearchInferenceProvider.mqh",
    "core\ai\inference\SimpleTrendBaselineInferenceProvider.mqh",
    "core\ai\strategy\models\HybridRuleSetupContext.mqh",
    "core\ai\strategy\models\TradeSetupCandidate.mqh",
    "core\ai\strategy\models\StructureAwareTradePlan.mqh",
    "core\ai\strategy\models\ObjectiveMultiTimeframeSetupInput.mqh",
    "core\ai\strategy\models\ObjectiveHybridSetupConfig.mqh",
    "core\ai\strategy\models\ObjectiveMultiTimeframeSetupEvidence.mqh",
    "core\ai\strategy\HybridRuleSetupEngine.mqh",
    "core\ai\strategy\StructureAwareTradePlanner.mqh",
    "core\ai\strategy\ObjectiveMultiTimeframeSetupAdapter.mqh",
    "core\ai\strategy\ObjectiveSetupResearchProvider.mqh",
    "core\decision\AIDecisionIntentAdapter.mqh",
    "core\decision\DecisionAnalyzer.mqh",
    "core\decision\DecisionManager.mqh",
    "core\decision\DecisionPipeline.mqh",
    "core\execution\builder\ExecutionContextBuilder.mqh",
    "core\execution\models\ExecutionModeConfig.mqh",
    "core\execution\models\ExecutionPricePlan.mqh",
    "core\execution\shadow\models\ShadowTrade.mqh",
    "core\execution\shadow\ShadowAuditLogger.mqh",
    "core\execution\shadow\ShadowExecutionConfig.mqh",
    "core\execution\shadow\ShadowExecutionEngine.mqh",
    "core\execution\shadow\ShadowExecutionManager.mqh",
    "core\execution\shadow\ShadowStateStore.mqh",
    "core\kernel\Application.mqh",
    "core\kernel\Kernel.mqh",
    "core\risk\models\ShadowRiskContext.mqh",
    "core\risk\models\RiskResult.mqh",
    "core\risk\RiskAnalyzer.mqh",
    "core\risk\RiskEngine.mqh",
    "core\risk\RiskManager.mqh",
    "core\runtime\RuntimeManager.mqh",
    "core\runtime\ClosedBarFreshnessGuard.mqh",
    "core\runtime\StructureAwareExecutionPlanAdapter.mqh",
    "core\runtime\models\ShadowRuntimeConfig.mqh",
    "core\system\SystemManager.mqh",
    "core\telemetry\models\ShadowTelemetrySnapshot.mqh",
    "core\telemetry\models\ShadowBacktestReport.mqh",
    "core\telemetry\ShadowBacktestReportLogger.mqh",
    "core\telemetry\ShadowDecisionAuditLogger.mqh",
    "core\telemetry\ObjectiveSetupAuditLogger.mqh",
    "core\telemetry\ShadowTelemetryLogger.mqh",
    "tests\TestClosedBarBrainContext.mq5",
    "tests\TestShadowRiskGate.mq5",
    "tests\TestShadowExecutionSafety.mq5",
    "tests\TestShadowBacktestContract.mq5",
    "tests\TestClosedBarFreshnessGuard.mq5",
    "tests\TestShadowInferenceProvider.mq5",
    "tests\TestShadowDirectionalInferenceProvider.mq5",
    "tests\TestShadowSimpleBaselineInferenceProvider.mq5",
    "tests\TestObjectiveMultiTimeframeSetupAdapter.mq5",
    "tests\TestObjectiveSetupResearchProvider.mq5",
    "tests\TestClosedBarSwingStructureProvider.mq5",
    "tests\TestShadowStructuralExecutionSafety.mq5"
)

foreach ($relativeFile in $relativeFiles) {
    $source = Join-Path $projectRoot $relativeFile
    $destination = Join-Path $terminalRoot $relativeFile
    $destinationDirectory = Split-Path -Parent $destination
    $sourceHash = (Get-FileHash -LiteralPath $source -Algorithm SHA256).Hash
    if (Test-Path -LiteralPath $destination) {
        $existingHash = (Get-FileHash -LiteralPath $destination -Algorithm SHA256).Hash
        if ($sourceHash -eq $existingHash) {
            Write-Output "CURRENT $relativeFile SHA256=$sourceHash"
            continue
        }
    }
    if (-not (Test-Path -LiteralPath $destinationDirectory)) {
        New-Item -ItemType Directory -Path $destinationDirectory | Out-Null
    }
    if (Test-Path -LiteralPath $destination) {
        (Get-Item -LiteralPath $destination).IsReadOnly = $false
    }
    Copy-Item -LiteralPath $source -Destination $destination -Force
    $destinationHash = (Get-FileHash -LiteralPath $destination -Algorithm SHA256).Hash
    if ($sourceHash -ne $destinationHash) {
        throw "Hash verification failed: $relativeFile"
    }
    Write-Output "SYNCED $relativeFile SHA256=$sourceHash"
}

Write-Output "Shadow Runtime files synchronized successfully."
