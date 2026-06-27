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

echo Starting Django backend on http://127.0.0.1:8000 ...
"venv\Scripts\python.exe" manage.py runserver
pause
