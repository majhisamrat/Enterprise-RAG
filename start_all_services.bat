@echo off
REM ============================================================================
REM Start All Enterprise RAG Services
REM Run this first to start: PostgreSQL, Qdrant, Elasticsearch, Redis
REM ============================================================================

echo.
echo ============================================================
echo Starting Enterprise RAG Services
echo ============================================================
echo.

REM Check if Docker is running
docker ps >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Docker is not running. Please start Docker Desktop first.
    pause
    exit /b 1
)

echo [1/4] Starting PostgreSQL...
docker run --name enterprise-postgres ^
  -e POSTGRES_USER=postgres ^
  -e POSTGRES_PASSWORD=password123 ^
  -e POSTGRES_DB=enterprise_rag ^
  -p 5432:5432 ^
  -d ^
  postgres:15-alpine >nul 2>&1

if %errorlevel% equ 0 (
    echo [OK] PostgreSQL container created
) else (
    docker start enterprise-postgres >nul 2>&1
    if %errorlevel% equ 0 (
        echo [OK] PostgreSQL already running
    )
)

timeout /t 3 /nobreak

echo [2/4] Starting Qdrant Vector Store...
docker run --name enterprise-qdrant ^
  -p 6333:6333 ^
  -p 6334:6334 ^
  -d ^
  qdrant/qdrant:latest >nul 2>&1

if %errorlevel% equ 0 (
    echo [OK] Qdrant container created
) else (
    docker start enterprise-qdrant >nul 2>&1
    if %errorlevel% equ 0 (
        echo [OK] Qdrant already running
    )
)

timeout /t 3 /nobreak

echo [3/4] Starting Elasticsearch...
docker run --name enterprise-elasticsearch ^
  -e discovery.type=single-node ^
  -e xpack.security.enabled=false ^
  -p 9200:9200 ^
  -p 9300:9300 ^
  -d ^
  docker.elastic.co/elasticsearch/elasticsearch:8.11.0 >nul 2>&1

if %errorlevel% equ 0 (
    echo [OK] Elasticsearch container created
) else (
    docker start enterprise-elasticsearch >nul 2>&1
    if %errorlevel% equ 0 (
        echo [OK] Elasticsearch already running
    )
)

timeout /t 3 /nobreak

echo [4/4] Starting Redis...
docker run --name enterprise-redis ^
  -p 6379:6379 ^
  -d ^
  redis:7-alpine >nul 2>&1

if %errorlevel% equ 0 (
    echo [OK] Redis container created
) else (
    docker start enterprise-redis >nul 2>&1
    if %errorlevel% equ 0 (
        echo [OK] Redis already running
    )
)

echo.
echo ============================================================
echo SUCCESS: All services started!
echo ============================================================
echo.
echo Services running on:
echo   - PostgreSQL:     localhost:5432
echo   - Qdrant:         localhost:6333
echo   - Elasticsearch:  localhost:9200
echo   - Redis:          localhost:6379
echo.
echo Next steps:
echo   1. Open a new command prompt and run: start_celery_worker.bat
echo   2. Open another command prompt and run: start_app.bat
echo.
echo To verify services:
echo   docker ps
echo.
echo Press any key to keep this window open (Ctrl+C to close)...
pause
