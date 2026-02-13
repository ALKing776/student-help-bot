@echo off
REM Enhanced Student Help Bot Startup Script - Windows

echo 🚀 Starting Enhanced Student Help Bot...
echo ==================================================

REM Check for Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python not found. Please install Python 3.8 or higher.
    pause
    exit /b 1
)

REM Check for .env file
if not exist .env (
    echo ⚠️  .env file not found.
    echo 📋 Creating .env from example...
    copy .env.example .env >nul
    echo ✏️  Please edit .env file with your credentials
    echo    notepad .env
    pause
    exit /b 1
)

REM Install requirements
echo 📦 Checking requirements...
pip install -r requirements.txt -q

REM Check if enhanced_bot.py exists
if exist enhanced_bot.py (
    echo 🤖 Starting Enhanced Bot...
    python enhanced_bot.py
) else (
    echo ⚠️  enhanced_bot.py not found, falling back to original bot...
    python student_help_bot.py
)

pause