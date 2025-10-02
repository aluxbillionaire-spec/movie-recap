<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;

class ContentModeration extends Model
{
    use HasFactory;

    protected $table = 'content_moderation';

    protected $fillable = [
        'asset_id',
        'tenant_id',
        'moderation_type',
        'status',
        'detection_confidence',
        'detected_items',
        'moderator_notes',
        'user_response',
        'resolved_at',
    ];

    protected $casts = [
        'detected_items' => 'array',
        'user_response' => 'array',
        'detection_confidence' => 'decimal:4',
        'resolved_at' => 'datetime',
        'created_at' => 'datetime',
        'updated_at' => 'datetime',
    ];

    /**
     * Get the asset that owns the content moderation record.
     */
    public function asset(): BelongsTo
    {
        return $this->belongsTo(Asset::class);
    }

    /**
     * Get the tenant that owns the content moderation record.
     */
    public function tenant(): BelongsTo
    {
        return $this->belongsTo(Tenant::class);
    }
}
