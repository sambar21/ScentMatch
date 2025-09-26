'use client';

import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation'; // Add this import
import { Button } from "@/components/ui/button";
import { 
  Home, 
  Sparkles, 
  User, 
  Search, 
  Heart, 
  Settings, 
  LogOut,
  Menu,
  X,
  ArrowRight,
  ChevronRight,
  Star,
  Target,
  TrendingUp
} from "lucide-react";

// Main Navigation Bar Component
export const MainNavigation = () => {
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const [currentPath, setCurrentPath] = useState('/');
  const [isDashboard, setIsDashboard] = useState(false);
  const router = useRouter(); // Add this line

  useEffect(() => {
    const checkAuthAndPath = () => {
      const token = localStorage.getItem('access_token');
      const expiresAt = localStorage.getItem('expires_at');
      
      if (token && expiresAt) {
        const isExpired = Date.now() > parseInt(expiresAt);
        setIsLoggedIn(!isExpired);
      } else {
        setIsLoggedIn(false);
      }

      // Check if we're on pages that shouldn't show navigation
      const path = window.location.pathname || '/';
      setCurrentPath(path);
      console.log('Auth check - Path:', path, 'Token exists:', !!token, 'Is logged in:', !!(token && expiresAt && Date.now() <= parseInt(expiresAt)));
      
      // Hide navigation only on homepage, login, and dashboard
      const hiddenPaths = ['/', '/login', '/dashboard'];
      setIsDashboard(hiddenPaths.includes(path));
    };

    // Initial check
    checkAuthAndPath();

    // Listen for storage changes (works across tabs)
    const handleStorageChange = (e) => {
      // Only react to auth-related storage changes
      if (e.key === 'access_token' || e.key === 'expires_at' || e.key === null) {
        checkAuthAndPath();
      }
    };

    // Listen for custom login/logout events
    const handleAuthChange = () => {
      console.log('Auth event detected, rechecking...');
      checkAuthAndPath();
    };

    // Listen for route changes in Next.js
    const handleRouteChange = () => {
      // Small delay to ensure URL is updated
      setTimeout(checkAuthAndPath, 10);
    };

    window.addEventListener('storage', handleStorageChange);
    window.addEventListener('auth-login', handleAuthChange);
    window.addEventListener('auth-logout', handleAuthChange);
    window.addEventListener('popstate', handleRouteChange); // For browser back/forward
    
    // Check path on any navigation - this catches client-side routing
    const originalPushState = history.pushState;
    const originalReplaceState = history.replaceState;
    
    history.pushState = function(...args) {
      originalPushState.apply(history, args);
      setTimeout(checkAuthAndPath, 10);
    };
    
    history.replaceState = function(...args) {
      originalReplaceState.apply(history, args);
      setTimeout(checkAuthAndPath, 10);
    };
    
    return () => {
      window.removeEventListener('storage', handleStorageChange);
      window.removeEventListener('auth-login', handleAuthChange);
      window.removeEventListener('auth-logout', handleAuthChange);
      window.removeEventListener('popstate', handleRouteChange);
      
      // Restore original functions
      history.pushState = originalPushState;
      history.replaceState = originalReplaceState;
    };
  }, []);

  const handleNavigation = (path) => {
    console.log(`Navigating to: ${path}`);
    setCurrentPath(path);
    setIsMobileMenuOpen(false);
    
    // Force refresh for dashboard to ensure proper loading
    if (path === '/dashboard') {
      window.location.href = '/dashboard';
    } else {
      router.push(path);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('expires_at');
    setIsLoggedIn(false);
    
    // Dispatch a custom event to notify other components
    window.dispatchEvent(new Event('auth-logout'));
    
    // Force redirect to home
    window.location.href = '/';
  };

  const navItems = isLoggedIn ? [
    { path: '/dashboard', label: 'Home', icon: Home },
    { path: '/quiz', label: 'Take Quiz', icon: Target },
    { path: '/discover', label: 'Discover', icon: Search },
    { path: '/trending', label: 'Trending', icon: TrendingUp }
  ] : [
    { path: '/', label: 'Home', icon: Home },
    { path: '/quiz', label: 'Take Quiz', icon: Target },
    { path: '/discover', label: 'Discover', icon: Search },
    { path: '/trending', label: 'Trending', icon: TrendingUp }
  ];

  // Don't render navigation on dashboard
  if (isDashboard) {
    return null;
  }

  return (
    <>
      {/* Main Navigation Bar */}
      <nav className="fixed top-0 left-0 right-0 z-50 transition-all duration-300 backdrop-blur-xl bg-white/95 shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            {/* Logo */}
            <div 
              className="flex items-center space-x-3 cursor-pointer group"
              onClick={() => handleNavigation(isLoggedIn ? '/dashboard' : '/')}
            >
              <div className="w-8 h-8 rounded-full flex items-center justify-center bg-red-500 shadow-lg transition-all">
                <Sparkles className="w-4 h-4 text-white" />
              </div>
              <div className="relative">
                <h1 className="text-xl font-bold text-gray-800 group-hover:text-gray-900 transition-colors">
                  ScentMatch
                </h1>
                <div className="absolute inset-0 bg-gradient-to-r from-pink-600 to-orange-500 bg-clip-text text-transparent opacity-0 group-hover:opacity-100 transition-opacity">
                  <h1 className="text-xl font-bold">ScentMatch</h1>
                </div>
              </div>
            </div>

            {/* Desktop Navigation */}
            <div className="hidden md:flex items-center space-x-1">
              {navItems.map((item) => {
                const Icon = item.icon;
                const isActive = currentPath === item.path;
                return (
                  <Button
                    key={item.path}
                    variant="ghost"
                    onClick={() => handleNavigation(item.path)}
                    className={`flex items-center space-x-2 rounded-full px-4 py-2 transition-all duration-200 ${
                      isActive 
                        ? 'bg-gradient-to-r from-pink-100 to-orange-100 text-pink-700' 
                        : 'hover:bg-pink-50'
                    }`}
                  >
                    <Icon className="w-4 h-4" />
                    <span>{item.label}</span>
                  </Button>
                );
              })}
            </div>

            {/* User Actions */}
            <div className="flex items-center space-x-3">
              {isLoggedIn ? (
                <>
                  <Button
                    variant="ghost"
                    onClick={() => handleNavigation('/dashboard')}
                    className="hidden sm:flex items-center space-x-2 bg-gradient-to-r from-pink-50 to-orange-50 hover:from-pink-100 hover:to-orange-100 rounded-full px-4 py-2"
                  >
                    <User className="w-4 h-4" />
                    <span>Dashboard</span>
                  </Button>
                  <Button
                    variant="ghost"
                    onClick={handleLogout}
                    className="hidden sm:flex items-center space-x-2 rounded-full px-3 py-2 hover:bg-red-50 text-red-600"
                  >
                    <LogOut className="w-4 h-4" />
                  </Button>
                </>
              ) : (
                <Button
                  onClick={() => handleNavigation('/login')}
                  className="bg-gradient-to-r from-pink-500 to-orange-400 hover:from-pink-600 hover:to-orange-500 text-white rounded-full px-6 py-2 shadow-lg"
                >
                  Login
                </Button>
              )}

              {/* Mobile Menu Toggle */}
              <Button
                variant="ghost"
                className="md:hidden rounded-full p-2"
                onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
              >
                {isMobileMenuOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
              </Button>
            </div>
          </div>
        </div>

        {/* Mobile Menu */}
        {isMobileMenuOpen && (
          <div className="md:hidden bg-white/95 backdrop-blur-xl border-t border-pink-100/50">
            <div className="px-4 py-4 space-y-2">
              {navItems.map((item) => {
                const Icon = item.icon;
                const isActive = currentPath === item.path;
                return (
                  <Button
                    key={item.path}
                    variant="ghost"
                    onClick={() => handleNavigation(item.path)}
                    className={`w-full justify-start flex items-center space-x-3 rounded-lg px-4 py-3 ${
                      isActive 
                        ? 'bg-gradient-to-r from-pink-100 to-orange-100 text-pink-700' 
                        : 'hover:bg-pink-50'
                    }`}
                  >
                    <Icon className="w-5 h-5" />
                    <span>{item.label}</span>
                    {isActive && <div className="ml-auto w-2 h-2 bg-pink-500 rounded-full" />}
                  </Button>
                );
              })}
              
              {isLoggedIn && (
                <>
                  <div className="border-t border-pink-100 my-2" />
                  <Button
                    variant="ghost"
                    onClick={() => handleNavigation('/dashboard')}
                    className="w-full justify-start flex items-center space-x-3 rounded-lg px-4 py-3 hover:bg-pink-50"
                  >
                    <User className="w-5 h-5" />
                    <span>Dashboard</span>
                  </Button>
                  <Button
                    variant="ghost"
                    onClick={handleLogout}
                    className="w-full justify-start flex items-center space-x-3 rounded-lg px-4 py-3 hover:bg-red-50 text-red-600"
                  >
                    <LogOut className="w-5 h-5" />
                    <span>Logout</span>
                  </Button>
                </>
              )}
            </div>
          </div>
        )}
      </nav>

      {/* Spacer for fixed nav */}
      <div className="h-16" />
    </>
  );
};