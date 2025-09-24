import apiClient from '@/lib/api-client';
import { 
  Project, 
  CreateProjectRequest, 
  PaginatedResponse 
} from '@/types/api';

export const projectsApi = {
  // Get all projects
  getProjects: async (params?: {
    page?: number;
    limit?: number;
    search?: string;
    status?: string;
  }): Promise<PaginatedResponse<Project>> => {
    return apiClient.get('/projects', { params });
  },

  // Get project by ID
  getProject: async (id: string): Promise<Project> => {
    return apiClient.get(`/projects/${id}`);
  },

  // Create new project
  createProject: async (data: CreateProjectRequest): Promise<Project> => {
    return apiClient.post('/projects', data);
  },

  // Update project
  updateProject: async (id: string, data: Partial<CreateProjectRequest>): Promise<Project> => {
    return apiClient.put(`/projects/${id}`, data);
  },

  // Delete project
  deleteProject: async (id: string): Promise<void> => {
    return apiClient.delete(`/projects/${id}`);
  },

  // Archive project
  archiveProject: async (id: string): Promise<Project> => {
    return apiClient.post(`/projects/${id}/archive`);
  },

  // Restore project
  restoreProject: async (id: string): Promise<Project> => {
    return apiClient.post(`/projects/${id}/restore`);
  },

  // Get project statistics
  getProjectStats: async (id: string): Promise<{
    total_uploads: number;
    total_jobs: number;
    completed_jobs: number;
    total_size_gb: number;
    processing_time_hours: number;
  }> => {
    return apiClient.get(`/projects/${id}/stats`);
  },
};