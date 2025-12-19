Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  BH2025 WOWU Development Servers" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 가상환경 활성화
Write-Host "[1/3] Activating Python virtual environment..." -ForegroundColor Yellow
& ".\backend\venv\Scripts\Activate.ps1"

# PM2로 서버 시작
Write-Host "[2/3] Starting servers with PM2..." -ForegroundColor Yellow
pm2 start ecosystem.config.cjs

# 상태 확인
Write-Host "[3/3] Showing server status..." -ForegroundColor Yellow
pm2 status

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "  Servers Started Successfully!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host "  Frontend: http://localhost:3000" -ForegroundColor White
Write-Host "  Backend:  http://localhost:8000" -ForegroundColor White
Write-Host "  API Docs: http://localhost:8000/docs" -ForegroundColor White
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Commands:" -ForegroundColor Cyan
Write-Host "  pm2 status          - Check server status"
Write-Host "  pm2 logs            - View logs"
Write-Host "  pm2 logs frontend-server  - Frontend logs only"
Write-Host "  pm2 logs backend-server   - Backend logs only"
Write-Host "  pm2 restart all     - Restart both servers"
Write-Host "  pm2 stop all        - Stop servers"
Write-Host "  pm2 delete all      - Stop and remove servers"
Write-Host ""
