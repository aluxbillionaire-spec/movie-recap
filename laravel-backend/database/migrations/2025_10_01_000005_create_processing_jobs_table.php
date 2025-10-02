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
        Schema::create('processing_jobs', function (Blueprint $table) {
            $table->uuid('id')->primary();
            $table->foreignUuid('project_id')->constrained('projects')->onDelete('cascade');
            $table->foreignUuid('tenant_id')->constrained('tenants')->onDelete('cascade');
            $table->string('type'); // preprocess, align, assemble, upscale, finalize
            $table->string('status')->default('pending'); // pending, running, manual_review, completed, failed, cancelled
            $table->integer('priority')->default(0);
            $table->json('progress')->nullable(); // {"percent": 0, "stage": "initializing", "details": {}}
            $table->json('config')->nullable();
            $table->json('input_assets')->nullable(); // Array of asset UUIDs
            $table->json('output_assets')->nullable(); // Array of asset UUIDs
            $table->text('error_message')->nullable();
            $table->integer('retry_count')->default(0);
            $table->integer('max_retries')->default(3);
            $table->integer('estimated_duration')->nullable(); // seconds
            $table->timestamp('started_at')->nullable();
            $table->timestamp('completed_at')->nullable();
            $table->timestamps();

            $table->index(['project_id']);
            $table->index(['tenant_id']);
            $table->index(['status']);
            $table->index(['type']);
            $table->index(['created_at']);
            $table->index(['priority', 'created_at']);
        });
    }

    /**
     * Reverse the migrations.
     */
    public function down(): void
    {
        Schema::dropIfExists('processing_jobs');
    }
};
