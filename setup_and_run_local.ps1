# ATLAS Local Development Setup

Write-Host "Starting Docker services..." -ForegroundColor Green
docker-compose -f docker-compose.services-only.yml up -d

Write-Host "Waiting 15 seconds for services to be healthy..." -ForegroundColor Yellow
Start-Sleep -Seconds 15

# Activate venv
Write-Host "Activating Python virtual environment..." -ForegroundColor Green
if (-Not (Test-Path ".venv")) {
    Write-Host "Creating virtual environment..." -ForegroundColor Yellow
    python -m venv .venv
}
.\.venv\Scripts\Activate.ps1

# Install dependencies
Write-Host "Installing Python dependencies..." -ForegroundColor Green
pip install -r requirements.txt --quiet

# Run migrations
Write-Host "Running database migrations..." -ForegroundColor Green
try {
    alembic upgrade head
    Write-Host "Database migrations complete" -ForegroundColor Green
} catch {
    Write-Host "Migration failed: $_" -ForegroundColor Red
    exit 1
}

# Create directories
Write-Host "Creating data directories..." -ForegroundColor Green
New-Item -ItemType Directory -Force -Path "data\uploads" | Out-Null
New-Item -ItemType Directory -Force -Path "data\duckdb" | Out-Null
New-Item -ItemType Directory -Force -Path "logs" | Out-Null

Write-Host ""
Write-Host "Setup complete!" -ForegroundColor Green
Write-Host ""
Write-Host "Services running:" -ForegroundColor Cyan
Write-Host "  PostgreSQL:     localhost:5432" -ForegroundColor Gray
Write-Host "  Redis:          localhost:6379" -ForegroundColor Gray
Write-Host "  Qdrant:         http://localhost:6333/dashboard" -ForegroundColor Gray
Write-Host "  Elasticsearch:  http://localhost:9200" -ForegroundColor Gray
Write-Host ""
Write-Host "Next steps (in separate terminals):" -ForegroundColor Yellow
Write-Host "  Terminal 2: .\start_local.ps1" -ForegroundColor Cyan
Write-Host "  Terminal 3: .\start_celery.ps1" -ForegroundColor Cyan
Write-Host ""
