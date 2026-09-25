@echo off
setlocal enabledelayedexpansion

echo ===================================================================
echo               FINNEWS AI - Financial News Simplifier
echo                   Capstone Project Startup Script
echo ===================================================================
echo.

:: 1. Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not in your system PATH!
    echo Please download and install Python 3.12 or newer from https://www.python.org/
    echo Make sure to check "Add Python to PATH" during installation.
    echo.
    pause
    exit /b 1
)

echo [OK] Python is available:
python --version
echo.

:: 2. Check or create virtual environment
if not exist "venv" (
    echo [*] Creating Python virtual environment in .\venv...
    python -m venv venv
    if %errorlevel% neq 0 (
        echo [ERROR] Failed to create virtual environment!
        pause
        exit /b 1
    )
    echo [OK] Virtual environment created successfully.
) else (
    echo [OK] Virtual environment found.
)
echo.

:: 3. Activate virtual environment
echo [*] Activating virtual environment...
call venv\Scripts\activate.bat
if %errorlevel% neq 0 (
    echo [ERROR] Could not activate virtual environment!
    pause
    exit /b 1
)
echo [OK] Virtual environment activated.
echo.

:: 4. Ensure .env exists
if not exist "backend\.env" (
    if not exist ".env" (
        if exist "backend\.env.example" (
            echo [*] Initializing backend\.env from backend\.env.example...
            copy backend\.env.example backend\.env >nul
            copy backend\.env.example .env >nul
            echo [!] Created .env and backend\.env files.
            echo [!] Remember to open backend\.env and add your NEWS_API_KEY and GROQ_API_KEY!
        )
    )
)
echo.

:: 5. Install / update dependencies
echo [*] Installing requirements from backend\requirements.txt...
pip install -r backend\requirements.txt
if %errorlevel% neq 0 (
    echo [ERROR] Failed to install required packages!
    pause
    exit /b 1
)
echo [OK] All dependencies installed successfully.
echo.

:: 6. Launch FastAPI backend with Uvicorn
echo ===================================================================
echo Starting FINNEWS AI Backend Server...
echo API URL:          http://127.0.0.1:8000
echo Swagger UI Docs:  http://127.0.0.1:8000/docs
echo Web Application:  http://127.0.0.1:8000/app/
echo ===================================================================
echo Press CTRL+C at any time to stop the server.
echo.

python -m uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000
pause
