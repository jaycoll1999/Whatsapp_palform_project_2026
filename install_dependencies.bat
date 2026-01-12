@echo off
echo Installing dependencies...
cd /d "d:\RSL_2026\Whatsapp_Api_Project_htjscssfast\backend"
if not exist venv (
    echo Creating virtual environment...
    python -m venv venv
)
call venv\Scripts\activate
pip install --upgrade pip
if exist requirements.txt (
    pip install -r requirements.txt
    echo Dependencies installed successfully!
) else (
    echo ERROR: requirements.txt not found in %CD%
)
pause
