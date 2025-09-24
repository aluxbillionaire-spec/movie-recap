// API configuration and types
export const API_BASE_URL = (import.meta as any).env?.VITE_API_BASE_URL || '/api/v1';

// API Response types
export interface ApiResponse<T = any> {
  data?: T;
  message?: string;
  error?: {
    code: string;
    message: string;
    details?: any;
  };
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  pages: number;
  limit: number;
}

// Auth types
export interface LoginRequest {
  email: string;
  password: string;
}

export interface RegisterRequest {
  email: string;
  password: string;
  full_name: string;
}

export interface AuthResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
  user: User;
}

export interface User {
  id: string;
  email: string;
  full_name: string;
  role: string;
  is_active: boolean;
  tenant_id: string;
  created_at: string;
  updated_at: string;
}

// Project types
export interface Project {
  id: string;
  name: string;
  description?: string;
  status: 'active' | 'archived' | 'processing';
  settings: ProjectSettings;
  created_at: string;
  updated_at: string;
  tenant_id: string;
  user_id: string;
}

export interface ProjectSettings {
  target_resolution: '1080p' | '1440p' | '4K';
  quality: 'low' | 'medium' | 'high' | 'ultra';
  frame_rate?: number;
  enable_watermark?: boolean;
  intro_duration?: number;
  outro_duration?: number;
}

export interface CreateProjectRequest {
  name: string;
  description?: string;
  settings: ProjectSettings;
}

// Upload types
export interface Upload {
  id: string;
  filename: string;
  file_type: string;
  file_size: number;
  status: 'uploading' | 'uploaded' | 'processing' | 'completed' | 'failed';
  upload_url?: string;
  processed_url?: string;
  metadata?: any;
  created_at: string;
  project_id: string;
}

// Job types
export interface Job {
  id: string;
  type: 'video_processing' | 'script_extraction' | 'alignment' | 'assembly' | 'moderation';
  status: 'pending' | 'running' | 'completed' | 'failed' | 'cancelled';
  progress: number;
  priority: 'low' | 'normal' | 'high';
  settings: any;
  metadata?: any;
  error_message?: string;
  started_at?: string;
  completed_at?: string;
  created_at: string;
  project_id: string;
  tenant_id: string;
}

export interface CreateJobRequest {
  project_id: string;
  type: Job['type'];
  settings: any;
  priority?: Job['priority'];
}

// File upload types
export interface FileUploadProgress {
  loaded: number;
  total: number;
  percentage: number;
}

export interface UploadOptions {
  onProgress?: (progress: FileUploadProgress) => void;
  signal?: AbortSignal;
}

// Error types
export interface ApiError {
  code: string;
  message: string;
  details?: any;
  timestamp?: string;
  path?: string;
}

// Tenant types
export interface Tenant {
  id: string;
  name: string;
  slug: string;
  email: string;
  plan: 'free' | 'basic' | 'professional' | 'enterprise';
  is_active: boolean;
  settings: TenantSettings;
  created_at: string;
}

export interface TenantSettings {
  max_concurrent_jobs: number;
  storage_limit_gb: number;
  api_rate_limit: number;
  features: string[];
}

// Dashboard stats
export interface DashboardStats {
  total_projects: number;
  active_jobs: number;
  completed_jobs: number;
  total_uploads: number;
  storage_used_gb: number;
  processing_time_hours: number;
}

// Notification types
export interface Notification {
  id: string;
  type: 'info' | 'success' | 'warning' | 'error';
  title: string;
  message: string;
  read: boolean;
  created_at: string;
}