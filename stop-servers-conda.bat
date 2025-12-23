@echo off
echo ========================================
echo   Stopping BH2025 WOWU Servers
echo ========================================
echo.

echo Stopping all PM2 processes...
call pm2 stop all

echo.
echo Deleting all PM2 processes...
call pm2 delete all

echo.
echo ========================================
echo   All Servers Stopped
echo ========================================
pause
