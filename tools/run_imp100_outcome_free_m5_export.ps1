param(
    [string]$TerminalId = "D0E8209F77C8CF37AD8BF550E51FF075",
    [string]$Terminal = "C:\Program Files\MetaTrader 5\terminal64.exe"
)
$ErrorActionPreference = "Stop"
$projectRoot = Split-Path -Parent $PSScriptRoot
$python = Join-Path $projectRoot "training\.venv\Scripts\python.exe"
$request = Join-Path $projectRoot "training\output\imp100_train_only_replay_preparation\active_replay_requests.csv"
$outputRoot = Join-Path $projectRoot "training\output\imp100_outcome_free_m5_export"
$commonFiles = Join-Path $env:APPDATA "MetaQuotes\Terminal\Common\Files"
$commonRequest = Join-Path $commonFiles "XAU_AI_IMP100_OUTCOME_FREE_M5_REQUESTS.csv"
$commonExport = Join-Path $commonFiles "XAU_AI_IMP100_OUTCOME_FREE_M5_PATHS.csv"
$validator = Join-Path $projectRoot "training\validate_imp100_outcome_free_m5_export.py"
$presets = Join-Path $env:APPDATA "MetaQuotes\Terminal\$TerminalId\MQL5\Presets"
$parameterFile = Join-Path $presets "IMP100_OutcomeFreeM5Exporter.set"
$expectedRequestHash = "C4BDA8102E50F266714D99EE0CF27D71540DEA1ADC7DA3757528BC7155B63085"
$expectedContractHash = "9D0142D1671E80C1263D93A61E1CB53316EC8E816040B251F477F974540494A9"
$contract = Join-Path $projectRoot "training\config\imp100_train_only_replay_contract.json"

if ((Get-FileHash -LiteralPath $contract -Algorithm SHA256).Hash -ne $expectedContractHash) {
    throw "Frozen IMP-100 contract hash changed."
}
if ((Get-FileHash -LiteralPath $request -Algorithm SHA256).Hash -ne $expectedRequestHash) {
    throw "Frozen IMP-100 active request hash changed."
}
if (Get-Process terminal64 -ErrorAction SilentlyContinue) {
    throw "MetaTrader 5 is already running; export aborted to avoid disturbing an active session."
}
New-Item -ItemType Directory -Force -Path $outputRoot,$commonFiles,$presets | Out-Null
Copy-Item -LiteralPath $request -Destination $commonRequest -Force
if ((Get-FileHash -LiteralPath $commonRequest -Algorithm SHA256).Hash -ne $expectedRequestHash) {
    throw "Common Files request copy hash mismatch."
}
$parameterText = @"
RequestFile=XAU_AI_IMP100_OUTCOME_FREE_M5_REQUESTS.csv
OutputFile=XAU_AI_IMP100_OUTCOME_FREE_M5_PATHS.csv
TrainEndExclusive=2024.07.01 00:00
MaximumPathM5Bars=192||192||1||192||N
ProgressInterval=25||25||1||100||N
ShutdownTerminalAfterExport=true
"@
[System.IO.File]::WriteAllText(
    $parameterFile,$parameterText,(New-Object System.Text.UTF8Encoding($false))
)

$runHashes = @()
for ($run = 1; $run -le 2; $run++) {
    if (Test-Path -LiteralPath $commonExport) {
        Remove-Item -LiteralPath $commonExport -Force
    }
    $config = Join-Path $outputRoot "imp100_export_run_$run.ini"
    $report = Join-Path $outputRoot "imp100_export_run_$run"
    $configText = @"
[Experts]
Enabled=1
AllowLiveTrading=0
AllowDllImport=0
[StartUp]
Expert=XAU-AI-PLATFORM\tests\TestCurrentFeedJointGeometryM5Exporter
ExpertParameters=IMP100_OutcomeFreeM5Exporter.set
Symbol=XAUUSD
Period=M15
"@
    [System.IO.File]::WriteAllText(
        $config,$configText,(New-Object System.Text.UTF8Encoding($false))
    )
    $process = Start-Process -FilePath $Terminal `
        -ArgumentList ('/config:"{0}"' -f $config) -WindowStyle Hidden -PassThru
    if (-not $process.WaitForExit(1800000)) {
        Stop-Process -Id $process.Id -Force
        throw "IMP-100 export run $run exceeded 30 minutes."
    }
    if (-not (Test-Path -LiteralPath $commonExport)) {
        throw "IMP-100 export run $run did not create the M5 path file."
    }
    $runOutput = Join-Path $outputRoot "outcome_free_m5_paths_run_$run.csv"
    Copy-Item -LiteralPath $commonExport -Destination $runOutput -Force
    $validation = Join-Path $outputRoot "export_validation_run_$run.json"
    & $python $validator --requests $request --export $runOutput `
        --train-cutoff "2024.07.01 00:00" --expected-requests 685 `
        --path-bars 192 --output $validation
    if ($LASTEXITCODE -ne 0) {
        throw "IMP-100 export validation failed for run $run."
    }
    $runHashes += (Get-FileHash -LiteralPath $runOutput -Algorithm SHA256).Hash
}
if ($runHashes[0] -ne $runHashes[1]) {
    throw "IMP-100 export reproducibility hash mismatch."
}
$canonical = Join-Path $outputRoot "XAU_AI_IMP100_OUTCOME_FREE_M5_PATHS.csv"
Copy-Item -LiteralPath (Join-Path $outputRoot "outcome_free_m5_paths_run_2.csv") `
    -Destination $canonical -Force
$manifest = [ordered]@{
    manifest_schema_version = "1.0.0"
    experiment_id = "IMP-100"
    phase = "OUTCOME_FREE_M5_EXPORT_BOUNDARY"
    status = "PASS"
    contract_sha256 = $expectedContractHash
    request_sha256 = $expectedRequestHash
    request_count = 685
    path_bars_per_request = 192
    export_record_count = 131520
    export_sha256 = $runHashes[0]
    reproducible_export = $true
    outcome_fields_present = $false
    replay_executed = $false
    runtime_changed = $false
    protected_modules_changed = $false
    deployment_authorized = $false
}
$manifestPath = Join-Path $outputRoot "export_manifest.json"
[System.IO.File]::WriteAllText(
    $manifestPath,($manifest | ConvertTo-Json -Depth 4) + "`n",
    (New-Object System.Text.UTF8Encoding($false))
)
Write-Output "IMP-100 outcome-free M5 export boundary passed."
Write-Output "REQUESTS=685"
Write-Output "PATH_ROWS=131520"
Write-Output "EXPORT_SHA256=$($runHashes[0])"
Write-Output "MANIFEST=$manifestPath"
