@echo off
setlocal enabledelayedexpansion

set ADB_PATH=E:\sihpatientracking\platform-tools\adb.exe
set APK_PATH=E:\sihpatientracking\mobile\build\app\outputs\flutter-apk\app-debug.apk

echo =======================================================
echo    MediKiosk - Native Android App Installer (ADB)
echo =======================================================
echo.

if not exist "%APK_PATH%" (
    echo [ERROR] APK not found at:
    echo  %APK_PATH%
    echo Please run 'flutter build apk --debug' first.
    pause
    exit /b 1
)

echo [1/4] Checking for connected Android phone...
:check_device
"%ADB_PATH%" get-state >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo -------------------------------------------------------
    echo [!] Please plug your phone in with a USB cable!
    echo Ensure USB Debugging is ON and phone is unlocked.
    echo -------------------------------------------------------
    echo Waiting for device...
    timeout /t 3 /nobreak >nul
    goto check_device
)

echo [OK] Device detected:
"%ADB_PATH%" devices -l
echo.

echo [2/4] Setting up ADB Reverse Port Forwarding (Port 8000)...
"%ADB_PATH%" reverse tcp:8000 tcp:8000
if %ERRORLEVEL% EQU 0 (
    echo  [OK] Forwarded Port 8000 (Phone localhost:8000 ==^> PC FastAPI Backend)
) else (
    echo  [WARNING] Port forward failed, continuing install...
)
echo.

echo [3/4] Installing Native APK onto phone (this takes ~10-15 seconds)...
"%ADB_PATH%" install -r "%APK_PATH%"
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [ERROR] Installation failed!
    echo If prompted on your phone, tap 'Install anyway' or 'Allow'.
    pause
    exit /b 1
)
echo [OK] App installed successfully!
echo.

echo [4/4] Launching MediKiosk Native App on phone...
"%ADB_PATH%" shell am start -n com.example.mobile/.MainActivity
echo.
echo =======================================================
echo     MEDIKIOSK NATIVE APP IS RUNNING ON YOUR PHONE!
echo =======================================================
echo.
echo You can now test the real native app features:
echo  - 1-Tap Voice AI Fast Track
echo  - Live Queue Token Tracking
echo  - Prescription Camera Scanning & Evidence Polygons
echo.
echo All API requests route directly to your PC backend over USB!
echo.
pause
