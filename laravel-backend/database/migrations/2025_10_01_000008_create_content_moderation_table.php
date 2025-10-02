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
        Schema::create('content_moderation', function (Blueprint $table) {
            $table->uuid('id')->primary();
            $table->foreignUuid('asset_id')->constrained('assets')->onDelete('cascade');
            $table->foreignUuid('tenant_id')->constrained('tenants')->onDelete('cascade');
            $table->string('moderation_type'); // watermark, logo, copyright, content
            $table->string('status')->default('pending'); // pending, approved, rejected, requires_action
            $table->decimal('detection_confidence', 5, 4)->nullable();
            $table->json('detected_items')->nullable(); // Array of detected items with coordinates
            $table->text('moderator_notes')->nullable();
            $table->json('user_response')->nullable(); // User's response to moderation
            $table->timestamp('resolved_at')->nullable();
            $table->timestamps();

            $table->index(['asset_id']);
            $table->index(['tenant_id']);
            $table->index(['status']);
            $table->index(['moderation_type']);
        });
    }

    /**
     * Reverse the migrations.
     */
    public function down(): void
    {
        Schema::dropIfExists('content_moderation');
    }
};
