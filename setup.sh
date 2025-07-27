#!/bin/bash

echo "================================"
echo "    PROJECT SETUP SCRIPT"
echo "================================"
echo

echo "[1/4] Checking Python..."
if ! command -v python3 &> /dev/null; then
    if ! command -v python &> /dev/null; then
        echo "ERROR: Python not found"
        echo "Please install Python from https://python.org"
        exit 1
    else
        PYTHON_CMD="python"
    fi
else
    PYTHON_CMD="python3"
fi
echo "OK: Python found ($PYTHON_CMD)"

echo
echo "[2/4] Creating virtual environment..."
if [ -d "venv" ]; then
    echo "Virtual environment already exists, skipping..."
else
    $PYTHON_CMD -m venv venv
    if [ $? -ne 0 ]; then
        echo "ERROR: Cannot create virtual environment"
        exit 1
    fi
    echo "OK: Virtual environment created"
fi

echo
echo "[3/4] Activating virtual environment..."
source venv/bin/activate
if [ $? -ne 0 ]; then
    echo "ERROR: Cannot activate virtual environment"
    exit 1
fi
echo "OK: Virtual environment activated"

echo
echo "[4/4] Installing dependencies..."
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "WARNING: Error installing requirements"
    echo "But project should still work as it uses built-in modules"
fi

echo
echo "================================"
echo "      SETUP COMPLETE!"
echo "================================"
echo
echo "Next steps:"
echo "1. Run: source venv/bin/activate"
echo "2. Run manga tool: python manga_renamer.py"
echo "3. Run video tool: python video_thumbnail_generator.py"
echo
echo "Note: Install FFmpeg for video thumbnail generator"
echo "macOS: brew install ffmpeg"
echo "Ubuntu: sudo apt install ffmpeg"
echo "Or download from: https://ffmpeg.org/download.html"
echo
