-- Movie Recap Pipeline Database Schema
-- PostgreSQL 14+ with JSONB support
-- Multi-tenant architecture with proper isolation

-- Extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";
CREATE EXTENSION IF NOT EXISTS "btree_gin";

-- Tenants table - Multi-tenancy support
CREATE TABLE tenants (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL UNIQUE,
    display_name VARCHAR(255) NOT NULL,
    billing_plan VARCHAR(50) DEFAULT 'free',
    quota_storage_bytes BIGINT DEFAULT 10737418240, -- 10GB
    quota_processing_hours INTEGER DEFAULT 10,
    quota_jobs_per_month INTEGER DEFAULT 50,
    settings JSONB DEFAULT '{}',
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create index for tenant lookups
CREATE INDEX idx_tenants_name ON tenants(name);
CREATE INDEX idx_tenants_active ON tenants(is_active);

-- Users table
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    email VARCHAR(255) NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    roles TEXT[] DEFAULT ARRAY['user'],
    is_active BOOLEAN DEFAULT true,
    email_verified BOOLEAN DEFAULT false,
    preferences JSONB DEFAULT '{}',
    last_login TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Ensure email uniqueness within tenant
    CONSTRAINT unique_email_per_tenant UNIQUE(tenant_id, email)
);

-- Indexes for users
CREATE INDEX idx_users_tenant_id ON users(tenant_id);
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_active ON users(is_active);

-- Projects table
CREATE TABLE projects (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    settings JSONB DEFAULT '{}',
    status VARCHAR(50) DEFAULT 'active',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for projects
CREATE INDEX idx_projects_user_id ON projects(user_id);
CREATE INDEX idx_projects_tenant_id ON projects(tenant_id);
CREATE INDEX idx_projects_status ON projects(status);

-- Assets table - Store file metadata
CREATE TABLE assets (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    type VARCHAR(50) NOT NULL, -- video, script, thumbnail, output
    filename VARCHAR(255) NOT NULL,
    storage_path TEXT NOT NULL,
    content_type VARCHAR(100),
    size_bytes BIGINT NOT NULL,
    duration_seconds DECIMAL(10,3), -- For video/audio files
    metadata JSONB DEFAULT '{}',
    checksum VARCHAR(64),
    status VARCHAR(50) DEFAULT 'uploaded',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for assets
CREATE INDEX idx_assets_project_id ON assets(project_id);
CREATE INDEX idx_assets_tenant_id ON assets(tenant_id);
CREATE INDEX idx_assets_type ON assets(type);
CREATE INDEX idx_assets_status ON assets(status);
CREATE INDEX idx_assets_checksum ON assets(checksum);

-- Jobs table - Processing jobs
CREATE TABLE jobs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    type VARCHAR(50) NOT NULL, -- preprocess, align, assemble, upscale, finalize
    status VARCHAR(50) DEFAULT 'pending', -- pending, running, manual_review, completed, failed, cancelled
    priority INTEGER DEFAULT 0,
    progress JSONB DEFAULT '{"percent": 0, "stage": "initializing", "details": {}}',
    config JSONB DEFAULT '{}',
    input_assets UUID[] DEFAULT ARRAY[]::UUID[],
    output_assets UUID[] DEFAULT ARRAY[]::UUID[],
    error_message TEXT,
    retry_count INTEGER DEFAULT 0,
    max_retries INTEGER DEFAULT 3,
    estimated_duration INTEGER, -- seconds
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for jobs
CREATE INDEX idx_jobs_project_id ON jobs(project_id);
CREATE INDEX idx_jobs_tenant_id ON jobs(tenant_id);
CREATE INDEX idx_jobs_status ON jobs(status);
CREATE INDEX idx_jobs_type ON jobs(type);
CREATE INDEX idx_jobs_created_at ON jobs(created_at);
CREATE INDEX idx_jobs_priority_created ON jobs(priority DESC, created_at ASC);

-- Scenes table - Script and video scene matching
CREATE TABLE scenes (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    job_id UUID NOT NULL REFERENCES jobs(id) ON DELETE CASCADE,
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    scene_number INTEGER NOT NULL,
    script_text TEXT,
    script_embedding VECTOR(384), -- For sentence-transformers embeddings
    video_start_time DECIMAL(10,3),
    video_end_time DECIMAL(10,3),
    confidence_score DECIMAL(5,4),
    manual_review_required BOOLEAN DEFAULT false,
    flagged_reason VARCHAR(255),
    user_approved BOOLEAN,
    transformations JSONB DEFAULT '{}', -- flip, crop, color adjustments
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for scenes
CREATE INDEX idx_scenes_job_id ON scenes(job_id);
CREATE INDEX idx_scenes_tenant_id ON scenes(tenant_id);
CREATE INDEX idx_scenes_confidence ON scenes(confidence_score);
CREATE INDEX idx_scenes_manual_review ON scenes(manual_review_required);
CREATE INDEX idx_scenes_scene_number ON scenes(scene_number);

-- Transcripts table - Store transcription results
CREATE TABLE transcripts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    asset_id UUID NOT NULL REFERENCES assets(id) ON DELETE CASCADE,
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    full_text TEXT NOT NULL,
    language VARCHAR(10) DEFAULT 'en',
    confidence_score DECIMAL(5,4),
    word_timestamps JSONB, -- Array of {word, start, end, confidence}
    processing_info JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for transcripts
CREATE INDEX idx_transcripts_asset_id ON transcripts(asset_id);
CREATE INDEX idx_transcripts_tenant_id ON transcripts(tenant_id);
CREATE INDEX idx_transcripts_full_text_gin ON transcripts USING gin(to_tsvector('english', full_text));

-- Content moderation table
CREATE TABLE content_moderation (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    asset_id UUID NOT NULL REFERENCES assets(id) ON DELETE CASCADE,
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    moderation_type VARCHAR(50) NOT NULL, -- watermark, logo, copyright, content
    status VARCHAR(50) DEFAULT 'pending', -- pending, approved, rejected, requires_action
    detection_confidence DECIMAL(5,4),
    detected_items JSONB DEFAULT '[]', -- Array of detected items with coordinates
    moderator_notes TEXT,
    user_response JSONB, -- User's response to moderation
    resolved_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for content moderation
CREATE INDEX idx_moderation_asset_id ON content_moderation(asset_id);
CREATE INDEX idx_moderation_tenant_id ON content_moderation(tenant_id);
CREATE INDEX idx_moderation_status ON content_moderation(status);
CREATE INDEX idx_moderation_type ON content_moderation(moderation_type);

-- Usage tracking table
CREATE TABLE usage_tracking (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    resource_type VARCHAR(50) NOT NULL, -- storage, processing_time, api_calls
    amount DECIMAL(15,6) NOT NULL,
    unit VARCHAR(20) NOT NULL, -- bytes, seconds, calls
    job_id UUID REFERENCES jobs(id) ON DELETE SET NULL,
    period_start DATE NOT NULL,
    period_end DATE NOT NULL,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for usage tracking
CREATE INDEX idx_usage_tenant_period ON usage_tracking(tenant_id, period_start, period_end);
CREATE INDEX idx_usage_resource_type ON usage_tracking(resource_type);
CREATE INDEX idx_usage_job_id ON usage_tracking(job_id);

-- Audit logs table
CREATE TABLE audit_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID REFERENCES tenants(id) ON DELETE SET NULL,
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    action VARCHAR(100) NOT NULL,
    resource_type VARCHAR(50),
    resource_id UUID,
    old_values JSONB,
    new_values JSONB,
    ip_address INET,
    user_agent TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for audit logs
CREATE INDEX idx_audit_tenant_id ON audit_logs(tenant_id);
CREATE INDEX idx_audit_user_id ON audit_logs(user_id);
CREATE INDEX idx_audit_action ON audit_logs(action);
CREATE INDEX idx_audit_created_at ON audit_logs(created_at);
CREATE INDEX idx_audit_resource ON audit_logs(resource_type, resource_id);

-- Session storage table (for refresh tokens)
CREATE TABLE user_sessions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    refresh_token_hash VARCHAR(255) NOT NULL,
    device_info JSONB DEFAULT '{}',
    ip_address INET,
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_used_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for sessions
CREATE INDEX idx_sessions_user_id ON user_sessions(user_id);
CREATE INDEX idx_sessions_token_hash ON user_sessions(refresh_token_hash);
CREATE INDEX idx_sessions_expires_at ON user_sessions(expires_at);
CREATE INDEX idx_sessions_active ON user_sessions(is_active);

-- Row Level Security (RLS) for multi-tenancy
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE projects ENABLE ROW LEVEL SECURITY;
ALTER TABLE assets ENABLE ROW LEVEL SECURITY;
ALTER TABLE jobs ENABLE ROW LEVEL SECURITY;
ALTER TABLE scenes ENABLE ROW LEVEL SECURITY;
ALTER TABLE transcripts ENABLE ROW LEVEL SECURITY;
ALTER TABLE content_moderation ENABLE ROW LEVEL SECURITY;
ALTER TABLE usage_tracking ENABLE ROW LEVEL SECURITY;

-- RLS Policies (will be created based on application user context)
-- These are examples - actual policies depend on application architecture

-- Triggers for updated_at timestamps
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply updated_at triggers
CREATE TRIGGER update_tenants_updated_at BEFORE UPDATE ON tenants 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_projects_updated_at BEFORE UPDATE ON projects 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_assets_updated_at BEFORE UPDATE ON assets 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_jobs_updated_at BEFORE UPDATE ON jobs 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_scenes_updated_at BEFORE UPDATE ON scenes 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_moderation_updated_at BEFORE UPDATE ON content_moderation 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Views for common queries
CREATE VIEW user_quota_usage AS
SELECT 
    t.id as tenant_id,
    u.id as user_id,
    t.quota_storage_bytes,
    t.quota_processing_hours,
    t.quota_jobs_per_month,
    COALESCE(SUM(CASE WHEN ut.resource_type = 'storage' THEN ut.amount ELSE 0 END), 0) as storage_used,
    COALESCE(SUM(CASE WHEN ut.resource_type = 'processing_time' THEN ut.amount ELSE 0 END), 0) as processing_hours_used,
    COALESCE(COUNT(CASE WHEN ut.resource_type = 'job' AND ut.period_start >= date_trunc('month', CURRENT_DATE) THEN 1 END), 0) as jobs_this_month
FROM tenants t
JOIN users u ON u.tenant_id = t.id
LEFT JOIN usage_tracking ut ON ut.tenant_id = t.id AND ut.user_id = u.id
GROUP BY t.id, u.id, t.quota_storage_bytes, t.quota_processing_hours, t.quota_jobs_per_month;

-- Job progress summary view
CREATE VIEW job_progress_summary AS
SELECT 
    j.id,
    j.project_id,
    j.tenant_id,
    j.type,
    j.status,
    j.progress->>'percent' as progress_percent,
    j.progress->>'stage' as current_stage,
    EXTRACT(EPOCH FROM (NOW() - j.started_at)) as runtime_seconds,
    j.estimated_duration,
    j.created_at,
    j.updated_at
FROM jobs j;

-- Active jobs view
CREATE VIEW active_jobs AS
SELECT * FROM jobs 
WHERE status IN ('pending', 'running', 'manual_review');

-- Insert default tenant for development
INSERT INTO tenants (name, display_name, billing_plan) 
VALUES ('default', 'Default Tenant', 'free')
ON CONFLICT (name) DO NOTHING;