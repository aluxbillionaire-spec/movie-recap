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
        Schema::create('user_sessions', function (Blueprint $table) {
            $table->uuid('id')->primary();
            $table->foreignId('user_id')->constrained('users')->onDelete('cascade');
            $table->string('refresh_token_hash');
            $table->json('device_info')->nullable();
            $table->ipAddress('ip_address')->nullable();
            $table->timestamp('expires_at');
            $table->boolean('is_active')->default(true);
            $table->timestamps();
            $table->timestamp('last_used_at')->nullable();

            $table->index(['user_id']);
            $table->index(['refresh_token_hash']);
            $table->index(['expires_at']);
            $table->index(['is_active']);
        });
    }

    /**
     * Reverse the migrations.
     */
    public function down(): void
    {
        Schema::dropIfExists('user_sessions');
    }
};
