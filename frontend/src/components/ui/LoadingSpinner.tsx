import React from 'react';
import { clsx } from 'clsx';
import { Loader2 } from 'lucide-react';

interface LoadingSpinnerProps {
  size?: 'sm' | 'md' | 'lg';
  className?: string;
}

const LoadingSpinner: React.FC<LoadingSpinnerProps> = ({ 
  size = 'md', 
  className 
}) => {
  const sizeClasses = {
    sm: 'w-4 h-4',
    md: 'w-6 h-6',
    lg: 'w-8 h-8',
  };

  return (
    <div className={clsx('flex items-center justify-center', className)}>
      <Loader2 className={clsx(
        'animate-spin text-primary-600',
        sizeClasses[size]
      )} />
    </div>
  );
};

export default LoadingSpinner;