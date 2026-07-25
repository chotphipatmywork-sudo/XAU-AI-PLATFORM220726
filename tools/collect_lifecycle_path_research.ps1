param(
    [string]$TerminalId = "D0E8209F77C8CF37AD8BF550E51FF075"
)

$ErrorActionPreference = "Stop"
$projectRoot = Split-Path -Parent $PSScriptRoot
$python = Join-Path $projectRoot "training\.venv\Scripts\python.exe"
$outputRoot = Join-Path $projectRoot "training\output\lifecycle_m5_replay_imp084"
$sourceRoot = Join-Path $outputRoot "source_artifacts"
$request = Join-Path $outputRoot "XAU_AI_LIFECYCLE_PATH_REQUESTS.csv"
$manifest = Join-Path $outputRoot "lifecycle_path_request_manifest.json"
$terminalFiles = Join-Path $env:APPDATA "MetaQuotes\Terminal\$TerminalId\MQL5\Files"
$terminalExport = Join-Path $terminalFiles "XAU_AI_LIFECYCLE_M5_PATHS.csv"
$export = Join-Path $sourceRoot "XAU_AI_LIFECYCLE_M5_PATHS.csv"
$report = Join-Path $outputRoot "lifecycle_management_replay.json"

foreach ($required in @($python, $request, $manifest, $terminalExport)) {
    if (-not (Test-Path -LiteralPath $required)) {
        throw "Lifecycle path collection required path not found: $required"
    }
}
New-Item -ItemType Directory -Path $sourceRoot -Force | Out-Null
Copy-Item -LiteralPath $terminalExport -Destination $export -Force
if ((Get-FileHash -LiteralPath $terminalExport -Algorithm SHA256).Hash -ne
    (Get-FileHash -LiteralPath $export -Algorithm SHA256).Hash) {
    throw "Lifecycle M5 path collection hash mismatch."
}

& $python (Join-Path $projectRoot "training\replay_lifecycle_management.py") `
    --request $request `
    --request-manifest $manifest `
    --m5-path-export $export `
    --output $report
if ($LASTEXITCODE -ne 0) {
    throw "Lifecycle management Train-only replay failed."
}
Write-Output "Lifecycle M5 path export collected and replayed successfully."
Write-Output $report
