# MediKiosk SIH26047 - Dual Clinical System Runner (PowerShell)
Write-Host "==============================================================================" -ForegroundColor Cyan
Write-Host "   __  ___         ___ __ __  _           __  " -ForegroundColor Cyan
Write-Host "  /  |/  /__  ____/ (_) //_(_)___  _____/ /__ " -ForegroundColor Cyan
Write-Host " / /|_/ / _ \/ __  / / ,< / / __ \/ ___/ //_/ " -ForegroundColor Cyan
Write-Host "/ /  / /  __/ /_/ / / /| / / /_/ (__  ) ,<   " -ForegroundColor Cyan
Write-Host "/_/  /_/\___/\__,_/_/_/ |/_/\____/____/_/|_|   " -ForegroundColor Cyan
Write-Host ""
Write-Host "  Ministry of AYUSH & AIIA - AI-Powered Patient Case-Taking Software" -ForegroundColor Yellow
Write-Host "  Problem Statement: SIH26047" -ForegroundColor Yellow
Write-Host "==============================================================================" -ForegroundColor Cyan

Write-Host "`n[1/3] Verifying Python and Node environments..." -ForegroundColor Green
$python = Get-Command python -ErrorAction SilentlyContinue
if (-not $python) {
    Write-Error "Python not found in PATH. Please install Python 3.10+."
    exit 1
}

$node = Get-Command node -ErrorAction SilentlyContinue
if (-not $node) {
    Write-Error "Node.js not found in PATH. Please install Node.js 18+."
    exit 1
}

Write-Host "[2/3] Starting MediKiosk FastAPI Clinical Backend (Port 8000)..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-Command", "python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"

Start-Sleep -Seconds 3

Write-Host "[3/3] Starting MediKiosk Frontend Dev Server (Port 5173)..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-Command", "npm --prefix frontend run dev -- --port 5173 --host 0.0.0.0"

Start-Sleep -Seconds 3

Write-Host "`n==============================================================================" -ForegroundColor Cyan
Write-Host " SYSTEM ONLINE! All services running:" -ForegroundColor Green
Write-Host " - Dual-Sided Web Hub:       http://localhost:5173/?view=hub" -ForegroundColor White
Write-Host " - Dedicated Patient Portal: http://localhost:5173/?view=patient" -ForegroundColor White
Write-Host " - Doctor Workstation:        http://localhost:5173/?view=doctor (PIN: 1234)" -ForegroundColor White
Write-Host " - Hospital Kiosk Terminal:   http://localhost:5173/" -ForegroundColor White
Write-Host " - Mobile BYOD View:          http://localhost:5173/mobile.html" -ForegroundColor White
Write-Host " - OpenAPI Documentation:     http://localhost:8000/docs" -ForegroundColor White
Write-Host "==============================================================================" -ForegroundColor Cyan

Start-Process "http://localhost:5173/?view=hub"
Write-Host "`nLaunched Web Hub in default browser!" -ForegroundColor Green
