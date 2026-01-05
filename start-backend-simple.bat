@echo off
echo ========================================
echo   BH2025 Backend Server (Simple)
echo ========================================
echo.

REM Conda 환경 이름
set CONDA_ENV=bh2025

echo [1/2] Activating Conda environment: %CONDA_ENV%...
call conda activate %CONDA_ENV%
if %errorlevel% neq 0 (
    echo    ERROR - Failed to activate conda environment
    echo.
    echo Please ensure conda environment exists:
    echo   conda env list
    echo   conda activate %CONDA_ENV%
    pause
    exit /b 1
)
echo    OK - Conda environment activated
echo.

echo [2/2] Starting backend server...
echo.
echo ========================================
echo   Server running on http://localhost:8000
echo   Press Ctrl+C to stop
echo ========================================
echo.

cd backend
python main.py

pause
