#!/bin/bash
# Simple launcher for YT2TranscriptBot Interactive CLI
# This shell script launches the interactive interface

echo
echo "=========================================="
echo "  YT2TranscriptBot Launcher"
echo "=========================================="
echo

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed or not in PATH"
    echo "Please install Python 3.9+ and try again"
    exit 1
fi

# Check if we're in the right directory
if [ ! -f "yt2transcript.py" ]; then
    echo "Error: yt2transcript.py not found"
    echo "Please run this from the yt2transcriptbot directory"
    exit 1
fi

# Launch the interactive CLI
echo "Launching interactive CLI..."
echo
python3 interactive_cli.py

echo
read -p "Press Enter to continue..."
