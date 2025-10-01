#!/bin/bash

# MovieRecap Laravel Deployment Script

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print status messages
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

# Function to print warning messages
print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Function to print error messages
print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running on Windows (Git Bash) or Linux
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    IS_WINDOWS=1
else
    IS_WINDOWS=0
fi

# Check if .env file exists
if [ ! -f ".env" ]; then
    print_warning ".env file not found. Copying .env.example..."
    cp .env.example .env
fi

# Install PHP dependencies
print_status "Installing PHP dependencies..."
if command -v composer &> /dev/null; then
    composer install --no-dev --optimize-autoloader
    if [ $? -ne 0 ]; then
        print_error "Failed to install PHP dependencies"
        exit 1
    fi
else
    print_error "Composer not found. Please install Composer first."
    exit 1
fi

# Install Node.js dependencies
print_status "Installing Node.js dependencies..."
if command -v npm &> /dev/null; then
    npm ci
    if [ $? -ne 0 ]; then
        print_error "Failed to install Node.js dependencies"
        exit 1
    fi
else
    print_error "npm not found. Please install Node.js first."
    exit 1
fi

# Generate application key if not exists
if ! grep -q "APP_KEY=base64:" .env; then
    print_status "Generating application key..."
    php artisan key:generate
    if [ $? -ne 0 ]; then
        print_error "Failed to generate application key"
        exit 1
    fi
fi

# Run database migrations
print_status "Running database migrations..."
php artisan migrate --force
if [ $? -ne 0 ]; then
    print_error "Failed to run database migrations"
    exit 1
fi

# Run database seeders
print_status "Running database seeders..."
php artisan db:seed --force
if [ $? -ne 0 ]; then
    print_error "Failed to run database seeders"
    exit 1
fi

# Build frontend assets
print_status "Building frontend assets..."
npm run build
if [ $? -ne 0 ]; then
    print_error "Failed to build frontend assets"
    exit 1
fi

# Cache optimization
print_status "Optimizing Laravel caches..."
php artisan config:cache
php artisan route:cache
php artisan view:cache
if [ $? -ne 0 ]; then
    print_error "Failed to optimize Laravel caches"
    exit 1
fi

# Set proper permissions
print_status "Setting proper permissions..."
if [ $IS_WINDOWS -eq 0 ]; then
    chmod -R 755 storage bootstrap/cache
    chmod -R 777 storage/logs
else
    print_warning "Skipping permissions setup on Windows"
fi

print_status "Deployment completed successfully!"
echo
print_status "Next steps:"
echo "1. Configure your web server to point to the public directory"
echo "2. Ensure your database is properly configured"
echo "3. Set up any required cron jobs for queue workers"
echo
print_status "The application should now be accessible through your web server."