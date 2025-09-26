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
// Quick Navigation Cards Component
export const QuickNavCards = () => {
  const [isLoggedIn, setIsLoggedIn] = useState(false);

  useEffect(() => {
    const token = localStorage.getItem('access_token');
    setIsLoggedIn(!!token);
  }, []);

  const handleNavigation = (path) => {
    console.log(`Navigating to: ${path}`);
    // In real app: router.push(path);
  };

  const cards = isLoggedIn ? [
    {
      icon: Target,
      title: "Take Quiz",
      description: "Discover your scent profile",
      path: "/quiz",
      color: "from-pink-500 to-orange-400"
    },
    {
      icon: Search,
      title: "Explore",
      description: "Browse fragrances",
      path: "/discover",
      color: "from-purple-500 to-pink-500"
    },
    {
      icon: User,
      title: "Dashboard",
      description: "View your profile",
      path: "/dashboard",
      color: "from-blue-500 to-purple-500"
    },
    {
      icon: Heart,
      title: "Favorites",
      description: "Your loved scents",
      path: "/favorites",
      color: "from-red-500 to-pink-500"
    }
  ] : [
    {
      icon: Target,
      title: "Start Quiz",
      description: "Find your perfect scent",
      path: "/login",
      color: "from-pink-500 to-orange-400"
    },
    {
      icon: Search,
      title: "Browse",
      description: "Explore fragrances",
      path: "/discover",
      color: "from-purple-500 to-pink-500"
    },
    {
      icon: User,
      title: "Join Us",
      description: "Create account",
      path: "/login",
      color: "from-blue-500 to-purple-500"
    },
    {
      icon: Star,
      title: "Features",
      description: "Why ScentMatch",
      path: "/features",
      color: "from-green-500 to-blue-500"
    }
  ];

  return (
    <section className="py-16 px-4">
      <div className="max-w-6xl mx-auto">
        <div className="text-center mb-12">
          <h2 className="text-3xl font-light text-gray-800 mb-4">
            Quick <span className="bg-gradient-to-r from-pink-600 to-orange-500 bg-clip-text text-transparent font-medium">Navigation</span>
          </h2>
          <p className="text-gray-600">Jump to what interests you most</p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {cards.map((card, index) => {
            const Icon = card.icon;
            return (
              <div
                key={index}
                onClick={() => handleNavigation(card.path)}
                className="group cursor-pointer bg-white/80 backdrop-blur-sm rounded-2xl p-6 border border-gray-100 hover:border-pink-200 transition-all duration-300 hover:shadow-xl hover:-translate-y-1"
              >
                <div className={`w-12 h-12 rounded-xl bg-gradient-to-r ${card.color} flex items-center justify-center mb-4 group-hover:scale-110 transition-transform duration-200`}>
                  <Icon className="w-6 h-6 text-white" />
                </div>
                <h3 className="text-lg font-semibold text-gray-800 mb-2">{card.title}</h3>
                <p className="text-gray-600 text-sm mb-4">{card.description}</p>
                <div className="flex items-center text-pink-600 text-sm font-medium group-hover:text-pink-700">
                  <span>Get started</span>
                  <ArrowRight className="w-4 h-4 ml-2 group-hover:translate-x-1 transition-transform" />
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </section>
  );
};