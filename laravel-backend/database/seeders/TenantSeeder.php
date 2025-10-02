<?php

namespace Database\Seeders;

use Illuminate\Database\Seeder;
use Illuminate\Support\Facades\DB;
use Illuminate\Support\Facades\Schema;
use Illuminate\Database\Console\Seeds\WithoutModelEvents;

class TenantSeeder extends Seeder
{
    /**
     * Run the database seeds.
     */
    public function run(): void
    {
        // Disable foreign key checks temporarily
        Schema::disableForeignKeyConstraints();

        // Create default tenant
        DB::table('tenants')->insert([
            'id' => 'default-tenant-id',
            'name' => 'default',
            'display_name' => 'Default Tenant',
            'billing_plan' => 'free',
            'quota_storage_bytes' => 10737418240, // 10GB
            'quota_processing_hours' => 10,
            'quota_jobs_per_month' => 50,
            'settings' => json_encode([]),
            'is_active' => true,
            'created_at' => now(),
            'updated_at' => now(),
        ]);

        // Re-enable foreign key checks
        Schema::enableForeignKeyConstraints();
    }
}
