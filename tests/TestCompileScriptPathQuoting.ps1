$ErrorActionPreference = "Stop"

$projectRoot = Split-Path -Parent $PSScriptRoot
$compileScripts = Get-ChildItem -LiteralPath (Join-Path $projectRoot "tools") `
    -Filter "compile*.ps1" -File

if ($compileScripts.Count -eq 0) {
    throw "No compile scripts were found."
}

$quotedCompile = "('/compile:`"{0}`"' -f `$source)"
$quotedLog = "('/log:`"{0}`"' -f `$log)"

foreach ($script in $compileScripts) {
    $content = Get-Content -LiteralPath $script.FullName -Raw
    if (-not $content.Contains($quotedCompile)) {
        throw "Quoted /compile argument missing: $($script.Name)"
    }
    if (-not $content.Contains($quotedLog)) {
        throw "Quoted /log argument missing: $($script.Name)"
    }
    if ($content -match '-ArgumentList\s+"/compile:\$source",\s+"/log:\$log"') {
        throw "Unquoted MetaEditor path arguments remain: $($script.Name)"
    }
}

Write-Output "PASS: $($compileScripts.Count) compile scripts quote MetaEditor /compile and /log paths."
