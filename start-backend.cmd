@echo off
REM Always runs the backend using the project's virtual environment,
REM regardless of the current directory or whether the venv is "activated".
cd /d "%~dp0backend"

if not exist "venv\Scripts\python.exe" (
  echo [ERROR] Virtual environment not found at backend\venv
  echo Create it first:  python -m venv venv ^&^& venv\Scripts\pip install -r requirements.txt
  pause
  exit /b 1
)

echo Starting Django backend (ASGI / WebSockets) on http://127.0.0.1:8000 ...
set DJANGO_SETTINGS_MODULE=config.settings.development
"venv\Scripts\python.exe" -m daphne -b 127.0.0.1 -p 8000 config.asgi:application
pause
