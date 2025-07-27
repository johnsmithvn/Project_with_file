@echo off
echo ================================
echo    PROJECT SETUP SCRIPT
echo ================================
echo.

echo [1/4] Kiem tra Python...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python khong duoc cai dat hoac khong co trong PATH
    echo Vui long cai dat Python tu https://python.org
    pause
    exit /b 1
)
echo OK: Python da duoc cai dat

echo.
echo [2/4] Tao virtual environment...
if exist venv (
    echo Virtual environment da ton tai, bo qua...
) else (
    python -m venv venv
    if %errorlevel% neq 0 (
        echo ERROR: Khong the tao virtual environment
        pause
        exit /b 1
    )
    echo OK: Da tao virtual environment
)

echo.
echo [3/4] Kich hoat virtual environment...
call venv\Scripts\activate.bat
if %errorlevel% neq 0 (
    echo ERROR: Khong the kich hoat virtual environment
    pause
    exit /b 1
)
echo OK: Da kich hoat virtual environment

echo.
echo [4/4] Cai dat dependencies...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo WARNING: Co loi khi cai dat requirements
    echo Nhung project van co the chay duoc vi chi su dung built-in modules
)

echo.
echo ================================
echo      SETUP HOAN THANH!
echo ================================
echo.
echo Cac buoc tiep theo:
echo 1. Chay: venv\Scripts\activate.bat
echo 2. Chay manga tool: python manga_renamer.py
echo 3. Chay video tool: python video_thumbnail_generator.py
echo.
echo Luu y: Cai dat FFmpeg cho video thumbnail generator
echo Windows: choco install ffmpeg
echo Hoac tai tu: https://ffmpeg.org/download.html
echo.
pause
