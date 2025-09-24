import apiClient from '@/lib/api-client';
import { 
  LoginRequest, 
  RegisterRequest, 
  AuthResponse, 
  User 
} from '@/types/api';

export const authApi = {
  // Login user
  login: async (credentials: LoginRequest): Promise<AuthResponse> => {
    return apiClient.post('/auth/login', credentials);
  },

  // Register user
  register: async (userData: RegisterRequest): Promise<AuthResponse> => {
    return apiClient.post('/auth/register', userData);
  },

  // Refresh token
  refresh: async (refreshToken: string): Promise<AuthResponse> => {
    return apiClient.post('/auth/refresh', { refresh_token: refreshToken });
  },

  // Logout
  logout: async (): Promise<void> => {
    try {
      await apiClient.post('/auth/logout');
    } finally {
      apiClient.logout();
    }
  },

  // Get current user profile
  getProfile: async (): Promise<User> => {
    return apiClient.get('/user/profile');
  },

  // Update user profile
  updateProfile: async (data: Partial<User>): Promise<User> => {
    return apiClient.put('/user/profile', data);
  },

  // Change password
  changePassword: async (data: { 
    current_password: string; 
    new_password: string;
  }): Promise<void> => {
    return apiClient.post('/user/change-password', data);
  },

  // Verify email
  verifyEmail: async (token: string): Promise<void> => {
    return apiClient.post('/auth/verify-email', { token });
  },

  // Request password reset
  requestPasswordReset: async (email: string): Promise<void> => {
    return apiClient.post('/auth/password-reset-request', { email });
  },

  // Reset password
  resetPassword: async (data: {
    token: string;
    new_password: string;
  }): Promise<void> => {
    return apiClient.post('/auth/password-reset', data);
  },
};