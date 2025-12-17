@echo off
echo 🚀 Starting News Recommendation System (Development Mode)

REM Check Python installation
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python is not installed or not in PATH
    exit /b 1
)

REM Check Node.js installation
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Node.js is not installed or not in PATH
    exit /b 1
)

echo ✅ Prerequisites check passed

REM Install Python dependencies
echo 📦 Installing Python dependencies...
pip install -r requirements.txt

if %errorlevel% neq 0 (
    echo ❌ Failed to install Python dependencies
    exit /b 1
)

REM Install Node.js dependencies
echo 📦 Installing Node.js dependencies...
cd frontend
npm install

if %errorlevel% neq 0 (
    echo ❌ Failed to install Node.js dependencies
    exit /b 1
)

cd ..

echo ✅ Dependencies installed successfully

REM Start backend in a new window
echo 🔧 Starting backend server...
start "NewsAI Backend" cmd /k "python run_backend.py"

REM Wait a bit for backend to start
timeout /t 5 /nobreak > nul

REM Start frontend in a new window
echo 🎨 Starting frontend server...
start "NewsAI Frontend" cmd /k "cd frontend && npm run dev"

echo ✅ Development servers started!
echo.
echo 🌐 Application URLs:
echo    - Frontend: http://localhost:3000
echo    - Backend API: http://localhost:8000
echo    - API Docs: http://localhost:8000/docs
echo.
echo 📝 Check the opened terminal windows for logs
echo 🛑 Close the terminal windows to stop the servers

pause