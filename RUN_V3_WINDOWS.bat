@echo off
cd /d "%~dp0"
echo ==============================================
echo ResilientCity AI V3 - Local PyCharm/Windows
echo ==============================================
python --version
echo.
python -m pip install -r requirements.txt
if errorlevel 1 (
    echo.
    echo ERROR: Could not install dependencies.
    echo Check the selected PyCharm Python interpreter and internet connection.
    pause
    exit /b 1
)
echo.
echo Running tests...
python -m pytest -q
echo.
echo Starting GUI...
python gui.py
pause
