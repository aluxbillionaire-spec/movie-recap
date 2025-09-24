import React, { useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { 
  Home, 
  FolderOpen, 
  Upload, 
  Activity, 
  Settings, 
  Menu, 
  X,
  LogOut,
  User,
  Bell,
  Search,
  Plus,
  ChevronDown,
  Zap,
  BarChart3,
  Globe2
} from 'lucide-react';

import { useAuthStore } from '@/stores/auth';
import Button from '@/components/ui/Button';
import LanguageSelector from '@/components/ui/LanguageSelector';

interface DashboardLayoutProps {
  children: React.ReactNode;
}

const DashboardLayout: React.FC<DashboardLayoutProps> = ({ children }) => {
  const { user, logout } = useAuthStore();
  const location = useLocation();
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [userMenuOpen, setUserMenuOpen] = useState(false);

  const navigation = [
    { name: 'Dashboard', href: '/dashboard', icon: Home, description: 'Overview & analytics' },
    { name: 'Projects', href: '/projects', icon: FolderOpen, description: 'Manage your recaps' },
    { name: 'Uploads', href: '/uploads', icon: Upload, description: 'Media & scripts' },
    { name: 'Jobs', href: '/jobs', icon: Activity, description: 'Processing status' },
    { name: 'Analytics', href: '/analytics', icon: BarChart3, description: 'Performance insights' },
    { name: 'Settings', href: '/settings', icon: Settings, description: 'Account & preferences' },
  ];

  const isActivePath = (path: string) => {
    return location.pathname === path || 
           (path !== '/dashboard' && location.pathname.startsWith(path));
  };

  const handleLogout = () => {
    logout();
  };

  const getPageTitle = () => {
    const path = location.pathname.split('/')[1] || 'dashboard';
    const navItem = navigation.find(item => item.href.includes(path));
    return navItem?.name || 'Dashboard';
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-white to-slate-100">
      {/* Mobile sidebar backdrop */}
      {sidebarOpen && (
        <div 
          className="fixed inset-0 bg-slate-900/50 backdrop-blur-sm z-40 lg:hidden transition-opacity"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      {/* Sidebar */}
      <div className={`
        fixed inset-y-0 left-0 z-50 w-72 bg-white/95 backdrop-blur-xl border-r border-slate-200/60 shadow-2xl transform transition-all duration-300 ease-out lg:translate-x-0 lg:static lg:inset-0
        ${sidebarOpen ? 'translate-x-0' : '-translate-x-full'}
      `}>
        <div className="flex flex-col h-full">
          {/* Logo */}
          <div className="flex items-center justify-between h-20 px-6 border-b border-slate-200/60 bg-gradient-to-r from-indigo-600 to-purple-600">
            <div className="flex items-center">
              <div className="w-10 h-10 bg-white/20 backdrop-blur-sm rounded-xl flex items-center justify-center border border-white/30">
                <Zap className="w-5 h-5 text-white" />
              </div>
              <div className="ml-3">
                <span className="text-xl font-bold text-white">
                  Movie Recap
                </span>
                <div className="flex items-center mt-0.5">
                  <Globe2 className="w-3 h-3 text-white/80 mr-1" />
                  <span className="text-xs text-white/80 font-medium">Global Platform</span>
                </div>
              </div>
            </div>
            <button
              className="lg:hidden text-white/80 hover:text-white transition-colors"
              onClick={() => setSidebarOpen(false)}
            >
              <X className="w-6 h-6" />
            </button>
          </div>

          {/* Quick Actions */}
          <div className="p-6 border-b border-slate-200/60">
            <Button 
              variant="primary" 
              size="sm" 
              className="w-full justify-center mb-3 bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-700 hover:to-purple-700"
            >
              <Plus className="w-4 h-4 mr-2" />
              New Project
            </Button>
            
            {/* Search */}
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-slate-400 w-4 h-4" />
              <input 
                type="text" 
                placeholder="Search projects..." 
                className="w-full pl-10 pr-3 py-2 text-sm bg-slate-50 border border-slate-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-all"
              />
            </div>
          </div>

          {/* Navigation */}
          <nav className="flex-1 px-4 py-6 space-y-2">
            {navigation.map((item) => {
              const Icon = item.icon;
              const isActive = isActivePath(item.href);
              
              return (
                <Link
                  key={item.name}
                  to={item.href}
                  className={`
                    group flex items-center px-4 py-3 text-sm font-medium rounded-xl transition-all duration-200 hover:scale-[1.02]
                    ${isActive
                      ? 'bg-gradient-to-r from-indigo-50 to-purple-50 text-indigo-700 shadow-sm border border-indigo-200/50'
                      : 'text-slate-600 hover:text-slate-900 hover:bg-slate-50'
                    }
                  `}
                  onClick={() => setSidebarOpen(false)}
                >
                  <div className={`
                    w-10 h-10 rounded-lg flex items-center justify-center mr-3 transition-colors
                    ${isActive ? 'bg-gradient-to-br from-indigo-500 to-purple-600 text-white shadow-md' : 'bg-slate-100 text-slate-500 group-hover:bg-slate-200'}
                  `}>
                    <Icon className="w-5 h-5" />
                  </div>
                  <div className="flex-1">
                    <div className="font-semibold">{item.name}</div>
                    <div className="text-xs text-slate-500 mt-0.5">{item.description}</div>
                  </div>
                  {isActive && (
                    <div className="w-2 h-2 bg-gradient-to-r from-indigo-500 to-purple-600 rounded-full" />
                  )}
                </Link>
              );
            })}
          </nav>

          {/* User info */}
          <div className="p-4 border-t border-slate-200/60 bg-slate-50/50">
            <div className="relative">
              <button
                className="w-full flex items-center p-3 rounded-xl hover:bg-white transition-colors"
                onClick={() => setUserMenuOpen(!userMenuOpen)}
              >
                <div className="w-10 h-10 bg-gradient-to-br from-indigo-500 to-purple-600 rounded-xl flex items-center justify-center">
                  <User className="w-5 h-5 text-white" />
                </div>
                <div className="ml-3 flex-1 text-left">
                  <p className="text-sm font-semibold text-slate-900">
                    {user?.full_name || 'User Name'}
                  </p>
                  <p className="text-xs text-slate-500">
                    {user?.email || 'user@example.com'}
                  </p>
                </div>
                <ChevronDown className={`w-4 h-4 text-slate-400 transition-transform ${userMenuOpen ? 'rotate-180' : ''}`} />
              </button>
              
              {userMenuOpen && (
                <div className="absolute bottom-full left-0 right-0 mb-2 p-2 bg-white rounded-xl border border-slate-200 shadow-xl animate-slide-up">
                  <Link
                    to="/settings"
                    className="flex items-center w-full px-3 py-2 text-sm text-slate-600 hover:text-slate-900 hover:bg-slate-50 rounded-lg transition-colors"
                    onClick={() => setUserMenuOpen(false)}
                  >
                    <Settings className="w-4 h-4 mr-2" />
                    Settings
                  </Link>
                  <button
                    onClick={handleLogout}
                    className="flex items-center w-full px-3 py-2 text-sm text-red-600 hover:text-red-700 hover:bg-red-50 rounded-lg transition-colors"
                  >
                    <LogOut className="w-4 h-4 mr-2" />
                    Sign out
                  </button>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Main content */}
      <div className="lg:ml-72">
        {/* Top bar */}
        <header className="sticky top-0 z-30 bg-white/95 backdrop-blur-md border-b border-slate-200/60 shadow-sm">
          <div className="flex items-center justify-between h-16 px-6">
            {/* Mobile menu button */}
            <button
              className="lg:hidden text-slate-500 hover:text-slate-700 p-2 rounded-lg hover:bg-slate-100 transition-colors"
              onClick={() => setSidebarOpen(true)}
            >
              <Menu className="w-6 h-6" />
            </button>

            {/* Page title */}
            <div className="flex-1 lg:flex lg:items-center lg:justify-between">
              <div className="flex items-center">
                <h1 className="text-2xl font-bold text-gradient">
                  {getPageTitle()}
                </h1>
                <div className="ml-3 px-3 py-1 bg-gradient-to-r from-indigo-100 to-purple-100 text-indigo-800 text-xs font-semibold rounded-full border border-indigo-200">
                  Pro
                </div>
              </div>

              {/* Right side */}
              <div className="hidden lg:flex items-center space-x-4">
                {/* Language Selector */}
                <LanguageSelector variant="compact" />
                
                {/* Notifications */}
                <button className="relative p-2 text-slate-400 hover:text-slate-600 hover:bg-slate-100 rounded-xl transition-colors">
                  <Bell className="w-5 h-5" />
                  <span className="absolute top-1 right-1 w-2 h-2 bg-gradient-to-r from-red-500 to-red-600 rounded-full animate-pulse"></span>
                </button>

                {/* Quick stats */}
                <div className="flex items-center space-x-4 px-4 py-2 bg-gradient-to-r from-slate-50 to-slate-100 rounded-xl border border-slate-200">
                  <div className="text-center">
                    <div className="text-lg font-bold text-slate-900">12</div>
                    <div className="text-xs text-slate-500">Projects</div>
                  </div>
                  <div className="w-px h-8 bg-slate-300"></div>
                  <div className="text-center">
                    <div className="text-lg font-bold text-emerald-600">5</div>
                    <div className="text-xs text-slate-500">Complete</div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </header>

        {/* Page content */}
        <main className="p-6">
          <div className="max-w-8xl mx-auto">
            {children}
          </div>
        </main>
      </div>
    </div>
  );
};

export default DashboardLayout;