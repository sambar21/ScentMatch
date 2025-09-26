'use client';

import React, { useState, useEffect } from 'react';
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

// Floating Action Buttons Component
export const FloatingActions = () => {
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [showTooltip, setShowTooltip] = useState(null);

  useEffect(() => {
    const token = localStorage.getItem('access_token');
    const expiresAt = localStorage.getItem('expires_at');
    
    if (token && expiresAt) {
      const isExpired = Date.now() > parseInt(expiresAt);
      setIsLoggedIn(!isExpired);
    }
  }, []);

  const handleNavigation = (path) => {
    console.log(`Navigating to: ${path}`);
    // In real app: router.push(path);
  };

  const FloatingButton = ({ icon: Icon, onClick, tooltip, color = "pink" }) => {
    const colorClasses = {
      pink: "bg-gradient-to-r from-pink-500 to-orange-400 hover:from-pink-600 hover:to-orange-500",
      purple: "bg-gradient-to-r from-purple-500 to-pink-500 hover:from-purple-600 hover:to-pink-600",
      blue: "bg-gradient-to-r from-blue-500 to-purple-500 hover:from-blue-600 hover:to-purple-600"
    };

    return (
      <div className="relative">
        <Button
          onClick={onClick}
          onMouseEnter={() => setShowTooltip(tooltip)}
          onMouseLeave={() => setShowTooltip(null)}
          className={`w-14 h-14 rounded-full shadow-lg ${colorClasses[color]} text-white p-0 transition-all duration-300 hover:scale-110 hover:shadow-xl`}
        >
          <Icon className="w-6 h-6" />
        </Button>
        
        {showTooltip === tooltip && (
          <div className="absolute right-16 top-1/2 transform -translate-y-1/2 bg-gray-900 text-white text-sm py-2 px-3 rounded-lg whitespace-nowrap z-10">
            {tooltip}
            <div className="absolute left-full top-1/2 transform -translate-y-1/2 border-4 border-transparent border-l-gray-900" />
          </div>
        )}
      </div>
    );
  };

  return (
    <div className="fixed bottom-6 right-6 z-40 flex flex-col space-y-3">
      {!isLoggedIn ? (
        <>
          <FloatingButton
            icon={Target}
            onClick={() => handleNavigation('/quiz')}
            tooltip="Take Quiz"
            color="pink"
          />
          <FloatingButton
            icon={User}
            onClick={() => handleNavigation('/login')}
            tooltip="Login"
            color="purple"
          />
        </>
      ) : (
        <>
          <FloatingButton
            icon={Search}
            onClick={() => handleNavigation('/discover')}
            tooltip="Discover"
            color="blue"
          />
          <FloatingButton
            icon={Heart}
            onClick={() => handleNavigation('/favorites')}
            tooltip="Favorites"
            color="pink"
          />
          <FloatingButton
            icon={User}
            onClick={() => handleNavigation('/dashboard')}
            tooltip="Dashboard"
            color="purple"
          />
        </>
      )}
    </div>
  );
};