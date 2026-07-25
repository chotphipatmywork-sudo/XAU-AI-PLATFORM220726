param(
    [string]$TerminalId = "D0E8209F77C8CF37AD8BF550E51FF075"
)

$ErrorActionPreference = "Stop"
$projectRoot = Split-Path -Parent $PSScriptRoot
$python = Join-Path $projectRoot "training\.venv\Scripts\python.exe"
$outputRoot = Join-Path $projectRoot "training\output\past_only_trigger_event_imp088"
$sourceRoot = Join-Path $outputRoot "source_artifacts"
$request = Join-Path $outputRoot "XAU_AI_TRIGGER_EVENT_REQUESTS.csv"
$manifest = Join-Path $outputRoot "trigger_event_request_manifest.json"
$terminalFiles = Join-Path $env:APPDATA "MetaQuotes\Terminal\$TerminalId\MQL5\Files"
$terminalExport = Join-Path $terminalFiles "XAU_AI_TRIGGER_EVENT_EVIDENCE.csv"
$export = Join-Path $sourceRoot "XAU_AI_TRIGGER_EVENT_EVIDENCE.csv"
$report = Join-Path $outputRoot "trigger_event_collection.json"

foreach ($required in @($python, $request, $manifest, $terminalExport)) {
    if (-not (Test-Path -LiteralPath $required)) {
        throw "Trigger-event collection required path not found: $required"
    }
}
New-Item -ItemType Directory -Path $sourceRoot -Force | Out-Null
Copy-Item -LiteralPath $terminalExport -Destination $export -Force
if ((Get-FileHash -LiteralPath $terminalExport -Algorithm SHA256).Hash -ne
    (Get-FileHash -LiteralPath $export -Algorithm SHA256).Hash) {
    throw "Trigger-event export collection hash mismatch."
}

& $python (Join-Path $projectRoot "training\test_trigger_event_export.py")
if ($LASTEXITCODE -ne 0) {
    throw "Trigger-event export focused validation test failed."
}
& $python (Join-Path $projectRoot "training\validate_trigger_event_export.py") `
    --request $request `
    --request-manifest $manifest `
    --trigger-event-export $export `
    --output $report
if ($LASTEXITCODE -ne 0) {
    throw "Trigger-event export validation failed."
}
Write-Output "Trigger-event evidence collected and validated successfully."
Write-Output $report
