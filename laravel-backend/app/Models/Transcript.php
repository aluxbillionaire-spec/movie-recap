<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;

class Transcript extends Model
{
    use HasFactory;

    protected $fillable = [
        'asset_id',
        'tenant_id',
        'full_text',
        'language',
        'confidence_score',
        'word_timestamps',
        'processing_info',
    ];

    protected $casts = [
        'word_timestamps' => 'array',
        'processing_info' => 'array',
        'confidence_score' => 'decimal:4',
        'created_at' => 'datetime',
    ];

    /**
     * Get the asset that owns the transcript.
     */
    public function asset(): BelongsTo
    {
        return $this->belongsTo(Asset::class);
    }

    /**
     * Get the tenant that owns the transcript.
     */
    public function tenant(): BelongsTo
    {
        return $this->belongsTo(Tenant::class);
    }
}
