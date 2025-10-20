@echo off
REM Start Milton AI Publicist Dashboard on Port 8081
REM (Use this if port 8080 is in use)

cd /d "%~dp0"

echo ======================================================================
echo MILTON AI PUBLICIST - DASHBOARD
echo ======================================================================
echo.
echo Starting dashboard on http://localhost:8081
echo (Using port 8081 because 8080 is in use by recruiting app)
echo.
echo Press Ctrl+C to stop the server
echo ======================================================================
echo.

set DASHBOARD_PORT=8081
python dashboard\app.py

pause
