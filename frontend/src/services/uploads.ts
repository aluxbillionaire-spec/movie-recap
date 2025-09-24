import apiClient from '@/lib/api-client';
import { 
  Upload, 
  PaginatedResponse,
  UploadOptions 
} from '@/types/api';

export const uploadsApi = {
  // Upload video file
  uploadVideo: async (
    file: File, 
    projectId: string,
    options?: UploadOptions
  ): Promise<Upload> => {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('project_id', projectId);

    return apiClient.upload('/uploads/video', formData, 
      options?.onProgress ? (progress) => {
        options.onProgress?.({ 
          loaded: (progress / 100) * file.size, 
          total: file.size, 
          percentage: progress 
        });
      } : undefined
    );
  },

  // Upload script file
  uploadScript: async (
    file: File, 
    projectId: string,
    options?: UploadOptions
  ): Promise<Upload> => {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('project_id', projectId);

    return apiClient.upload('/uploads/script', formData, 
      options?.onProgress ? (progress) => {
        options.onProgress?.({ 
          loaded: (progress / 100) * file.size, 
          total: file.size, 
          percentage: progress 
        });
      } : undefined
    );
  },

  // Get uploads for a project
  getUploads: async (
    projectId: string,
    params?: {
      page?: number;
      limit?: number;
      file_type?: string;
      status?: string;
    }
  ): Promise<PaginatedResponse<Upload>> => {
    return apiClient.get('/uploads', { 
      params: { project_id: projectId, ...params } 
    });
  },

  // Get upload by ID
  getUpload: async (id: string): Promise<Upload> => {
    return apiClient.get(`/uploads/${id}`);
  },

  // Delete upload
  deleteUpload: async (id: string): Promise<void> => {
    return apiClient.delete(`/uploads/${id}`);
  },

  // Download file
  downloadFile: async (id: string, filename?: string): Promise<void> => {
    return apiClient.download(`/uploads/${id}/download`, filename);
  },

  // Get upload progress
  getUploadProgress: async (id: string): Promise<{
    status: string;
    progress: number;
    message?: string;
  }> => {
    return apiClient.get(`/uploads/${id}/progress`);
  },
};