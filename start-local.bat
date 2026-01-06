@echo off
echo ========================================
echo   BH2025 Local Development Server
echo ========================================
echo.

echo Starting Backend (Port 8000)...
start "BH2025-Backend" cmd /k "cd backend && python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000"

timeout /t 3 /nobreak >nul

echo Starting Frontend (Port 8080)...
start "BH2025-Frontend" cmd /k "cd frontend && python -m http.server 8080"

echo.
echo ========================================
echo   Servers Started!
echo ========================================
echo   Frontend: http://localhost:8080
echo   Backend:  http://localhost:8000
echo   API Docs: http://localhost:8000/docs
echo ========================================
echo.
pause
