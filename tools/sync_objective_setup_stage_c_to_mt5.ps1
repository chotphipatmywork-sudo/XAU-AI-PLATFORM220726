param(
    [string]$TerminalId = "D0E8209F77C8CF37AD8BF550E51FF075"
)

$ErrorActionPreference = "Stop"
$projectRoot = Split-Path -Parent $PSScriptRoot
$terminalRoot = Join-Path $env:APPDATA "MetaQuotes\Terminal\$TerminalId\MQL5\Experts\XAU-AI-PLATFORM"
$relativeFiles = @(
    "XAU-AI-PLATFORM.mq5",
    "core\brain\Brain.mqh",
    "core\brain\trend\models\TrendResult.mqh",
    "core\brain\trend\models\ConfirmedSwingStructureResult.mqh",
    "core\brain\trend\engines\ConfirmedSwingStructureEngine.mqh",
    "core\brain\trend\providers\ClosedBarSwingStructureProvider.mqh",
    "core\ai\inference\models\ShadowInferenceProviderMode.mqh",
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
    "core\execution\models\ExecutionPricePlan.mqh",
    "core\execution\shadow\ShadowExecutionEngine.mqh",
    "core\execution\shadow\ShadowExecutionManager.mqh",
    "core\runtime\StructureAwareExecutionPlanAdapter.mqh",
    "core\runtime\models\ShadowRuntimeConfig.mqh",
    "core\runtime\RuntimeManager.mqh",
    "core\telemetry\ObjectiveSetupAuditLogger.mqh",
    "tests\TestObjectiveMultiTimeframeSetupAdapter.mq5",
    "tests\TestObjectiveSetupResearchProvider.mq5",
    "tests\TestClosedBarSwingStructureProvider.mq5",
    "tests\TestShadowStructuralExecutionSafety.mq5",
    "tests\TestShadowExecutionSafety.mq5",
    "tests\TestShadowRiskGate.mq5",
    "tests\TestShadowBacktestContract.mq5",
    "tests\TestShadowDirectionalInferenceProvider.mq5",
    "tests\TestShadowSimpleBaselineInferenceProvider.mq5"
)

foreach ($relativeFile in $relativeFiles) {
    $source = Join-Path $projectRoot $relativeFile
    $destination = Join-Path $terminalRoot $relativeFile
    $destinationDirectory = Split-Path -Parent $destination
    if (-not (Test-Path -LiteralPath $source)) {
        throw "Workspace source not found: $source"
    }
    if (-not (Test-Path -LiteralPath $destinationDirectory)) {
        New-Item -ItemType Directory -Path $destinationDirectory | Out-Null
    }
    $sourceHash = (Get-FileHash -LiteralPath $source -Algorithm SHA256).Hash
    if (Test-Path -LiteralPath $destination) {
        $destinationHash = (Get-FileHash -LiteralPath $destination -Algorithm SHA256).Hash
        if ($sourceHash -eq $destinationHash) {
            Write-Output "CURRENT $relativeFile SHA256=$sourceHash"
            continue
        }
        (Get-Item -LiteralPath $destination).IsReadOnly = $false
    }
    $copied = $false
    for ($attempt = 1; $attempt -le 10; $attempt++) {
        try {
            Copy-Item -LiteralPath $source -Destination $destination -Force
            $copied = $true
            break
        }
        catch [System.IO.IOException] {
            if ($attempt -eq 10) { throw }
            Start-Sleep -Milliseconds 500
        }
    }
    if (-not $copied) {
        throw "Copy did not complete: $relativeFile"
    }
    $destinationHash = (Get-FileHash -LiteralPath $destination -Algorithm SHA256).Hash
    if ($sourceHash -ne $destinationHash) {
        throw "Hash verification failed: $relativeFile"
    }
    Write-Output "SYNCED $relativeFile SHA256=$sourceHash"
}

Write-Output "Objective Setup Stage C files synchronized successfully."
