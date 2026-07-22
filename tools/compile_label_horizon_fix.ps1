param(
    [string]$TerminalId = "D0E8209F77C8CF37AD8BF550E51FF075",
    [string]$MetaEditor = "C:\Program Files\MetaTrader 5\MetaEditor64.exe"
)

$ErrorActionPreference = "Stop"
$projectRoot = Split-Path -Parent $PSScriptRoot
$terminalRoot = Join-Path $env:APPDATA "MetaQuotes\Terminal\$TerminalId\MQL5\Experts\XAU-AI-PLATFORM"
$logRoot = Join-Path $projectRoot "outputs\compile\label_horizon"
$targets = @(
    "tests\TestLabelGenerator.mq5",
    "tests\TestHistoricalDatasetBuilder.mq5",
    "tests\TestHistoricalDatasetOrchestrator.mq5"
)

& (Join-Path $PSScriptRoot "sync_label_horizon_fix_to_mt5.ps1") -TerminalId $TerminalId
if (-not (Test-Path -LiteralPath $MetaEditor)) {
    throw "MetaEditor not found: $MetaEditor"
}
if (-not (Test-Path -LiteralPath $logRoot)) {
    New-Item -ItemType Directory -Path $logRoot | Out-Null
}
foreach ($relativeFile in $targets) {
    $source = Join-Path $terminalRoot $relativeFile
    $name = [IO.Path]::GetFileNameWithoutExtension($relativeFile)
    $log = Join-Path $logRoot "$name.log"
    if (-not (Test-Path -LiteralPath $source)) {
        throw "Compile target not found: $source"
    }
    if (Test-Path -LiteralPath $log) {
        Remove-Item -LiteralPath $log -Force
    }
    $process = Start-Process -FilePath $MetaEditor `
        -ArgumentList ('/compile:"{0}"' -f $source), ('/log:"{0}"' -f $log) `
        -WindowStyle Hidden -Wait -PassThru
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

Write-Output "Label full-horizon correction compile passed: 3/3 targets, 0 errors, 0 warnings."
