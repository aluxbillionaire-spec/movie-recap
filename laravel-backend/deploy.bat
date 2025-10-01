@echo off
title MovieRecap Laravel Deployment

echo ========================================
echo MovieRecap Laravel Deployment Script
echo ========================================
echo.

REM Check if .env file exists
if not exist ".env" (
    echo [WARNING] .env file not found. Copying .env.example...
    copy .env.example .env
)

REM Install PHP dependencies
echo [INFO] Installing PHP dependencies...
composer install --no-dev --optimize-autoloader
if %errorlevel% neq 0 (
    echo [ERROR] Failed to install PHP dependencies
    exit /b 1
)

REM Install Node.js dependencies
echo [INFO] Installing Node.js dependencies...
npm ci
if %errorlevel% neq 0 (
    echo [ERROR] Failed to install Node.js dependencies
    exit /b 1
)

REM Generate application key if not exists
findstr /C:"APP_KEY=base64:" .env >nul
if %errorlevel% neq 0 (
    echo [INFO] Generating application key...
    php artisan key:generate
    if %errorlevel% neq 0 (
        echo [ERROR] Failed to generate application key
        exit /b 1
    )
)

REM Run database migrations
echo [INFO] Running database migrations...
php artisan migrate --force
if %errorlevel% neq 0 (
    echo [ERROR] Failed to run database migrations
    exit /b 1
)

REM Run database seeders
echo [INFO] Running database seeders...
php artisan db:seed --force
if %errorlevel% neq 0 (
    echo [ERROR] Failed to run database seeders
    exit /b 1
)

REM Build frontend assets
echo [INFO] Building frontend assets...
npm run build
if %errorlevel% neq 0 (
    echo [ERROR] Failed to build frontend assets
    exit /b 1
)

REM Cache optimization
echo [INFO] Optimizing Laravel caches...
php artisan config:cache
php artisan route:cache
php artisan view:cache
if %errorlevel% neq 0 (
    echo [ERROR] Failed to optimize Laravel caches
    exit /b 1
)

echo.
echo [INFO] Deployment completed successfully!
echo.
echo [INFO] Next steps:
echo 1. Configure your web server to point to the public directory
echo 2. Ensure your database is properly configured
echo 3. Set up any required cron jobs for queue workers
echo.
echo [INFO] The application should now be accessible through your web server.
echo.
pause