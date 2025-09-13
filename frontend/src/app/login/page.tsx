'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Sparkles, Heart } from "lucide-react";

export default function LoginPage() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const router = useRouter();

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);

    try {
      const response = await fetch('http://localhost:8000/api/v1/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password }),
      });

      const text = await response.text();
      console.log('Status:', response.status);
      console.log('Response body:', text);

      if (response.ok) {
        const data = JSON.parse(text);
        localStorage.setItem('token', data.access_token);
        router.push('/dashboard');
      } else {
        alert('Login failed! See console for details.');
      }
    } catch (error) {
      console.error('Fetch error:', error);
      alert('Something went wrong! See console for details.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center relative overflow-hidden">
      {/* Background with gradient */}
      <div className="absolute inset-0 bg-gradient-to-br from-pink-50 via-rose-50 to-orange-50"></div>

      {/* Floating elements */}
      <div className="absolute top-20 left-20">
        <Sparkles className="w-8 h-8 text-pink-300 animate-float" />
      </div>
      <div className="absolute bottom-20 right-20">
        <Heart className="w-6 h-6 text-rose-300 animate-float" style={{ animationDelay: '2s' }} />
      </div>
      <div className="absolute top-1/3 right-10">
        <div className="w-4 h-4 rounded-full bg-gradient-to-r from-pink-200 to-rose-200 animate-float" style={{ animationDelay: '1s' }}></div>
      </div>

      {/* Login form */}
      <div className="relative z-10 max-w-md w-full mx-4">
        <div className="glass rounded-3xl p-8 shadow-luxury">
          <div className="text-center mb-8">
            <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-gradient-to-r from-pink-400 to-rose-400 mb-4">
              <Sparkles className="w-8 h-8 text-white" />
            </div>
            <h2 className="text-3xl font-bold bg-gradient-to-r from-pink-600 to-rose-600 bg-clip-text text-transparent mb-2">
              Welcome Back
            </h2>
            <p className="text-muted-foreground">Sign in to match scents you’ll love</p>
          </div>

          <form onSubmit={handleLogin} className="space-y-6">
            <div className="space-y-2">
              <label htmlFor="email" className="text-sm font-medium text-foreground">
                Email
              </label>
              <Input
                id="email"
                name="email"
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="glass border-pink-200/50 focus:border-pink-400 focus:ring-pink-400"
                placeholder="Enter your email"
              />
            </div>

            <div className="space-y-2">
              <label htmlFor="password" className="text-sm font-medium text-foreground">
                Password
              </label>
              <Input
                id="password"
                name="password"
                type="password"
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="glass border-pink-200/50 focus:border-pink-400 focus:ring-pink-400"
                placeholder="Enter your password"
              />
            </div>

            <Button
              type="submit"
              disabled={isLoading}
              className="w-full bg-gradient-to-r from-pink-500 to-rose-500 hover:from-pink-600 hover:to-rose-600 text-white font-medium py-6 rounded-xl shadow-glow transition-luxury"
            >
              {isLoading ? (
                <div className="flex items-center space-x-2">
                  <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin"></div>
                  <span>Signing in...</span>
                </div>
              ) : (
                'Sign In'
              )}
            </Button>
          </form>

          <div className="mt-6 text-center">
            <button
              onClick={() => router.push('/')}
              className="text-sm text-muted-foreground hover:text-pink-600 transition-colors"
            >
              ← Back to home
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
