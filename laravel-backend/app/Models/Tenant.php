<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\HasMany;

class Tenant extends Model
{
    use HasFactory;

    protected $fillable = [
        'name',
        'display_name',
        'billing_plan',
        'quota_storage_bytes',
        'quota_processing_hours',
        'quota_jobs_per_month',
        'settings',
        'is_active',
    ];

    protected $casts = [
        'settings' => 'array',
        'quota_storage_bytes' => 'integer',
        'quota_processing_hours' => 'integer',
        'quota_jobs_per_month' => 'integer',
        'is_active' => 'boolean',
        'created_at' => 'datetime',
        'updated_at' => 'datetime',
    ];

    /**
     * Get the users for the tenant.
     */
    public function users(): HasMany
    {
        return $this->hasMany(User::class);
    }

    /**
     * Get the projects for the tenant.
     */
    public function projects(): HasMany
    {
        return $this->hasMany(Project::class);
    }

    /**
     * Get the assets for the tenant.
     */
    public function assets(): HasMany
    {
        return $this->hasMany(Asset::class);
    }

    /**
     * Get the jobs for the tenant.
     */
    public function jobs(): HasMany
    {
        return $this->hasMany(ProcessingJob::class);
    }

    /**
     * Get the scenes for the tenant.
     */
    public function scenes(): HasMany
    {
        return $this->hasMany(Scene::class);
    }

    /**
     * Get the transcripts for the tenant.
     */
    public function transcripts(): HasMany
    {
        return $this->hasMany(Transcript::class);
    }

    /**
     * Get the content moderation records for the tenant.
     */
    public function contentModeration(): HasMany
    {
        return $this->hasMany(ContentModeration::class);
    }

    /**
     * Get the usage tracking records for the tenant.
     */
    public function usageTracking(): HasMany
    {
        return $this->hasMany(UsageTracking::class);
    }

    /**
     * Get the audit logs for the tenant.
     */
    public function auditLogs(): HasMany
    {
        return $this->hasMany(AuditLog::class);
    }
}
