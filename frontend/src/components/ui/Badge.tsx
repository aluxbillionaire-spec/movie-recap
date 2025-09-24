import React from 'react';
import { clsx } from 'clsx';

export interface BadgeProps {
  children: React.ReactNode;
  variant?: 'primary' | 'secondary' | 'success' | 'warning' | 'error' | 'gray';
  size?: 'sm' | 'md';
  className?: string;
}

const Badge: React.FC<BadgeProps> = ({ 
  children, 
  variant = 'gray', 
  size = 'md',
  className 
}) => {
  const baseClasses = 'badge';
  
  const variants = {
    primary: 'badge-primary',
    secondary: 'badge-gray',
    success: 'badge-success',
    warning: 'badge-warning',
    error: 'badge-danger',
    gray: 'badge-gray',
  };
  
  const sizes = {
    sm: 'text-xs px-2 py-0.5',
    md: '',
  };

  return (
    <span className={clsx(
      baseClasses,
      variants[variant],
      sizes[size],
      className
    )}>
      {children}
    </span>
  );
};

export default Badge;