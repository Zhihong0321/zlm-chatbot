@echo off
REM Switch to Local Development Mode (Windows)

echo 🏠 Switching to LOCAL DEVELOPMENT mode...

REM Copy local environment config
copy .env.local .env

REM Start PostgreSQL if not running
docker ps | findstr "oneapi-postgres" >nul
if errorlevel 1 (
    echo 🚀 Starting PostgreSQL container...
    docker-compose up -d postgres
    echo ⏳ Waiting for database to be ready...
    timeout /t 5 /nobreak >nul
)

REM Test database connection
echo 🔍 Testing database connection...
python test_local_db.py

if %errorlevel% equ 0 (
    echo ✅ Local development setup complete!
    echo.
    echo 🚀 Start the application with:
    echo    cd backend ^&^& uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
) else (
    echo ❌ Database setup failed. Check the logs above.
)
