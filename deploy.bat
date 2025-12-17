@echo off
echo 🚀 Deploying News Recommendation System...

REM Check if .env file exists
if not exist .env (
    echo ❌ .env file not found. Please create one with your configuration.
    exit /b 1
)

echo ✅ Environment file found

REM Check if model files exist
set "model_files=mtl_model.py mtl_model.pt X_inputs.pkl y_click_labels.pkl y_relevance_labels.pkl"
for %%f in (%model_files%) do (
    if not exist "%%f" (
        echo ❌ Model file %%f not found
        exit /b 1
    )
)

echo ✅ Model files validated

REM Build and start services
echo 🔨 Building Docker images...
docker-compose build

if %errorlevel% neq 0 (
    echo ❌ Docker build failed
    exit /b 1
)

echo 🚀 Starting services...
docker-compose up -d

if %errorlevel% neq 0 (
    echo ❌ Failed to start services
    exit /b 1
)

REM Wait for services to be ready
echo ⏳ Waiting for services to be ready...
timeout /t 30 /nobreak > nul

echo ✅ Services are running successfully!
echo.
echo 🌐 Application URLs:
echo    - API: http://localhost:8000
echo    - API Docs: http://localhost:8000/docs
echo    - Health Check: http://localhost:8000/health
echo.
echo 📊 View logs with: docker-compose logs -f
echo 🛑 Stop services with: docker-compose down

pause