@echo off
echo ========================================
echo   BH2025 WOWU Development Servers
echo ========================================
echo.

REM 가상환경 활성화
echo [1/3] Activating Python virtual environment...
call backend\venv\Scripts\activate.bat
if %errorlevel% neq 0 (
    echo Error: Failed to activate virtual environment
    echo Please run: cd backend ^&^& python -m venv venv ^&^& venv\Scripts\activate ^&^& pip install -r requirements.txt
    pause
    exit /b 1
)

echo [2/3] Starting servers with PM2...
pm2 start ecosystem.config.cjs

echo [3/3] Showing server status...
pm2 status

echo.
echo ========================================
echo   Servers Started Successfully!
echo ========================================
echo   Frontend: http://localhost:3000
echo   Backend:  http://localhost:8000
echo   API Docs: http://localhost:8000/docs
echo ========================================
echo.
echo Commands:
echo   pm2 status          - Check server status
echo   pm2 logs            - View logs
echo   pm2 logs frontend-server  - Frontend logs only
echo   pm2 logs backend-server   - Backend logs only
echo   pm2 restart all     - Restart both servers
echo   pm2 stop all        - Stop servers
echo   pm2 delete all      - Stop and remove servers
echo.
pause
