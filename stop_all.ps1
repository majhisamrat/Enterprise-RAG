# Stop all services

Write-Host "Stopping Enterprise RAG services..." -ForegroundColor Yellow
Write-Host ""

# Stop Docker services
Write-Host "Stopping Docker services..." -ForegroundColor Cyan
docker-compose -f docker-compose.services-only.yml down

Write-Host ""
Write-Host "All services stopped" -ForegroundColor Green
