@echo off
setlocal enabledelayedexpansion

set ADB_PATH=E:\sihpatientracking\platform-tools\adb.exe

echo =======================================================
echo     MediKiosk - ADB Reverse Port Forwarding Setup
echo =======================================================
echo.

if not exist "%ADB_PATH%" (
    echo [ERROR] adb.exe not found at %ADB_PATH%!
    pause
    exit /b 1
)

echo [1/4] Starting ADB Server...
"%ADB_PATH%" start-server
echo.

echo [2/4] Checking connected Android devices...
"%ADB_PATH%" devices -l
echo.

"%ADB_PATH%" get-state >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo -------------------------------------------------------
    echo [!] NO AUTHORIZED ANDROID DEVICE DETECTED!
    echo.
    echo Please follow these steps on your Android phone:
    echo  1. Connect your phone to this PC with a USB cable.
    echo  2. Open Settings -> About Phone -> tap "Build Number" 7 times
    echo     to enable Developer Options.
    echo  3. Open Settings -> Developer Options -> turn ON "USB Debugging".
    echo  4. Unlock your phone screen and tap "Allow" on the
    echo     "Allow USB Debugging?" RSA key popup.
    echo -------------------------------------------------------
    echo.
    pause
)

echo [3/4] Establishing Reverse Port Forwarding...
"%ADB_PATH%" reverse tcp:8000 tcp:8000
if %ERRORLEVEL% EQU 0 (
    echo  [OK] Forwarded Port 8000  (Phone localhost:8000 ==^> PC FastAPI Backend)
) else (
    echo  [FAIL] Failed to reverse port 8000.
)

"%ADB_PATH%" reverse tcp:5173 tcp:5173
if %ERRORLEVEL% EQU 0 (
    echo  [OK] Forwarded Port 5173  (Phone localhost:5173 ==^> PC Vite Frontend)
) else (
    echo  [FAIL] Failed to reverse port 5173.
)
echo.

echo [4/4] Active ADB Reverse Forwards:
"%ADB_PATH%" reverse --list
echo.
echo =======================================================
echo     PORT FORWARDING ACTIVE! YOUR PHONE IS CONNECTED!
echo =======================================================
echo.
echo You can now test on your phone:
echo  * Mobile Browser: Open Chrome on your phone and go to:
echo      http://localhost:8000/api/health
echo      http://localhost:5173
echo.
echo  * Flutter Mobile App (mobile/):
echo      cd mobile
echo      flutter run
echo      (Traffic to localhost:8000 is automatically routed to this PC)
echo.
pause
