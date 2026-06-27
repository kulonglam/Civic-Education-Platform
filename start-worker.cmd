@echo off
REM Starts a Celery worker for background tasks (notifications fan-out, email, certificate PDFs).
REM Requires Redis running and CELERY_TASK_ALWAYS_EAGER=False in backend\.env
cd /d "%~dp0backend"

if not exist "venv\Scripts\python.exe" (
  echo [ERROR] Virtual environment not found at backend\venv
  echo Create it first:  python -m venv venv ^&^& venv\Scripts\pip install -r requirements.txt
  pause
  exit /b 1
)

echo Starting Celery worker ...
REM The solo pool is the most reliable worker pool on Windows.
"venv\Scripts\python.exe" -m celery -A config worker --loglevel=info --pool=solo
pause
