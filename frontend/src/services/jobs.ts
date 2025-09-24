import apiClient from '@/lib/api-client';
import { 
  Job, 
  CreateJobRequest, 
  PaginatedResponse 
} from '@/types/api';

export const jobsApi = {
  // Get all jobs
  getJobs: async (params?: {
    page?: number;
    limit?: number;
    project_id?: string;
    status?: string;
    type?: string;
  }): Promise<PaginatedResponse<Job>> => {
    return apiClient.get('/jobs', { params });
  },

  // Get job by ID
  getJob: async (id: string): Promise<Job> => {
    return apiClient.get(`/jobs/${id}`);
  },

  // Create new job
  createJob: async (data: CreateJobRequest): Promise<Job> => {
    return apiClient.post('/jobs', data);
  },

  // Cancel job
  cancelJob: async (id: string): Promise<Job> => {
    return apiClient.post(`/jobs/${id}/cancel`);
  },

  // Retry job
  retryJob: async (id: string): Promise<Job> => {
    return apiClient.post(`/jobs/${id}/retry`);
  },

  // Get job logs
  getJobLogs: async (id: string): Promise<{
    logs: Array<{
      timestamp: string;
      level: string;
      message: string;
    }>;
  }> => {
    return apiClient.get(`/jobs/${id}/logs`);
  },

  // Get job progress
  getJobProgress: async (id: string): Promise<{
    status: string;
    progress: number;
    current_step?: string;
    eta_seconds?: number;
    message?: string;
  }> => {
    return apiClient.get(`/jobs/${id}/progress`);
  },

  // Delete job
  deleteJob: async (id: string): Promise<void> => {
    return apiClient.delete(`/jobs/${id}`);
  },

  // Get job outputs/results
  getJobOutputs: async (id: string): Promise<{
    outputs: Array<{
      type: string;
      url: string;
      filename: string;
      size: number;
      created_at: string;
    }>;
  }> => {
    return apiClient.get(`/jobs/${id}/outputs`);
  },
};