# Build de l'exécutable Windows Gesco
# Prérequis : Python 3.12, venv activé, pip install -r requirements.txt -r requirements-build.txt
# Exécution : .\scripts\build_windows.ps1

$ErrorActionPreference = "Stop"
$ProjectRoot = Split-Path -Parent $PSScriptRoot
Set-Location $ProjectRoot

Write-Host "Build Gesco - Exécutable Windows" -ForegroundColor Cyan
Write-Host "Répertoire : $ProjectRoot" -ForegroundColor Gray

# Vérifier PyInstaller
$null = pip show pyinstaller 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "Installation des dépendances de build..." -ForegroundColor Yellow
    pip install -r requirements.txt -r requirements-build.txt -q
}

# Nettoyer un ancien build
if (Test-Path "dist\GescoServeur") {
    Remove-Item -Recurse -Force "dist\GescoServeur"
}
if (Test-Path "build") {
    Remove-Item -Recurse -Force "build"
}

# Build
Write-Host "Lancement de PyInstaller..." -ForegroundColor Yellow
pyinstaller gesco.spec

if ($LASTEXITCODE -ne 0) {
    Write-Host "Erreur PyInstaller." -ForegroundColor Red
    exit 1
}

# Copier le lanceur et .env.example à la racine (pour double-clic facile)
Copy-Item "dist\GescoServeur\_internal\Lancer_Gesco.bat" "dist\GescoServeur\" -Force
Copy-Item "dist\GescoServeur\_internal\.env.example" "dist\GescoServeur\" -Force

Write-Host ""
Write-Host "Build terminé." -ForegroundColor Green
Write-Host "Exécutable : dist\GescoServeur\GescoServeur.exe" -ForegroundColor White
Write-Host "Pour lancer avec une fenêtre visible : double-cliquez sur dist\GescoServeur\Lancer_Gesco.bat" -ForegroundColor White
Write-Host "Copiez le dossier dist\GescoServeur où vous voulez ; créez un .env à partir de .env.example à côté de l'exe." -ForegroundColor Gray
