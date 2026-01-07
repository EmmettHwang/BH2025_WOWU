@echo off
echo ========================================
echo   BH2025 WOWU Development Servers
echo   (Conda Environment)
echo ========================================
echo.

REM Conda 환경 이름 (필요시 수정)
set CONDA_ENV=bh2025

echo [1/3] Activating Conda environment: %CONDA_ENV%...
call conda activate %CONDA_ENV%
if %errorlevel% neq 0 (
    echo Error: Failed to activate conda environment '%CONDA_ENV%'
    echo Please create the environment first:
    echo   conda create -n %CONDA_ENV% python=3.8
    echo   conda activate %CONDA_ENV%
    echo   cd backend ^&^& pip install -r requirements.txt
    pause
    exit /b 1
)
echo    OK - Conda environment activated
echo.

echo [2/3] Starting PM2 servers...
call pm2 start ecosystem.config.windows.js
if %errorlevel% neq 0 (
    echo Error: Failed to start PM2 servers
    echo Please ensure PM2 is installed: npm install -g pm2
    pause
    exit /b 1
)
echo.

echo [3/3] Checking server status...
call pm2 status
echo.

echo ========================================
echo   Servers Started Successfully!
echo ========================================
echo.
echo Access URLs:
echo   - Frontend: http://localhost:3000
echo   - Backend:  http://localhost:8000
echo   - API Docs: http://localhost:8000/docs
echo.
echo Useful Commands:
echo   - pm2 status         : Check server status
echo   - pm2 logs           : View all logs
echo   - pm2 restart all    : Restart servers
echo   - pm2 stop all       : Stop servers
echo   - pm2 delete all     : Remove servers
echo.
pause
