<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;

class Scene extends Model
{
    use HasFactory;

    protected $fillable = [
        'job_id',
        'tenant_id',
        'scene_number',
        'script_text',
        'script_embedding',
        'video_start_time',
        'video_end_time',
        'confidence_score',
        'manual_review_required',
        'flagged_reason',
        'user_approved',
        'transformations',
    ];

    protected $casts = [
        'transformations' => 'array',
        'video_start_time' => 'decimal:3',
        'video_end_time' => 'decimal:3',
        'confidence_score' => 'decimal:4',
        'manual_review_required' => 'boolean',
        'user_approved' => 'boolean',
        'created_at' => 'datetime',
        'updated_at' => 'datetime',
    ];

    /**
     * Get the job that owns the scene.
     */
    public function job(): BelongsTo
    {
        return $this->belongsTo(ProcessingJob::class);
    }

    /**
     * Get the tenant that owns the scene.
     */
    public function tenant(): BelongsTo
    {
        return $this->belongsTo(Tenant::class);
    }
}
