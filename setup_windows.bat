@echo off
cd /d "%~dp0"
echo Creating Python 3 virtual environment...
py -3.12 -m venv .venv
if errorlevel 1 (
    echo Python 3.12 was not found. Install Python 3.12 and retry.
    pause
    exit /b 1
)
call .venv\Scripts\activate.bat
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
echo.
echo Setup complete. Run run_app.bat to start the dashboard.
pause
