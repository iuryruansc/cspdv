$ErrorActionPreference = "Stop"

$projectRoot = Split-Path -Parent $PSScriptRoot
$distExe = Join-Path $projectRoot "dist\CSPdv.exe"
$issFile = Join-Path $projectRoot "installer\CSPdv.iss"
$envExample = Join-Path $projectRoot ".env.example"
$isccCandidates = @()

if ($env:ProgramFiles -and $env:ProgramFiles -ne "") {
    $isccCandidates += (Join-Path $env:ProgramFiles "Inno Setup 6\ISCC.exe")
}

if (${env:ProgramFiles(x86)} -and ${env:ProgramFiles(x86)} -ne "") {
    $isccCandidates += (Join-Path ${env:ProgramFiles(x86)} "Inno Setup 6\ISCC.exe")
}

$isccFromPath = Get-Command ISCC.exe -ErrorAction SilentlyContinue
if ($isccFromPath -and $isccFromPath.Source) {
    $isccCandidates += $isccFromPath.Source
}

$isccCandidates = @(
    $isccCandidates | Where-Object { $_ -and (Test-Path $_) } | Select-Object -Unique
)

function Get-EnvValue([string]$Path, [string]$Name, [string]$DefaultValue) {
    if (-not (Test-Path $Path)) {
        return $DefaultValue
    }

    $line = Get-Content $Path | Where-Object { $_ -match "^$Name=" } | Select-Object -First 1
    if (-not $line) {
        return $DefaultValue
    }

    $value = $line.Substring($Name.Length + 1).Trim()
    if ([string]::IsNullOrWhiteSpace($value)) {
        return $DefaultValue
    }

    return $value
}

if (-not (Test-Path $distExe)) {
    throw "O executavel nao foi encontrado em '$distExe'. Gere primeiro o build com .\tools\empacotar.ps1."
}

if (-not $isccCandidates) {
    throw "O compilador do Inno Setup nao foi encontrado. Instale o Inno Setup 6 antes de gerar o installer."
}

$isccCmd = $isccCandidates[0]
$appName = Get-EnvValue $envExample "APP_NAME" "CSPdv"
$appVersion = Get-EnvValue $envExample "APP_VERSION" "1.0.0"

Write-Host "Compilando installer com: $isccCmd"
Write-Host "App: $appName | Versao: $appVersion"
& $isccCmd "/DMyAppName=$appName" "/DMyAppPublisher=$appName" "/DMyAppVersion=$appVersion" $issFile
