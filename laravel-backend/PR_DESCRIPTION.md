# Integrate Laravel 12 + Spatie + XAMPP MySQL; frontend redesign

## Description
This PR fully integrates Laravel 12 with Spatie packages (laravel-permission and laravel-medialibrary) and configures the application to work with XAMPP MySQL. It also includes a complete frontend redesign using Tailwind CSS.

## Changes Made
1. **Laravel 12 Integration**
   - Updated composer.json with Laravel 12 dependencies
   - Configured application for Laravel 12

2. **Spatie Packages Integration**
   - Installed spatie/laravel-permission for RBAC
   - Installed spatie/laravel-medialibrary for file management
   - Created and published migration files for both packages
   - Configured both packages with their respective config files

3. **XAMPP MySQL Configuration**
   - Updated .env.example with XAMPP MySQL defaults
   - Created database health check command (php artisan db:health-check)
   - Verified phpMyAdmin accessibility

4. **Database Setup**
   - Created migrations for roles/permissions and media tables
   - Created seeders for roles/permissions and media
   - Verified that `php artisan migrate --seed` works correctly

5. **Frontend Redesign**
   - Created responsive dashboard with upload/processing/download options
   - Implemented upload form for movie files
   - Created download page for processed files
   - Used Tailwind CSS for modern, clean UI

6. **CI/CD Pipeline**
   - Added GitHub Actions workflow at .github/workflows/ci.yml
   - Configured workflow to run composer install, npm ci, and test migrations

7. **Documentation**
   - Updated README with all setup steps
   - Added clear instructions for XAMPP/phpMyAdmin setup
   - Documented environment variables and local run instructions

## Test Instructions
1. **Database Setup in phpMyAdmin**
   - Start XAMPP and ensure MySQL is running
   - Open phpMyAdmin at http://localhost/phpmyadmin
   - Verify that you can see the `laravel` database

2. **Environment Configuration**
   - Copy .env.example to .env
   - Update database credentials if needed
   - Run `php artisan key:generate`

3. **Migration and Seeding**
   - Run `php artisan migrate --seed`
   - Verify tables are created in phpMyAdmin

4. **Frontend Access**
   - Run `php artisan serve`
   - Visit http://localhost:8000
   - Navigate to the dashboard, upload, and download pages

5. **Database Health Check**
   - Run `php artisan db:health-check`
   - Verify successful connection message

## Manual Steps Required
- Create a MySQL database named `laravel` in phpMyAdmin
- Ensure XAMPP is running with Apache and MySQL services started
- For production use, configure proper file storage permissions

## Security Considerations
- Default credentials are only for development
- File uploads are validated for type and size
- Spatie Permission provides role-based access control
- All credentials should be properly secured in production

## Related Issues
Closes #XX (if applicable)

## Screenshots (if applicable)
Dashboard:
![Dashboard](screenshot-dashboard.png)

Upload Page:
![Upload Page](screenshot-upload.png)

Download Page:
![Download Page](screenshot-download.png)
