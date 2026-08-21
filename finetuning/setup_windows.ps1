$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
$Venv = Join-Path $PSScriptRoot ".venv"
if (-not (Test-Path $Venv)) { py -3.12 -m venv $Venv }
& "$Venv\Scripts\python.exe" -m pip install --upgrade pip wheel
& "$Venv\Scripts\python.exe" -m pip install -r "$PSScriptRoot\requirements-windows.txt"
Write-Host "Environment ready. Confirm that tshark.exe is on PATH with: tshark --version"

