@echo off
echo Starting BH2025 with PM2...
pm2 start ecosystem.config.local.cjs
echo.
echo Server started!
echo   Frontend: http://localhost:8080
echo   Backend: http://localhost:8000
echo   API Docs: http://localhost:8000/docs
echo.
echo Commands:
echo   pm2 status      - Check status
echo   pm2 logs        - View logs
echo   pm2 restart all - Restart servers
echo   pm2 stop all    - Stop servers
pause
