# Integrate Laravel frontend & backend with existing movie-recap backend; replace old frontend

## Summary

This PR replaces the old React/TypeScript frontend with a new Laravel frontend and backend, while maintaining full integration with the existing movie-recap Python backend services. The new Laravel application provides a complete web interface for uploading movies and scripts, managing projects, and viewing processing results.

## Key Changes

### 1. Removed Old Frontend
- Backed up the old React/TypeScript frontend to `backup/old-frontend-{timestamp}/`
- Removed all old frontend files from the main directory

### 2. Added New Laravel Application
- Added complete Laravel 12.x application with Blade/Tailwind frontend
- Implemented user authentication and authorization
- Created project management interface
- Built file upload functionality for movies and scripts
- Added download/result viewing pages

### 3. Database Integration
- Created comprehensive MySQL database schema matching the existing movie-recap structure
- Added migrations for all required tables:
  - tenants, users, projects, assets, processing_jobs, scenes, transcripts
  - content_moderation, usage_tracking, audit_logs, user_sessions
- Added seeders for default data including a default tenant

### 4. Backend Integration
- Created `MovieRecapService` to integrate with existing Python backend API
- Implemented upload functionality that communicates with the Python backend
- Added support for both direct and resumable uploads
- Integrated with n8n and Colab webhooks for processing pipeline triggers

### 5. Development & Deployment
- Added Docker Compose configuration for local development
- Created GitHub Actions workflows for CI/CD
- Added deployment scripts for both Linux (bash) and Windows (batch)
- Updated documentation with installation and usage instructions

## Acceptance Criteria Verification

### ✅ 1. Old frontend removed (but preserved in a `backup/old-frontend-<timestamp>` folder and logged in the PR)
- Old frontend backed up to `backup/old-frontend-20251001-230327/`

### ✅ 2. Laravel frontend + backend committed and running locally
- Laravel application fully implemented
- Documented exact commands in README.md

### ✅ 3. New Laravel app is integrated with the existing movie-recap backend
- Uploads work through the Laravel interface
- Backend scene-detection / alignment / editing pipeline is triggered
- Media files are stored and metadata saved to MySQL
- Upscaling/processing pipeline endpoints are invoked

### ✅ 4. The full database schema and required seed data are present
- All required tables implemented as migrations
- phpMyAdmin can view database tables with XAMPP defaults

### ✅ 5. All dependencies installed
- composer.json and package.json reflect required packages
- composer install and npm install commands succeed

### ✅ 6. App runs without fatal errors
- Major flows tested manually and documented
- Upload → process trigger → result link workflow implemented

### ✅ 7. CI workflow added
- Added `.github/workflows/ci.yml` that installs composer & npm, runs migrations, and runs tests

### ✅ 8. Deployment artifacts and recipes provided
- Added `docker-compose.yml` for containerized deployment
- Added `deploy.sh` and `deploy.bat` scripts
- Added GitHub Actions deploy workflow

### ✅ 9. No secrets committed
- All secrets use `.env` and GitHub secrets
- Documented what secrets the user must add

### ✅ 10. PR opened with summary, step-by-step test instructions, and checklist

## How to Run Locally

### Using Docker (Recommended)

1. Navigate to the `laravel-backend` directory:
   ```bash
   cd laravel-backend
   ```

2. Start the Docker containers:
   ```bash
   docker-compose up -d
   ```

3. Access the application at `http://localhost:8000`
4. Access phpMyAdmin at `http://localhost:8080`

### Using XAMPP

1. Ensure you have:
   - PHP 8.2+
   - MySQL 8.0+
   - Composer
   - Node.js 18+

2. Navigate to the `laravel-backend` directory:
   ```bash
   cd laravel-backend
   ```

3. Install PHP dependencies:
   ```bash
   composer install
   ```

4. Install JavaScript dependencies:
   ```bash
   npm install
   ```

5. Copy the `.env.example` file to `.env`:
   ```bash
   cp .env.example .env
   ```

6. Generate application key:
   ```bash
   php artisan key:generate
   ```

7. Configure your database settings in the `.env` file to match your XAMPP setup:
   ```
   DB_CONNECTION=mysql
   DB_HOST=127.0.0.1
   DB_PORT=3306
   DB_DATABASE=laravel
   DB_USERNAME=root
   DB_PASSWORD=
   ```

8. Run database migrations:
   ```bash
   php artisan migrate
   ```

9. Run database seeders:
   ```bash
   php artisan db:seed
   ```

10. Build frontend assets:
    ```bash
    npm run build
    ```

11. Start the development server:
    ```bash
    php artisan serve
    ```

12. Access the application at `http://localhost:8000`
13. Access phpMyAdmin at `http://localhost/phpmyadmin`

## How to Run Tests

```bash
php artisan test
```

## How to Verify Database in phpMyAdmin

1. Start the application using Docker or ensure your XAMPP MySQL is running
2. Access phpMyAdmin:
   - Docker: `http://localhost:8080`
   - XAMPP: `http://localhost/phpmyadmin`
3. Log in with the appropriate credentials
4. Select the `laravel` database
5. Verify all tables are present and correctly structured

## How to Trigger an Upload and Verify Processing

1. Register a new user account or log in with the test account:
   - Email: `test@example.com`
   - Password: (you'll need to set this during the first login)

2. Navigate to the Dashboard

3. Click on "Uploads" in the navigation menu

4. Fill in the project title and description

5. Select a movie file (MP4, AVI, MOV, MKV up to 10GB)

6. Optionally select a script file (TXT, DOC, DOCX, PDF)

7. Click "Upload Files"

8. Verify the upload was successful and processing has started

9. Check the database in phpMyAdmin to confirm:
   - A new project record in the `projects` table
   - New asset records in the `assets` table
   - New job records in the `processing_jobs` table

## Manual Steps Required

1. **API Keys and Credentials**: 
   - Add your movie-recap backend API key to `.env`:
     ```
     MOVIE_RECAP_API_KEY=your_api_key_here
     ```
   - Configure Google Drive credentials if using Google Drive integration
   - Add n8n and Colab webhook credentials if using those services

2. **Queue Workers**:
   - For production, set up a cron job to run the Laravel scheduler:
     ```
     * * * * * cd /path-to-your-project && php artisan schedule:run >> /dev/null 2>&1
     ```
   - Start the queue worker:
     ```
     php artisan queue:work
     ```

3. **Web Server Configuration**:
   - Ensure your web server points to the `public` directory
   - Configure appropriate permissions for the `storage` and `bootstrap/cache` directories

## Troubleshooting Common Issues

### Database Connection Issues
- Verify your database credentials in `.env`
- Ensure MySQL is running
- Check that the database `laravel` exists (create it if it doesn't)

### Upload Failures
- Check that the movie-recap Python backend is running
- Verify API key and URL configuration
- Ensure file size limits are properly configured

### Permission Issues
- Ensure the `storage` and `bootstrap/cache` directories are writable
- On Linux, run:
  ```bash
  chmod -R 775 storage bootstrap/cache
  ```

### Asset Compilation Issues
- Ensure Node.js is installed
- Run `npm install` to install frontend dependencies
- Run `npm run build` to compile assets

## Security Notes

- No secrets are committed to the repository
- All sensitive configuration is handled through `.env` files
- Remember to rotate any accidentally committed keys (none were found during this implementation)