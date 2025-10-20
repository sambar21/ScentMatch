'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import {
  Search,
  User,
  Settings,
  LogOut,
  Sparkles,
  Heart,
  Star,
  ChevronLeft,
  ChevronRight,
  CheckCircle,
  Clock,
  Play,
  TrendingUp
} from "lucide-react";
import heroImage from "@/assets/hero-luxury-perfume.jpg";

interface User {
  id: string;
  email: string;
  display_name?: string;
}

// Original vibrant gradient colors
const ICON_GRADIENT = 'linear-gradient(90deg, #ff9ab3, #ffd09e)';
const TEXT_GRADIENT = 'linear-gradient(90deg, #ff6b9a, #ffb26b)';
const ACCENT_COLOR = '#ff6b9a';
const SOFT_ACCENT = '#ff9ab3';

export default function FragranceDashboard() {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const [quizTaken, setQuizTaken] = useState(false);
  const [currentSlide, setCurrentSlide] = useState(0);
  const router = useRouter();

  useEffect(() => {
    const checkAuth = async () => {
      const token = localStorage.getItem('access_token');

      if (!token) {
        router.push('/login');
        return;
      }

      try {
        const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/v1/auth/me`, {
          headers: {
            'Authorization': `Bearer ${token}`,
          },
        });

        if (response.ok) {
          const userData = await response.json();
          setUser(userData);
          setQuizTaken(false);
        } else {
          localStorage.removeItem('access_token');
          localStorage.removeItem('refresh_token');
          localStorage.removeItem('expires_at');
          router.push('/login');
        }
      } catch (error) {
        console.error('Auth check failed:', error);
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        localStorage.removeItem('expires_at');
        router.push('/login');
      } finally {
        setLoading(false);
      }
    };

    checkAuth();
  }, [router]);

  const handleLogout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('expires_at');
    router.push('/login');
  };

  const userPreferences = ["Woody", "Evening", "Moderate", "Fresh"];

  const recommendedFragrances = [
    { name: "Tom Ford Oud Wood", brand: "Tom Ford", match: 95, image: "🌲", notes: "Warm & Sophisticated" },
    { name: "Creed Aventus", brand: "Creed", match: 92, image: "🍃", notes: "Fresh & Bold" },
    { name: "Maison Margiela REPLICA", brand: "Maison Margiela", match: 89, image: "🔥", notes: "Intimate & Cozy" }
  ];

  const popularFragrances = [
    { name: "Dior Sauvage", brand: "Dior", rating: 4.8, image: "🌊", reviews: "2.4k" },
    { name: "Bleu de Chanel", brand: "Chanel", rating: 4.7, image: "💙", reviews: "1.8k" },
    { name: "Spicebomb", brand: "Viktor & Rolf", rating: 4.6, image: "💥", reviews: "1.2k" },
    { name: "1 Million", brand: "Paco Rabanne", rating: 4.5, image: "✨", reviews: "3.1k" }
  ];

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-pink-50 via-rose-50 to-orange-50">
        <div className="flex items-center space-x-3">
          <div className="w-8 h-8 border-3 rounded-full animate-spin" style={{ borderColor: 'rgba(255,154,179,0.25)', borderTopColor: '#ff9ab3' }} />
          <span className="text-lg text-gray-600">Loading your profile...</span>
        </div>
      </div>
    );
  }

  if (!user) return null;

  return (
    <div className="min-h-screen relative overflow-hidden bg-gradient-to-br from-pink-50/85 via-rose-50/65 to-orange-50/55">
      {/* Subtle background texture */}
      <div
        className="absolute inset-0 opacity-[0.03]"
        style={{
          backgroundImage: `url(${heroImage})`,
          backgroundSize: 'cover',
          backgroundPosition: 'center',
          filter: 'blur(40px) saturate(80%)',
        }}
        aria-hidden
      />

      {/* Elegant floating accents */}
      <div className="absolute top-20 right-16 z-0 opacity-40 animate-float">
        <div className="rounded-full p-4 bg-white/60 shadow-lg backdrop-blur-sm">
          <Sparkles className="w-6 h-6" style={{ color: SOFT_ACCENT }} />
        </div>
      </div>
      <div className="absolute bottom-32 left-16 z-0 opacity-30 animate-float" style={{ animationDelay: '2s' }}>
        <div className="rounded-full p-4 bg-white/60 shadow-lg backdrop-blur-sm">
          <Heart className="w-5 h-5" style={{ color: ACCENT_COLOR }} />
        </div>
      </div>

      {/* Refined Header */}
      <header className="relative z-10 bg-white/70 backdrop-blur-xl border-b border-pink-100/50 shadow-sm">
        <div className="max-w-7xl mx-auto px-6 lg:px-8">
          <div className="flex justify-between items-center py-4">
            {/* Logo */}
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 rounded-full flex items-center justify-center shadow-md" style={{ background: ICON_GRADIENT }}>
                <Sparkles className="w-5 h-5 text-white" />
              </div>
              <h1 className="text-2xl font-bold tracking-tight" style={{ background: TEXT_GRADIENT, WebkitBackgroundClip: 'text', color: 'transparent' }}>
                ScentMatch
              </h1>
            </div>

            {/* Search */}
            <div className="hidden md:flex items-center max-w-lg w-full mx-12">
              <div className="relative w-full">
                <Search className="absolute left-4 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
                <input
                  type="text"
                  placeholder="Search fragrances, brands, notes..."
                  className="w-full pl-11 pr-4 py-2.5 bg-white/80 border border-pink-100/50 rounded-full focus:outline-none focus:ring-2 focus:ring-pink-300/50 focus:border-transparent text-sm transition-all"
                />
              </div>
            </div>

            {/* User Actions */}
            <div className="flex items-center space-x-3">
              <div className="flex items-center space-x-2 bg-white/80 px-4 py-2 rounded-full border border-pink-100/50 shadow-sm">
                <User className="w-4 h-4" style={{ color: ACCENT_COLOR }} />
                <span className="text-sm font-medium text-gray-700">{user.display_name || user.email}</span>
              </div>
              <Button
                variant="outline"
                size="sm"
                className="bg-white/80 border-pink-100/50 text-gray-600 hover:bg-white hover:text-gray-800 rounded-full shadow-sm"
              >
                <Settings className="w-4 h-4" />
              </Button>
              <Button
                onClick={handleLogout}
                variant="outline"
                size="sm"
                className="bg-white/80 border-pink-100/50 text-gray-600 hover:bg-white hover:text-gray-800 rounded-full shadow-sm"
              >
                <LogOut className="w-4 h-4 mr-2" />
                Logout
              </Button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="relative z-10 max-w-7xl mx-auto px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
          {/* LEFT SIDEBAR - Navigation Block */}
          <div className="lg:col-span-1 space-y-5">
            <Card className="bg-white/80 backdrop-blur-sm shadow-md border border-transparent rounded-2xl overflow-hidden">
              <CardHeader className="text-center pb-4">
                <div className="w-20 h-20 mx-auto rounded-full flex items-center justify-center mb-4 shadow-lg" style={{ background: ICON_GRADIENT }}>
                  <User className="w-10 h-10 text-white" />
                </div>
                <CardTitle className="text-xl font-semibold text-foreground">{user.display_name || 'FragranceLover'}</CardTitle>
                <CardDescription className="text-sm text-muted-foreground">Member since March 2024</CardDescription>
                {!quizTaken && (
                  <div className="mt-3 px-3 py-1.5 bg-amber-50 border border-amber-200 rounded-full">
                    <div className="flex items-center justify-center gap-2">
                      <Clock className="w-3.5 h-3.5 text-amber-600" />
                      <span className="text-xs font-medium text-amber-700">Profile: 25% Complete</span>
                    </div>
                  </div>
                )}
              </CardHeader>
            </Card>

            <Card className="bg-white/80 backdrop-blur-sm shadow-md border border-transparent rounded-2xl overflow-hidden">
              <CardHeader className="pb-3">
                <CardTitle className="text-sm font-semibold text-muted-foreground uppercase tracking-wide">Navigation</CardTitle>
              </CardHeader>
              <CardContent className="space-y-1.5">
                <Button variant="ghost" className="w-full justify-start bg-gradient-to-r from-pink-100/50 to-rose-100/40 text-foreground font-medium rounded-xl hover:bg-pink-100/60">
                  Dashboard
                </Button>
                <Button variant="ghost" className="w-full justify-start text-foreground hover:bg-white/60 rounded-xl"onClick={() => router.push('/profile')}>My Profile</Button>
                <Button variant="ghost" className="w-full justify-start text-foreground hover:bg-white/60 rounded-xl">Quiz Results</Button>
                <Button variant="ghost" className="w-full justify-start text-foreground hover:bg-white/60 rounded-xl">Recommendations</Button>
              </CardContent>
            </Card>

            <Card className="bg-white/80 backdrop-blur-sm shadow-md border border-transparent rounded-2xl overflow-hidden">
              <CardHeader className="pb-3">
                <CardTitle className="text-sm font-semibold text-muted-foreground uppercase tracking-wide">Your Activity</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="text-center p-4 bg-gradient-to-br from-pink-50 to-orange-50/50 rounded-xl">
                  <div className="text-3xl font-bold" style={{ color: ACCENT_COLOR }}>{quizTaken ? 12 : 0}</div>
                  <div className="text-sm text-muted-foreground mt-1">Fragrances Explored</div>
                </div>
                <div className="flex items-center justify-between text-sm">
                  <span className="text-muted-foreground">Quiz Status</span>
                  <span className="font-semibold" style={{ color: quizTaken ? '#10b981' : ACCENT_COLOR }}>
                    {quizTaken ? 'Complete' : 'Pending'}
                  </span>
                </div>
                <div className="text-xs text-muted-foreground text-center pt-2 border-t border-gray-100">
                  Last active: 2 hours ago
                </div>
              </CardContent>
            </Card>
          </div>

          {/* CENTER & RIGHT COLUMNS */}
          <div className="lg:col-span-3 space-y-6">
            {/* Hero Welcome Section */}
            <Card className="bg-gradient-to-br from-white/90 to-pink-50/60 backdrop-blur-sm shadow-xl border border-transparent rounded-2xl overflow-hidden">
              <CardContent className="py-12 px-8 text-center">
                <div className="inline-flex items-center justify-center w-20 h-20 rounded-full mb-6 shadow-lg animate-pulse" style={{ background: ICON_GRADIENT }}>
                  <Sparkles className="w-10 h-10 text-white" />
                </div>
                <h2 className="text-4xl font-bold mb-3 tracking-tight" style={{ background: TEXT_GRADIENT, WebkitBackgroundClip: 'text', color: 'transparent' }}>
                  Welcome, {user.display_name || 'Fragrance Enthusiast'}
                </h2>
                <p className="text-lg text-gray-600 mb-8 max-w-2xl mx-auto leading-relaxed">
                  Discover your signature scent through our personalized fragrance journey. Let us guide you to perfumes that truly resonate with your unique style and preferences.
                </p>
                {!quizTaken && (
                  <Button 
                    onClick={() => router.push('/quiz')}
                    size="lg"
                    className="px-8 py-6 text-base font-medium text-white rounded-full shadow-lg hover:shadow-xl transition-all transform hover:scale-105"
                    style={{ background: TEXT_GRADIENT }}
                  >
                    <Play className="w-5 h-5 mr-2" />
                    Start Your Fragrance Quiz
                  </Button>
                )}
              </CardContent>
            </Card>

            {/* Main Content Grid */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              {/* Primary Content - Spans 2 columns */}
              <div className="lg:col-span-2 space-y-6">
                {/* Recommendations Section */}
                <Card className="bg-white/80 backdrop-blur-sm shadow-md border border-transparent rounded-2xl overflow-hidden">
                  <CardHeader className="border-b border-gray-100 bg-gradient-to-r from-white to-pink-50/30">
                    <div className="flex items-center justify-between">
                      <div>
                        <CardTitle className="text-2xl font-semibold text-foreground">
                          {!quizTaken ? "Your Personal Recommendations" : "Curated Just For You"}
                        </CardTitle>
                        <CardDescription className="text-muted-foreground mt-1">
                          {!quizTaken ? "Complete your quiz to unlock personalized matches" : `${recommendedFragrances.length} fragrances matched to your profile`}
                        </CardDescription>
                      </div>
                      {quizTaken && (
                        <TrendingUp className="w-6 h-6" style={{ color: SOFT_ACCENT }} />
                      )}
                    </div>
                  </CardHeader>
                  <CardContent className="pt-6">
                    {!quizTaken ? (
                      <div className="text-center py-8">
                        <div className="mb-8 p-8 bg-gradient-to-br from-pink-50 to-orange-50/40 rounded-2xl border border-transparent">
                          <div className="text-5xl mb-4 opacity-30">🌸</div>
                          <h3 className="text-lg font-semibold text-foreground mb-3">Unlock Your Perfect Matches</h3>
                          <p className="text-sm text-muted-foreground mb-6 max-w-md mx-auto">
                            Our intelligent quiz analyzes your preferences across fragrance families, occasions, and intensity to create a truly personalized recommendation profile.
                          </p>
                          <div className="flex flex-wrap gap-3 justify-center mb-6">
                            <span className="px-4 py-2 bg-white border border-pink-100 rounded-full text-xs font-medium text-gray-700 shadow-sm">
                              Fragrance Families
                            </span>
                            <span className="px-4 py-2 bg-white border border-pink-100 rounded-full text-xs font-medium text-gray-700 shadow-sm">
                              Lifestyle & Occasions
                            </span>
                            <span className="px-4 py-2 bg-white border border-pink-100 rounded-full text-xs font-medium text-gray-700 shadow-sm">
                              Intensity Preferences
                            </span>
                          </div>
                        </div>
                        <Button 
                          onClick={() => router.push('/quiz')}
                          size="lg"
                          className="px-8 py-3 text-white rounded-full shadow-md hover:shadow-lg transition-all"
                          style={{ background: TEXT_GRADIENT }}
                        >
                          Begin Your Discovery
                        </Button>
                      </div>
                    ) : (
                      <div className="space-y-6">
                        <div className="flex flex-wrap gap-2 mb-4">
                          {userPreferences.map((pref, index) => (
                            <span key={index} className="px-4 py-1.5 bg-gradient-to-r from-pink-50 to-orange-50 border border-pink-200 text-gray-700 rounded-full text-sm font-medium">
                              {pref}
                            </span>
                          ))}
                        </div>
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                          {recommendedFragrances.slice(currentSlide, currentSlide + 2).map((fragrance, index) => (
                            <div key={index} className="group bg-gradient-to-br from-white to-pink-50/40 border border-transparent rounded-2xl p-6 hover:shadow-lg transition-all cursor-pointer">
                              <div className="text-4xl mb-4">{fragrance.image}</div>
                              <h4 className="text-base font-semibold text-foreground mb-1">{fragrance.name}</h4>
                              <p className="text-sm text-muted-foreground mb-3">{fragrance.brand}</p>
                              <p className="text-xs text-gray-600 mb-4 italic">{fragrance.notes}</p>
                              <div className="flex items-center justify-between">
                                <div className="flex items-center gap-2">
                                  <Heart className="w-4 h-4" style={{ color: ACCENT_COLOR }} />
                                  <span className="text-sm font-semibold" style={{ color: ACCENT_COLOR }}>{fragrance.match}% Match</span>
                                </div>
                                <Button variant="ghost" size="sm" className="text-xs text-muted-foreground hover:text-foreground">
                                  View Details
                                </Button>
                              </div>
                            </div>
                          ))}
                        </div>
                        {recommendedFragrances.length > 2 && (
                          <div className="flex items-center justify-center gap-3 pt-4">
                            <Button 
                              variant="outline" 
                              size="sm" 
                              onClick={() => setCurrentSlide(Math.max(0, currentSlide - 1))} 
                              disabled={currentSlide === 0}
                              className="rounded-full border-pink-200"
                            >
                              <ChevronLeft className="w-4 h-4" />
                            </Button>
                            <span className="text-sm text-muted-foreground">
                              {currentSlide + 1}-{Math.min(currentSlide + 2, recommendedFragrances.length)} of {recommendedFragrances.length}
                            </span>
                            <Button 
                              variant="outline" 
                              size="sm" 
                              onClick={() => setCurrentSlide(Math.min(recommendedFragrances.length - 2, currentSlide + 1))} 
                              disabled={currentSlide >= recommendedFragrances.length - 2}
                              className="rounded-full border-pink-200"
                            >
                              <ChevronRight className="w-4 h-4" />
                            </Button>
                          </div>
                        )}
                      </div>
                    )}
                  </CardContent>
                </Card>

                {/* Popular Fragrances */}
                <Card className="bg-white/80 backdrop-blur-sm shadow-md border border-transparent rounded-2xl overflow-hidden">
                  <CardHeader className="border-b border-gray-100">
                    <CardTitle className="text-xl font-semibold text-foreground">Trending Discoveries</CardTitle>
                    <CardDescription className="text-muted-foreground">Most loved by our community this month</CardDescription>
                  </CardHeader>
                  <CardContent className="pt-6">
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
                      {popularFragrances.map((fragrance, index) => (
                        <div key={index} className="group bg-gradient-to-br from-white to-pink-50/40 border border-transparent rounded-xl p-4 text-center hover:shadow-md transition-all cursor-pointer">
                          <div className="text-3xl mb-3">{fragrance.image}</div>
                          <h4 className="text-sm font-medium text-foreground mb-1 truncate">{fragrance.name}</h4>
                          <p className="text-xs text-muted-foreground mb-3 truncate">{fragrance.brand}</p>
                          <div className="flex items-center justify-center gap-1.5 mb-2">
                            <Star className="w-3.5 h-3.5 text-amber-500 fill-amber-500" />
                            <span className="text-sm font-semibold text-foreground">{fragrance.rating}</span>
                          </div>
                          <p className="text-xs text-muted-foreground">{fragrance.reviews} reviews</p>
                        </div>
                      ))}
                    </div>
                    <div className="text-center">
                      <Button variant="outline" className="border-pink-200 text-foreground hover:bg-pink-50 rounded-full px-6">
                        Explore More Trending Scents
                      </Button>
                    </div>
                  </CardContent>
                </Card>
              </div>

              {/* Right Sidebar - Next Steps */}
              <div className="lg:col-span-1 space-y-6">
                <Card className="bg-white/80 backdrop-blur-sm shadow-md border border-transparent rounded-2xl overflow-hidden">
                  <CardHeader className="bg-gradient-to-br from-white to-pink-50/40 border-b border-gray-100">
                    <CardTitle className="text-sm font-semibold text-muted-foreground uppercase tracking-wide">Your Journey</CardTitle>
                  </CardHeader>
                  <CardContent className="pt-5 space-y-4">
                    <div className="flex items-start gap-3">
                      <CheckCircle className="w-5 h-5 text-green-500 mt-0.5 flex-shrink-0" />
                      <div>
                        <p className="text-sm font-medium text-foreground">Account Created</p>
                        <p className="text-xs text-muted-foreground mt-0.5">Welcome to ScentMatch</p>
                      </div>
                    </div>
                    <div className="flex items-start gap-3">
                      {quizTaken ? (
                        <CheckCircle className="w-5 h-5 text-green-500 mt-0.5 flex-shrink-0" />
                      ) : (
                        <div className="w-5 h-5 rounded-full border-2 border-gray-300 mt-0.5 flex-shrink-0" />
                      )}
                      <div>
                        <p className="text-sm font-medium text-foreground">Complete Quiz</p>
                        <p className="text-xs text-muted-foreground mt-0.5">Unlock personalized matches</p>
                      </div>
                    </div>
                    <div className="flex items-start gap-3 opacity-50">
                      <div className="w-5 h-5 rounded-full border-2 border-gray-300 mt-0.5 flex-shrink-0" />
                      <div>
                        <p className="text-sm font-medium text-foreground">Rate Fragrances</p>
                        <p className="text-xs text-muted-foreground mt-0.5">Refine your recommendations</p>
                      </div>
                    </div>
                    <div className="flex items-start gap-3 opacity-50">
                      <div className="w-5 h-5 rounded-full border-2 border-gray-300 mt-0.5 flex-shrink-0" />
                      <div>
                        <p className="text-sm font-medium text-foreground">Build Wishlist</p>
                        <p className="text-xs text-muted-foreground mt-0.5">Save your favorites</p>
                      </div>
                    </div>
                  </CardContent>
                </Card>

                <Card className="bg-gradient-to-br from-orange-50 to-pink-50/60 backdrop-blur-sm shadow-md border border-transparent rounded-2xl overflow-hidden">
                  <CardContent className="pt-6 text-center">
                    <Sparkles className="w-8 h-8 mx-auto mb-3" style={{ color: ACCENT_COLOR }} />
                    <h3 className="text-sm font-semibold text-foreground mb-2">Pro Tip</h3>
                    <p className="text-xs text-gray-600 leading-relaxed">
                      {!quizTaken 
                        ? "Complete your quiz to receive expert recommendations tailored to your unique preferences and lifestyle."
                        : "Rate at least 3 fragrances to enhance your recommendation accuracy by 40%."
                      }
                    </p>
                  </CardContent>
                </Card>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}