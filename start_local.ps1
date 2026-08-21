# Enterprise RAG Local Development Startup Script

Write-Host "Starting Enterprise RAG (Local Development Mode)" -ForegroundColor Green
Write-Host ""

# Check if services are running
Write-Host "Checking Docker services..." -ForegroundColor Cyan
$services = docker-compose -f docker-compose.services-only.yml ps --services --filter "status=running"
if ($services.Count -lt 4) {
    Write-Host "Services not running. Starting services..." -ForegroundColor Yellow
    docker-compose -f docker-compose.services-only.yml up -d
    Write-Host "Waiting for services to be healthy (30 seconds)..." -ForegroundColor Yellow
    Start-Sleep -Seconds 30
} else {
    Write-Host "Services already running" -ForegroundColor Green
}

# Check if virtual environment exists
if (-Not (Test-Path ".venv")) {
    Write-Host "Virtual environment not found. Creating..." -ForegroundColor Yellow
    python -m venv .venv
    Write-Host "Virtual environment created" -ForegroundColor Green
    Write-Host "Installing dependencies..." -ForegroundColor Cyan
    .\.venv\Scripts\Activate.ps1
    pip install -r requirements.txt
} else {
    Write-Host "Virtual environment found" -ForegroundColor Green
}

# Check if database is initialized
Write-Host "Checking database..." -ForegroundColor Cyan
.\.venv\Scripts\Activate.ps1
$dbCheck = alembic current 2>&1
if ($dbCheck -match "Can''t locate revision") {
    Write-Host "Database not initialized. Running migrations..." -ForegroundColor Yellow
    alembic upgrade head
    Write-Host "Database initialized" -ForegroundColor Green
} else {
    Write-Host "Database already initialized" -ForegroundColor Green
}

# Create data directories
Write-Host "Creating data directories..." -ForegroundColor Cyan
New-Item -ItemType Directory -Force -Path "data\uploads" | Out-Null
New-Item -ItemType Directory -Force -Path "data\duckdb" | Out-Null
New-Item -ItemType Directory -Force -Path "logs" | Out-Null
Write-Host "Data directories ready" -ForegroundColor Green

Write-Host ""
Write-Host "Setup complete! Starting backend..." -ForegroundColor Green
Write-Host ""
Write-Host "Backend: http://localhost:8000" -ForegroundColor Cyan
Write-Host "API Docs: http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host "Health: http://localhost:8000/api/v1/health" -ForegroundColor Cyan
Write-Host ""
Write-Host "Press Ctrl+C to stop" -ForegroundColor Yellow
Write-Host ""

# Start backend with hot reload
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
