@echo off
REM Milestone 6: Full Deployment & Integration Testing for Windows
REM This script deploys both backend and frontend to Railway and runs integration tests

echo 🚀 Starting Milestone 6 Deployment...

REM Check if Railway CLI is installed
where railway >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo ❌ Railway CLI not found. Installing...
    npm install -g @railway/cli
    if %ERRORLEVEL% NEQ 0 (
        echo ❌ Failed to install Railway CLI
        exit /b 1
    )
)

REM Check if user is logged in to Railway
railway whoami >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo ❌ Not logged in to Railway. Please run 'railway login' first.
    exit /b 1
)

echo ✅ Railway CLI authenticated

REM Deploy backend first
echo 📦 Deploying backend to Railway...
cd backend

REM Set up environment variables for Railway
echo 🔧 Setting up environment variables...
if defined ZAI_API_KEY (
    railway variables set ZAI_API_KEY=%ZAI_API_KEY%
) else (
    echo ⚠️ ZAI_API_KEY not set. Please set it before running this script.
)

if defined DATABASE_URL (
    railway variables set DATABASE_URL=%DATABASE_URL%
) else (
    echo ⚠️ DATABASE_URL not set. Railway will create PostgreSQL for you.
)

REM Deploy backend
echo 🚢 Deploying backend service...
railway up
if %ERRORLEVEL% NEQ 0 (
    echo ❌ Backend deployment failed
    exit /b 1
)

REM Get backend URL
echo 🌐 Getting backend URL...
for /f "tokens=*" %%i in ('railway domain') do set BACKEND_URL=%%i
echo ✅ Backend deployed to: %BACKEND_URL%

REM Wait for backend to be ready
echo ⏳ Waiting for backend to be ready...
timeout /t 30 /nobreak >nul

REM Test backend health
echo 🏥 Testing backend health...
curl -f "%BACKEND_URL%/api/v1/ui/health"
if %ERRORLEVEL% NEQ 0 (
    echo ❌ Backend health check failed
    exit /b 1
)

cd ..\frontend

REM Update frontend environment to use Railway backend
echo 🔧 Updating frontend configuration...
echo VITE_API_BASE_URL=%BACKEND_URL% > .env.production

REM Deploy frontend
echo 🚢 Deploying frontend service...
railway up
if %ERRORLEVEL% NEQ 0 (
    echo ❌ Frontend deployment failed
    exit /b 1
)

REM Get frontend URL
echo 🌐 Getting frontend URL...
for /f "tokens=*" %%i in ('railway domain') do set FRONTEND_URL=%%i
echo ✅ Frontend deployed to: %FRONTEND_URL%

REM Wait for frontend to be ready
echo ⏳ Waiting for frontend to be ready...
timeout /t 30 /nobreak >nul

REM Test frontend health
echo 🏥 Testing frontend health...
curl -f "%FRONTEND_URL%"
if %ERRORLEVEL% NEQ 0 (
    echo ❌ Frontend health check failed
    exit /b 1
)

echo 🧪 Running integration tests...

REM Test API endpoints
echo 📋 Testing API endpoints...

REM Create a test session
echo Creating test session...
curl -s -X POST "%BACKEND_URL%/api/v1/sessions" -H "Content-Type: application/json" -d "{\"title\": \"Milestone 6 Test Session\"}" > session_response.json

REM Extract session ID (simplified for batch)
for /f "tokens=2 delims=:\" %%i in ('findstr "\"id\"" session_response.json') do set SESSION_ID=%%i

if "%SESSION_ID%"=="" (
    echo ❌ Failed to create test session
    del session_response.json
    exit /b 1
)

echo ✅ Test session created: %SESSION_ID%

REM Send a test message
echo Sending test message...
curl -s -X POST "%BACKEND_URL%/api/v1/sessions/%SESSION_ID%/messages" -H "Content-Type: application/json" -d "{\"content\": \"Hello, this is a test message for Milestone 6\"}"

echo ✅ Test message sent

REM Verify session history
echo Verifying session history...
curl -s "%BACKEND_URL%/api/v1/sessions/%SESSION_ID%/history" | findstr "Hello, this is a test message"
if %ERRORLEVEL% NEQ 0 (
    echo ❌ Failed to retrieve session history
    del session_response.json
    exit /b 1
)

echo ✅ Session history verified

REM Test agent creation
echo Creating test agent...
curl -s -X POST "%BACKEND_URL%/api/v1/agents" -H "Content-Type: application/json" -d "{\"name\": \"Milestone 6 Test Agent\", \"model\": \"glm-4.5\", \"system_prompt\": \"You are a helpful assistant for testing.\"}" > agent_response.json

REM Extract agent ID (simplified for batch)
for /f "tokens=2 delims=:\" %%i in ('findstr "\"id\"" agent_response.json') do set AGENT_ID=%%i

if "%AGENT_ID%"=="" (
    echo ❌ Failed to create test agent
    del session_response.json agent_response.json
    exit /b 1
)

echo ✅ Test agent created: %AGENT_ID%

REM Clean up test data
echo 🧹 Cleaning up test data...
curl -s -X DELETE "%BACKEND_URL%/api/v1/sessions/%SESSION_ID%"
curl -s -X DELETE "%BACKEND_URL%/api/v1/agents/%AGENT_ID%"

REM Clean up temporary files
del session_response.json agent_response.json

echo ✅ Integration tests completed successfully!

REM Display deployment summary
echo.
echo 🎉 Milestone 6 Deployment Complete!
echo ===================================
echo Backend URL: %BACKEND_URL%
echo Frontend URL: %FRONTEND_URL%
echo API Documentation: %BACKEND_URL%/docs
echo Health Check: %BACKEND_URL%/api/v1/ui/health
echo.
echo ✅ All integration tests passed!
echo ✅ Ready to proceed to Milestone 7: Polish & Optimization