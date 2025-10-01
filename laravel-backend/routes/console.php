<?php

use Illuminate\Foundation\Inspiring;
use Illuminate\Support\Facades\Artisan;
use Illuminate\Support\Facades\DB;

Artisan::command('inspire', function () {
    $this->comment(Inspiring::quote());
})->purpose('Display an inspiring quote');

// Register our custom command
Artisan::command('db:health-check', function () {
    try {
        // Test database connection
        DB::connection()->getPdo();

        // Get database name
        $databaseName = DB::connection()->getDatabaseName();

        $this->info('✓ Database connection successful!');
        $this->info("✓ Connected to database: {$databaseName}");

        // Test if we can query the database
        $tables = DB::select('SHOW TABLES');
        $this->info('✓ Database query successful!');
        $this->info('✓ phpMyAdmin should be able to access this database');

        return 0;
    } catch (\Exception $e) {
        $this->error('✗ Database connection failed!');
        $this->error("Error: " . $e->getMessage());

        return 1;
    }
})->purpose('Check database connection health');
