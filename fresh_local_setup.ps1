# Fresh local setup with docker-compose.services-only.yml

Write-Host "Stopping any existing Docker services..." -ForegroundColor Yellow
docker-compose -f docker-compose.services-only.yml down -v

Write-Host "Starting fresh Docker services..." -ForegroundColor Green
docker-compose -f docker-compose.services-only.yml up -d

Write-Host "Waiting 20 seconds for services to be healthy..." -ForegroundColor Cyan
Start-Sleep -Seconds 20

Write-Host ""
Write-Host "Docker services are now running!" -ForegroundColor Green
Write-Host ""
Write-Host "Services available at:" -ForegroundColor Cyan
Write-Host "  PostgreSQL:     localhost:5432 (postgres / password123)" -ForegroundColor Gray
Write-Host "  Redis:          localhost:6379" -ForegroundColor Gray
Write-Host "  Qdrant:         http://localhost:6333/dashboard" -ForegroundColor Gray
Write-Host "  Elasticsearch:  http://localhost:9200" -ForegroundColor Gray
Write-Host ""
Write-Host "Next steps (in separate terminals):" -ForegroundColor Yellow
Write-Host "  Terminal 2: .\start_local.ps1" -ForegroundColor Cyan
Write-Host "  Terminal 3: .\start_celery.ps1" -ForegroundColor Cyan
Write-Host ""
Write-Host "Keep this terminal open to keep services running" -ForegroundColor Yellow
