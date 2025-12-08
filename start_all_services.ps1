# Start All ShizishanGPT Services
# PowerShell script to start Frontend, Middleware, and Backend

Write-Host "🚀 Starting ShizishanGPT Services..." -ForegroundColor Green
Write-Host ""

# Start Backend
Write-Host "Starting Backend (Port 8000)..." -ForegroundColor Cyan
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd 'd:\Ps-3(git)\ShizishanGPT'; uvicorn src.backend.main:app --host 0.0.0.0 --port 8000"
Start-Sleep -Seconds 3

# Start Middleware  
Write-Host "Starting Middleware (Port 5000)..." -ForegroundColor Cyan
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd 'd:\Ps-3(git)\ShizishanGPT\middleware'; node server.js"
Start-Sleep -Seconds 2

# Start Frontend
Write-Host "Starting Frontend (Port 3000)..." -ForegroundColor Cyan
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd 'd:\Ps-3(git)\ShizishanGPT\frontend'; npm start"
Start-Sleep -Seconds 2

Write-Host ""
Write-Host "✅ All services started in separate windows!" -ForegroundColor Green
Write-Host ""
Write-Host "Services:" -ForegroundColor Yellow
Write-Host "  - Backend:    http://localhost:8000" -ForegroundColor White
Write-Host "  - Middleware: http://localhost:5000" -ForegroundColor White
Write-Host "  - Frontend:   http://localhost:3000" -ForegroundColor White
Write-Host ""
Write-Host "Press any key to check service health..." -ForegroundColor Yellow
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")

Write-Host ""
Write-Host "Checking services..." -ForegroundColor Cyan
Start-Sleep -Seconds 10

# Check Backend
Write-Host "Backend Health: " -NoNewline
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/health" -UseBasicParsing -TimeoutSec 5
    Write-Host "✓ RUNNING" -ForegroundColor Green
} catch {
    Write-Host "✗ NOT ACCESSIBLE" -ForegroundColor Red
}

# Check Middleware
Write-Host "Middleware Health: " -NoNewline
try {
    $response = Invoke-WebRequest -Uri "http://localhost:5000/health" -UseBasicParsing -TimeoutSec 5
    Write-Host "✓ RUNNING" -ForegroundColor Green
} catch {
    Write-Host "✗ NOT ACCESSIBLE" -ForegroundColor Red
}

# Check Frontend
Write-Host "Frontend Health: " -NoNewline
try {
    $response = Invoke-WebRequest -Uri "http://localhost:3000" -UseBasicParsing -TimeoutSec 5
    Write-Host "✓ RUNNING" -ForegroundColor Green
} catch {
    Write-Host "✗ NOT ACCESSIBLE" -ForegroundColor Red
}

Write-Host ""
Write-Host "To run tests, execute:" -ForegroundColor Yellow
Write-Host "  python -m pytest tests/ -v" -ForegroundColor White
Write-Host ""