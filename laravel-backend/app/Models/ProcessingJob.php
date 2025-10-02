<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;
use Illuminate\Database\Eloquent\Relations\HasMany;

class ProcessingJob extends Model
{
    use HasFactory;

    protected $table = 'processing_jobs';

    protected $fillable = [
        'project_id',
        'tenant_id',
        'type',
        'status',
        'priority',
        'progress',
        'config',
        'input_assets',
        'output_assets',
        'error_message',
        'retry_count',
        'max_retries',
        'estimated_duration',
        'started_at',
        'completed_at',
    ];

    protected $casts = [
        'progress' => 'array',
        'config' => 'array',
        'input_assets' => 'array',
        'output_assets' => 'array',
        'priority' => 'integer',
        'retry_count' => 'integer',
        'max_retries' => 'integer',
        'estimated_duration' => 'integer',
        'started_at' => 'datetime',
        'completed_at' => 'datetime',
        'created_at' => 'datetime',
        'updated_at' => 'datetime',
    ];

    /**
     * Get the project that owns the job.
     */
    public function project(): BelongsTo
    {
        return $this->belongsTo(Project::class);
    }

    /**
     * Get the tenant that owns the job.
     */
    public function tenant(): BelongsTo
    {
        return $this->belongsTo(Tenant::class);
    }

    /**
     * Get the scenes for the job.
     */
    public function scenes(): HasMany
    {
        return $this->hasMany(Scene::class);
    }
}
