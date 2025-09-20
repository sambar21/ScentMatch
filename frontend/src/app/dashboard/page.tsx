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
  Play
} from "lucide-react";
import heroImage from "@/assets/hero-luxury-perfume.jpg";

interface User {
  id: string;
  email: string;
  display_name?: string;
}

// Gradient constants (only the two you liked)
const ICON_GRADIENT = 'linear-gradient(90deg,#ff9ab3,#ffd09e)'; // profile icon gradient
const TEXT_GRADIENT = 'linear-gradient(90deg,#ff6b9a,#ffb26b)';  // welcome / CTA gradient

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
          setQuizTaken(false); // demo default
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
    { name: "Tom Ford Oud Wood", brand: "Tom Ford", match: 95, image: "🌲" },
    { name: "Creed Aventus", brand: "Creed", match: 92, image: "🍃" },
    { name: "Maison Margiela REPLICA", brand: "Maison Margiela", match: 89, image: "🔥" }
  ];

  const popularFragrances = [
    { name: "Dior Sauvage", brand: "Dior", rating: 4.8, image: "🌊" },
    { name: "Chanel Bleu de Chanel", brand: "Chanel", rating: 4.7, image: "💙" },
    { name: "Viktor & Rolf Spicebomb", brand: "Viktor & Rolf", rating: 4.6, image: "💥" },
    { name: "Paco Rabanne 1 Million", brand: "Paco Rabanne", rating: 4.5, image: "✨" }
  ];

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="flex items-center space-x-2">
          <div className="w-6 h-6 border-2" style={{ borderColor: 'rgba(255,154,179,0.25)', borderTopColor: '#ff9ab3' , borderRadius: '9999px' , animation: 'spin 1s linear infinite' }} />
          <span className="text-lg text-muted-foreground">Loading...</span>
        </div>
      </div>
    );
  }

  if (!user) return null;

  return (
    <div className="min-h-screen relative overflow-hidden">
      {/* Background: hero photo + soft neutral gradient overlay to keep landing continuity */}
      <div
        className="absolute inset-0 bg-cover bg-center opacity-28"
        style={{
          backgroundImage: `url(${heroImage})`,
          filter: 'blur(6px) saturate(110%) contrast(95%)',
          transform: 'scale(1.03)'
        }}
        aria-hidden
      />
      <div className="absolute inset-0 bg-gradient-to-br from-pink-50/85 via-rose-50/65 to-orange-50/55" aria-hidden />

      {/* Subtle icon accents using ICON_GRADIENT colors */}
      <div className="absolute top-16 left-12 z-0 animate-float">
        <div className="glass rounded-full p-3" style={{ background: 'linear-gradient(180deg, rgba(255,255,255,0.9), rgba(255,250,250,0.8))' }}>
          <Sparkles className="w-6 h-6" style={{ color: '#ff9ab3' }} />
        </div>
      </div>
      <div className="absolute bottom-12 right-12 z-0 animate-float" style={{ animationDelay: '1.2s' }}>
        <div className="glass rounded-full p-3" style={{ background: 'linear-gradient(180deg, rgba(255,255,255,0.9), rgba(255,250,250,0.8))' }}>
          <Heart className="w-5 h-5" style={{ color: '#ffd09e' }} />
        </div>
      </div>

      {/* Header */}
      <header className="relative z-10 glass border-transparent backdrop-blur-lg">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-4">
            {/* Left - Logo */}
            <div className="flex items-center space-x-3">
              <div className="w-9 h-9 rounded-full flex items-center justify-center" style={{ background: ICON_GRADIENT }}>
                <Sparkles className="w-4 h-4 text-white" />
              </div>
              <h1 className="text-2xl font-bold" style={{ background: TEXT_GRADIENT, WebkitBackgroundClip: 'text', color: 'transparent' }}>
                ScentMatch
              </h1>
            </div>

            {/* Center - Search */}
            <div className="hidden md:flex items-center max-w-md w-full mx-8">
              <div className="relative w-full">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-muted-foreground w-4 h-4" />
                <input
                  type="text"
                  placeholder="Search fragrances..."
                  className="w-full pl-10 pr-4 py-2 glass border border-transparent rounded-full focus:outline-none focus:ring-2 focus:ring-primary/30"
                />
              </div>
            </div>

            {/* Right - User & Settings */}
            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-2 glass px-3 py-2 rounded-full" style={{ background: 'linear-gradient(180deg, rgba(255,255,255,0.92), rgba(255,250,250,0.86))' }}>
                <User className="w-4 h-4" style={{ color: '#ff9ab3' }} />
                <span className="text-sm font-medium text-foreground">{user.display_name || user.email}</span>
              </div>
              <Button
                variant="outline"
                size="sm"
                className="glass border-transparent text-foreground hover:bg-white/40 rounded-full"
              >
                <Settings className="w-4 h-4" />
              </Button>
              <Button
                onClick={handleLogout}
                variant="outline"
                size="sm"
                className="glass border-transparent text-foreground hover:bg-white/40"
              >
                <LogOut className="w-4 h-4 mr-2" />
                Logout
              </Button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="relative z-10 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
          {/* LEFT SIDEBAR */}
          <div className="lg:col-span-1 space-y-6">
            <Card className="glass shadow-luxury border-transparent" style={{ background: 'linear-gradient(180deg, rgba(255,255,255,0.94), rgba(255,250,250,0.9))' }}>
              <CardHeader className="text-center">
                <div className="w-16 h-16 mx-auto rounded-full flex items-center justify-center mb-3" style={{ background: ICON_GRADIENT }}>
                  <User className="w-8 h-8 text-white" />
                </div>
                <CardTitle className="text-lg">{user.display_name || 'FragranceLover'}</CardTitle>
                <CardDescription>Account created: March 2024</CardDescription>
              </CardHeader>
            </Card>

            <Card className="glass shadow-luxury border-transparent">
              <CardHeader>
                <CardTitle className="text-sm font-semibold text-muted-foreground">Navigation</CardTitle>
              </CardHeader>
              <CardContent className="space-y-2">
                <Button variant="ghost" className="w-full justify-start bg-white/40 text-pink-700 rounded-full">
                  Dashboard
                </Button>
                <Button variant="ghost" className="w-full justify-start rounded-full">My Profile</Button>
                <Button variant="ghost" className="w-full justify-start rounded-full">Quiz Results</Button>
                <Button variant="ghost" className="w-full justify-start rounded-full">Recommendations</Button>
              </CardContent>
            </Card>

            <Card className="glass shadow-luxury border-transparent">
              <CardHeader>
                <CardTitle className="text-sm font-semibold text-muted-foreground">Quick Actions</CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                {!quizTaken ? (
                  <Button 
                    onClick={() => router.push('/quiz')}
                    className="w-full" 
                    style={{ background: TEXT_GRADIENT, color: 'white', borderRadius: 9999, padding: '0.75rem 1rem', boxShadow: 'var(--shadow-glow)' }}
                  >
                    <Play className="w-4 h-4 mr-2" />
                    Take Fragrance Quiz
                  </Button>
                ) : (
                  <Button variant="outline" className="w-full border-transparent text-foreground rounded-full">Update Preferences</Button>
                )}
              </CardContent>
            </Card>
          </div>

          {/* CENTER COLUMN */}
          <div className="lg:col-span-2 space-y-8">
            <Card className="glass shadow-luxury border-transparent">
              <CardHeader className="text-center py-8">
                <div className="inline-flex items-center justify-center w-16 h-16 rounded-full mb-4 mx-auto animate-glow" style={{ background: ICON_GRADIENT }}>
                  <Sparkles className="w-8 h-8 text-white" />
                </div>
                <CardTitle className="text-2xl font-bold" style={{ background: TEXT_GRADIENT, WebkitBackgroundClip: 'text', color: 'transparent' }}>
                  Welcome to your fragrance journey!
                </CardTitle>
                <CardDescription className="text-lg mt-2">Discover scents tailored perfectly to your unique preferences</CardDescription>
              </CardHeader>
            </Card>

            <Card className="glass shadow-luxury border-transparent">
              <CardHeader>
                <CardTitle className="text-xl font-semibold">{!quizTaken ? "Find Your Perfect Fragrance" : "Your Fragrance Profile"}</CardTitle>
              </CardHeader>
              <CardContent>
                {!quizTaken ? (
                  <div className="text-center space-y-4">
                    <CardDescription className="text-lg">Take our quick quiz to discover scents tailored to you</CardDescription>
                    <div className="bg-white/60 rounded-lg p-4 mb-6">
                      <p className="text-sm text-muted-foreground mb-2">Our quiz covers:</p>
                      <div className="flex flex-wrap gap-2 justify-center">
                        <span className="px-3 py-1 bg-white/80 rounded-full text-xs">Fragrance Families</span>
                        <span className="px-3 py-1 bg-white/80 rounded-full text-xs">Occasions</span>
                        <span className="px-3 py-1 bg-white/80 rounded-full text-xs">Intensity Preferences</span>
                      </div>
                    </div>
                    <Button 
                      onClick={() => router.push('/quiz')}
                      size="lg"
                      style={{ background: TEXT_GRADIENT, color: 'white', padding: '0.75rem 2rem', borderRadius: 9999, boxShadow: 'var(--shadow-glow)' }}
                    >
                      Start Quiz
                    </Button>
                  </div>
                ) : (
                  <div className="space-y-4">
                    <div className="flex flex-wrap gap-2">
                      {userPreferences.map((pref, index) => (
                        <span key={index} className="px-3 py-1" style={{ background: 'rgba(255,240,250,0.9)', color: '#b84a2f', borderRadius: 9999 }}>
                          {pref}
                        </span>
                      ))}
                    </div>
                    <Button variant="outline" className="border-transparent text-foreground rounded-full">Retake Quiz</Button>
                  </div>
                )}
              </CardContent>
            </Card>

            <Card className="glass shadow-luxury border-transparent">
              <CardHeader>
                <CardTitle className="text-xl font-semibold">{!quizTaken ? "Your Recommendations" : "Recommended for You"}</CardTitle>
              </CardHeader>
              <CardContent>
                {!quizTaken ? (
                  <div className="text-center space-y-4">
                    <CardDescription>Complete your quiz to see personalized recommendations</CardDescription>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4 opacity-60">
                      {[1, 2].map((item) => (
                        <div key={item} className="glass border-transparent rounded-lg p-4">
                          <div className="text-2xl mb-2">🌸</div>
                          <div className="text-sm font-medium text-muted-foreground">Sample Fragrance</div>
                          <div className="text-xs text-muted-foreground">Luxury Brand</div>
                        </div>
                      ))}
                    </div>
                  </div>
                ) : (
                  <div className="space-y-4">
                    <div className="flex items-center justify-between">
                      <div>
                        <Button variant="ghost" size="sm" onClick={() => setCurrentSlide(Math.max(0, currentSlide - 1))} disabled={currentSlide === 0} className="border-transparent">
                          <ChevronLeft className="w-4 h-4" />
                        </Button>
                      </div>
                      <div>
                        <Button variant="ghost" size="sm" onClick={() => setCurrentSlide(Math.min(recommendedFragrances.length - 1, currentSlide + 1))} disabled={currentSlide >= recommendedFragrances.length - 1} className="border-transparent">
                          <ChevronRight className="w-4 h-4" />
                        </Button>
                      </div>
                    </div>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      {recommendedFragrances.slice(currentSlide, currentSlide + 2).map((fragrance, index) => (
                        <div key={index} className="glass border-transparent rounded-lg p-4 hover:shadow-glow transition">
                          <div className="text-2xl mb-2">{fragrance.image}</div>
                          <div className="text-sm font-medium">{fragrance.name}</div>
                          <div className="text-xs text-muted-foreground mb-2">{fragrance.brand}</div>
                          <div className="flex items-center gap-1">
                            <Heart className="w-3 h-3" style={{ color: '#ff9ab3' }} />
                            <span className="text-xs" style={{ color: '#ff6b9a' }}>{fragrance.match}% match</span>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>

            <Card className="glass shadow-luxury border-transparent">
              <CardHeader>
                <CardTitle className="text-xl font-semibold">Popular Fragrances</CardTitle>
                <CardDescription>Trending choices from our community</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  {popularFragrances.map((fragrance, index) => (
                    <div key={index} className="glass border-transparent rounded-lg p-3 text-center hover:shadow-glow transition">
                      <div className="text-xl mb-2">{fragrance.image}</div>
                      <div className="text-xs font-medium truncate">{fragrance.name}</div>
                      <div className="text-xs text-muted-foreground truncate">{fragrance.brand}</div>
                      <div className="flex items-center justify-center gap-1 mt-1">
                        <Star className="w-3 h-3 text-yellow-400" />
                        <span className="text-xs">{fragrance.rating}</span>
                      </div>
                    </div>
                  ))}
                </div>
                <div className="text-center mt-4">
                  <Button variant="outline" className="border-transparent text-foreground rounded-full">See more popular choices</Button>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* RIGHT SIDEBAR */}
          <div className="lg:col-span-1 space-y-6">
            <Card className="glass shadow-luxury border-transparent">
              <CardHeader>
                <CardTitle className="text-sm font-semibold text-muted-foreground">Getting Started</CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <div className="flex items-center gap-3">
                  <CheckCircle className="w-4 h-4 text-green-500" />
                  <span className="text-sm">Account created</span>
                </div>
                <div className="flex items-center gap-3">
                  {quizTaken ? <CheckCircle className="w-4 h-4 text-green-500" /> : <Clock className="w-4 h-4" />}
                  <span className="text-sm">Take preference quiz</span>
                </div>
                <div className="flex items-center gap-3">
                  <Clock className="w-4 h-4 text-gray-400" />
                  <span className="text-sm">Rate your first fragrance</span>
                </div>
                <div className="flex items-center gap-3">
                  <Clock className="w-4 h-4 text-gray-400" />
                  <span className="text-sm">Explore recommendations</span>
                </div>
              </CardContent>
            </Card>

            <Card className="glass shadow-luxury border-transparent">
              <CardHeader>
                <CardTitle className="text-sm font-semibold text-muted-foreground">Your Activity</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="text-center">
                  <div className="text-2xl font-bold" style={{ color: '#ff6b9a' }}>{quizTaken ? 12 : 0}</div>
                  <div className="text-xs text-muted-foreground">Fragrances explored</div>
                </div>
                <div className="text-center">
                  <div className="text-sm">Quiz completed: <span className="font-medium" style={{ color: '#ff6b9a' }}>{quizTaken ? 'Yes' : 'No'}</span></div>
                </div>
                <div className="text-center">
                  <div className="text-xs text-muted-foreground">Last activity: 2 hours ago</div>
                </div>
              </CardContent>
            </Card>

            <Card className="glass shadow-luxury border-transparent">
              <CardHeader>
                <CardTitle className="text-sm font-semibold text-muted-foreground">Next Steps</CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                {!quizTaken ? (
                  <>
                    <p className="text-sm text-muted-foreground">Complete your quiz for better recommendations</p>
                    <p className="text-sm text-muted-foreground">Explore popular fragrances while you decide</p>
                  </>
                ) : (
                  <>
                    <p className="text-sm text-muted-foreground">Rate recommended fragrances</p>
                    <p className="text-sm text-muted-foreground">Build your fragrance wishlist</p>
                  </>
                )}
              </CardContent>
            </Card>
          </div>
        </div>
      </main>
    </div>
  );
}
