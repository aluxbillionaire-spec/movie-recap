import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Link } from 'react-router-dom';
import { 
  Plus, 
  Search, 
  Filter, 
  MoreVertical,
  Play,
  Calendar,
  Clock,
  Settings as SettingsIcon
} from 'lucide-react';

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import Button from '@/components/ui/Button';
import Input from '@/components/ui/Input';
import Badge from '@/components/ui/Badge';
import LoadingSpinner from '@/components/ui/LoadingSpinner';
import CreateProjectModal from '@/components/projects/CreateProjectModal';

// Mock API call - replace with actual API
const fetchProjects = async () => {
  return {
    items: [
      {
        id: '1',
        name: 'Action Movie Recap',
        description: 'High-energy action sequences and key plot points',
        status: 'processing',
        settings: {
          target_resolution: '4K',
          quality: 'high',
          frame_rate: 30,
        },
        created_at: '2024-01-15T10:30:00Z',
        updated_at: '2024-01-15T12:45:00Z',
      },
      {
        id: '2',
        name: 'Comedy Highlights',
        description: 'Best funny moments and comedic timing',
        status: 'completed',
        settings: {
          target_resolution: '1080p',
          quality: 'medium',
          frame_rate: 24,
        },
        created_at: '2024-01-14T15:20:00Z',
        updated_at: '2024-01-14T18:30:00Z',
      },
      {
        id: '3',
        name: 'Drama Summary',
        description: 'Emotional key scenes and character development',
        status: 'active',
        settings: {
          target_resolution: '1440p',
          quality: 'high',
          frame_rate: 24,
        },
        created_at: '2024-01-13T09:15:00Z',
        updated_at: '2024-01-13T11:20:00Z',
      },
    ],
    total: 3,
    page: 1,
    pages: 1,
    limit: 10,
  };
};

const ProjectsPage: React.FC = () => {
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');
  const [showCreateModal, setShowCreateModal] = useState(false);

  const { data: projectsData, isLoading } = useQuery({
    queryKey: ['projects', { search: searchTerm, status: statusFilter }],
    queryFn: () => fetchProjects(),
  });

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'completed':
        return <Badge variant="success">Completed</Badge>;
      case 'processing':
        return <Badge variant="warning">Processing</Badge>;
      case 'active':
        return <Badge variant="primary">Active</Badge>;
      case 'archived':
        return <Badge variant="gray">Archived</Badge>;
      default:
        return <Badge variant="gray">{status}</Badge>;
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Projects</h1>
          <p className="text-gray-600 mt-1">
            Manage your movie recap projects and track their progress
          </p>
        </div>
        <Button 
          variant="primary" 
          size="lg"
          onClick={() => setShowCreateModal(true)}
        >
          <Plus className="w-5 h-5 mr-2" />
          New Project
        </Button>
      </div>

      {/* Filters */}
      <Card>
        <CardContent className="p-6">
          <div className="flex flex-col lg:flex-row gap-4">
            <div className="flex-1">
              <Input
                placeholder="Search projects..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                leftIcon={<Search className="w-4 h-4" />}
              />
            </div>
            <div className="flex gap-2">
              <select
                value={statusFilter}
                onChange={(e) => setStatusFilter(e.target.value)}
                className="input min-w-[140px]"
              >
                <option value="all">All Status</option>
                <option value="active">Active</option>
                <option value="processing">Processing</option>
                <option value="completed">Completed</option>
                <option value="archived">Archived</option>
              </select>
              <Button variant="outline" size="md">
                <Filter className="w-4 h-4 mr-2" />
                More Filters
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Projects Grid */}
      {isLoading ? (
        <div className="flex justify-center py-12">
          <LoadingSpinner size="lg" />
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {projectsData?.items.map((project) => (
            <Card key={project.id} hover className="group">
              <CardHeader>
                <div className="flex items-start justify-between">
                  <div className="flex items-center space-x-3">
                    <div className="w-10 h-10 bg-primary-100 rounded-lg flex items-center justify-center">
                      <Play className="w-5 h-5 text-primary-600" />
                    </div>
                    <div>
                      <CardTitle className="text-lg">{project.name}</CardTitle>
                      {getStatusBadge(project.status)}
                    </div>
                  </div>
                  <div className="relative">
                    <button className="p-1 text-gray-400 hover:text-gray-600 opacity-0 group-hover:opacity-100 transition-opacity">
                      <MoreVertical className="w-4 h-4" />
                    </button>
                  </div>
                </div>
              </CardHeader>
              
              <CardContent className="space-y-4">
                <p className="text-gray-600 text-sm line-clamp-2">
                  {project.description}
                </p>
                
                <div className="space-y-2 text-sm">
                  <div className="flex items-center justify-between">
                    <span className="text-gray-500">Resolution:</span>
                    <span className="font-medium">{project.settings.target_resolution}</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-gray-500">Quality:</span>
                    <span className="font-medium capitalize">{project.settings.quality}</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-gray-500">Frame Rate:</span>
                    <span className="font-medium">{project.settings.frame_rate} fps</span>
                  </div>
                </div>
                
                <div className="pt-4 border-t border-gray-200">
                  <div className="flex items-center justify-between text-xs text-gray-500 mb-3">
                    <div className="flex items-center">
                      <Calendar className="w-3 h-3 mr-1" />
                      Created {formatDate(project.created_at)}
                    </div>
                    <div className="flex items-center">
                      <Clock className="w-3 h-3 mr-1" />
                      Updated {formatDate(project.updated_at)}
                    </div>
                  </div>
                  
                  <div className="flex gap-2">
                    <Button variant="primary" size="sm" className="flex-1">
                      <Link to={`/projects/${project.id}`}>
                        View Details
                      </Link>
                    </Button>
                    <Button variant="outline" size="sm">
                      <SettingsIcon className="w-4 h-4" />
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      {/* Empty State */}
      {!isLoading && projectsData?.items.length === 0 && (
        <Card>
          <CardContent className="text-center py-12">
            <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <Play className="w-8 h-8 text-gray-400" />
            </div>
            <h3 className="text-lg font-medium text-gray-900 mb-2">
              No projects found
            </h3>
            <p className="text-gray-600 mb-6">
              {searchTerm || statusFilter !== 'all' 
                ? 'Try adjusting your search or filter criteria.'
                : 'Get started by creating your first project.'
              }
            </p>
            <Button 
              variant="primary"
              onClick={() => setShowCreateModal(true)}
            >
              <Plus className="w-4 h-4 mr-2" />
              Create First Project
            </Button>
          </CardContent>
        </Card>
      )}

      {/* Pagination */}
      {projectsData && projectsData.pages > 1 && (
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <p className="text-sm text-gray-600">
                Showing {((projectsData.page - 1) * projectsData.limit) + 1} to{' '}
                {Math.min(projectsData.page * projectsData.limit, projectsData.total)} of{' '}
                {projectsData.total} projects
              </p>
              <div className="flex gap-2">
                <Button variant="outline" size="sm" disabled={projectsData.page === 1}>
                  Previous
                </Button>
                <Button variant="outline" size="sm" disabled={projectsData.page === projectsData.pages}>
                  Next
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Create Project Modal */}
      {showCreateModal && (
        <CreateProjectModal
          isOpen={showCreateModal}
          onClose={() => setShowCreateModal(false)}
        />
      )}
    </div>
  );
};

export default ProjectsPage;