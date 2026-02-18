@echo off
cd /d "%~dp0"
if not exist "GescoServeur.exe" cd ..

echo Demarrage de Gesco...
echo.
echo Si une erreur s'affiche (ex: SECRET_KEY manquant), creez un fichier .env
echo dans ce dossier avec au moins : SECRET_KEY=votre-cle-32-caracteres-min
echo PORT=9111
echo.
echo L'API sera accessible sur : http://localhost:9111
echo Documentation : http://localhost:9111/docs
echo.
echo Pour arreter : fermez cette fenetre ou appuyez sur Ctrl+C
echo.

if not exist "GescoServeur.exe" (
    echo Fichier GescoServeur.exe introuvable.
    echo Lancez ce script depuis le dossier GescoServeur.
    pause
    exit /b 1
)

GescoServeur.exe

pause
