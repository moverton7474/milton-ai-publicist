# Quick test script for Milton Overton AI Publicist (PowerShell)

Write-Host "==================================" -ForegroundColor Cyan
Write-Host "Milton Overton AI Publicist" -ForegroundColor Cyan
Write-Host "Quick System Test" -ForegroundColor Cyan
Write-Host "==================================" -ForegroundColor Cyan
Write-Host ""

# Check if we're in the right directory
if (-Not (Test-Path "requirements.txt")) {
    Write-Host "❌ Error: Please run this script from the milton-publicist directory" -ForegroundColor Red
    exit 1
}

# Check if .env exists
if (-Not (Test-Path ".env")) {
    Write-Host "⚠️  Warning: .env file not found" -ForegroundColor Yellow
    Write-Host "Creating from template..." -ForegroundColor Yellow
    Copy-Item ".env.template" ".env"
    Write-Host "✅ Created .env file" -ForegroundColor Green
    Write-Host ""
    Write-Host "⚠️  IMPORTANT: Edit .env and add your API keys:" -ForegroundColor Yellow
    Write-Host "   - ANTHROPIC_API_KEY=sk-ant-xxxxx"
    Write-Host "   - DATABASE_URL=postgresql://..."
    Write-Host ""
    Write-Host "Press Enter after you've updated .env..." -ForegroundColor Yellow
    Read-Host
}

# Check Python version
Write-Host "Checking Python version..."
$pythonVersion = python --version 2>&1
Write-Host "✅ $pythonVersion" -ForegroundColor Green
Write-Host ""

# Check if virtual environment exists
if (-Not (Test-Path "venv")) {
    Write-Host "Creating virtual environment..."
    python -m venv venv
    Write-Host "✅ Virtual environment created" -ForegroundColor Green
}

# Activate virtual environment
Write-Host "Activating virtual environment..."
& "venv\Scripts\Activate.ps1"
Write-Host "✅ Virtual environment activated" -ForegroundColor Green
Write-Host ""

# Install dependencies
Write-Host "Installing dependencies..."
pip install -q -r requirements.txt
Write-Host "✅ Dependencies installed" -ForegroundColor Green
Write-Host ""

# Run system test
Write-Host "Running system test..." -ForegroundColor Cyan
Write-Host ""
python scripts/test_system.py

Write-Host ""
Write-Host "==================================" -ForegroundColor Cyan
Write-Host "Test complete!" -ForegroundColor Cyan
Write-Host "==================================" -ForegroundColor Cyan
