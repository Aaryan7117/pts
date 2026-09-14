# MediKiosk - ADB Reverse Port Forwarding PowerShell Script
$AdbPath = "E:\sihpatientracking\platform-tools\adb.exe"

Write-Host "=======================================================" -ForegroundColor Cyan
Write-Host "    MediKiosk - ADB Reverse Port Forwarding Setup" -ForegroundColor Cyan
Write-Host "=======================================================" -ForegroundColor Cyan
Write-Host ""

if (-not (Test-Path $AdbPath)) {
    Write-Host "[ERROR] adb.exe not found at $AdbPath!" -ForegroundColor Red
    exit 1
}

Write-Host "[1/4] Starting ADB Server..." -ForegroundColor Yellow
& $AdbPath start-server

Write-Host "`n[2/4] Checking connected Android devices..." -ForegroundColor Yellow
& $AdbPath devices -l

$devices = (& $AdbPath devices) | Where-Object { $_ -match "\tdevice$" }
if (-not $devices) {
    Write-Host "`n-------------------------------------------------------" -ForegroundColor Red
    Write-Host "[!] NO AUTHORIZED ANDROID DEVICE DETECTED!" -ForegroundColor Red
    Write-Host "Please follow these steps on your Android phone:" -ForegroundColor White
    Write-Host " 1. Connect your phone to this PC with a USB cable." -ForegroundColor Gray
    Write-Host " 2. Open Settings -> About Phone -> tap 'Build Number' 7 times." -ForegroundColor Gray
    Write-Host " 3. Open Settings -> Developer Options -> turn ON 'USB Debugging'." -ForegroundColor Gray
    Write-Host " 4. Unlock phone and tap 'Allow' on the 'Allow USB Debugging?' popup." -ForegroundColor Gray
    Write-Host "-------------------------------------------------------`n" -ForegroundColor Red
} else {
    Write-Host "[OK] Connected Device Detected!" -ForegroundColor Green
}

Write-Host "`n[3/4] Establishing Reverse Port Forwarding..." -ForegroundColor Yellow

# Forward FastAPI Backend
& $AdbPath reverse tcp:8000 tcp:8000
if ($LASTEXITCODE -eq 0) {
    Write-Host " [OK] Forwarded Port 8000  (Phone localhost:8000 -> PC Backend)" -ForegroundColor Green
} else {
    Write-Host " [FAIL] Could not reverse port 8000" -ForegroundColor Red
}

# Forward Vite Frontend
& $AdbPath reverse tcp:5173 tcp:5173
if ($LASTEXITCODE -eq 0) {
    Write-Host " [OK] Forwarded Port 5173  (Phone localhost:5173 -> PC Frontend)" -ForegroundColor Green
} else {
    Write-Host " [FAIL] Could not reverse port 5173" -ForegroundColor Red
}

Write-Host "`n[4/4] Active ADB Reverse Forwards:" -ForegroundColor Yellow
& $AdbPath reverse --list

Write-Host "`n=======================================================" -ForegroundColor Cyan
Write-Host "    PORT FORWARDING ACTIVE! YOUR PHONE IS READY!" -ForegroundColor Cyan
Write-Host "=======================================================" -ForegroundColor Cyan
Write-Host "URLs to test on phone:" -ForegroundColor White
Write-Host " * Health API:  http://localhost:8000/api/health" -ForegroundColor Green
Write-Host " * API Docs:    http://localhost:8000/docs" -ForegroundColor Green
Write-Host " * Web UI:      http://localhost:5173" -ForegroundColor Green
Write-Host " * Flutter App: Run 'flutter run' in mobile/ directory" -ForegroundColor Green
