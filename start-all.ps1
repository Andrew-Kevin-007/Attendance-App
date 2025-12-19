# Main Startup Script - Starts both Backend and Frontend
# Run this from the project root: .\start-all.ps1

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Attendance Tracker - Full Stack Start" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Resolve script paths
$root = Split-Path -Parent $PSCommandPath
$backendScript = Join-Path $root "backend\start.ps1"
$frontendScript = Join-Path $root "frontend\start.ps1"

# Start Backend
Write-Host "🔧 Starting Backend Server..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-ExecutionPolicy", "Bypass", "-File", $backendScript -WorkingDirectory $root

# Wait a bit for backend to start
Start-Sleep -Seconds 3

# Start Frontend
Write-Host "🎨 Starting Frontend Server..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-ExecutionPolicy", "Bypass", "-File", $frontendScript -WorkingDirectory $root

Write-Host ""
Write-Host "✅ Both servers are starting in separate windows" -ForegroundColor Green
Write-Host ""
Write-Host "📍 Access points:" -ForegroundColor Cyan
Write-Host "   Frontend: http://localhost:5173" -ForegroundColor White
Write-Host "   Backend:  http://127.0.0.1:8001" -ForegroundColor White
Write-Host "   API Docs: http://127.0.0.1:8001/api/docs" -ForegroundColor White
Write-Host ""
Write-Host "Press any key to close this window..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
