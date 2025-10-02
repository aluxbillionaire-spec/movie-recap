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
        Schema::create('transcripts', function (Blueprint $table) {
            $table->uuid('id')->primary();
            $table->foreignUuid('asset_id')->constrained('assets')->onDelete('cascade');
            $table->foreignUuid('tenant_id')->constrained('tenants')->onDelete('cascade');
            $table->text('full_text');
            $table->string('language')->default('en');
            $table->decimal('confidence_score', 5, 4)->nullable();
            $table->json('word_timestamps')->nullable(); // Array of {word, start, end, confidence}
            $table->json('processing_info')->nullable();
            $table->timestamp('created_at')->useCurrent();

            $table->index(['asset_id']);
            $table->index(['tenant_id']);
            // Note: We can't create full-text search indexes in Laravel migrations directly
            // This would need to be handled separately for MySQL
        });
    }

    /**
     * Reverse the migrations.
     */
    public function down(): void
    {
        Schema::dropIfExists('transcripts');
    }
};
