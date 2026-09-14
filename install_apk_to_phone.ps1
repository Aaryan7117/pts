# MediKiosk - Install Native APK to Android Device via ADB
$AdbPath = "E:\sihpatientracking\platform-tools\adb.exe"
$ApkPath = "E:\sihpatientracking\mobile\build\app\outputs\flutter-apk\app-debug.apk"

Write-Host "=======================================================" -ForegroundColor Cyan
Write-Host "   MediKiosk - Native Android App Installer (ADB)" -ForegroundColor Cyan
Write-Host "=======================================================" -ForegroundColor Cyan
Write-Host ""

if (-not (Test-Path $ApkPath)) {
    Write-Host "[ERROR] APK not found at: $ApkPath" -ForegroundColor Red
    exit 1
}

Write-Host "[1/4] Checking for connected Android phone..." -ForegroundColor Yellow

while ($true) {
    $devices = (& $AdbPath devices) | Where-Object { $_ -match "\tdevice$" }
    if ($devices) {
        Write-Host "[OK] Connected Device Detected!" -ForegroundColor Green
        & $AdbPath devices -l
        break
    } else {
        Write-Host "[!] Please plug your phone in via USB with USB Debugging enabled..." -ForegroundColor Red
        Start-Sleep -Seconds 3
    }
}

Write-Host "`n[2/4] Setting up ADB Reverse Port Forwarding (Port 8000)..." -ForegroundColor Yellow
& $AdbPath reverse tcp:8000 tcp:8000
Write-Host " [OK] Forwarded Port 8000 (Phone localhost:8000 -> PC Backend)" -ForegroundColor Green

Write-Host "`n[3/4] Installing Native APK onto phone (144 MB)..." -ForegroundColor Yellow
& $AdbPath install -r $ApkPath

if ($LASTEXITCODE -eq 0) {
    Write-Host "[OK] Installation succeeded!" -ForegroundColor Green
} else {
    Write-Host "[ERROR] Installation failed. Check phone screen for install confirmation." -ForegroundColor Red
    exit 1
}

Write-Host "`n[4/4] Launching MediKiosk Native App on phone..." -ForegroundColor Yellow
& $AdbPath shell am start -n com.example.mobile/.MainActivity

Write-Host "`n=======================================================" -ForegroundColor Cyan
Write-Host "    MEDIKIOSK NATIVE APP IS RUNNING ON YOUR PHONE!" -ForegroundColor Cyan
Write-Host "=======================================================" -ForegroundColor Cyan
Write-Host "All API requests route directly to your PC backend over USB!" -ForegroundColor Green
