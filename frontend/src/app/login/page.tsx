'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Sparkles, Heart, User, Mail, Lock, Eye, EyeOff } from "lucide-react";

export default function AuthPage() {
  const [activeTab, setActiveTab] = useState<'login' | 'signup'>('login');
  const [showPassword, setShowPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const router = useRouter();

  // Login form state
  const [loginForm, setLoginForm] = useState({
    email: '',
    password: ''
  });

  // Signup form state
  const [signupForm, setSignupForm] = useState({
    email: '',
    password: '',
    display_name: '',
    first_name: '',
    last_name: '',
    bio: '',
    avatar_url: ''
  });

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);

    try {
      // Use environment variable for API URL, fallback to localhost
      const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
      console.log(' Login API URL:', API_URL);

      const response = await fetch(`${API_URL}/api/v1/auth/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          email: loginForm.email,
          password: loginForm.password
        }),
      });

      const text = await response.text();
      console.log('Status:', response.status);
      console.log('Response body:', text);

        if (response.ok) {
          const data = JSON.parse(text);

        localStorage.setItem("access_token", data.access_token);
        localStorage.setItem("refresh_token", data.refresh_token);
        localStorage.setItem("expires_at", (Date.now() + data.expires_in * 1000).toString());
        window.dispatchEvent(new Event('auth-login'));
        
        router.push("/dashboard");
      } else {
        alert('Login failed! Please check your credentials.');
      }
    } catch (error) {
      console.error('Login error:', error);
      alert('Something went wrong! Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleSignup = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);

    try {
      console.log(' Sending signup data:', signupForm);
      
      // Use environment variable for API URL, fallback to localhost
      const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
      console.log(' API URL:', API_URL);
      
      const endpoint = `${API_URL}/api/v1/auth/register`;
      console.log(' Using endpoint:', endpoint);
      
      const response = await fetch(endpoint, {
        method: 'POST',
        headers: { 
          'Content-Type': 'application/json',
          'Accept': 'application/json'
        },
        body: JSON.stringify(signupForm),
      });

      console.log('📥 Response status:', response.status);
      console.log('📥 Response headers:', Object.fromEntries(response.headers));

      const text = await response.text();
      console.log('📥 Raw response:', text);

      if (response.ok) {
        const data = JSON.parse(text);
        console.log('✅ Success data:', data);
        alert('Account created successfully! Please sign in.');
        setActiveTab('login');
        setSignupForm({
          email: '',
          password: '',
          display_name: '',
          first_name: '',
          last_name: '',
          bio: '',
          avatar_url: ''
        });
      } else {
        // Enhanced error handling for the new API format
        let errorMessage = 'Registration failed';
        try {
          const errorData = JSON.parse(text);
          console.error(' Error response:', errorData);
          
          if (errorData.error) {
            // Handle the new error format from your API
            errorMessage = errorData.error.message;
            
            if (errorData.error.details && Array.isArray(errorData.error.details)) {
              const fieldErrors = errorData.error.details.map((detail: any) => 
                `${detail.field || 'Field'}: ${detail.message}`
              ).join('\n');
              errorMessage += '\n\nDetails:\n' + fieldErrors;
            }
          } else if (errorData.detail) {
            // Handle FastAPI default error format
            if (Array.isArray(errorData.detail)) {
              errorMessage = errorData.detail.map((err: any) => 
                `${err.loc ? err.loc.join('.') : 'Field'}: ${err.msg}`
              ).join('\n');
            } else if (typeof errorData.detail === 'string') {
              errorMessage = errorData.detail;
            }
          } else if (errorData.message) {
            errorMessage = errorData.message;
          }
        } catch (parseError) {
          console.error(' Could not parse error response:', text);
          errorMessage = `HTTP ${response.status}: ${text.substring(0, 200)}`;
        }
        
        alert(`Registration failed:\n${errorMessage}`);
      }
    } catch (error: any) {
      console.error(' Network/Fetch error:', error);
      let errorMsg = 'Network error occurred';
      
      if (error.name === 'TypeError' && error.message.includes('fetch')) {
        errorMsg = 'Cannot connect to server. Please check if the backend is running.';
      } else if (error.message) {
        errorMsg = error.message;
      }
      
      alert(`Network error: ${errorMsg}`);
    } finally {
      setIsLoading(false);
    }
  };

  const updateLoginForm = (field: keyof typeof loginForm, value: string) => {
    setLoginForm(prev => ({ ...prev, [field]: value }));
  };

  const updateSignupForm = (field: keyof typeof signupForm, value: string) => {
    setSignupForm(prev => ({ ...prev, [field]: value }));
  };

  return (
    <div className="min-h-screen flex items-center justify-center relative overflow-hidden py-8">
      {/* Background with gradient */}
      <div className="absolute inset-0 bg-gradient-secondary"></div>

      {/* Floating elements */}
      <div className="absolute top-20 left-20 animate-float">
        <div className="glass rounded-full p-4">
          <Sparkles className="w-8 h-8 text-primary" />
        </div>
      </div>
      <div className="absolute bottom-20 right-20 animate-float" style={{ animationDelay: '2s' }}>
        <div className="glass rounded-full p-4">
          <Heart className="w-6 h-6 text-accent" />
        </div>
      </div>
      <div className="absolute top-1/3 right-10 animate-float" style={{ animationDelay: '1s' }}>
        <div className="w-4 h-4 rounded-full bg-gradient-primary"></div>
      </div>

      {/* Auth form */}
      <div className="relative z-10 max-w-md w-full mx-4">
        <div className="glass rounded-3xl p-8 shadow-luxury animate-glow">
          {/* Header */}
          <div className="text-center mb-8">
            <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-gradient-primary mb-4 animate-glow">
              {activeTab === 'login' ? (
                <Sparkles className="w-8 h-8 text-primary-foreground" />
              ) : (
                <User className="w-8 h-8 text-primary-foreground" />
              )}
            </div>
            <h2 className="text-3xl font-light mb-2 text-foreground">
              {activeTab === 'login' ? (
                <>Welcome <span className="bg-gradient-primary bg-clip-text text-transparent font-medium">Back</span></>
              ) : (
                <>Join <span className="bg-gradient-primary bg-clip-text text-transparent font-medium">ScentMatch</span></>
              )}
            </h2>
            <p className="text-muted-foreground">
              {activeTab === 'login' ? 'Sign in to match scents you\'ll love' : 'Create an account to discover your signature scent'}
            </p>
          </div>

          {/* Tab switcher */}
          <div className="flex rounded-2xl bg-muted/50 p-1 mb-6">
            <button
              onClick={() => setActiveTab('login')}
              className={`flex-1 py-3 px-4 rounded-xl transition-luxury text-sm font-medium ${
                activeTab === 'login'
                  ? 'bg-gradient-primary text-primary-foreground shadow-glow'
                  : 'text-muted-foreground hover:text-foreground'
              }`}
            >
              Sign In
            </button>
            <button
              onClick={() => setActiveTab('signup')}
              className={`flex-1 py-3 px-4 rounded-xl transition-luxury text-sm font-medium ${
                activeTab === 'signup'
                  ? 'bg-gradient-primary text-primary-foreground shadow-glow'
                  : 'text-muted-foreground hover:text-foreground'
              }`}
            >
              Sign Up
            </button>
          </div>

          {/* Login Form */}
          {activeTab === 'login' && (
            <form onSubmit={handleLogin} className="space-y-6">
              <div className="space-y-2">
                <label htmlFor="login-email" className="text-sm font-medium text-foreground flex items-center gap-2">
                  <Mail className="w-4 h-4" />
                  Email
                </label>
                <Input
                  id="login-email"
                  type="email"
                  required
                  value={loginForm.email}
                  onChange={(e) => updateLoginForm('email', e.target.value)}
                  className="glass border-primary/20 focus:border-primary focus:ring-primary/20 transition-luxury"
                  placeholder="Enter your email"
                />
              </div>

              <div className="space-y-2">
                <label htmlFor="login-password" className="text-sm font-medium text-foreground flex items-center gap-2">
                  <Lock className="w-4 h-4" />
                  Password
                </label>
                <div className="relative">
                  <Input
                    id="login-password"
                    type={showPassword ? 'text' : 'password'}
                    required
                    value={loginForm.password}
                    onChange={(e) => updateLoginForm('password', e.target.value)}
                    className="glass border-primary/20 focus:border-primary focus:ring-primary/20 transition-luxury pr-12"
                    placeholder="Enter your password"
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground transition-colors"
                  >
                    {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                  </button>
                </div>
              </div>

              <Button
                type="submit"
                disabled={isLoading}
                className="w-full bg-gradient-primary hover:opacity-90 text-primary-foreground font-medium py-6 rounded-xl shadow-glow transition-luxury"
              >
                {isLoading ? (
                  <div className="flex items-center space-x-2">
                    <div className="w-4 h-4 border-2 border-primary-foreground/30 border-t-primary-foreground rounded-full animate-spin"></div>
                    <span>Signing in...</span>
                  </div>
                ) : (
                  'Sign In'
                )}
              </Button>
            </form>
          )}

          {/* Signup Form */}
          {activeTab === 'signup' && (
            <form onSubmit={handleSignup} className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <label className="text-sm font-medium text-foreground">First Name</label>
                  <Input
                    type="text"
                    value={signupForm.first_name}
                    onChange={(e) => updateSignupForm('first_name', e.target.value)}
                    className="glass border-primary/20 focus:border-primary focus:ring-primary/20 transition-luxury"
                    placeholder="First name"
                  />
                </div>
                <div className="space-y-2">
                  <label className="text-sm font-medium text-foreground">Last Name</label>
                  <Input
                    type="text"
                    value={signupForm.last_name}
                    onChange={(e) => updateSignupForm('last_name', e.target.value)}
                    className="glass border-primary/20 focus:border-primary focus:ring-primary/20 transition-luxury"
                    placeholder="Last name"
                  />
                </div>
              </div>

              <div className="space-y-2">
                <label className="text-sm font-medium text-foreground flex items-center gap-2">
                  <User className="w-4 h-4" />
                  Display Name
                </label>
                <Input
                  type="text"
                  value={signupForm.display_name}
                  onChange={(e) => updateSignupForm('display_name', e.target.value)}
                  className="glass border-primary/20 focus:border-primary focus:ring-primary/20 transition-luxury"
                  placeholder="How should we call you?"
                />
              </div>

              <div className="space-y-2">
                <label className="text-sm font-medium text-foreground flex items-center gap-2">
                  <Mail className="w-4 h-4" />
                  Email
                </label>
                <Input
                  type="email"
                  required
                  value={signupForm.email}
                  onChange={(e) => updateSignupForm('email', e.target.value)}
                  className="glass border-primary/20 focus:border-primary focus:ring-primary/20 transition-luxury"
                  placeholder="Enter your email"
                />
              </div>

              <div className="space-y-2">
                <label className="text-sm font-medium text-foreground flex items-center gap-2">
                  <Lock className="w-4 h-4" />
                  Password
                </label>
                <div className="relative">
                  <Input
                    type={showPassword ? 'text' : 'password'}
                    required
                    value={signupForm.password}
                    onChange={(e) => updateSignupForm('password', e.target.value)}
                    className="glass border-primary/20 focus:border-primary focus:ring-primary/20 transition-luxury pr-12"
                    placeholder="Create a strong password"
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground transition-colors"
                  >
                    {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                  </button>
                </div>
                <p className="text-xs text-muted-foreground">
                  8+ characters with mixed case, numbers recommended
                </p>
              </div>

              <div className="space-y-2">
                <label className="text-sm font-medium text-foreground">Bio (Optional)</label>
                <Input
                  type="text"
                  value={signupForm.bio}
                  onChange={(e) => updateSignupForm('bio', e.target.value)}
                  className="glass border-primary/20 focus:border-primary focus:ring-primary/20 transition-luxury"
                  placeholder="Tell us a bit about yourself"
                />
              </div>

              <Button
                type="submit"
                disabled={isLoading}
                className="w-full bg-gradient-primary hover:opacity-90 text-primary-foreground font-medium py-6 rounded-xl shadow-glow transition-luxury"
              >
                {isLoading ? (
                  <div className="flex items-center space-x-2">
                    <div className="w-4 h-4 border-2 border-primary-foreground/30 border-t-primary-foreground rounded-full animate-spin"></div>
                    <span>Creating account...</span>
                  </div>
                ) : (
                  'Create Account'
                )}
              </Button>
            </form>
          )}

          <div className="mt-6 text-center">
            <button
              onClick={() => router.push('/')}
              className="text-sm text-muted-foreground hover:text-primary transition-colors"
            >
              ← Back to home
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}