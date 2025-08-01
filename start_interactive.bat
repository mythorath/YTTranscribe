@echo off
REM Simple launcher for YT2TranscriptBot Interactive CLI
REM This batch file launches the interactive interface

echo.
echo ==========================================
echo   YT2TranscriptBot Launcher
echo ==========================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python 3.9+ and try again
    pause
    exit /b 1
)

REM Check if we're in the right directory
if not exist "yt2transcript.py" (
    echo Error: yt2transcript.py not found
    echo Please run this from the yt2transcriptbot directory
    pause
    exit /b 1
)

REM Launch the interactive CLI
echo Launching interactive CLI...
echo.
python interactive_cli.py

echo.
pause
