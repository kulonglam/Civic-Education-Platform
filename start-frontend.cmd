@echo off
REM Starts the Vite/React dev server.
cd /d "%~dp0frontend"

if not exist "node_modules" (
  echo Installing frontend dependencies (first run)...
  call npm install
)

echo Starting frontend on http://localhost:5173 ...
call npm run dev
pause
