@echo off
echo ============================================
echo Starting WhatsApp Platform (Backend + Frontend)
echo ============================================

echo 1. Launching Backend API...
start "WhatsApp Backend" cmd /k "call run_backend.bat"

echo 2. Launching Frontend Server...
start "WhatsApp Frontend" cmd /k "call run_frontend.bat"

echo.
echo Process started! 
echo Please wait a moment for the backend to initialize...
echo The application should automatically open in your default browser at http://localhost:8080
echo.
pause
