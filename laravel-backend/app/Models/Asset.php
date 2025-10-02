<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;

class Asset extends Model
{
    use HasFactory;

    protected $fillable = [
        'project_id',
        'tenant_id',
        'type',
        'filename',
        'storage_path',
        'content_type',
        'size_bytes',
        'duration_seconds',
        'metadata',
        'checksum',
        'status',
    ];

    protected $casts = [
        'metadata' => 'array',
        'size_bytes' => 'integer',
        'duration_seconds' => 'decimal:3',
        'created_at' => 'datetime',
        'updated_at' => 'datetime',
    ];

    /**
     * Get the project that owns the asset.
     */
    public function project(): BelongsTo
    {
        return $this->belongsTo(Project::class);
    }

    /**
     * Get the tenant that owns the asset.
     */
    public function tenant(): BelongsTo
    {
        return $this->belongsTo(Tenant::class);
    }

    /**
     * Get the transcript for the asset.
     */
    public function transcript(): \Illuminate\Database\Eloquent\Relations\HasOne
    {
        return $this->hasOne(Transcript::class);
    }

    /**
     * Get the content moderation records for the asset.
     */
    public function contentModeration(): \Illuminate\Database\Eloquent\Relations\HasMany
    {
        return $this->hasMany(ContentModeration::class);
    }
}
