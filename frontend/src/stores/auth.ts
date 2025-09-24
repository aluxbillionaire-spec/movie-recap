import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { User, AuthResponse } from '@/types/api';
import { authApi } from '@/services/auth';
import apiClient from '@/lib/api-client';

interface AuthState {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
  
  // Actions
  login: (credentials: { email: string; password: string }) => Promise<void>;
  register: (userData: { email: string; password: string; full_name: string }) => Promise<void>;
  logout: () => void;
  refreshToken: () => Promise<boolean>;
  updateProfile: (data: Partial<User>) => Promise<void>;
  clearError: () => void;
  setLoading: (loading: boolean) => void;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      user: null,
      isAuthenticated: false,
      isLoading: false,
      error: null,

      login: async (credentials) => {
        try {
          set({ isLoading: true, error: null });
          
          const response: AuthResponse = await authApi.login(credentials);
          
          // Store tokens
          apiClient.setAuthToken(response.access_token, response.refresh_token);
          
          // Set tenant ID if available
          if (response.user.tenant_id) {
            apiClient.setTenantId(response.user.tenant_id);
          }
          
          set({
            user: response.user,
            isAuthenticated: true,
            isLoading: false,
            error: null,
          });
        } catch (error: any) {
          set({
            isLoading: false,
            error: error.message || 'Login failed',
            isAuthenticated: false,
            user: null,
          });
          throw error;
        }
      },

      register: async (userData) => {
        try {
          set({ isLoading: true, error: null });
          
          const response: AuthResponse = await authApi.register(userData);
          
          // Store tokens
          apiClient.setAuthToken(response.access_token, response.refresh_token);
          
          // Set tenant ID if available
          if (response.user.tenant_id) {
            apiClient.setTenantId(response.user.tenant_id);
          }
          
          set({
            user: response.user,
            isAuthenticated: true,
            isLoading: false,
            error: null,
          });
        } catch (error: any) {
          set({
            isLoading: false,
            error: error.message || 'Registration failed',
            isAuthenticated: false,
            user: null,
          });
          throw error;
        }
      },

      logout: () => {
        authApi.logout().catch(() => {
          // Ignore errors during logout
        });
        
        set({
          user: null,
          isAuthenticated: false,
          error: null,
        });
      },

      refreshToken: async () => {
        try {
          const refreshToken = localStorage.getItem('refresh_token');
          if (!refreshToken) return false;

          const response: AuthResponse = await authApi.refresh(refreshToken);
          
          apiClient.setAuthToken(response.access_token, response.refresh_token);
          
          set({
            user: response.user,
            isAuthenticated: true,
          });
          
          return true;
        } catch (error) {
          get().logout();
          return false;
        }
      },

      updateProfile: async (data) => {
        try {
          set({ isLoading: true, error: null });
          
          const updatedUser = await authApi.updateProfile(data);
          
          set({
            user: updatedUser,
            isLoading: false,
          });
        } catch (error: any) {
          set({
            isLoading: false,
            error: error.message || 'Profile update failed',
          });
          throw error;
        }
      },

      clearError: () => set({ error: null }),
      setLoading: (loading) => set({ isLoading: loading }),
    }),
    {
      name: 'auth-storage',
      partialize: (state) => ({
        user: state.user,
        isAuthenticated: state.isAuthenticated,
      }),
    }
  )
);