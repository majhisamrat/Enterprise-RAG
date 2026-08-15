# ============================================================================
# Start Celery Worker for Enterprise RAG
# Run this in a separate terminal after start_all_services.ps1
# ============================================================================

Write-Host "🚀 Starting Celery Worker" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

$ProjectPath = "c:\Users\Samratmajhi\Downloads\enterprise-rag"

Write-Host "📁 Project Path: $ProjectPath" -ForegroundColor Gray
Write-Host ""

# Check if Redis is running
Write-Host "🔍 Checking Redis connection..." -ForegroundColor Yellow
try {
    $ping = docker exec enterprise-redis redis-cli ping 2>&1
    if ($ping -eq "PONG") {
        Write-Host "✅ Redis is running" -ForegroundColor Green
    } else {
        Write-Host "⚠️  Redis may not be responding correctly" -ForegroundColor Yellow
    }
} catch {
    Write-Host "❌ Redis is not running!" -ForegroundColor Red
    Write-Host "   Please run start_all_services.ps1 first" -ForegroundColor Yellow
    exit 1
}

Write-Host ""

# Change to project directory
Set-Location $ProjectPath

# Activate virtual environment if it exists
if (Test-Path ".venv\Scripts\Activate.ps1") {
    Write-Host "🐍 Activating virtual environment..." -ForegroundColor Yellow
    & ".venv\Scripts\Activate.ps1"
    Write-Host "✅ Virtual environment activated" -ForegroundColor Green
}

Write-Host ""
Write-Host "⏳ Starting Celery worker..." -ForegroundColor Cyan
Write-Host ""

# Start Celery
celery -A app.tasks worker --loglevel=info

Write-Host ""
Write-Host "Celery worker stopped." -ForegroundColor Yellow
