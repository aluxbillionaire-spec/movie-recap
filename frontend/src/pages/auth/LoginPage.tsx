import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useForm } from 'react-hook-form';
import { toast } from 'react-hot-toast';
import { useTranslation } from 'react-i18next';
import { Mail, Lock, Eye, EyeOff, Zap, Globe2, Play, Shield, Sparkles } from 'lucide-react';

import { useAuthStore } from '@/stores/auth';
import Button from '@/components/ui/Button';
import Input from '@/components/ui/Input';
import { Card, CardContent } from '@/components/ui/Card';
import LanguageSelector from '@/components/ui/LanguageSelector';

interface LoginFormData {
  email: string;
  password: string;
}

const LoginPage: React.FC = () => {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const { login, isLoading } = useAuthStore();
  const [showPassword, setShowPassword] = useState(false);

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<LoginFormData>();

  const onSubmit = async (data: LoginFormData) => {
    try {
      await login(data);
      toast.success('Welcome back!');
      navigate('/dashboard');
    } catch (error: any) {
      toast.error(error.message || 'Login failed');
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-50 via-white to-purple-50 flex items-center justify-center p-4 relative overflow-hidden">
      {/* Background pattern */}
      <div className="absolute inset-0 grid-pattern opacity-30"></div>
      
      {/* Floating elements */}
      <div className="absolute top-20 left-20 w-32 h-32 bg-gradient-to-br from-indigo-400 to-purple-600 rounded-full opacity-10 animate-float"></div>
      <div className="absolute bottom-20 right-20 w-24 h-24 bg-gradient-to-br from-purple-400 to-pink-600 rounded-full opacity-10 animate-float" style={{animationDelay: '2s'}}></div>
      <div className="absolute top-1/2 right-10 w-16 h-16 bg-gradient-to-br from-indigo-400 to-blue-600 rounded-full opacity-10 animate-float" style={{animationDelay: '4s'}}></div>
      
      <div className="w-full max-w-6xl grid lg:grid-cols-2 gap-8 items-center relative z-10">
        {/* Left side - Branding */}
        <div className="hidden lg:block space-y-8 animate-fade-in">
          <div className="flex items-center space-x-3">
            <div className="w-12 h-12 bg-gradient-to-br from-indigo-600 to-purple-600 rounded-2xl flex items-center justify-center shadow-xl animate-glow">
              <Zap className="w-6 h-6 text-white" />
            </div>
            <div>
              <h1 className="text-3xl font-bold text-gradient">
                Movie Recap
              </h1>
              <div className="flex items-center mt-1">
                <Globe2 className="w-4 h-4 text-indigo-600 mr-1" />
                <span className="text-sm text-slate-600 font-medium">Global AI Platform</span>
              </div>
            </div>
          </div>
          
          <div className="space-y-6">
            <h2 className="text-4xl font-bold text-slate-900 leading-tight">
              Transform movies into
              <span className="text-gradient block">
                engaging recaps
              </span>
            </h2>
            
            <p className="text-lg text-slate-600 leading-relaxed">
              AI-powered platform that creates professional movie recaps with multi-language support, 
              advanced analytics, and global distribution.
            </p>
            
            {/* Features */}
            <div className="space-y-4">
              {[
                { icon: Play, text: '4K Video Processing', color: 'from-blue-500 to-indigo-600' },
                { icon: Globe2, text: '12 Language Support', color: 'from-green-500 to-emerald-600' },
                { icon: Shield, text: 'Enterprise Security', color: 'from-purple-500 to-violet-600' },
                { icon: Sparkles, text: 'AI-Powered Analytics', color: 'from-pink-500 to-rose-600' }
              ].map((feature, index) => (
                <div key={index} className="flex items-center space-x-3 animate-slide-left" style={{animationDelay: `${index * 0.1}s`}}>
                  <div className={`w-8 h-8 bg-gradient-to-r ${feature.color} rounded-lg flex items-center justify-center shadow-md`}>
                    <feature.icon className="w-4 h-4 text-white" />
                  </div>
                  <span className="text-slate-700 font-medium">{feature.text}</span>
                </div>
              ))}
            </div>
            
            {/* Stats */}
            <div className="grid grid-cols-3 gap-6 pt-6 border-t border-slate-200">
              {[
                { number: '10k+', label: 'Projects Created' },
                { number: '50+', label: 'Countries' },
                { number: '99.9%', label: 'Uptime' }
              ].map((stat, index) => (
                <div key={index} className="text-center">
                  <div className="text-2xl font-bold text-gradient">{stat.number}</div>
                  <div className="text-sm text-slate-600">{stat.label}</div>
                </div>
              ))}
            </div>
          </div>
        </div>
        
        {/* Right side - Login form */}
        <div className="w-full max-w-md mx-auto animate-slide-up">
          {/* Language Selector */}
          <div className="flex justify-end mb-6">
            <LanguageSelector variant="compact" />
          </div>
          
          {/* Login Card */}
          <Card className="glass border-white/20 shadow-2xl">
            <CardContent className="p-8">
              {/* Header */}
              <div className="text-center mb-8">
                <div className="w-16 h-16 bg-gradient-to-br from-indigo-600 to-purple-600 rounded-2xl flex items-center justify-center mx-auto mb-4 shadow-xl animate-glow">
                  <Zap className="w-8 h-8 text-white" />
                </div>
                <h2 className="text-2xl font-bold text-slate-900 mb-2">
                  {t('auth.login')}
                </h2>
                <p className="text-slate-600">
                  Welcome back to your recap studio
                </p>
              </div>

              {/* Login Form */}
              <form className="space-y-6" onSubmit={handleSubmit(onSubmit)}>
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-semibold text-slate-700 mb-2">
                      Email address
                    </label>
                    <div className="relative">
                      <Mail className="absolute left-3 top-1/2 transform -translate-y-1/2 text-slate-400 w-5 h-5" />
                      <input
                        type="email"
                        autoComplete="email"
                        className={`w-full pl-12 pr-4 py-3 border rounded-xl text-sm transition-all duration-200 ${
                          errors.email 
                            ? 'border-red-300 focus:ring-red-500 bg-red-50' 
                            : 'border-slate-300 focus:ring-indigo-500 focus:border-transparent bg-white'
                        } focus:outline-none focus:ring-2 shadow-sm`}
                        placeholder="Enter your email"
                        {...register('email', {
                          required: 'Email is required',
                          pattern: {
                            value: /^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$/i,
                            message: 'Invalid email address',
                          },
                        })}
                      />
                    </div>
                    {errors.email && (
                      <p className="mt-1 text-sm text-red-600">{errors.email.message}</p>
                    )}
                  </div>

                  <div>
                    <label className="block text-sm font-semibold text-slate-700 mb-2">
                      Password
                    </label>
                    <div className="relative">
                      <Lock className="absolute left-3 top-1/2 transform -translate-y-1/2 text-slate-400 w-5 h-5" />
                      <input
                        type={showPassword ? 'text' : 'password'}
                        autoComplete="current-password"
                        className={`w-full pl-12 pr-12 py-3 border rounded-xl text-sm transition-all duration-200 ${
                          errors.password 
                            ? 'border-red-300 focus:ring-red-500 bg-red-50' 
                            : 'border-slate-300 focus:ring-indigo-500 focus:border-transparent bg-white'
                        } focus:outline-none focus:ring-2 shadow-sm`}
                        placeholder="Enter your password"
                        {...register('password', {
                          required: 'Password is required',
                          minLength: {
                            value: 8,
                            message: 'Password must be at least 8 characters',
                          },
                        })}
                      />
                      <button
                        type="button"
                        onClick={() => setShowPassword(!showPassword)}
                        className="absolute right-3 top-1/2 transform -translate-y-1/2 text-slate-400 hover:text-slate-600 transition-colors"
                      >
                        {showPassword ? (
                          <EyeOff className="w-5 h-5" />
                        ) : (
                          <Eye className="w-5 h-5" />
                        )}
                      </button>
                    </div>
                    {errors.password && (
                      <p className="mt-1 text-sm text-red-600">{errors.password.message}</p>
                    )}
                  </div>
                </div>

                <div className="flex items-center justify-between">
                  <div className="flex items-center">
                    <input
                      id="remember-me"
                      name="remember-me"
                      type="checkbox"
                      className="h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-slate-300 rounded"
                    />
                    <label htmlFor="remember-me" className="ml-2 block text-sm text-slate-700">
                      Remember me
                    </label>
                  </div>

                  <Link
                    to="/auth/forgot-password"
                    className="text-sm font-medium text-indigo-600 hover:text-indigo-500 transition-colors"
                  >
                    Forgot password?
                  </Link>
                </div>

                <Button
                  type="submit"
                  variant="primary"
                  size="lg"
                  loading={isLoading}
                  className="w-full bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-700 hover:to-purple-700 transform hover:scale-[1.02] transition-all duration-200 shadow-xl"
                >
                  {isLoading ? 'Signing in...' : 'Sign in to your studio'}
                </Button>
              </form>

              {/* Sign up link */}
              <div className="mt-6 text-center">
                <p className="text-sm text-slate-600">
                  Don't have an account?{' '}
                  <Link
                    to="/auth/register"
                    className="font-semibold text-indigo-600 hover:text-indigo-500 transition-colors"
                  >
                    Start your free trial
                  </Link>
                </p>
              </div>

              {/* Footer */}
              <div className="mt-8 pt-6 border-t border-slate-200 text-center">
                <p className="text-xs text-slate-500">
                  By signing in, you agree to our{' '}
                  <Link to="/terms" className="text-indigo-600 hover:text-indigo-500">
                    Terms
                  </Link>{' '}
                  and{' '}
                  <Link to="/privacy" className="text-indigo-600 hover:text-indigo-500">
                    Privacy Policy
                  </Link>
                </p>
              </div>
            </CardContent>
          </Card>
          
          {/* Mobile branding */}
          <div className="lg:hidden mt-8 text-center animate-fade-in">
            <p className="text-sm text-slate-600">
              Trusted by creators worldwide
            </p>
            <div className="flex justify-center space-x-8 mt-4">
              <div className="text-center">
                <div className="text-lg font-bold text-gradient">10k+</div>
                <div className="text-xs text-slate-600">Projects</div>
              </div>
              <div className="text-center">
                <div className="text-lg font-bold text-gradient">50+</div>
                <div className="text-xs text-slate-600">Countries</div>
              </div>
              <div className="text-center">
                <div className="text-lg font-bold text-gradient">99.9%</div>
                <div className="text-xs text-slate-600">Uptime</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default LoginPage;