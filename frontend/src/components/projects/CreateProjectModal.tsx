import React, { useState } from 'react';
import { useForm } from 'react-hook-form';
import { toast } from 'react-hot-toast';
import { X } from 'lucide-react';

import Button from '@/components/ui/Button';
import Input from '@/components/ui/Input';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';

interface CreateProjectModalProps {
  isOpen: boolean;
  onClose: () => void;
}

interface ProjectFormData {
  name: string;
  description: string;
  target_resolution: '1080p' | '1440p' | '4K';
  quality: 'low' | 'medium' | 'high' | 'ultra';
  frame_rate: number;
  enable_watermark: boolean;
}

const CreateProjectModal: React.FC<CreateProjectModalProps> = ({ isOpen, onClose }) => {
  const [isLoading, setIsLoading] = useState(false);

  const {
    register,
    handleSubmit,
    formState: { errors },
    reset,
  } = useForm<ProjectFormData>({
    defaultValues: {
      target_resolution: '4K',
      quality: 'high',
      frame_rate: 30,
      enable_watermark: true,
    },
  });

  const onSubmit = async (data: ProjectFormData) => {
    try {
      setIsLoading(true);
      
      // Here you would call the actual API
      console.log('Creating project:', data);
      
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      toast.success('Project created successfully!');
      reset();
      onClose();
    } catch (error: any) {
      toast.error(error.message || 'Failed to create project');
    } finally {
      setIsLoading(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
      <Card className="w-full max-w-lg max-h-[90vh] overflow-y-auto">
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle>Create New Project</CardTitle>
            <button
              onClick={onClose}
              className="text-gray-400 hover:text-gray-600 transition-colors"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
        </CardHeader>
        
        <CardContent>
          <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
            <Input
              label="Project Name"
              placeholder="Enter project name"
              error={errors.name?.message}
              {...register('name', {
                required: 'Project name is required',
                minLength: {
                  value: 3,
                  message: 'Project name must be at least 3 characters',
                },
              })}
            />

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Description
              </label>
              <textarea
                className="input min-h-[80px] resize-none"
                placeholder="Enter project description (optional)"
                {...register('description')}
              />
              {errors.description && (
                <p className="mt-1 text-sm text-error-600">
                  {errors.description.message}
                </p>
              )}
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Target Resolution
                </label>
                <select
                  className="input"
                  {...register('target_resolution', {
                    required: 'Target resolution is required',
                  })}
                >
                  <option value="1080p">1080p (Full HD)</option>
                  <option value="1440p">1440p (2K)</option>
                  <option value="4K">4K (Ultra HD)</option>
                </select>
                {errors.target_resolution && (
                  <p className="mt-1 text-sm text-error-600">
                    {errors.target_resolution.message}
                  </p>
                )}
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Quality
                </label>
                <select
                  className="input"
                  {...register('quality', {
                    required: 'Quality is required',
                  })}
                >
                  <option value="low">Low</option>
                  <option value="medium">Medium</option>
                  <option value="high">High</option>
                  <option value="ultra">Ultra</option>
                </select>
                {errors.quality && (
                  <p className="mt-1 text-sm text-error-600">
                    {errors.quality.message}
                  </p>
                )}
              </div>
            </div>

            <Input
              label="Frame Rate (fps)"
              type="number"
              min="1"
              max="120"
              placeholder="30"
              error={errors.frame_rate?.message}
              {...register('frame_rate', {
                required: 'Frame rate is required',
                min: {
                  value: 1,
                  message: 'Frame rate must be at least 1',
                },
                max: {
                  value: 120,
                  message: 'Frame rate cannot exceed 120',
                },
                valueAsNumber: true,
              })}
            />

            <div className="flex items-center">
              <input
                id="enable_watermark"
                type="checkbox"
                className="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
                {...register('enable_watermark')}
              />
              <label htmlFor="enable_watermark" className="ml-2 text-sm text-gray-700">
                Enable watermark protection
              </label>
            </div>

            <div className="flex gap-3 pt-4">
              <Button
                type="button"
                variant="outline"
                onClick={onClose}
                className="flex-1"
                disabled={isLoading}
              >
                Cancel
              </Button>
              <Button
                type="submit"
                variant="primary"
                loading={isLoading}
                className="flex-1"
              >
                Create Project
              </Button>
            </div>
          </form>
        </CardContent>
      </Card>
    </div>
  );
};

export default CreateProjectModal;