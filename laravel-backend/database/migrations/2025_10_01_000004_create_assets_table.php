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
        Schema::create('assets', function (Blueprint $table) {
            $table->uuid('id')->primary();
            $table->foreignUuid('project_id')->constrained('projects')->onDelete('cascade');
            $table->foreignUuid('tenant_id')->constrained('tenants')->onDelete('cascade');
            $table->string('type'); // video, script, thumbnail, output
            $table->string('filename');
            $table->text('storage_path');
            $table->string('content_type')->nullable();
            $table->bigInteger('size_bytes');
            $table->decimal('duration_seconds', 10, 3)->nullable(); // For video/audio files
            $table->json('metadata')->nullable();
            $table->string('checksum')->nullable();
            $table->string('status')->default('uploaded');
            $table->timestamps();
            
            $table->index(['project_id']);
            $table->index(['tenant_id']);
            $table->index(['type']);
            $table->index(['status']);
            $table->index(['checksum']);
        });
    }

    /**
     * Reverse the migrations.
     */
    public function down(): void
    {
        Schema::dropIfExists('assets');
    }
};