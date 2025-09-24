import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { useTranslation } from 'react-i18next';
import { 
  Play, 
  Users, 
  Clock, 
  HardDrive,
  TrendingUp,
  CheckCircle,
  AlertCircle,
  Activity,
  Upload
} from 'lucide-react';

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import Button from '@/components/ui/Button';
import Badge from '@/components/ui/Badge';
import LoadingSpinner from '@/components/ui/LoadingSpinner';

// Mock API call - replace with actual API
const fetchDashboardStats = async () => {
  // This would be replaced with actual API call
  return {
    total_projects: 12,
    active_jobs: 3,
    completed_jobs: 28,
    total_uploads: 45,
    storage_used_gb: 156.7,
    processing_time_hours: 87.3,
  };
};

const fetchRecentProjects = async () => {
  return [
    {
      id: '1',
      name: 'Action Movie Recap',
      status: 'processing',
      progress: 65,
      created_at: '2024-01-15T10:30:00Z',
    },
    {
      id: '2',
      name: 'Comedy Highlights',
      status: 'completed',
      progress: 100,
      created_at: '2024-01-14T15:20:00Z',
    },
    {
      id: '3',
      name: 'Drama Summary',
      status: 'pending',
      progress: 0,
      created_at: '2024-01-13T09:15:00Z',
    },
  ];
};

const DashboardPage: React.FC = () => {
  const { t } = useTranslation();
  
  const { data: stats, isLoading: statsLoading } = useQuery({
    queryKey: ['dashboard-stats'],
    queryFn: fetchDashboardStats,
  });

  const { data: recentProjects, isLoading: projectsLoading } = useQuery({
    queryKey: ['recent-projects'],
    queryFn: fetchRecentProjects,
  });

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'completed':
        return <Badge variant="success">{t('dashboard.projectStatus.completed')}</Badge>;
      case 'processing':
        return <Badge variant="warning">{t('dashboard.projectStatus.processing')}</Badge>;
      case 'pending':
        return <Badge variant="gray">{t('dashboard.projectStatus.pending')}</Badge>;
      case 'failed':
        return <Badge variant="error">{t('dashboard.projectStatus.failed')}</Badge>;
      default:
        return <Badge variant="gray">{status}</Badge>;
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  return (
    <div className="space-y-6">
      {/* Welcome Section */}
      <div className="bg-gradient-to-r from-primary-600 to-primary-700 rounded-xl p-6 text-white">
        <h1 className="text-3xl font-bold mb-2">{t('app.welcome')}</h1>
        <p className="text-primary-100 mb-4">
          {t('dashboard.welcomeMessage')}
        </p>
        <Button variant="secondary" size="lg">
          <Play className="w-5 h-5 mr-2" />
          {t('dashboard.createProject')}
        </Button>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {statsLoading ? (
          <div className="col-span-full flex justify-center py-8">
            <LoadingSpinner size="lg" />
          </div>
        ) : (
          <>
            <Card>
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-gray-600">{t('dashboard.stats.totalProjects')}</p>
                    <p className="text-3xl font-bold text-gray-900">{stats?.total_projects}</p>
                  </div>
                  <div className="w-12 h-12 bg-primary-100 rounded-lg flex items-center justify-center">
                    <Users className="w-6 h-6 text-primary-600" />
                  </div>
                </div>
                <div className="mt-4 flex items-center text-sm">
                  <TrendingUp className="w-4 h-4 text-success-500 mr-1" />
                  <span className="text-success-600">+12%</span>
                  <span className="text-gray-500 ml-1">from last month</span>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-gray-600">Active Jobs</p>
                    <p className="text-3xl font-bold text-gray-900">{stats?.active_jobs}</p>
                  </div>
                  <div className="w-12 h-12 bg-warning-100 rounded-lg flex items-center justify-center">
                    <Activity className="w-6 h-6 text-warning-600" />
                  </div>
                </div>
                <div className="mt-4 flex items-center text-sm">
                  <AlertCircle className="w-4 h-4 text-warning-500 mr-1" />
                  <span className="text-warning-600">2 pending review</span>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-gray-600">Completed Jobs</p>
                    <p className="text-3xl font-bold text-gray-900">{stats?.completed_jobs}</p>
                  </div>
                  <div className="w-12 h-12 bg-success-100 rounded-lg flex items-center justify-center">
                    <CheckCircle className="w-6 h-6 text-success-600" />
                  </div>
                </div>
                <div className="mt-4 flex items-center text-sm">
                  <Clock className="w-4 h-4 text-gray-400 mr-1" />
                  <span className="text-gray-500">{stats?.processing_time_hours}h total</span>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-gray-600">Storage Used</p>
                    <p className="text-3xl font-bold text-gray-900">
                      {stats?.storage_used_gb}
                      <span className="text-lg text-gray-500">GB</span>
                    </p>
                  </div>
                  <div className="w-12 h-12 bg-gray-100 rounded-lg flex items-center justify-center">
                    <HardDrive className="w-6 h-6 text-gray-600" />
                  </div>
                </div>
                <div className="mt-4">
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div 
                      className="bg-primary-600 h-2 rounded-full" 
                      style={{ width: `${(stats?.storage_used_gb || 0) / 1000 * 100}%` }}
                    ></div>
                  </div>
                  <p className="text-xs text-gray-500 mt-1">of 1TB limit</p>
                </div>
              </CardContent>
            </Card>
          </>
        )}
      </div>

      {/* Recent Projects */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle>Recent Projects</CardTitle>
            <Button variant="outline" size="sm">
              View All
            </Button>
          </div>
        </CardHeader>
        <CardContent>
          {projectsLoading ? (
            <div className="flex justify-center py-8">
              <LoadingSpinner />
            </div>
          ) : (
            <div className="space-y-4">
              {recentProjects?.map((project) => (
                <div key={project.id} className="flex items-center justify-between p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors">
                  <div className="flex items-center space-x-4">
                    <div className="w-10 h-10 bg-primary-100 rounded-lg flex items-center justify-center">
                      <Play className="w-5 h-5 text-primary-600" />
                    </div>
                    <div>
                      <h3 className="font-medium text-gray-900">{project.name}</h3>
                      <p className="text-sm text-gray-500">
                        Created {formatDate(project.created_at)}
                      </p>
                    </div>
                  </div>
                  <div className="flex items-center space-x-4">
                    {project.status === 'processing' && (
                      <div className="flex items-center space-x-2">
                        <div className="w-20 bg-gray-200 rounded-full h-2">
                          <div 
                            className="bg-primary-600 h-2 rounded-full transition-all duration-300" 
                            style={{ width: `${project.progress}%` }}
                          ></div>
                        </div>
                        <span className="text-sm text-gray-500">{project.progress}%</span>
                      </div>
                    )}
                    {getStatusBadge(project.status)}
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Quick Actions */}
      <Card>
        <CardHeader>
          <CardTitle>Quick Actions</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <Button variant="outline" size="lg" className="h-24 flex-col">
              <Play className="w-8 h-8 mb-2" />
              <span>New Project</span>
            </Button>
            <Button variant="outline" size="lg" className="h-24 flex-col">
              <Upload className="w-8 h-8 mb-2" />
              <span>Upload Video</span>
            </Button>
            <Button variant="outline" size="lg" className="h-24 flex-col">
              <Activity className="w-8 h-8 mb-2" />
              <span>View Jobs</span>
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default DashboardPage;