@echo off
echo 🚀 YT2TranscriptBot Setup Script for Windows
echo ==========================================

echo.
echo 📋 Step 1: Creating virtual environment...
python -m venv venv
if %errorlevel% neq 0 (
    echo ❌ Failed to create virtual environment
    echo Please ensure Python 3.9+ is installed
    pause
    exit /b 1
)

echo ✅ Virtual environment created

echo.
echo 📋 Step 2: Activating virtual environment...
call venv\Scripts\activate
if %errorlevel% neq 0 (
    echo ❌ Failed to activate virtual environment
    pause
    exit /b 1
)

echo ✅ Virtual environment activated

echo.
echo 📋 Step 3: Installing Python packages...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo ❌ Failed to install packages
    echo Please check your internet connection and try again
    pause
    exit /b 1
)

echo ✅ Python packages installed

echo.
echo 📋 Step 4: Checking FFmpeg installation...
ffmpeg -version >nul 2>&1
if %errorlevel% neq 0 (
    echo ⚠️  FFmpeg not found in PATH
    echo.
    echo Please install FFmpeg:
    echo   Option 1: Using Chocolatey: choco install ffmpeg
    echo   Option 2: Download from https://ffmpeg.org/download.html
    echo.
    echo After installation, restart this script
    pause
    exit /b 1
) else (
    echo ✅ FFmpeg is available
)

echo.
echo 📋 Step 5: Running setup validation...
python test_setup.py

echo.
echo 🎉 Setup complete!
echo.
echo 📝 Next steps:
echo   1. (Optional) Set your OpenAI API key: set OPENAI_API_KEY=your_key_here
echo   2. Try the tool: python yt2transcript.py "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
echo.
echo 📚 For more information, see README.md
echo.
pause
