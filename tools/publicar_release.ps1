$ErrorActionPreference = "Stop"

$projectRoot = Split-Path -Parent $PSScriptRoot
$installerPath = Join-Path $projectRoot "dist-installer\Setup_CSPdv.exe"
$releaseDir = if ($env:CSPDV_RELEASE_DIR) { $env:CSPDV_RELEASE_DIR } else { Join-Path $projectRoot "releases" }

Write-Host "Gerando executavel..."
& (Join-Path $PSScriptRoot "empacotar.ps1")

Write-Host "Gerando instalador..."
& (Join-Path $PSScriptRoot "gerar_installer.ps1")

if (-not (Test-Path -LiteralPath $installerPath)) {
    throw "O instalador não foi encontrado em '$installerPath'."
}

New-Item -ItemType Directory -Path $releaseDir -Force | Out-Null
$destino = Join-Path $releaseDir (Split-Path -Leaf $installerPath)
Copy-Item -LiteralPath $installerPath -Destination $destino -Force

Write-Host "Release pronta em: $destino"
Write-Host "Para distribuir automaticamente, configure CSPDV_RELEASE_DIR apontando para uma pasta sincronizada (por exemplo, Google Drive)."
