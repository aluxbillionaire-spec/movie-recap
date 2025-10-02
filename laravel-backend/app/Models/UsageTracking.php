<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;

class UsageTracking extends Model
{
    use HasFactory;

    protected $table = 'usage_tracking';

    protected $fillable = [
        'tenant_id',
        'user_id',
        'resource_type',
        'amount',
        'unit',
        'job_id',
        'period_start',
        'period_end',
        'metadata',
    ];

    protected $casts = [
        'amount' => 'decimal:6',
        'metadata' => 'array',
        'period_start' => 'date',
        'period_end' => 'date',
        'created_at' => 'datetime',
    ];

    /**
     * Get the tenant that owns the usage tracking record.
     */
    public function tenant(): BelongsTo
    {
        return $this->belongsTo(Tenant::class);
    }

    /**
     * Get the user that owns the usage tracking record.
     */
    public function user(): BelongsTo
    {
        return $this->belongsTo(User::class);
    }

    /**
     * Get the job associated with the usage tracking record.
     */
    public function job(): BelongsTo
    {
        return $this->belongsTo(ProcessingJob::class);
    }
}
