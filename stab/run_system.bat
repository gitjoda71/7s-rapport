@echo off
title Stabssystem – 7S-ingest

echo ============================================
echo  Stabssystem – Signal ^> Obsidian
echo ============================================
echo.

:: Kontrollera att .env finns
if not exist .env (
    echo FEL: .env saknas. Kopiera .env.example till .env och fyll i token.
    pause
    exit /b 1
)

:: Installera beroenden om de saknas
pip show fastapi >nul 2>&1
if %errorlevel% neq 0 (
    echo Installerar Python-beroenden...
    pip install -r requirements.txt
    echo.
)

echo Startar ingest-servern pa http://localhost:8000
echo Tryck Ctrl+C for att stanga av.
echo.

uvicorn ingest:app --host 0.0.0.0 --port 8000 --reload

pause
