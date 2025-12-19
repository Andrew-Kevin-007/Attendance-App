# Backend Startup Script for Windows
# Run this from the backend/ directory: .\start.ps1

Write-Host "🚀 Starting Attendance Tracker Backend..." -ForegroundColor Cyan

# Check if .env exists
if (-not (Test-Path ".env")) {
    Write-Host "⚠️  Warning: .env file not found. Creating from .env.example..." -ForegroundColor Yellow
    if (Test-Path ".env.example") {
        Copy-Item ".env.example" ".env"
        Write-Host "✓ Created .env file. Please edit it with your SECRET_KEY" -ForegroundColor Green
    } else {
        Write-Host "❌ Error: .env.example not found" -ForegroundColor Red
        exit 1
    }
}

# Check if venv exists
$venvPath = "..\. venv312\Scripts\python.exe"
if (-not (Test-Path $venvPath)) {
    Write-Host "⚠️  Virtual environment not found at ..\.venv312" -ForegroundColor Yellow
    Write-Host "Creating virtual environment..." -ForegroundColor Yellow
    python -m venv venv
    $venvPath = "venv\Scripts\python.exe"
    
    Write-Host "Installing dependencies..." -ForegroundColor Yellow
    & $venvPath -m pip install --upgrade pip
    & $venvPath -m pip install -r requirements.txt
}

# Create uploads directory if it doesn't exist
if (-not (Test-Path "uploads")) {
    New-Item -ItemType Directory -Path "uploads" | Out-Null
    New-Item -ItemType Directory -Path "uploads\registrations" | Out-Null
    New-Item -ItemType Directory -Path "uploads\attendance" | Out-Null
    Write-Host "✓ Created uploads directories" -ForegroundColor Green
}

Write-Host ""
Write-Host "📍 Server will start on: http://127.0.0.1:8001" -ForegroundColor Cyan
Write-Host "📚 API Documentation: http://127.0.0.1:8001/api/docs" -ForegroundColor Cyan
Write-Host ""
Write-Host "⚠️  Note: Do NOT use --reload flag (causes OpenCV issues)" -ForegroundColor Yellow
Write-Host ""

# Start the server
& $venvPath -m uvicorn app.main:app --host 127.0.0.1 --port 8001
