# Frontend Startup Script for Windows
# Run this from the frontend/ directory: .\start.ps1

Write-Host "🚀 Starting Attendance Tracker Frontend..." -ForegroundColor Cyan

# Check if node_modules exists
if (-not (Test-Path "node_modules")) {
    Write-Host "📦 Installing dependencies..." -ForegroundColor Yellow
    npm install
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Failed to install dependencies" -ForegroundColor Red
        exit 1
    }
}

# Check if .env exists
if (-not (Test-Path ".env")) {
    Write-Host "⚠️  Warning: .env file not found. Creating from .env.example..." -ForegroundColor Yellow
    if (Test-Path ".env.example") {
        Copy-Item ".env.example" ".env"
        Write-Host "✓ Created .env file" -ForegroundColor Green
    }
}

Write-Host ""
Write-Host "📍 Frontend will start on: http://localhost:5173" -ForegroundColor Cyan
Write-Host "🔗 Backend API: http://127.0.0.1:8001" -ForegroundColor Cyan
Write-Host ""
Write-Host "⚠️  Make sure the backend is running first!" -ForegroundColor Yellow
Write-Host ""

# Start the dev server
npm run dev
