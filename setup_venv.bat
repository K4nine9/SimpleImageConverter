@echo off
REM Setup script for creating virtual environment and installing dependencies (Windows)

echo Creating virtual environment...
python -m venv venv

echo Activating virtual environment...
call venv\Scripts\activate.bat

echo Installing dependencies...
python -m pip install --upgrade pip
pip install -r requirements.txt

echo.
echo Setup complete!
echo To activate the virtual environment, run:
echo   venv\Scripts\activate.bat
echo.
echo To run the application:
echo   python image_converter.py
pause
