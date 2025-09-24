@echo off
REM Movie Recap Service - Windows Installation Script
echo Movie Recap Service - Windows Installation
echo ==========================================

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Python is not installed or not in PATH
    echo Please install Python 3.11+ from https://python.org
    pause
    exit /b 1
)

REM Check Python version
echo Checking Python version...
python -c "import sys; print(f'Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}'); exit(0 if sys.version_info >= (3, 11) else 1)"
if %errorlevel% neq 0 (
    echo Python 3.11+ required
    pause
    exit /b 1
)

REM Install Chocolatey if not present
where choco >nul 2>&1
if %errorlevel% neq 0 (
    echo Installing Chocolatey package manager...
    powershell -Command "Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))"
    if %errorlevel% neq 0 (
        echo Failed to install Chocolatey
        echo Please install manually from https://chocolatey.org/install
    )
)

REM Install required tools via Chocolatey
echo Installing required tools...
choco install -y git
choco install -y postgresql
choco install -y redis-64
choco install -y docker-desktop
choco install -y ffmpeg
choco install -y nodejs

REM Install Python dependencies
echo Installing Python dependencies...
python -m pip install --upgrade pip
pip install -r backend/requirements.txt
pip install -r requirements-test.txt

REM Create environment file
if not exist ".env" (
    if exist ".env.example" (
        copy ".env.example" ".env"
        echo Created .env file from template
        echo Please edit .env file with your configuration
    )
)

REM Create database (if PostgreSQL is running)
echo Setting up database...
createdb movie_recap 2>nul
createdb test_movie_recap 2>nul

REM Run database migrations
if exist "backend\alembic" (
    cd backend
    alembic upgrade head
    cd ..
)

echo.
echo Installation completed!
echo.
echo Next steps:
echo 1. Edit .env file with your configuration
echo 2. Start Docker Desktop
echo 3. Run: docker-compose up -d
echo 4. Run tests: python run_tests.py --all
echo 5. Access API: http://localhost:8000/docs
echo.
pause