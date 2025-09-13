'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { FileText, Upload, Settings, LogOut, User, Sparkles } from "lucide-react";

interface User {
  id: string;
  email: string;
  display_name?: string;
}

export default function DashboardPage() {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const router = useRouter();

  useEffect(() => {
    const checkAuth = async () => {
      const token = localStorage.getItem('token');

      if (!token) {
        router.push('/login');
        return;
      }

      try {
        const response = await fetch('http://localhost:8000/api/v1/auth/me', {
          headers: {
            'Authorization': `Bearer ${token}`,
          },
        });

        if (response.ok) {
          const userData = await response.json();
          setUser(userData);
        } else {
          localStorage.removeItem('token');
          router.push('/login');
        }
      } catch (error) {
        console.error('Auth check failed:', error);
        localStorage.removeItem('token');
        router.push('/login');
      } finally {
        setLoading(false);
      }
    };

    checkAuth();
  }, [router]);

  const handleLogout = () => {
    localStorage.removeItem('token');
    router.push('/login');
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="flex items-center space-x-2">
          <div className="w-6 h-6 border-2 border-pink-500/30 border-t-pink-500 rounded-full animate-spin"></div>
          <span className="text-lg text-muted-foreground">Loading...</span>
        </div>
      </div>
    );
  }

  if (!user) {
    return null;
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-pink-50 via-rose-50 to-orange-50">
      {/* Header */}
      <header className="glass border-b border-pink-200/30 sticky top-0 z-10 backdrop-blur-lg">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-4">
            <div className="flex items-center space-x-3">
              <div className="w-8 h-8 rounded-full bg-gradient-to-r from-pink-500 to-rose-500 flex items-center justify-center">
                <FileText className="w-4 h-4 text-white" />
              </div>
              <h1 className="text-2xl font-bold bg-gradient-to-r from-pink-600 to-rose-600 bg-clip-text text-transparent">
                ScentMatch
              </h1>
            </div>

            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-2 glass px-3 py-2 rounded-full">
                <User className="w-4 h-4 text-pink-500" />
                <span className="text-sm font-medium text-foreground">
                  {user.display_name || user.email}
                </span>
              </div>
              <Button
                onClick={handleLogout}
                variant="outline"
                size="sm"
                className="glass border-pink-200/50 text-rose-600 hover:bg-rose-50 hover:border-rose-300"
              >
                <LogOut className="w-4 h-4 mr-2" />
                Logout
              </Button>
            </div>
          </div>
        </div>
      </header>

      {/* Main content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Welcome Section */}
        <div className="mb-8">
          <Card className="glass border-pink-200/30 shadow-luxury">
            <CardHeader className="text-center py-8">
              <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-gradient-to-r from-pink-400 to-rose-400 mb-4 mx-auto animate-glow">
                <Sparkles className="w-8 h-8 text-white" />
              </div>
              <CardTitle className="text-3xl font-bold bg-gradient-to-r from-pink-600 to-rose-600 bg-clip-text text-transparent">
                Welcome to Your Dashboard!
              </CardTitle>
              <CardDescription className="text-lg mt-2">
                Your Next.js frontend is successfully connected to FastAPI
              </CardDescription>
              <div className="mt-4 px-4 py-2 glass rounded-full inline-block">
                <p className="text-sm text-muted-foreground">
                  User ID: <span className="font-medium text-pink-600">{user.id}</span>
                </p>
              </div>
            </CardHeader>
          </Card>
        </div>

        {/* Action Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          <Card className="glass border-pink-200/30 hover:shadow-glow transition-luxury cursor-pointer group">
            <CardHeader className="text-center py-8">
              <div className="inline-flex items-center justify-center w-12 h-12 rounded-full bg-gradient-to-r from-blue-400 to-blue-500 mb-4 mx-auto group-hover:scale-110 transition-transform">
                <Upload className="w-6 h-6 text-white" />
              </div>
              <CardTitle className="text-xl font-semibold">Upload PDF</CardTitle>
              <CardDescription>
                Placeholder
              </CardDescription>
            </CardHeader>
          </Card>

          <Card className="glass border-pink-200/30 hover:shadow-glow transition-luxury cursor-pointer group">
            <CardHeader className="text-center py-8">
              <div className="inline-flex items-center justify-center w-12 h-12 rounded-full bg-gradient-to-r from-green-400 to-green-500 mb-4 mx-auto group-hover:scale-110 transition-transform">
                <FileText className="w-6 h-6 text-white" />
              </div>
              <CardTitle className="text-xl font-semibold">My Documents</CardTitle>
              <CardDescription>
                Placeholder
              </CardDescription>
            </CardHeader>
          </Card>

          <Card className="glass border-pink-200/30 hover:shadow-glow transition-luxury cursor-pointer group">
            <CardHeader className="text-center py-8">
              <div className="inline-flex items-center justify-center w-12 h-12 rounded-full bg-gradient-to-r from-purple-400 to-purple-500 mb-4 mx-auto group-hover:scale-110 transition-transform">
                <Settings className="w-6 h-6 text-white" />
              </div>
              <CardTitle className="text-xl font-semibold">Settings</CardTitle>
              <CardDescription>
                Configure your preferences and account
              </CardDescription>
            </CardHeader>
          </Card>
        </div>

        {/* Stats Section */}
        <div className="mt-8">
          <Card className="glass border-pink-200/30 shadow-luxury">
            <CardHeader>
              <CardTitle className="text-center text-xl font-semibold text-foreground">
                Your Activity
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6 text-center">
                <div className="space-y-2">
                  <div className="text-3xl font-bold bg-gradient-to-r from-pink-500 to-rose-500 bg-clip-text text-transparent">0</div>
                  <div className="text-sm text-muted-foreground">Documents Uploaded</div>
                </div>
                <div className="space-y-2">
                  <div className="text-3xl font-bold bg-gradient-to-r from-blue-500 to-cyan-500 bg-clip-text text-transparent">0</div>
                  <div className="text-sm text-muted-foreground">Annotations Made</div>
                </div>
                <div className="space-y-2">
                  <div className="text-3xl font-bold bg-gradient-to-r from-green-500 to-emerald-500 bg-clip-text text-transparent">0</div>
                  <div className="text-sm text-muted-foreground">Hours Saved</div>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </main>
    </div>
  );
}
