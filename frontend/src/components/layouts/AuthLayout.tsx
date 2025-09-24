import React from 'react';

interface AuthLayoutProps {
  children: React.ReactNode;
}

const AuthLayout: React.FC<AuthLayoutProps> = ({ children }) => {
  return (
    <div className="min-h-screen bg-gradient-to-br from-primary-50 to-primary-100">
      {/* Background Pattern */}
      <div className="absolute inset-0 bg-grid-pattern opacity-5"></div>
      
      {/* Content */}
      <div className="relative z-10">
        {children}
      </div>
      
      {/* Footer */}
      <div className="absolute bottom-0 w-full p-4 text-center">
        <p className="text-sm text-gray-600">
          © 2024 Movie Recap Service. All rights reserved.
        </p>
      </div>
    </div>
  );
};

export default AuthLayout;