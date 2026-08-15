# ============================================================================
# Start FastAPI Application for Enterprise RAG
# Run this in a separate terminal after start_all_services.ps1
# ============================================================================

Write-Host "🚀 Starting FastAPI Application" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

$ProjectPath = "c:\Users\Samratmajhi\Downloads\enterprise-rag"
$Port = 8000

Write-Host "📁 Project Path: $ProjectPath" -ForegroundColor Gray
Write-Host "🌐 Port:         $Port" -ForegroundColor Gray
Write-Host ""

# Check if all services are running
Write-Host "🔍 Checking services..." -ForegroundColor Yellow

$services = @(
    @{ Name = "PostgreSQL"; Check = { docker ps --filter "name=enterprise-postgres" --format "{{.Names}}" 2>/dev/null } },
    @{ Name = "Qdrant"; Check = { docker ps --filter "name=enterprise-qdrant" --format "{{.Names}}" 2>/dev/null } },
    @{ Name = "Elasticsearch"; Check = { docker ps --filter "name=enterprise-elasticsearch" --format "{{.Names}}" 2>/dev/null } },
    @{ Name = "Redis"; Check = { docker ps --filter "name=enterprise-redis" --format "{{.Names}}" 2>/dev/null } }
)

$allRunning = $true
foreach ($service in $services) {
    $running = & $service.Check
    if ($running) {
        Write-Host "   ✅ $($service.Name)" -ForegroundColor Green
    } else {
        Write-Host "   ❌ $($service.Name)" -ForegroundColor Red
        $allRunning = $false
    }
}

if (-not $allRunning) {
    Write-Host ""
    Write-Host "⚠️  Some services are not running!" -ForegroundColor Red
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
Write-Host "⏳ Starting FastAPI application..." -ForegroundColor Cyan
Write-Host ""

# Start the app
python -m uvicorn app.app_config:app --reload --host 0.0.0.0 --port $Port

Write-Host ""
Write-Host "FastAPI application stopped." -ForegroundColor Yellow
