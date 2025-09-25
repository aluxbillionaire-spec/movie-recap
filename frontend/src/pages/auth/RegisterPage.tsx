import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useForm } from 'react-hook-form';
import { toast } from 'react-hot-toast';
// import { useTranslation } from 'react-i18next'; // Removed unused import
import { Mail, Lock, User, Eye, EyeOff, Zap, Globe2, Shield, Users, Award, Clock } from 'lucide-react';

import { useAuthStore } from '@/stores/auth';
import Button from '@/components/ui/Button';
import Input from '@/components/ui/Input';
import { Card, CardContent } from '@/components/ui/Card';
import LanguageSelector from '@/components/ui/LanguageSelector';

interface RegisterFormData {
  full_name: string;
  email: string;
  password: string;
  confirmPassword: string;
  terms: boolean;
}

const RegisterPage: React.FC = () => {
  // const { t } = useTranslation(); // Removed unused translation hook
  const navigate = useNavigate();
  const { register: registerUser, isLoading } = useAuthStore();
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);

  const {
    register,
    handleSubmit,
    watch,
    formState: { errors },
  } = useForm<RegisterFormData>();

  const password = watch('password');

  const onSubmit = async (data: RegisterFormData) => {
    try {
      await registerUser({
        full_name: data.full_name,
        email: data.email,
        password: data.password,
      });
      toast.success('Account created successfully!');
      navigate('/dashboard');
    } catch (error: any) {
      toast.error(error.message || 'Registration failed');
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-indigo-50 flex items-center justify-center p-4 relative overflow-hidden">
      {/* Background pattern */}
      <div className="absolute inset-0 grid-pattern opacity-30"></div>
      
      {/* Floating elements */}
      <div className="absolute top-20 right-20 w-32 h-32 bg-gradient-to-br from-blue-400 to-indigo-600 rounded-full opacity-10 animate-float"></div>
      <div className="absolute bottom-20 left-20 w-24 h-24 bg-gradient-to-br from-indigo-400 to-purple-600 rounded-full opacity-10 animate-float" style={{animationDelay: '2s'}}></div>
      <div className="absolute top-1/2 left-10 w-16 h-16 bg-gradient-to-br from-blue-400 to-cyan-600 rounded-full opacity-10 animate-float" style={{animationDelay: '4s'}}></div>
      
      <div className="w-full max-w-6xl grid lg:grid-cols-2 gap-8 items-center relative z-10">
        {/* Left side - Registration form */}
        <div className="w-full max-w-md mx-auto lg:order-2 animate-slide-up">
          {/* Language Selector */}
          <div className="flex justify-end mb-6">
            <LanguageSelector variant="compact" />
          </div>
          
          {/* Registration Card */}
          <Card className="glass border-white/20 shadow-2xl">
            <CardContent className="p-8">
              {/* Header */}
              <div className="text-center mb-8">
                <div className="w-16 h-16 bg-gradient-to-br from-blue-600 to-indigo-600 rounded-2xl flex items-center justify-center mx-auto mb-4 shadow-xl animate-glow">
                  <Zap className="w-8 h-8 text-white" />
                </div>
                <h2 className="text-2xl font-bold text-slate-900 mb-2">
                  Create Account
                </h2>
                <p className="text-slate-600">
                  Start your movie recap journey
                </p>
              </div>

              {/* Registration Form */}
              <form className="space-y-6" onSubmit={handleSubmit(onSubmit)}>
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-semibold text-slate-700 mb-2">
                      Full Name
                    </label>
                    <div className="relative">
                      <User className="absolute left-3 top-1/2 transform -translate-y-1/2 text-slate-400 w-5 h-5" />
                      <Input
                        type="text"
                        autoComplete="name"
                        placeholder="Enter your full name"
                        error={errors.full_name?.message}
                        {...register('full_name', {
                          required: 'Full name is required',
                          minLength: {
                            value: 2,
                            message: 'Full name must be at least 2 characters',
                          },
                        })}
                      />
                    </div>
                  </div>

                  <div>
                    <label className="block text-sm font-semibold text-slate-700 mb-2">
                      Email Address
                    </label>
                    <div className="relative">
                      <Mail className="absolute left-3 top-1/2 transform -translate-y-1/2 text-slate-400 w-5 h-5" />
                      <Input
                        type="email"
                        autoComplete="email"
                        placeholder="Enter your email"
                        error={errors.email?.message}
                        {...register('email', {
                          required: 'Email is required',
                          pattern: {
                            value: /^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$/i,
                            message: 'Invalid email address',
                          },
                        })}
                      />
                    </div>
                  </div>

                  <div>
                    <label className="block text-sm font-semibold text-slate-700 mb-2">
                      Password
                    </label>
                    <div className="relative">
                      <Lock className="absolute left-3 top-1/2 transform -translate-y-1/2 text-slate-400 w-5 h-5" />
                      <Input
                        type={showPassword ? 'text' : 'password'}
                        autoComplete="new-password"
                        placeholder="Create a strong password"
                        error={errors.password?.message}
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
                    <p className="mt-1 text-xs text-slate-500">
                      At least 8 characters with mix of letters and numbers
                    </p>
                  </div>

                  <div>
                    <label className="block text-sm font-semibold text-slate-700 mb-2">
                      Confirm Password
                    </label>
                    <div className="relative">
                      <Lock className="absolute left-3 top-1/2 transform -translate-y-1/2 text-slate-400 w-5 h-5" />
                      <Input
                        type={showConfirmPassword ? 'text' : 'password'}
                        autoComplete="new-password"
                        placeholder="Confirm your password"
                        error={errors.confirmPassword?.message}
                        {...register('confirmPassword', {
                          required: 'Please confirm your password',
                          validate: (value) => value === password || 'Passwords do not match',
                        })}
                      />
                      <button
                        type="button"
                        onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                        className="absolute right-3 top-1/2 transform -translate-y-1/2 text-slate-400 hover:text-slate-600 transition-colors"
                      >
                        {showConfirmPassword ? (
                          <EyeOff className="w-5 h-5" />
                        ) : (
                          <Eye className="w-5 h-5" />
                        )}
                      </button>
                    </div>
                  </div>
                </div>

                <div className="flex items-start space-x-3">
                  <input
                    id="terms"
                    type="checkbox"
                    className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-slate-300 rounded mt-1"
                    {...register('terms', {
                      required: 'You must agree to the terms and conditions',
                    })}
                  />
                  <div className="flex-1">
                    <label htmlFor="terms" className="text-sm text-slate-600 leading-relaxed">
                      I agree to the{' '}
                      <Link to="/terms" className="text-blue-600 hover:text-blue-500 font-medium">
                        Terms of Service
                      </Link>{' '}
                      and{' '}
                      <Link to="/privacy" className="text-blue-600 hover:text-blue-500 font-medium">
                        Privacy Policy
                      </Link>
                    </label>
                    {errors.terms && (
                      <p className="mt-1 text-sm text-red-600">{errors.terms.message}</p>
                    )}
                  </div>
                </div>

                <Button
                  type="submit"
                  variant="primary"
                  size="lg"
                  loading={isLoading}
                  className="w-full bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 transform hover:scale-[1.02] transition-all duration-200 shadow-xl"
                >
                  {isLoading ? 'Creating account...' : 'Create your account'}
                </Button>
              </form>

              {/* Sign in link */}
              <div className="mt-6 text-center">
                <p className="text-sm text-slate-600">
                  Already have an account?{' '}
                  <Link
                    to="/auth/login"
                    className="font-semibold text-blue-600 hover:text-blue-500 transition-colors"
                  >
                    Sign in here
                  </Link>
                </p>
              </div>

              {/* Footer */}
              <div className="mt-8 pt-6 border-t border-slate-200 text-center">
                <p className="text-xs text-slate-500">
                  By creating an account, you agree to receive product updates.
                </p>
              </div>
            </CardContent>
          </Card>
        </div>
        
        {/* Right side - Branding */}
        <div className="hidden lg:block space-y-8 animate-fade-in lg:order-1">
          <div className="flex items-center space-x-3">
            <div className="w-12 h-12 bg-gradient-to-br from-blue-600 to-indigo-600 rounded-2xl flex items-center justify-center shadow-xl animate-glow">
              <Zap className="w-6 h-6 text-white" />
            </div>
            <div>
              <h1 className="text-3xl font-bold text-gradient">
                Movie Recap
              </h1>
              <div className="flex items-center mt-1">
                <Globe2 className="w-4 h-4 text-blue-600 mr-1" />
                <span className="text-sm text-slate-600 font-medium">Join Our Community</span>
              </div>
            </div>
          </div>
          
          <div className="space-y-6">
            <h2 className="text-4xl font-bold text-slate-900 leading-tight">
              Start creating
              <span className="text-gradient block">
                amazing recaps today
              </span>
            </h2>
            
            <p className="text-lg text-slate-600 leading-relaxed">
              Join thousands of creators worldwide who trust our AI-powered platform 
              to transform movies into engaging, professional recaps.
            </p>
            
            {/* Benefits */}
            <div className="space-y-4">
              {[
                { icon: Users, text: 'Join 10,000+ Creators', color: 'from-blue-500 to-cyan-600' },
                { icon: Globe2, text: 'Global Multi-Language Support', color: 'from-green-500 to-emerald-600' },
                { icon: Shield, text: 'Enterprise-Grade Security', color: 'from-purple-500 to-violet-600' },
                { icon: Award, text: 'Professional Templates', color: 'from-orange-500 to-red-600' },
                { icon: Clock, text: '24/7 Priority Support', color: 'from-pink-500 to-rose-600' }
              ].map((benefit, index) => (
                <div key={index} className="flex items-center space-x-3 animate-slide-right" style={{animationDelay: `${index * 0.1}s`}}>
                  <div className={`w-8 h-8 bg-gradient-to-r ${benefit.color} rounded-lg flex items-center justify-center shadow-md`}>
                    <benefit.icon className="w-4 h-4 text-white" />
                  </div>
                  <span className="text-slate-700 font-medium">{benefit.text}</span>
                </div>
              ))}
            </div>
            
            {/* Testimonial */}
            <div className="bg-white/70 backdrop-blur-sm rounded-2xl p-6 border border-white/50 shadow-xl">
              <div className="flex items-start space-x-4">
                <div className="w-12 h-12 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-full flex items-center justify-center text-white font-bold text-lg">
                  M
                </div>
                <div className="flex-1">
                  <p className="text-slate-700 italic mb-2">
                    "Movie Recap has transformed how I create content. The AI is incredibly accurate and the multi-language support is game-changing."
                  </p>
                  <div>
                    <div className="font-semibold text-slate-900">Maria Rodriguez</div>
                    <div className="text-sm text-slate-600">Content Creator, Spain</div>
                  </div>
                </div>
              </div>
            </div>
            
            {/* Trust indicators */}
            <div className="grid grid-cols-3 gap-6 pt-6 border-t border-slate-200">
              {[
                { number: '10k+', label: 'Active Users' },
                { number: '50+', label: 'Countries' },
                { number: '1M+', label: 'Videos Processed' }
              ].map((stat, index) => (
                <div key={index} className="text-center">
                  <div className="text-2xl font-bold text-gradient">{stat.number}</div>
                  <div className="text-sm text-slate-600">{stat.label}</div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default RegisterPage;