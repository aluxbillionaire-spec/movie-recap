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
  Activity,
  Upload,
  Zap,
  Globe2,
  Sparkles,
  Plus,
  BarChart3,
  AlertCircle,
  ArrowUpRight,
  Film,
  Star,
  Calendar,
  Eye
} from 'lucide-react';

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
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
    <div className="space-y-8 relative">
      {/* Floating Background Elements */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none">
        <div className="absolute -top-4 -right-4 w-72 h-72 bg-gradient-to-br from-primary-400/20 to-accent-400/20 rounded-full blur-3xl animate-float"></div>
        <div className="absolute -bottom-8 -left-8 w-96 h-96 bg-gradient-to-tr from-secondary-400/20 to-primary-400/20 rounded-full blur-3xl animate-float-delayed"></div>
      </div>

      {/* Hero Section */}
      <div className="relative bg-gradient-to-br from-primary-600 via-primary-700 to-secondary-600 rounded-2xl p-8 text-white overflow-hidden shadow-2xl">
        <div className="absolute inset-0 bg-gradient-to-r from-black/20 to-transparent"></div>
        <div className="absolute top-0 right-0 w-64 h-64 bg-white/10 rounded-full blur-3xl transform translate-x-32 -translate-y-32"></div>
        <div className="relative z-10">
          <div className="flex items-center mb-4">
            <div className="p-3 bg-white/20 rounded-xl backdrop-blur-sm mr-4">
              <Zap className="w-8 h-8 text-white" />
            </div>
            <div>
              <h1 className="text-4xl font-bold mb-2 bg-gradient-to-r from-white to-primary-100 bg-clip-text text-transparent">
                {t('app.welcome')}
              </h1>
              <p className="text-primary-100 text-lg opacity-90">
                {t('dashboard.welcomeMessage')}
              </p>
            </div>
          </div>
          <div className="flex flex-wrap gap-4 mt-6">
            <Button className="btn-primary-glow shadow-xl">
              <Play className="w-5 h-5 mr-2" />
              {t('dashboard.createProject')}
            </Button>
            <Button variant="outline" className="text-white border-white/30 hover:bg-white/10 backdrop-blur-sm">
              <Upload className="w-5 h-5 mr-2" />
              Upload Video
            </Button>
          </div>
        </div>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {statsLoading ? (
          <div className="col-span-full flex justify-center py-12">
            <LoadingSpinner size="lg" />
          </div>
        ) : (
          <>
            <Card className="group hover:shadow-2xl transition-all duration-300 border-0 bg-gradient-to-br from-white to-gray-50/50 backdrop-blur-sm">
              <CardContent className="p-6">
                <div className="flex items-center justify-between mb-4">
                  <div className="p-3 bg-gradient-to-br from-primary-500 to-primary-600 rounded-xl shadow-lg">
                    <Users className="w-6 h-6 text-white" />
                  </div>
                  <ArrowUpRight className="w-5 h-5 text-gray-400 group-hover:text-primary-500 transition-colors" />
                </div>
                <div className="space-y-1">
                  <p className="text-sm font-medium text-gray-600">{t('dashboard.stats.totalProjects')}</p>
                  <p className="text-3xl font-bold bg-gradient-to-r from-gray-900 to-gray-700 bg-clip-text text-transparent">
                    {stats?.total_projects}
                  </p>
                </div>
                <div className="mt-4 flex items-center text-sm">
                  <div className="flex items-center px-2 py-1 bg-success-100 rounded-full">
                    <TrendingUp className="w-3 h-3 text-success-600 mr-1" />
                    <span className="text-success-700 font-medium">+12%</span>
                  </div>
                  <span className="text-gray-500 ml-2">vs last month</span>
                </div>
              </CardContent>
            </Card>

            <Card className="group hover:shadow-2xl transition-all duration-300 border-0 bg-gradient-to-br from-white to-orange-50/30 backdrop-blur-sm">
              <CardContent className="p-6">
                <div className="flex items-center justify-between mb-4">
                  <div className="p-3 bg-gradient-to-br from-warning-500 to-orange-600 rounded-xl shadow-lg">
                    <Activity className="w-6 h-6 text-white" />
                  </div>
                  <div className="w-2 h-2 bg-warning-500 rounded-full animate-pulse"></div>
                </div>
                <div className="space-y-1">
                  <p className="text-sm font-medium text-gray-600">Active Jobs</p>
                  <p className="text-3xl font-bold bg-gradient-to-r from-warning-600 to-orange-600 bg-clip-text text-transparent">
                    {stats?.active_jobs}
                  </p>
                </div>
                <div className="mt-4 flex items-center text-sm">
                  <div className="flex items-center px-2 py-1 bg-warning-100 rounded-full">
                    <AlertCircle className="w-3 h-3 text-warning-600 mr-1" />
                    <span className="text-warning-700 font-medium">2 pending</span>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card className="group hover:shadow-2xl transition-all duration-300 border-0 bg-gradient-to-br from-white to-green-50/30 backdrop-blur-sm">
              <CardContent className="p-6">
                <div className="flex items-center justify-between mb-4">
                  <div className="p-3 bg-gradient-to-br from-success-500 to-green-600 rounded-xl shadow-lg">
                    <CheckCircle className="w-6 h-6 text-white" />
                  </div>
                  <Star className="w-5 h-5 text-yellow-400 fill-current" />
                </div>
                <div className="space-y-1">
                  <p className="text-sm font-medium text-gray-600">Completed Jobs</p>
                  <p className="text-3xl font-bold bg-gradient-to-r from-success-600 to-green-600 bg-clip-text text-transparent">
                    {stats?.completed_jobs}
                  </p>
                </div>
                <div className="mt-4 flex items-center text-sm">
                  <Clock className="w-3 h-3 text-gray-400 mr-1" />
                  <span className="text-gray-600 font-medium">{stats?.processing_time_hours}h</span>
                  <span className="text-gray-500 ml-1">total time</span>
                </div>
              </CardContent>
            </Card>

            <Card className="group hover:shadow-2xl transition-all duration-300 border-0 bg-gradient-to-br from-white to-blue-50/30 backdrop-blur-sm">
              <CardContent className="p-6">
                <div className="flex items-center justify-between mb-4">
                  <div className="p-3 bg-gradient-to-br from-gray-600 to-gray-700 rounded-xl shadow-lg">
                    <HardDrive className="w-6 h-6 text-white" />
                  </div>
                  <div className="text-right">
                    <p className="text-xs text-gray-500">Usage</p>
                    <p className="text-sm font-semibold text-gray-700">{Math.round((stats?.storage_used_gb || 0) / 10)}%</p>
                  </div>
                </div>
                <div className="space-y-1">
                  <p className="text-sm font-medium text-gray-600">Storage Used</p>
                  <p className="text-3xl font-bold bg-gradient-to-r from-gray-700 to-gray-600 bg-clip-text text-transparent">
                    {stats?.storage_used_gb}
                    <span className="text-lg text-gray-500 ml-1">GB</span>
                  </p>
                </div>
                <div className="mt-4 space-y-2">
                  <div className="w-full bg-gray-200 rounded-full h-2 overflow-hidden">
                    <div 
                      className="bg-gradient-to-r from-primary-500 to-primary-600 h-2 rounded-full transition-all duration-1000 ease-out" 
                      style={{ width: `${Math.min((stats?.storage_used_gb || 0) / 10, 100)}%` }}
                    ></div>
                  </div>
                  <p className="text-xs text-gray-500">of 1TB limit</p>
                </div>
              </CardContent>
            </Card>
          </>
        )}
      </div>

      {/* Recent Projects */}
      <Card className="overflow-hidden border-0 shadow-xl bg-gradient-to-br from-white to-gray-50/50 backdrop-blur-sm">
        <CardHeader className="bg-gradient-to-r from-gray-50 to-white border-b border-gray-100">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="p-2 bg-gradient-to-br from-primary-500 to-primary-600 rounded-lg shadow-lg">
                <Film className="w-5 h-5 text-white" />
              </div>
              <CardTitle className="text-xl bg-gradient-to-r from-gray-900 to-gray-700 bg-clip-text text-transparent">
                Recent Projects
              </CardTitle>
            </div>
            <Button variant="outline" size="sm" className="btn-gradient-border">
              <Eye className="w-4 h-4 mr-2" />
              View All
            </Button>
          </div>
        </CardHeader>
        <CardContent className="p-6">
          {projectsLoading ? (
            <div className="flex justify-center py-12">
              <LoadingSpinner />
            </div>
          ) : (
            <div className="space-y-4">
              {recentProjects?.map((project, index) => (
                <div 
                  key={project.id} 
                  className="group flex items-center justify-between p-5 bg-white rounded-xl border border-gray-100 hover:border-primary-200 hover:shadow-lg transition-all duration-300 cursor-pointer"
                >
                  <div className="flex items-center space-x-4">
                    <div className="relative">
                      <div className="w-12 h-12 bg-gradient-to-br from-primary-500 to-primary-600 rounded-xl flex items-center justify-center shadow-lg group-hover:shadow-primary-500/25 transition-all duration-300">
                        <Play className="w-6 h-6 text-white" />
                      </div>
                      {project.status === 'processing' && (
                        <div className="absolute -top-1 -right-1 w-4 h-4 bg-warning-500 rounded-full border-2 border-white animate-pulse"></div>
                      )}
                    </div>
                    <div className="space-y-1">
                      <h3 className="font-semibold text-gray-900 group-hover:text-primary-600 transition-colors">
                        {project.name}
                      </h3>
                      <div className="flex items-center space-x-3 text-sm text-gray-500">
                        <div className="flex items-center space-x-1">
                          <Calendar className="w-3 h-3" />
                          <span>Created {formatDate(project.created_at)}</span>
                        </div>
                      </div>
                    </div>
                  </div>
                  <div className="flex items-center space-x-4">
                    {project.status === 'processing' && (
                      <div className="flex items-center space-x-3">
                        <div className="w-24 bg-gray-200 rounded-full h-2 overflow-hidden">
                          <div 
                            className="bg-gradient-to-r from-primary-500 to-primary-600 h-2 rounded-full transition-all duration-1000 ease-out" 
                            style={{ width: `${project.progress}%` }}
                          ></div>
                        </div>
                        <span className="text-sm font-medium text-gray-600 min-w-[40px]">{project.progress}%</span>
                      </div>
                    )}
                    <div className="flex items-center space-x-2">
                      {getStatusBadge(project.status)}
                      <ArrowUpRight className="w-4 h-4 text-gray-400 group-hover:text-primary-500 transition-colors" />
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Quick Actions */}
      <Card className="border-0 shadow-xl bg-gradient-to-br from-white to-gray-50/50 backdrop-blur-sm">
        <CardHeader className="bg-gradient-to-r from-gray-50 to-white border-b border-gray-100">
          <div className="flex items-center space-x-3">
            <div className="p-2 bg-gradient-to-br from-accent-500 to-accent-600 rounded-lg shadow-lg">
              <Sparkles className="w-5 h-5 text-white" />
            </div>
            <CardTitle className="text-xl bg-gradient-to-r from-gray-900 to-gray-700 bg-clip-text text-transparent">
              Quick Actions
            </CardTitle>
          </div>
        </CardHeader>
        <CardContent className="p-6">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <Button 
              className="h-28 flex-col bg-gradient-to-br from-primary-500 to-primary-600 hover:from-primary-600 hover:to-primary-700 text-white shadow-xl hover:shadow-2xl hover:shadow-primary-500/25 transition-all duration-300 border-0"
            >
              <div className="p-3 bg-white/20 rounded-xl mb-3 backdrop-blur-sm">
                <Play className="w-8 h-8" />
              </div>
              <span className="font-semibold">New Project</span>
              <span className="text-xs opacity-80">Start creating</span>
            </Button>
            <Button 
              variant="outline" 
              className="h-28 flex-col btn-gradient-border hover:bg-gradient-to-br hover:from-blue-50 hover:to-indigo-50 group transition-all duration-300"
            >
              <div className="p-3 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-xl mb-3 shadow-lg group-hover:shadow-blue-500/25 transition-all duration-300">
                <Upload className="w-8 h-8 text-white" />
              </div>
              <span className="font-semibold">Upload Video</span>
              <span className="text-xs text-gray-500">Drag & drop</span>
            </Button>
            <Button 
              variant="outline" 
              className="h-28 flex-col btn-gradient-border hover:bg-gradient-to-br hover:from-green-50 hover:to-emerald-50 group transition-all duration-300"
            >
              <div className="p-3 bg-gradient-to-br from-green-500 to-emerald-600 rounded-xl mb-3 shadow-lg group-hover:shadow-green-500/25 transition-all duration-300">
                <Activity className="w-8 h-8 text-white" />
              </div>
              <span className="font-semibold">View Jobs</span>
              <span className="text-xs text-gray-500">Monitor progress</span>
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default DashboardPage;