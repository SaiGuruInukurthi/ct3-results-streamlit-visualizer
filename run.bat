@echo off
echo ========================================
echo TCD Technical Scorecard - Setup & Run
echo ========================================
echo.

cd /d "%~dp0"

REM Check if venv exists
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
    echo.
)

REM Activate venv
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Install/upgrade dependencies
echo Installing dependencies...
pip install -r requirements.txt --quiet

echo.
echo ========================================
echo Starting Streamlit App...
echo ========================================
echo.
echo Open your browser at: http://localhost:8501
echo Press Ctrl+C to stop the server
echo.

python -m streamlit run "%~dp0app.py"
