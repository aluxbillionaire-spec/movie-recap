<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    /**
     * Run the migrations.
     */
    public function up(): void
    {
        Schema::create('tenants', function (Blueprint $table) {
            $table->uuid('id')->primary();
            $table->string('name')->unique();
            $table->string('display_name');
            $table->string('billing_plan')->default('free');
            $table->bigInteger('quota_storage_bytes')->default(10737418240); // 10GB
            $table->integer('quota_processing_hours')->default(10);
            $table->integer('quota_jobs_per_month')->default(50);
            $table->json('settings')->nullable();
            $table->boolean('is_active')->default(true);
            $table->timestamps();

            $table->index(['name']);
            $table->index(['is_active']);
        });

        // Create tenant settings table
        Schema::create('tenant_settings', function (Blueprint $table) {
            $table->uuid('id')->primary();
            $table->foreignUuid('tenant_id')->constrained('tenants')->onDelete('cascade');
            $table->string('key');
            $table->text('value')->nullable();
            $table->timestamps();

            $table->unique(['tenant_id', 'key']);
        });
    }

    /**
     * Reverse the migrations.
     */
    public function down(): void
    {
        Schema::dropIfExists('tenant_settings');
        Schema::dropIfExists('tenants');
    }
};
