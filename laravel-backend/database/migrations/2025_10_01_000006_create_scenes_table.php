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
        Schema::create('scenes', function (Blueprint $table) {
            $table->uuid('id')->primary();
            $table->foreignUuid('job_id')->constrained('processing_jobs')->onDelete('cascade');
            $table->foreignUuid('tenant_id')->constrained('tenants')->onDelete('cascade');
            $table->integer('scene_number');
            $table->text('script_text')->nullable();
            $table->binary('script_embedding')->nullable(); // For sentence-transformers embeddings
            $table->decimal('video_start_time', 10, 3)->nullable();
            $table->decimal('video_end_time', 10, 3)->nullable();
            $table->decimal('confidence_score', 5, 4)->nullable();
            $table->boolean('manual_review_required')->default(false);
            $table->string('flagged_reason')->nullable();
            $table->boolean('user_approved')->nullable();
            $table->json('transformations')->nullable(); // flip, crop, color adjustments
            $table->timestamps();

            $table->index(['job_id']);
            $table->index(['tenant_id']);
            $table->index(['confidence_score']);
            $table->index(['manual_review_required']);
            $table->index(['scene_number']);
        });
    }

    /**
     * Reverse the migrations.
     */
    public function down(): void
    {
        Schema::dropIfExists('scenes');
    }
};
