@echo off
cd /d "d:\RSL_2026\Whatsapp_Api_Project_htjscssfast\backend"
echo Starting Backend in %CD%...
if not exist venv (
    echo Virtual environment not found. Please run install_dependencies.bat first.
    pause
    exit
)
call venv\Scripts\activate
uvicorn main:app --reload --host 0.0.0.0 --port 8000
pause
