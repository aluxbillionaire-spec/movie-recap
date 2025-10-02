# Movie Recap Laravel Backend

This is the Laravel 12 backend for the Movie Recap service, integrated with Spatie packages and MySQL (XAMPP).

## Features

- Laravel 12 with modern PHP 8.2+
- Spatie Permission for role-based access control
- Spatie Media Library for file management
- MySQL database integration with XAMPP
- Responsive frontend with Tailwind CSS
- CI/CD workflow with GitHub Actions

## Prerequisites

- PHP 8.2 or higher
- Composer
- MySQL (XAMPP recommended)
- Node.js and NPM
- XAMPP (for local development)

## Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd movie-recap/laravel-backend
   ```

2. **Install PHP dependencies**
   ```bash
   composer install
   ```

3. **Install Node dependencies**
   ```bash
   npm install
   ```

4. **Configure environment**
   ```bash
   cp .env.example .env
   php artisan key:generate
   ```

5. **Configure Database**
   - Start XAMPP and ensure MySQL is running
   - Create a database named `laravel` in phpMyAdmin
   - Update `.env` with your database credentials:
     ```
     DB_CONNECTION=mysql
     DB_HOST=127.0.0.1
     DB_PORT=3306
     DB_DATABASE=laravel
     DB_USERNAME=root
     DB_PASSWORD=
     ```

6. **Run Migrations and Seeders**
   ```bash
   php artisan migrate --seed
   ```

7. **Start the development server**
   ```bash
   php artisan serve
   ```

## Database Health Check

To verify database connection and phpMyAdmin access:
```bash
php artisan db:health-check
```

## Frontend

The frontend includes:
- Dashboard with upload/processing/download options
- Upload form for movie files
- Download page for processed files

Access the application at `http://localhost:8000`

## CI/CD

GitHub Actions workflow runs:
- Composer install
- NPM install
- Database migrations
- Unit tests

## Spatie Packages

### Laravel Permission
- Role-based access control
- Predefined roles: admin, user, guest
- Permissions for various actions

### Laravel Media Library
- File upload and management
- Metadata storage
- Integration with local storage

## Testing

Run tests with:
```bash
php artisan test
```

## License

This project is licensed under the MIT License.
