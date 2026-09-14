@echo off
title MediKiosk - Exotel IVR Public Webhook Tunnel
echo ==============================================================================
echo    __  ___         ___ __ __  _           __  
echo   /  ^|/  /__  ____/ (_) //_(_)___  _____/ /__
echo  / /^|_/ / _ \/ __  / / ,^< / / __ \/ ___/ //_/
echo / /  / /  __/ /_/ / / /^| / / /_/ (__  ) ,^<   
echo /_/  /_/\___/\__,_/_/_/ ^|/_/\____/____/_/^|_^|   
echo.
echo   Exotel Channel 3 Telephony Webhook Tunnel (Port 8000)
echo ==============================================================================
echo.

echo [1/2] Checking if MediKiosk Backend (Port 8000) is running...
powershell -Command "$conn = Test-NetConnection -ComputerName 127.0.0.1 -Port 8000 -InformationLevel Quiet; if (-not $conn) { Write-Host '[Starting Backend...]' -ForegroundColor Yellow; Start-Process cmd -ArgumentList '/k python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload' -WindowStyle Minimized; Start-Sleep -Seconds 3 }"

echo.
echo [2/2] Launching Ngrok Public HTTPS Tunnel for Port 8000...
echo.
echo ==============================================================================
echo  INSTRUCTIONS FOR EXOTEL DASHBOARD:
echo  1. Copy the HTTPS URL from below (e.g., https://xxxx.ngrok-free.app)
echo  2. In your Exotel App Flow, set Passthru Webhook URL to:
echo     https://YOUR-NGROK-URL/api/ivr/exotel/incoming-call
echo  3. Set HTTP Method to: POST
echo ==============================================================================
echo.

"C:\Users\lenovo\AppData\Roaming\npm\ngrok.cmd" http 8000
