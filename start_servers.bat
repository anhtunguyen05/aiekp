@echo off
echo Starting AIEKP Backend and Frontend servers...

:: Start Backend in a new command window
echo Starting Backend (API)...
start "AIEKP Backend API" cmd /k "cd /d d:\AIEKP\apps\api && uv run uvicorn src.main:app --reload --port 8000"

:: Start Frontend in a new command window
echo Starting Frontend (Dashboard)...
start "AIEKP Frontend Dashboard" cmd /k "cd /d d:\AIEKP\apps\dashboard && npm run dev"

echo Both servers are starting up in separate windows!
echo Backend will run on: http://localhost:8000
echo Frontend will run on: http://localhost:3000 (usually)
pause
