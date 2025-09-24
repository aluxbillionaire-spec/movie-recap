import { useEffect } from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { useAuthStore } from '@/stores/auth';

// Layout components
import AuthLayout from '@/components/layouts/AuthLayout';
import DashboardLayout from '@/components/layouts/DashboardLayout';

// Page components
import LoginPage from '@/pages/auth/LoginPage';
import RegisterPage from '@/pages/auth/RegisterPage';
import DashboardPage from '@/pages/DashboardPage';
import ProjectsPage from '@/pages/ProjectsPage';
import ProjectDetailPage from '@/pages/ProjectDetailPage';
import UploadsPage from '@/pages/UploadsPage';
import JobsPage from '@/pages/JobsPage';
import SettingsPage from '@/pages/SettingsPage';
import TestPage from '@/pages/TestPage';

// Components
import LoadingSpinner from '@/components/ui/LoadingSpinner';
import ProtectedRoute from '@/components/auth/ProtectedRoute';

function App() {
  const { isAuthenticated, isLoading, refreshToken } = useAuthStore();

  useEffect(() => {
    // Try to refresh token on app load
    const token = localStorage.getItem('access_token');
    if (token && !isAuthenticated) {
      refreshToken();
    }
  }, [isAuthenticated, refreshToken]);

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <Routes>
        {/* Public routes */}
        <Route path="/test" element={<TestPage />} />
        <Route path="/auth/*" element={
          <AuthLayout>
            <Routes>
              <Route path="login" element={<LoginPage />} />
              <Route path="register" element={<RegisterPage />} />
              <Route path="*" element={<Navigate to="/auth/login" replace />} />
            </Routes>
          </AuthLayout>
        } />

        {/* Protected routes */}
        <Route path="/*" element={
          <ProtectedRoute>
            <DashboardLayout>
              <Routes>
                <Route path="/" element={<DashboardPage />} />
                <Route path="/dashboard" element={<DashboardPage />} />
                <Route path="/projects" element={<ProjectsPage />} />
                <Route path="/projects/:id" element={<ProjectDetailPage />} />
                <Route path="/uploads" element={<UploadsPage />} />
                <Route path="/jobs" element={<JobsPage />} />
                <Route path="/settings" element={<SettingsPage />} />
                <Route path="*" element={<Navigate to="/dashboard" replace />} />
              </Routes>
            </DashboardLayout>
          </ProtectedRoute>
        } />
      </Routes>
    </div>
  );
}

export default App;