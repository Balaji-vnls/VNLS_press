@echo off
echo 🏢 Starting NARAYANASWAMY SONS News Intelligence Platform
echo ================================================================

REM Check if Python is available
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python is not installed or not in PATH
    pause
    exit /b 1
)

REM Check if Node.js is available
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Node.js is not installed or not in PATH
    pause
    exit /b 1
)

echo ✅ Prerequisites check passed

REM Check if .env file exists
if not exist .env (
    echo ❌ .env file not found. Please ensure Supabase credentials are configured.
    pause
    exit /b 1
)

echo ✅ Environment configuration found

REM Install Python dependencies
echo 📦 Installing Python dependencies...
pip install -q fastapi uvicorn supabase python-dotenv aiohttp feedparser beautifulsoup4 lxml aiofiles "pydantic[email]"

REM Install Node.js dependencies
echo 📦 Installing Node.js dependencies...
cd frontend
npm install --silent

if %errorlevel% neq 0 (
    echo ❌ Failed to install Node.js dependencies
    pause
    exit /b 1
)

cd ..

echo ✅ Dependencies installed successfully

REM Start backend in a new window
echo 🔧 Starting NARAYANASWAMY SONS Secure Backend...
start "NARAYANASWAMY SONS Backend" cmd /k "python secure_backend.py"

REM Wait for backend to start
timeout /t 8 /nobreak > nul

REM Start frontend in a new window
echo 🎨 Starting NARAYANASWAMY SONS Frontend...
start "NARAYANASWAMY SONS Frontend" cmd /k "cd frontend && npm run dev"

echo ✅ NARAYANASWAMY SONS News Intelligence Platform Started!
echo.
echo 🌐 Application URLs:
echo    - Main Application: http://localhost:3001
echo    - Secure API Backend: http://localhost:8000
echo    - API Documentation: http://localhost:8000/docs
echo    - System Status: http://localhost:8000/api/status
echo.
echo 🔐 Security Features:
echo    - Supabase Authentication with Email Verification
echo    - JWT Token-based Sessions
echo    - Password Reset Functionality
echo    - Protected Routes
echo.
echo 📰 Live News Features:
echo    - Real-time news from NewsAPI and GNews
echo    - AI-powered recommendations
echo    - Category filtering
echo    - Search functionality
echo.
echo 🏢 Company: Narayanaswamy Sons
echo 📝 Check the opened terminal windows for logs
echo 🛑 Close the terminal windows to stop the services

pause