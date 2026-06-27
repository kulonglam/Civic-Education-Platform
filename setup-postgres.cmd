@echo off
REM Creates the civic_education PostgreSQL database (run once).
REM Edit backend\.env first: set DATABASE_URL with your postgres password.
cd /d "%~dp0backend"

echo.
echo Ensure PostgreSQL is running and backend\.env has the correct DATABASE_URL, e.g.:
echo   postgres://postgres:YOUR_PASSWORD@localhost:5432/civic_education
echo.

set /p PGUSER=PostgreSQL user [postgres]: 
if "%PGUSER%"=="" set PGUSER=postgres
set /p PGPASSWORD=PostgreSQL password: 

"C:\Program Files\PostgreSQL\18\bin\psql.exe" -U %PGUSER% -h localhost -p 5432 -d postgres -c "CREATE DATABASE civic_education;" 2>nul
if errorlevel 1 (
  echo Database may already exist, or connection failed. Check credentials and try again.
) else (
  echo Database civic_education created.
)

echo Running migrations...
"venv\Scripts\python.exe" manage.py migrate
"venv\Scripts\python.exe" manage.py seed_data
echo Done.
pause
