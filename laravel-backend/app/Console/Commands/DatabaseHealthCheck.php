<?php

namespace App\Console\Commands;

use Illuminate\Console\Command;
use Illuminate\Support\Facades\DB;

class DatabaseHealthCheck extends Command
{
    /**
     * The name and signature of the console command.
     *
     * @var string
     */
    protected $signature = 'db:health-check';

    /**
     * The console command description.
     *
     * @var string
     */
    protected $description = 'Check database connection health';

    /**
     * Execute the console command.
     */
    public function handle()
    {
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

            return Command::SUCCESS;
        } catch (\Exception $e) {
            $this->error('✗ Database connection failed!');
            $this->error("Error: " . $e->getMessage());

            return Command::FAILURE;
        }
    }
}
