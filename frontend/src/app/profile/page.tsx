'use client';

import React, { useState, useEffect, useMemo } from 'react';
import { motion } from 'framer-motion';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import {
  User,
  Sparkles,
  Heart,
  Star,
  TrendingUp,
  Award,
  Settings,
  Share2,
  ChevronRight,
  Zap,
  Target,
  Activity,
  AlertCircle
} from "lucide-react";
import { PieChart, Pie, Cell, BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Radar } from 'recharts';

const API_BASE_URL = `${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/v1`;

const FragranceProfile = ({ userId: propUserId }) => {
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [profileData, setProfileData] = useState(null);
  const [userId, setUserId] = useState(null);

  const decodeJWT = (token) => {
    try {
      const payload = token.split('.')[1];
      const decoded = JSON.parse(atob(payload));
      return decoded.sub;
    } catch (e) {
      console.error('Error decoding JWT:', e);
      return null;
    }
  };

  useEffect(() => {
    if (propUserId) {
      setUserId(propUserId);
      return;
    }

    const token = localStorage.getItem('access_token');
    if (token) {
      const decodedUserId = decodeJWT(token);
      if (decodedUserId) {
        setUserId(decodedUserId);
        return;
      }
    }

    const storedUserId = localStorage.getItem('user_id');
    if (storedUserId) {
      setUserId(storedUserId);
      return;
    }

    setError('User ID is required. Make sure you are logged in.');
    setIsLoading(false);
  }, [propUserId]);

  useEffect(() => {
    if (!userId) return;

    const loadProfile = async () => {
      try {
        setIsLoading(true);
        setError(null);

        const token = localStorage.getItem('access_token');
        const url = `${API_BASE_URL}/profile/${userId}`;
        
        const response = await fetch(url, {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json',
            ...(token && { 'Authorization': `Bearer ${token}` })
          }
        });

        if (!response.ok) {
          const errorText = await response.text();
          if (response.status === 404) {
            throw new Error(`User profile not found for userId: ${userId}`);
          } else if (response.status === 401) {
            throw new Error('Unauthorized - please log in again');
          } else {
            throw new Error(`Failed to load profile (${response.status}): ${errorText}`);
          }
        }

        const data = await response.json();
        setProfileData(data);
      } catch (err) {
        console.error('Error loading profile:', err);
        setError(err.message || 'Failed to load profile data');
      } finally {
        setIsLoading(false);
      }
    };

    loadProfile();
  }, [userId]);

  // Memoize chart data
  const memoizedChartData = useMemo(() => {
    if (!profileData) return null;
    return {
      noteBreakdown: profileData.note_breakdown,
      accordProfile: profileData.accord_profile,
      radarData: profileData.radar_data
    };
  }, [profileData]);

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-pink-50/80 via-rose-50/60 to-orange-50/50">
        <div className="w-16 h-16 rounded-full animate-spin" style={{ background: 'linear-gradient(90deg, #ff9ab3, #ffd09e)' }} />
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-pink-50/80 via-rose-50/60 to-orange-50/50">
        <Card className="bg-white/80 backdrop-blur-sm border-transparent p-6 max-w-md shadow-xl">
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-red-600">
              <AlertCircle className="w-5 h-5" />
              Error Loading Profile
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-muted-foreground mb-4">{error}</p>
            <Button 
              onClick={() => window.location.reload()} 
              className="w-full bg-gradient-to-r from-pink-600 to-orange-500 text-white"
            >
              Try Again
            </Button>
          </CardContent>
        </Card>
      </div>
    );
  }

  if (!profileData) return null;

  const { user, stats, note_breakdown, accord_profile, radar_data, fragrances, insights, recent_activity } = profileData;

  return (
    <div className="min-h-screen relative overflow-hidden pb-20">
      {/* Optimized Background - Static gradients with CSS animations */}
      <div className="absolute inset-0 bg-gradient-to-br from-pink-50/80 via-rose-50/60 to-orange-50/50" />
      <div className="absolute top-20 left-12 w-64 h-64 rounded-full opacity-20 animate-float-slow" style={{ background: 'linear-gradient(135deg, #ff9ab3, #ffd09e)', filter: 'blur(40px)' }} />
      <div className="absolute bottom-20 right-12 w-80 h-80 rounded-full opacity-20 animate-float-slower" style={{ background: 'linear-gradient(135deg, #ffd09e, #ff9ab3)', filter: 'blur(40px)' }} />

      <style jsx>{`
        @keyframes float-slow {
          0%, 100% { transform: translateY(0) scale(1); }
          50% { transform: translateY(20px) scale(1.05); }
        }
        @keyframes float-slower {
          0%, 100% { transform: translateY(0) scale(1); }
          50% { transform: translateY(-20px) scale(1.05); }
        }
        @keyframes fadeInUp {
          from { opacity: 0; transform: translateY(20px); }
          to { opacity: 1; transform: translateY(0); }
        }
        .animate-float-slow { animation: float-slow 8s ease-in-out infinite; }
        .animate-float-slower { animation: float-slower 10s ease-in-out infinite 1s; }
        .animate-fade-in-up { animation: fadeInUp 0.6s ease-out forwards; }
      `}</style>

      <div className="relative z-10 max-w-[1600px] mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-6">
        
        {/* HEADER - Only animate once on load */}
        <motion.div initial={{ opacity: 0, y: -20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.5 }}>
          <Card className="bg-white/80 backdrop-blur-sm border-transparent shadow-xl rounded-2xl">
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-6">
                  <div className="w-20 h-20 rounded-full flex items-center justify-center text-2xl font-bold text-white relative transition-transform hover:scale-105" style={{ background: 'linear-gradient(135deg, #ff9ab3, #ffd09e)' }}>
                    {user.avatar}
                    <div className="absolute -bottom-1 -right-1 w-6 h-6 bg-green-400 rounded-full border-4 border-white" />
                  </div>
                  <div>
                    <h1 className="text-3xl font-bold bg-gradient-to-r from-pink-600 to-orange-500 bg-clip-text text-transparent">
                      {user.name}'s Fragrance DNA
                    </h1>
                    <p className="text-muted-foreground mt-1">Member since {user.member_since}</p>
                    <div className="flex items-center gap-2 mt-2">
                      <Badge className="bg-pink-100 text-pink-700 border-0">
                        <Award className="w-3 h-3 mr-1" />
                        Expert Nose
                      </Badge>
                      <Badge className="bg-orange-100 text-orange-700 border-0">
                        <TrendingUp className="w-3 h-3 mr-1" />
                        Top 10%
                      </Badge>
                    </div>
                  </div>
                </div>
                <div className="flex gap-2">
                  <Button variant="outline" size="sm" className="bg-white/80 backdrop-blur-sm border-pink-100">
                    <Share2 className="w-4 h-4 mr-2" />
                    Share
                  </Button>
                  <Button variant="outline" size="sm" className="bg-white/80 backdrop-blur-sm border-pink-100">
                    <Settings className="w-4 h-4" />
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>
        </motion.div>

        {/* 3-COLUMN LAYOUT */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
          
          {/* LEFT COLUMN */}
          <div className="lg:col-span-3 space-y-6">
            
            {/* Quick Stats - Simplified animations */}
            <motion.div initial={{ opacity: 0, x: -50 }} animate={{ opacity: 1, x: 0 }} transition={{ duration: 0.6, delay: 0.1 }}>
            <Card className="bg-white/80 backdrop-blur-sm border-transparent shadow-lg rounded-2xl">
              <CardHeader>
                <CardTitle className="text-lg">Quick Stats</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                {[
                  { icon: Heart, label: "Fragrances", value: stats.fragrances_owned, color: "#ff9ab3" },
                  { icon: Star, label: "Match Score", value: `${stats.avg_match_score}%`, color: "#ffb8a3" },
                  { icon: Sparkles, label: "Notes", value: stats.notes_explored, color: "#ffd09e" },
                  { icon: TrendingUp, label: "Explored", value: stats.total_explorations, color: "#ffe4b8" }
                ].map((stat) => (
                  <div key={stat.label} className="flex items-center justify-between p-3 rounded-lg bg-gradient-to-r from-pink-50/50 to-orange-50/50 transition-transform hover:scale-105">
                    <div className="flex items-center gap-3">
                      <div className="w-10 h-10 rounded-full flex items-center justify-center" style={{ background: `linear-gradient(135deg, ${stat.color}, ${stat.color}dd)` }}>
                        <stat.icon className="w-5 h-5 text-white" />
                      </div>
                      <span className="text-sm font-medium">{stat.label}</span>
                    </div>
                    <span className="text-xl font-bold bg-gradient-to-r from-pink-600 to-orange-500 bg-clip-text text-transparent">
                      {stat.value}
                    </span>
                  </div>
                ))}
              </CardContent>
            </Card>
            </motion.div>

            {/* Note Breakdown - Disabled animations */}
            <motion.div initial={{ opacity: 0, x: -50 }} animate={{ opacity: 1, x: 0 }} transition={{ duration: 0.6, delay: 0.2 }}>
            <Card className="bg-white/80 backdrop-blur-sm border-transparent shadow-lg rounded-2xl">
              <CardHeader>
                <CardTitle className="text-lg">Note Breakdown</CardTitle>
                <CardDescription>Your favorite notes</CardDescription>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={220}>
                  <PieChart>
                    <Pie
                      data={memoizedChartData?.noteBreakdown}
                      cx="50%"
                      cy="50%"
                      innerRadius={50}
                      outerRadius={80}
                      paddingAngle={5}
                      dataKey="value"
                      isAnimationActive={false}
                    >
                      {note_breakdown.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.color} />
                      ))}
                    </Pie>
                    <Tooltip 
                      contentStyle={{ 
                        background: 'rgba(255, 255, 255, 0.95)', 
                        border: '1px solid rgba(255, 154, 179, 0.3)',
                        borderRadius: '8px'
                      }}
                    />
                  </PieChart>
                </ResponsiveContainer>
                <div className="flex flex-wrap gap-2 mt-4">
                  {note_breakdown.map((note) => (
                    <Badge key={note.name} variant="secondary" className="bg-white/60 backdrop-blur-sm text-xs">
                      <div className="w-2 h-2 rounded-full mr-1" style={{ background: note.color }} />
                      {note.name}
                    </Badge>
                  ))}
                </div>
              </CardContent>
            </Card>
            </motion.div>

            {/* Recent Activity */}
            <motion.div initial={{ opacity: 0, x: -50 }} animate={{ opacity: 1, x: 0 }} transition={{ duration: 0.6, delay: 0.3 }}>
            <Card className="bg-white/80 backdrop-blur-sm border-transparent shadow-lg rounded-2xl">
              <CardHeader>
                <CardTitle className="text-lg flex items-center gap-2">
                  <Activity className="w-4 h-4" />
                  Recent Activity
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                {recent_activity.map((activity, idx) => (
                  <div key={idx} className="flex items-start gap-2 text-sm">
                    <div className="w-2 h-2 rounded-full mt-1.5" style={{ background: '#ff9ab3' }} />
                    <div>
                      <p className="text-foreground">{activity.action}</p>
                      <p className="text-xs text-muted-foreground">{activity.time}</p>
                    </div>
                  </div>
                ))}
              </CardContent>
            </Card>
            </motion.div>

          </div>

          {/* CENTER COLUMN - Optimized visualization */}
          <div className="lg:col-span-6">
            <motion.div initial={{ opacity: 0, scale: 0.95 }} animate={{ opacity: 1, scale: 1 }} transition={{ duration: 0.6, delay: 0.2 }}>
            <Card className="bg-white/80 backdrop-blur-sm border-transparent shadow-xl rounded-2xl h-full">
              <CardHeader className="text-center pb-3">
                <div className="inline-flex items-center justify-center w-16 h-16 rounded-full mb-3 mx-auto animate-spin-slow" style={{ background: 'linear-gradient(135deg, #ff9ab3, #ffd09e)' }}>
                  <Sparkles className="w-8 h-8 text-white" />
                </div>
                <CardTitle className="text-3xl bg-gradient-to-r from-pink-600 to-orange-500 bg-clip-text text-transparent">
                  Your Scent Universe
                </CardTitle>
                <CardDescription>Interactive fragrance connection network</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="h-[600px] bg-white/40 backdrop-blur-sm rounded-lg flex items-center justify-center relative overflow-hidden border border-pink-100/50">
                  <div className="absolute inset-0 bg-gradient-to-br from-pink-50 to-orange-50 opacity-40" />
                  
                  <div className="absolute inset-0 opacity-10">
                    <svg className="w-full h-full">
                      <defs>
                        <pattern id="grid" width="40" height="40" patternUnits="userSpaceOnUse">
                          <path d="M 40 0 L 0 0 0 40" fill="none" stroke="#ff9ab3" strokeWidth="0.5"/>
                        </pattern>
                      </defs>
                      <rect width="100%" height="100%" fill="url(#grid)" />
                    </svg>
                  </div>

                  <div className="relative z-10 w-full h-full flex items-center justify-center">
                    <svg className="w-full h-full">
                      {/* Static lines instead of animated */}
                      <line x1="30%" y1="30%" x2="50%" y2="50%" stroke="#ff9ab3" strokeWidth="2" opacity="0.3" />
                      <line x1="70%" y1="30%" x2="50%" y2="50%" stroke="#ff9ab3" strokeWidth="2" opacity="0.3" />
                      <line x1="30%" y1="70%" x2="50%" y2="50%" stroke="#ff9ab3" strokeWidth="2" opacity="0.3" />
                      <line x1="70%" y1="70%" x2="50%" y2="50%" stroke="#ff9ab3" strokeWidth="2" opacity="0.3" />

                      {/* Simplified nodes */}
                      {[
                        { x: '50%', y: '50%', emoji: '⭐', size: 60 },
                        { x: '30%', y: '30%', emoji: '🌲', size: 50 },
                        { x: '70%', y: '30%', emoji: '🌸', size: 50 },
                        { x: '30%', y: '70%', emoji: '🍋', size: 50 },
                        { x: '70%', y: '70%', emoji: '💙', size: 50 }
                      ].map((node, idx) => (
                        <g key={idx}>
                          <circle cx={node.x} cy={node.y} r={node.size/2} fill="url(#nodeGradient)" className="cursor-pointer transition-transform hover:scale-110" style={{ transformOrigin: `${node.x} ${node.y}` }} />
                          <text x={node.x} y={node.y} fontSize={node.size * 0.6} textAnchor="middle" dominantBaseline="central">
                            {node.emoji}
                          </text>
                        </g>
                      ))}

                      <defs>
                        <linearGradient id="nodeGradient" x1="0%" y1="0%" x2="100%" y2="100%">
                          <stop offset="0%" stopColor="#ff9ab3" stopOpacity="0.8" />
                          <stop offset="100%" stopColor="#ffd09e" stopOpacity="0.8" />
                        </linearGradient>
                      </defs>
                    </svg>
                  </div>

                  <div className="absolute bottom-4 left-1/2 transform -translate-x-1/2">
                    <Button className="bg-gradient-to-r from-pink-600 to-orange-500 text-white shadow-lg hover:shadow-xl transition-shadow">
                      Explore Interactive Network
                      <ChevronRight className="w-4 h-4 ml-2" />
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>
            </motion.div>
          </div>

          {/* RIGHT COLUMN */}
          <div className="lg:col-span-3 space-y-6">
            
            {/* Accord Profile */}
            <motion.div initial={{ opacity: 0, x: 50 }} animate={{ opacity: 1, x: 0 }} transition={{ duration: 0.6, delay: 0.1 }}>
            <Card className="bg-white/80 backdrop-blur-sm border-transparent shadow-lg rounded-2xl">
              <CardHeader>
                <CardTitle className="text-lg">Fragrance Families</CardTitle>
                <CardDescription>Your accord distribution</CardDescription>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={240}>
                  <BarChart data={memoizedChartData?.accordProfile} layout="vertical">
                    <XAxis type="number" domain={[0, 50]} tick={{ fontSize: 10 }} />
                    <YAxis dataKey="name" type="category" width={70} tick={{ fontSize: 11 }} />
                    <Tooltip 
                      contentStyle={{ 
                        background: 'rgba(255, 255, 255, 0.95)', 
                        border: '1px solid rgba(255, 154, 179, 0.3)',
                        borderRadius: '8px',
                        fontSize: '12px'
                      }}
                    />
                    <Bar dataKey="value" radius={[0, 8, 8, 0]} isAnimationActive={false}>
                      {accord_profile.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.color} />
                      ))}
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>
            </motion.div>

            {/* Radar Chart */}
            <motion.div initial={{ opacity: 0, x: 50 }} animate={{ opacity: 1, x: 0 }} transition={{ duration: 0.6, delay: 0.2 }}>
            <Card className="bg-white/80 backdrop-blur-sm border-transparent shadow-lg rounded-2xl">
              <CardHeader>
                <CardTitle className="text-lg">Scent Personality</CardTitle>
                <CardDescription>Your fragrance DNA map</CardDescription>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={220}>
                  <RadarChart data={memoizedChartData?.radarData}>
                    <PolarGrid stroke="#ff9ab3" opacity={0.2} />
                    <PolarAngleAxis dataKey="category" tick={{ fill: '#666', fontSize: 10 }} />
                    <PolarRadiusAxis angle={90} domain={[0, 100]} tick={false} />
                    <Radar 
                      name="Your Profile" 
                      dataKey="value" 
                      stroke="#ff9ab3" 
                      fill="#ff9ab3" 
                      fillOpacity={0.5}
                      isAnimationActive={false}
                    />
                  </RadarChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>
            </motion.div>

            {/* Insights */}
            <motion.div initial={{ opacity: 0, x: 50 }} animate={{ opacity: 1, x: 0 }} transition={{ duration: 0.6, delay: 0.3 }}>
            <Card className="bg-white/80 backdrop-blur-sm border-transparent shadow-lg rounded-2xl">
              <CardHeader>
                <CardTitle className="text-lg flex items-center gap-2">
                  <Target className="w-4 h-4" />
                  Insights
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                {insights.map((insight, index) => (
                  <div key={index} className="flex items-start gap-2 p-3 rounded-lg bg-gradient-to-r from-pink-50/50 to-orange-50/50 transition-transform hover:translate-x-1">
                    <div className="w-5 h-5 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5 text-xs font-bold text-white" style={{ background: 'linear-gradient(135deg, #ff9ab3, #ffd09e)' }}>
                      {index + 1}
                    </div>
                    <p className="text-xs text-foreground leading-relaxed">{insight}</p>
                  </div>
                ))}
                <Button variant="outline" className="w-full mt-2 bg-white/60 backdrop-blur-sm border-pink-100 text-sm">
                  Get More Insights
                  <Zap className="w-3 h-3 ml-2" />
                </Button>
              </CardContent>
            </Card>
            </motion.div>

          </div>
        </div>

        {/* FRAGRANCE COLLECTION - Optimized */}
        <motion.div initial={{ opacity: 0, y: 50 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.6, delay: 0.4 }}>
        <Card className="bg-white/80 backdrop-blur-sm border-transparent shadow-xl rounded-2xl">
          <CardHeader>
            <CardTitle>Your Fragrance Collection</CardTitle>
            <CardDescription>Fragrances you love, organized by match score</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
              {fragrances.map((fragrance) => (
                <div
                  key={fragrance.id}
                  className="bg-white/60 backdrop-blur-sm border border-pink-100 rounded-lg p-4 text-center cursor-pointer hover:shadow-lg transition-all duration-300 hover:-translate-y-2"
                >
                  <div className="text-4xl mb-2">{fragrance.emoji}</div>
                  <div className="text-sm font-medium truncate">{fragrance.name}</div>
                  <div className="text-xs text-muted-foreground truncate">{fragrance.brand}</div>
                  <div className="flex items-center justify-center gap-1 mt-2">
                    <Heart className="w-3 h-3 text-pink-500 fill-current" />
                    <span className="text-xs font-medium text-pink-600">{fragrance.match}%</span>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
        </motion.div>

      </div>

      <style jsx>{`
        @keyframes spin-slow {
          from { transform: rotate(0deg); }
          to { transform: rotate(360deg); }
        }
        .animate-spin-slow {
          animation: spin-slow 20s linear infinite;
        }
      `}</style>
    </div>
  );
};

export default FragranceProfile;