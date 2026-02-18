@echo off
rem Lance uvicorn sur le port 9111 (base SQLite locale)
cd /d "%~dp0"
set DATABASE_URL=sqlite+aiosqlite:///./app/db/gesco.db
set DATABASE_URL_SYNC=sqlite:///./app/db/gesco.db

rem Venv : D:\work\Gesco\backend\.venv (a cote de ce script)
set "PYEXE=%~dp0.venv\Scripts\python.exe"
if not exist "%PYEXE%" (
    echo Erreur : .venv introuvable. Attendu : %~dp0.venv
    echo Creez-le avec : python -m venv .venv
    pause
    exit /b 1
)

echo Demarrage uvicorn sur http://localhost:9111
echo Docs : http://localhost:9111/docs
echo.
"%PYEXE%" -m uvicorn app.main:app --host 0.0.0.0 --port 9000
pause
