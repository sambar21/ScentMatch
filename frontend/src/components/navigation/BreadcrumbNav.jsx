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
// Breadcrumb Navigation Component
export const BreadcrumbNav = ({ items }) => {
  const handleNavigation = (path) => {
    console.log(`Navigating to: ${path}`);
    // In real app: router.push(path);
  };

  return (
    <nav className="flex items-center space-x-2 text-sm text-gray-600 mb-6">
      {items.map((item, index) => (
        <React.Fragment key={index}>
          {index > 0 && <ChevronRight className="w-4 h-4 text-gray-400" />}
          {item.path ? (
            <button
              onClick={() => handleNavigation(item.path)}
              className="hover:text-pink-600 transition-colors cursor-pointer"
            >
              {item.label}
            </button>
          ) : (
            <span className="text-gray-800 font-medium">{item.label}</span>
          )}
        </React.Fragment>
      ))}
    </nav>
  );
};
