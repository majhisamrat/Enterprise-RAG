@echo off
REM ============================================================================
REM Start Celery Worker
REM Run this in a separate command prompt after start_all_services.bat
REM ============================================================================

echo.
echo ============================================================
echo Starting Celery Worker
echo ============================================================
echo.

cd /d "c:\Users\Samratmajhi\Downloads\enterprise-rag"

REM Check if Redis is running
docker ps | findstr "enterprise-redis" >nul
if %errorlevel% neq 0 (
    echo ERROR: Redis not running. Please run start_all_services.bat first.
    pause
    exit /b 1
)

echo [OK] Redis is running
echo.
echo Starting Celery worker...
echo.

REM Activate virtual environment if it exists
if exist ".venv\Scripts\activate.bat" (
    call .venv\Scripts\activate.bat
)

REM Start Celery
celery -A app.tasks worker --loglevel=info

pause
