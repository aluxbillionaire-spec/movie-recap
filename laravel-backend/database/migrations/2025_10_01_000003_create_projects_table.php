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
        Schema::create('projects', function (Blueprint $table) {
            $table->uuid('id')->primary();
            $table->foreignId('user_id')->constrained('users')->onDelete('cascade');
            $table->foreignUuid('tenant_id')->constrained('tenants')->onDelete('cascade');
            $table->string('title');
            $table->text('description')->nullable();
            $table->json('settings')->nullable();
            $table->string('status')->default('active');
            $table->timestamps();

            $table->index(['user_id']);
            $table->index(['tenant_id']);
            $table->index(['status']);
        });
    }

    /**
     * Reverse the migrations.
     */
    public function down(): void
    {
        Schema::dropIfExists('projects');
    }
};
