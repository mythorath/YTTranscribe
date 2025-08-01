@echo off
echo 🎬 YT2TranscriptBot - Quick Start
echo ========================================
echo.
echo Activating virtual environment...
cd /d "C:\randomcode\YoutubeTranscribe\yt2transcriptbot"
call venv\Scripts\activate.bat

echo.
echo Starting Interactive CLI...
echo (This provides better progress feedback)
echo.
python interactive_cli.py

pause
