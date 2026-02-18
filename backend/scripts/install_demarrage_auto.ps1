# Installe Gesco pour qu'il démarre automatiquement au démarrage de Windows
# À exécuter en tant qu'administrateur pour "Au démarrage", ou en utilisateur pour "À l'ouverture de session"
# Usage : .\scripts\install_demarrage_auto.ps1 [-CheminExe "C:\Gesco\GescoServeur.exe"] [-AuDemarrage]

param(
    [string]$CheminExe = "",
    [switch]$AuDemarrage  # Si présent : tâche au démarrage (nécessite admin). Sinon : à l'ouverture de session.
)

$ErrorActionPreference = "Stop"
# Dossier contenant le script (soit projet\scripts, soit dossier copié\scripts)
$BundleRoot = Split-Path -Parent $PSScriptRoot

if (-not $CheminExe) {
    $ExeDansBundle = Join-Path $BundleRoot "GescoServeur.exe"
    if (Test-Path $ExeDansBundle) {
        $CheminExe = $ExeDansBundle
    } else {
        $CheminExe = Join-Path (Split-Path -Parent $BundleRoot) "dist\GescoServeur\GescoServeur.exe"
    }
}

if (-not (Test-Path $CheminExe)) {
    Write-Host "Exécutable introuvable : $CheminExe" -ForegroundColor Red
    Write-Host "Construisez d'abord avec : .\scripts\build_windows.ps1" -ForegroundColor Yellow
    Write-Host "Ou indiquez le chemin : .\scripts\install_demarrage_auto.ps1 -CheminExe 'C:\Program Files\Gesco\GescoServeur.exe'" -ForegroundColor Gray
    exit 1
}

$NomTache = "GescoAPI"
$DossierExe = Split-Path -Parent $CheminExe

# Supprimer l'ancienne tâche si elle existe
$null = schtasks /Query /TN $NomTache 2>$null
if ($LASTEXITCODE -eq 0) {
    schtasks /Delete /TN $NomTache /F | Out-Null
}

if ($AuDemarrage) {
    Write-Host "Création de la tâche au démarrage du système (nécessite administrateur)..." -ForegroundColor Cyan
    schtasks /Create /TN $NomTache /TR "`"$CheminExe`"" /SC ONSTART /RU SYSTEM /F
} else {
    Write-Host "Création de la tâche à l'ouverture de session..." -ForegroundColor Cyan
    schtasks /Create /TN $NomTache /TR "`"$CheminExe`"" /SC ONLOGON /F
}

if ($LASTEXITCODE -ne 0) {
    Write-Host "Échec de la création de la tâche. Essayez en ouvrant PowerShell en tant qu'administrateur." -ForegroundColor Red
    exit 1
}

Write-Host "Tâche '$NomTache' créée. Gesco démarrera automatiquement." -ForegroundColor Green
Write-Host "Pour désactiver : Planificateur de tâches > Tâches du Planificateur > '$NomTache' > Désactiver" -ForegroundColor Gray
