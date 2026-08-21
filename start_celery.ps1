# Start Celery Worker (For File Upload Processing)

Write-Host "Starting Celery Worker..." -ForegroundColor Green
Write-Host ""

# Activate virtual environment
.\.venv\Scripts\Activate.ps1

# Start Celery worker
Write-Host "Processing file uploads in background..." -ForegroundColor Cyan
Write-Host "Press Ctrl+C to stop" -ForegroundColor Yellow
Write-Host ""

celery -A app.tasks worker --loglevel=info --pool=solo
