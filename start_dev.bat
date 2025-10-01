@echo off
echo Starting Movie Recap Service - Development Mode
echo =============================================

REM Start Redis if not running
echo Starting Redis...
start /B redis-server

REM Start PostgreSQL if not running  
echo Starting PostgreSQL...
net start postgresql-x64-14

REM Wait a moment for services to start
timeout /t 5

REM Set environment
set ENVIRONMENT=development

REM Start the application
echo Starting FastAPI application...
cd backend
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

pause
