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
        Schema::create('usage_tracking', function (Blueprint $table) {
            $table->uuid('id')->primary();
            $table->foreignUuid('tenant_id')->constrained('tenants')->onDelete('cascade');
            $table->foreignId('user_id')->nullable()->constrained('users')->onDelete('set null');
            $table->string('resource_type'); // storage, processing_time, api_calls
            $table->decimal('amount', 15, 6);
            $table->string('unit'); // bytes, seconds, calls
            $table->foreignUuid('job_id')->nullable()->constrained('processing_jobs')->onDelete('set null');
            $table->date('period_start');
            $table->date('period_end');
            $table->json('metadata')->nullable();
            $table->timestamps();

            $table->index(['tenant_id', 'period_start', 'period_end']);
            $table->index(['resource_type']);
            $table->index(['job_id']);
        });
    }

    /**
     * Reverse the migrations.
     */
    public function down(): void
    {
        Schema::dropIfExists('usage_tracking');
    }
};
