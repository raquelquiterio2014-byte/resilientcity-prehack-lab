@echo off
cd /d "%~dp0"
echo =================================================
echo ResilientCity AI V4 Experimental - Windows/PyCharm
echo =================================================
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
echo Running V4 tests...
python -m pytest -q
if errorlevel 1 (
    echo.
    echo WARNING: One or more tests failed. GUI will not start automatically.
    pause
    exit /b 1
)
echo.
echo Starting V4 GUI...
python gui.py
pause
