@echo off
echo ========================================
echo   Stopping BH2025 WOWU Servers
echo ========================================
echo.

pm2 stop all
pm2 delete all

echo.
echo ========================================
echo   Servers Stopped Successfully!
echo ========================================
echo.
pause
