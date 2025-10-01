# MovieRecap Laravel Backend

This is the Laravel backend and frontend for the MovieRecap application. It provides a web interface for uploading movies and scripts, and integrates with the existing Python backend for processing.

## Features

- User authentication and authorization
- Project management
- File upload interface (movies and scripts)
- Integration with the existing movie-recap Python backend
- MySQL database storage
- Dockerized development environment

## Requirements

- PHP 8.2+
- Composer
- Node.js 18+
- MySQL 8.0+
- Docker (optional, for containerized development)

## Installation

1. Clone the repository
2. Navigate to the `laravel-backend` directory
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
7. Configure your database settings in the `.env` file
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

## Running the Application

### Using Laravel's Development Server

```bash
php artisan serve
```

The application will be available at `http://localhost:8000`.

### Using Docker

```bash
docker-compose up -d
```

The application will be available at `http://localhost:8000`.
phpMyAdmin will be available at `http://localhost:8080`.

## Database Schema

The application uses a MySQL database with the following tables:

- `users` - User accounts
- `tenants` - Multi-tenant support
- `projects` - Movie projects
- `assets` - Uploaded files (movies, scripts, etc.)
- `processing_jobs` - Processing jobs
- `scenes` - Scene detection results
- `transcripts` - Transcription results
- `content_moderation` - Content moderation records
- `usage_tracking` - Usage tracking
- `audit_logs` - Audit logs
- `user_sessions` - User sessions

## Integration with Movie-Recap Python Backend

The Laravel application integrates with the existing Python backend through API calls. The integration is handled by the `MovieRecapService` class in `app/Services/MovieRecapService.php`.

Configuration for the integration is stored in the `.env` file:

- `MOVIE_RECAP_API_URL` - URL of the Python backend API
- `MOVIE_RECAP_API_KEY` - API key for authentication
- `GOOGLE_DRIVE_CREDENTIALS_FILE` - Path to Google Drive credentials
- `GOOGLE_DRIVE_ROOT_FOLDER` - Root folder for Google Drive storage
- `COLAB_WEBHOOK_URL` - URL for Colab webhook
- `COLAB_WEBHOOK_SECRET` - Secret for Colab webhook
- `N8N_WEBHOOK_URL` - URL for n8n webhook
- `N8N_API_URL` - URL for n8n API
- `N8N_API_KEY` - API key for n8n

## Development

### Running Tests

```bash
php artisan test
```

### Code Style

The project follows PSR-12 coding standards. You can check and fix code style with:

```bash
./vendor/bin/php-cs-fixer fix
```

## Deployment

The application includes GitHub Actions workflows for CI/CD:

- `.github/workflows/ci.yml` - Continuous integration
- `.github/workflows/deploy.yml` - Deployment

For manual deployment, ensure you:

1. Set the proper environment variables
2. Run migrations
3. Build frontend assets
4. Configure your web server

## License

This project is licensed under the MIT License.