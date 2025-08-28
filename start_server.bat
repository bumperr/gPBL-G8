@echo off
echo Activating virtual environment...
call venv\Scripts\activate.bat

echo Starting FastAPI server...
python main.py

pause