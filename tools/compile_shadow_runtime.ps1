param(
    [string]$TerminalId = "D0E8209F77C8CF37AD8BF550E51FF075",
    [string]$MetaEditor = "C:\Program Files\MetaTrader 5\MetaEditor64.exe"
)

$ErrorActionPreference = "Stop"
$projectRoot = Split-Path -Parent $PSScriptRoot
$terminalRoot = Join-Path $env:APPDATA "MetaQuotes\Terminal\$TerminalId\MQL5\Experts\XAU-AI-PLATFORM"
$logRoot = Join-Path $projectRoot "outputs\compile\shadow"

& (Join-Path $PSScriptRoot "sync_shadow_runtime_to_mt5.ps1") `
    -TerminalId $TerminalId

if (-not (Test-Path -LiteralPath $MetaEditor)) {
    throw "MetaEditor not found: $MetaEditor"
}
if (-not (Test-Path -LiteralPath $logRoot)) {
    New-Item -ItemType Directory -Path $logRoot | Out-Null
}

$targets = @(
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
    "tests\TestShadowStructuralExecutionSafety.mq5",
    "XAU-AI-PLATFORM.mq5"
)

foreach ($relativeFile in $targets) {
    $source = Join-Path $terminalRoot $relativeFile
    if (-not (Test-Path -LiteralPath $source)) {
        throw "Compile target not found: $source"
    }
    $name = [IO.Path]::GetFileNameWithoutExtension($relativeFile)
    $log = Join-Path $logRoot "$name.log"
    if (Test-Path -LiteralPath $log) {
        Remove-Item -LiteralPath $log -Force
    }
    $process = Start-Process -FilePath $MetaEditor `
        -ArgumentList ('/compile:"{0}"' -f $source), ('/log:"{0}"' -f $log) `
        -WindowStyle Hidden `
        -Wait `
        -PassThru
    if (-not (Test-Path -LiteralPath $log)) {
        throw "MetaEditor did not create a log for $relativeFile"
    }
    $content = Get-Content -LiteralPath $log -Raw
    if ($content -notmatch '0 errors, 0 warnings') {
        Write-Output $content
        throw "Compile failed or warned: $relativeFile"
    }
    Write-Output "COMPILE PASSED $relativeFile"
}

Write-Output "Shadow Runtime compile passed: 13/13 targets, 0 errors, 0 warnings."
