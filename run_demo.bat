@echo off
title MediKiosk SIH26047 - Dual Clinical System Runner
echo ==============================================================================
echo    __  ___         ___ __ __  _           __  
echo   /  ^|/  /__  ____/ (_) //_(_)___  _____/ /__
echo  / /^|_/ / _ \/ __  / / ,^< / / __ \/ ___/ //_/
echo / /  / /  __/ /_/ / / /^| / / /_/ (__  ) ,^<   
echo /_/  /_/\___/\__,_/_/_/ ^|/_/\____/____/_/^|_^|   
echo.
echo   Ministry of AYUSH ^& AIIA - AI-Powered Patient Case-Taking Software
echo   Problem Statement: SIH26047
echo ==============================================================================
echo.

echo [1/3] Verifying Python and Node environments...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python not found in PATH. Please install Python 3.10+.
    pause
    exit /b 1
)

node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Node.js not found in PATH. Please install Node.js 18+.
    pause
    exit /b 1
)

echo [2/3] Starting MediKiosk FastAPI Clinical Backend (Port 8000)...
start "MediKiosk Backend (Port 8000)" cmd /k "python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"

timeout /t 3 /nobreak >nul

echo [3/3] Starting MediKiosk Frontend Dev Server (Port 5173)...
start "MediKiosk Frontend (Port 5173)" cmd /k "npm --prefix frontend run dev -- --port 5173 --host 0.0.0.0"

timeout /t 3 /nobreak >nul

echo.
echo ==============================================================================
echo  SYSTEM ONLINE! All services running:
echo  - Dual-Sided Web Hub:     http://localhost:5173/?view=hub
echo  - Dedicated Patient Portal: http://localhost:5173/?view=patient
echo  - Doctor Workstation:      http://localhost:5173/?view=doctor (PIN: 1234)
echo  - Hospital Kiosk Terminal: http://localhost:5173/
echo  - Mobile BYOD View:        http://localhost:5173/mobile.html
echo  - OpenAPI Documentation:   http://localhost:8000/docs
echo ==============================================================================
echo.
echo Launching Web Hub in your default browser...
start http://localhost:5173/?view=hub

echo.
echo Press any key to exit this launcher window (servers will stay running)...
pause >nul
