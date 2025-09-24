import axios, { AxiosInstance, AxiosRequestConfig, AxiosResponse } from 'axios';
import { API_BASE_URL, ApiResponse, ApiError } from '@/types/api';

class ApiClient {
  private client: AxiosInstance;
  private tenant_id: string | null = null;

  constructor() {
    this.client = axios.create({
      baseURL: API_BASE_URL,
      timeout: 30000,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    this.setupInterceptors();
  }

  private setupInterceptors() {
    // Request interceptor
    this.client.interceptors.request.use(
      (config) => {
        // Add auth token
        const token = this.getAuthToken();
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }

        // Add tenant ID
        if (this.tenant_id) {
          config.headers['X-Tenant-ID'] = this.tenant_id;
        }

        return config;
      },
      (error) => {
        return Promise.reject(error);
      }
    );

    // Response interceptor
    this.client.interceptors.response.use(
      (response: AxiosResponse<ApiResponse>) => {
        return response;
      },
      async (error) => {
        if (error.response?.status === 401) {
          // Try to refresh token
          const refreshed = await this.refreshToken();
          if (refreshed) {
            // Retry original request
            return this.client.request(error.config);
          } else {
            // Redirect to login
            this.clearAuth();
            window.location.href = '/login';
          }
        }
        
        return Promise.reject(this.formatError(error));
      }
    );
  }

  private getAuthToken(): string | null {
    return localStorage.getItem('access_token');
  }

  private getRefreshToken(): string | null {
    return localStorage.getItem('refresh_token');
  }

  private async refreshToken(): Promise<boolean> {
    try {
      const refreshToken = this.getRefreshToken();
      if (!refreshToken) return false;

      const response = await axios.post(`${API_BASE_URL}/auth/refresh`, {
        refresh_token: refreshToken,
      });

      const { access_token, refresh_token: newRefreshToken } = response.data;
      
      localStorage.setItem('access_token', access_token);
      localStorage.setItem('refresh_token', newRefreshToken);
      
      return true;
    } catch (error) {
      return false;
    }
  }

  private clearAuth() {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('user');
    this.tenant_id = null;
  }

  private formatError(error: any): ApiError {
    if (error.response?.data?.error) {
      return error.response.data.error;
    }
    
    if (error.response?.data?.message) {
      return {
        code: 'API_ERROR',
        message: error.response.data.message,
      };
    }

    if (error.message) {
      return {
        code: 'NETWORK_ERROR',
        message: error.message,
      };
    }

    return {
      code: 'UNKNOWN_ERROR',
      message: 'An unexpected error occurred',
    };
  }

  // Public methods
  setTenantId(tenantId: string) {
    this.tenant_id = tenantId;
  }

  setAuthToken(token: string, refreshToken?: string) {
    localStorage.setItem('access_token', token);
    if (refreshToken) {
      localStorage.setItem('refresh_token', refreshToken);
    }
  }

  logout() {
    this.clearAuth();
  }

  // Generic HTTP methods
  async get<T = any>(url: string, config?: AxiosRequestConfig): Promise<T> {
    const response = await this.client.get<ApiResponse<T>>(url, config);
    return (response.data.data || response.data) as T;
  }

  async post<T = any>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T> {
    const response = await this.client.post<ApiResponse<T>>(url, data, config);
    return (response.data.data || response.data) as T;
  }

  async put<T = any>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T> {
    const response = await this.client.put<ApiResponse<T>>(url, data, config);
    return (response.data.data || response.data) as T;
  }

  async delete<T = any>(url: string, config?: AxiosRequestConfig): Promise<T> {
    const response = await this.client.delete<ApiResponse<T>>(url, config);
    return (response.data.data || response.data) as T;
  }

  // File upload with progress
  async upload<T = any>(
    url: string,
    formData: FormData,
    onProgress?: (progress: number) => void
  ): Promise<T> {
    const response = await this.client.post<ApiResponse<T>>(url, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      onUploadProgress: (progressEvent) => {
        if (onProgress && progressEvent.total) {
          const progress = Math.round((progressEvent.loaded * 100) / progressEvent.total);
          onProgress(progress);
        }
      },
    });
    return (response.data.data || response.data) as T;
  }

  // Download file
  async download(url: string, filename?: string): Promise<void> {
    const response = await this.client.get(url, {
      responseType: 'blob',
    });

    const blob = new Blob([response.data]);
    const downloadUrl = window.URL.createObjectURL(blob);
    
    const link = document.createElement('a');
    link.href = downloadUrl;
    link.download = filename || 'download';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    
    window.URL.revokeObjectURL(downloadUrl);
  }
}

// Create singleton instance
const apiClient = new ApiClient();

export default apiClient;