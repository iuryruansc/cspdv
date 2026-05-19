$ErrorActionPreference = "Stop"

$projectRoot = Split-Path -Parent $PSScriptRoot
$venvPython = Join-Path $projectRoot ".venv\Scripts\python.exe"
$pythonCmd = if (Test-Path $venvPython) { $venvPython } else { "python" }

Write-Host "Usando Python: $pythonCmd"
& $pythonCmd -m PyInstaller --noconfirm --clean "$projectRoot\cspdv.spec"
