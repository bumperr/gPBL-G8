@echo off
echo ================================================
echo    Elder Care System Startup Script
echo ================================================

:: Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ and try again
    pause
    exit /b 1
)

:: Check if Node.js is installed
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Node.js is not installed or not in PATH
    echo Please install Node.js 16+ and try again
    pause
    exit /b 1
)

:: Check if Ollama is installed
ollama --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Ollama is not installed or not in PATH
    echo Please install Ollama from https://ollama.ai/download
    echo Required AI models: gemma3:4b, llava
    pause
    exit /b 1
)

echo ✓ Python, Node.js, and Ollama detected

:: Create virtual environment if it doesn't exist
if not exist "venv" (
    echo Creating Python virtual environment...
    python -m venv venv
    if %errorlevel% neq 0 (
        echo ERROR: Failed to create virtual environment
        pause
        exit /b 1
    )
)

:: Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat
if %errorlevel% neq 0 (
    echo ERROR: Failed to activate virtual environment
    pause
    exit /b 1
)

:: Install Python dependencies
echo Installing Python dependencies...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo ERROR: Failed to install Python dependencies
    pause
    exit /b 1
)

:: Install Node.js dependencies
@REM echo Installing Node.js dependencies...
@REM cd eldercare-app
@REM npm install
@REM if %errorlevel% neq 0 (
@REM     echo ERROR: Failed to install Node.js dependencies
@REM     cd ..
@REM     pause
@REM     exit /b 1
@REM )
@REM cd ..

:: Check and install required AI models
echo.
echo Checking AI models...
ollama list | findstr "gemma3" >nul 2>&1
if %errorlevel% neq 0 (
    echo Installing gemma3:4b model (required for text chat)...
    ollama pull gemma3:4b
    if %errorlevel% neq 0 (
        echo WARNING: Failed to install gemma3:4b model
        echo AI chat may not work properly
    ) else (
        echo ✓ gemma3:4b model installed
    )
) else (
    echo ✓ gemma3 model already available
)

ollama list | findstr "llava" >nul 2>&1
if %errorlevel% neq 0 (
    echo Installing llava model (required for image processing)...
    ollama pull llava
    if %errorlevel% neq 0 (
        echo WARNING: Failed to install llava model
        echo Image analysis may not work properly
    ) else (
        echo ✓ llava model installed
    )
) else (
    echo ✓ llava model already available
)

echo.
echo ================================================
echo    Dependencies installed successfully!
echo ================================================
echo.
echo Starting Elder Care System...
echo.
echo 1. Ollama AI Service: http://localhost:11434
echo 2. Backend API will start on: http://localhost:8000
echo 3. Frontend will start on: http://localhost:3000
echo 4. API Documentation: http://localhost:8000/docs
echo.
echo Press Ctrl+C to stop the services
echo.

:: Start Ollama service first (if not already running)
echo Starting Ollama AI service...
start "Ollama AI Service" cmd /k "ollama serve"

:: Wait for Ollama to start
echo Waiting for Ollama service to initialize...
timeout /t 10 /nobreak >nul

:: Start backend in new window
echo Starting Backend API...
start "Elder Care Backend" cmd /k "venv\Scripts\activate.bat && python main.py"

:: Wait a moment for backend to start
timeout /t 5 /nobreak >nul

:: Start frontend in new window
echo Starting Frontend...
start "Elder Care Frontend" cmd /k "cd eldercare-app && npm run dev"

:: Wait a moment for frontend to start
timeout /t 5 /nobreak >nul

:: Open browser to the application
echo Opening Elder Care System in browser...
timeout /t 3 /nobreak >nul
start http://localhost:3000

echo.
echo ================================================
echo    Elder Care System Started Successfully!
echo ================================================
echo.
echo Backend API: http://localhost:8000
echo Frontend App: http://localhost:3000
echo Caregiver Dashboard: http://localhost:3000/caregiver
echo API Documentation: http://localhost:8000/docs
echo.
echo Both services are running in separate windows.
echo Close this window or press any key to exit.
echo To stop services, close the Backend and Frontend windows.
echo.
pause