@echo off
REM ============================================================================
REM Start FastAPI Application
REM Run this in a separate command prompt after start_all_services.bat
REM ============================================================================

echo.
echo ============================================================
echo Starting FastAPI Application
echo ============================================================
echo.

cd /d "c:\Users\Samratmajhi\Downloads\enterprise-rag"

REM Check if all services are running
echo Checking services...
docker ps | findstr "enterprise-postgres" >nul
if %errorlevel% neq 0 (
    echo ERROR: PostgreSQL not running
    goto error
)
echo [OK] PostgreSQL

docker ps | findstr "enterprise-qdrant" >nul
if %errorlevel% neq 0 (
    echo ERROR: Qdrant not running
    goto error
)
echo [OK] Qdrant

docker ps | findstr "enterprise-elasticsearch" >nul
if %errorlevel% neq 0 (
    echo ERROR: Elasticsearch not running
    goto error
)
echo [OK] Elasticsearch

docker ps | findstr "enterprise-redis" >nul
if %errorlevel% neq 0 (
    echo ERROR: Redis not running
    goto error
)
echo [OK] Redis

echo.
echo All services are running!
echo.

REM Activate virtual environment if it exists
if exist ".venv\Scripts\activate.bat" (
    call .venv\Scripts\activate.bat
)

REM Start the app
echo Starting FastAPI application on http://localhost:8000
echo.
python -m uvicorn app.app_config:app --reload --host 0.0.0.0 --port 8000

pause
exit /b 0

:error
echo.
echo ERROR: Not all services are running!
echo Please run start_all_services.bat first.
pause
exit /b 1
