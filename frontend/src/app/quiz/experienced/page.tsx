'use client';

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Sparkles, Search, X, ArrowRight, ArrowLeft, Star, Heart, Zap } from "lucide-react";

const ExperiencedQuiz = () => {
  const [step, setStep] = useState(1);
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState([]);
  const [selectedFragrances, setSelectedFragrances] = useState([]);
  const [searchLoading, setSearchLoading] = useState(false);
  const [recommendations, setRecommendations] = useState(null);
  const [loading, setLoading] = useState(false);
  const [userId, setUserId] = useState<string | null>(null);

  // Initialize recommenders when component loads
  useEffect(() => {
    const initializeRecommenders = async () => {
      try {
        const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
        console.log('Initializing recommenders...');
        
        const response = await fetch(`${API_URL}/api/v1/recommendations/debug/initialize`, {
          method: 'POST',
        });
        
        if (response.ok) {
          console.log('Recommenders initialized successfully');
        } else {
          console.warn('Failed to initialize recommenders:', response.status);
        }
      } catch (error) {
        console.error('Failed to initialize recommenders:', error);
      }
    };
    
    initializeRecommenders();
  }, []);
  useEffect(() => {
    const getUserId = async () => {
      const token = localStorage.getItem('access_token');
      if (!token) return;

      try {
        const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
        const response = await fetch(`${API_URL}/api/v1/auth/me`, {
          headers: {
            'Authorization': `Bearer ${token}`,
          },
        });
        
        if (response.ok) {
          const userData = await response.json();
          setUserId(userData.id);
          console.log(' User authenticated:', userData.id);
        }
      } catch (error) {
        console.error('Failed to get user:', error);
      }
    };
    
    getUserId();
  }, []);
  const searchFragrances = async (query) => {
    if (!query.trim() || query.length < 2) {
      setSearchResults([]);
      return;
    }

    setSearchLoading(true);
    try {
      const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
      // FIXED: Use autocomplete endpoint for better UX
      const response = await fetch(`${API_URL}/api/v1/recommendations/autocomplete?q=${encodeURIComponent(query)}&limit=10`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      });
      
      if (response.ok) {
        const data = await response.json();
        // FIXED: The response is directly an array, not data.fragrances
        setSearchResults(Array.isArray(data) ? data : []);
      } else {
        console.error('Search failed:', response.status);
        setSearchResults([]);
      }
    } catch (error) {
      console.error('Search error:', error);
      setSearchResults([]);
    } finally {
      setSearchLoading(false);
    }
  };

  const handleSearchInput = (e) => {
    const value = e.target.value;
    setSearchQuery(value);
    
    // Debounce search
    clearTimeout(window.searchTimeout);
    window.searchTimeout = setTimeout(() => {
      searchFragrances(value);
    }, 300);
  };

  const addFragrance = (fragrance) => {
    if (!selectedFragrances.find(f => f.id === fragrance.id)) {
      setSelectedFragrances([...selectedFragrances, fragrance]);
      setSearchQuery('');
      setSearchResults([]);
    }
  };

  const removeFragrance = (fragranceId) => {
    setSelectedFragrances(selectedFragrances.filter(f => f.id !== fragranceId));
  };

  const getSimilarRecommendations = async () => {
  if (selectedFragrances.length === 0) return;
  
  setLoading(true);
  try {
    const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
    
    console.log('Getting similar fragrances for:', selectedFragrances.map(f => f.id));
    
    // 1. Get recommendations
    const requestBody = {
      target_fragrance_ids: selectedFragrances.length === 1 
        ? selectedFragrances[0].id
        : selectedFragrances.map(f => f.id),
      limit: 10
    };
    
    console.log('Request body:', requestBody);
    
    const response = await fetch(`${API_URL}/api/v1/recommendations/similarity`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(requestBody)
    });
    
    console.log('Response status:', response.status);
    
    if (!response.ok) {
      const errorText = await response.text();
      console.error('Error response:', errorText);
      throw new Error(`API request failed: ${response.status} - ${errorText}`);
    }
    
    const data = await response.json();
    console.log('Success response:', data);
    setRecommendations(data);
    
    // 2. AUTO-SAVE OWNED FRAGRANCES (ADD THIS)
    if (userId) {
      await saveOwnedFragrances(userId);
    } else {
      console.warn(' No user ID - skipping fragrance save');
    }
    
    setStep(4);
  } catch (error) {
    console.error('Full error getting recommendations:', error);
    alert(`Error: ${error.message}`);
  } finally {
    setLoading(false);
  }
};


const saveOwnedFragrances = async (userId: string) => {
  try {
    const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
    const token = localStorage.getItem('access_token');
    
    console.log(' Saving owned fragrances for user:', userId);
    
    const response = await fetch(`${API_URL}/api/v1/recommendations/save-owned-fragrances`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`,
      },
      body: JSON.stringify({
        user_id: userId,
        fragrance_ids: selectedFragrances.map(f => f.id)
      })
    });
    
    if (response.ok) {
      const result = await response.json();
      console.log(` Saved ${result.items_saved} fragrances to collection`);
      //  Show a subtle success message to user
    } else {
      const errorText = await response.text();
      console.warn(' Failed to save fragrances:', response.status, errorText);
    }
  } catch (error) {
    console.error(' Error saving fragrances:', error);
    // Don't block user experience if save fails
  }
};

  if (loading) {
    return (
      <div className="min-h-screen bg-background relative overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-br from-purple-500/5 via-pink-500/5 to-orange-500/5" />
        <div className="relative z-10 flex items-center justify-center min-h-screen">
          <div className="text-center">
            <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-gradient-to-r from-purple-600 to-pink-600 mb-6 animate-pulse">
              <Zap className="w-8 h-8 text-white" />
            </div>
            <h2 className="text-2xl font-medium text-foreground mb-2">Finding Your Matches</h2>
            <p className="text-muted-foreground">Analyzing similarity patterns...</p>
          </div>
        </div>
      </div>
    );
  }

  if (step === 4 && recommendations) {
    return (
      <div className="min-h-screen bg-background relative overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-br from-purple-500/5 via-pink-500/5 to-orange-500/5" />
        <div className="relative z-10 p-6">
          <div className="max-w-4xl mx-auto">
            <div className="text-center mb-8">
              <h1 className="text-3xl font-medium mb-4 text-foreground">Similar Fragrances</h1>
              {/* FIXED: Handle both single and multiple target fragrances */}
              <p className="text-muted-foreground">
                {recommendations.analysis_type === 'single' ? (
                  <>Based on "{recommendations.target_fragrances[0].name}" by {recommendations.target_fragrances[0].brand}</>
                ) : (
                  <>Based on your collection of {recommendations.target_fragrances.length} fragrances</>
                )}
              </p>
              {recommendations.analysis_type === 'collection' && (
                <div className="mt-2 text-sm text-muted-foreground">
                  Collection: {recommendations.target_fragrances.map(f => f.name).join(', ')}
                </div>
              )}
            </div>
            
            <div className="grid gap-6">
              {recommendations.recommendations.map((rec) => (
                <Card key={rec.fragrance.id} className="border-2 border-purple-100 hover:border-purple-200 hover:shadow-lg transition-all duration-200">
                  <CardContent className="p-6">
                    <div className="flex justify-between items-start mb-4">
                      <div>
                        <h3 className="text-xl font-medium text-foreground">{rec.fragrance.name}</h3>
                        <p className="text-muted-foreground">{rec.fragrance.brand}</p>
                        <div className="flex items-center gap-2 mt-2">
                          <div className="flex items-center">
                            <Star className="w-4 h-4 text-yellow-500 fill-current" />
                            <span className="text-sm text-muted-foreground ml-1">
                              {rec.fragrance.avg_rating}/5 ({rec.fragrance.num_ratings} reviews)
                            </span>
                          </div>
                        </div>
                      </div>
                      <div className="text-right">
                        <div className="text-2xl font-bold text-purple-600">#{rec.rank}</div>
                        <div className="text-sm text-muted-foreground">{Math.round(rec.score * 100)}% similar</div>
                      </div>
                    </div>
                    
                    <div className="mb-4">
                      <p className="text-foreground mb-2">{rec.explanation.primary_reason}</p>
                      {rec.explanation.quality_note && (
                        <p className="text-sm text-green-600">{rec.explanation.quality_note}</p>
                      )}
                    </div>
                    
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
                      <div>
                        <h4 className="font-medium text-foreground mb-2">Top Notes</h4>
                        <p className="text-muted-foreground">{rec.fragrance.top_notes.join(', ') || 'Not specified'}</p>
                      </div>
                      <div>
                        <h4 className="font-medium text-foreground mb-2">Heart Notes</h4>
                        <p className="text-muted-foreground">{rec.fragrance.middle_notes.join(', ') || 'Not specified'}</p>
                      </div>
                      <div>
                        <h4 className="font-medium text-foreground mb-2">Base Notes</h4>
                        <p className="text-muted-foreground">{rec.fragrance.base_notes.join(', ') || 'Not specified'}</p>
                      </div>
                    </div>
                    
                    {rec.fragrance.accords.length > 0 && (
                      <div className="mt-4">
                        <h4 className="font-medium text-foreground mb-2">Fragrance Family</h4>
                        <div className="flex flex-wrap gap-2">
                          {rec.fragrance.accords.map((accord) => (
                            <Badge key={accord} variant="secondary" className="bg-purple-100 text-purple-700">
                              {accord}
                            </Badge>
                          ))}
                        </div>
                      </div>
                    )}
                  </CardContent>
                </Card>
              ))}
            </div>
            
            <div className="text-center mt-8">
              <Button onClick={() => { setStep(1); setSelectedFragrances([]); setRecommendations(null); }} 
                      variant="outline" 
                      className="rounded-full">
                Try Different Fragrances
              </Button>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background relative overflow-hidden">
      <div className="absolute inset-0 bg-gradient-to-br from-purple-500/5 via-pink-500/5 to-orange-500/5" />
      <div className="absolute top-20 left-20 w-96 h-96 bg-purple-400/10 rounded-full blur-3xl animate-pulse" />
      <div className="absolute bottom-20 right-20 w-96 h-96 bg-pink-400/10 rounded-full blur-3xl animate-pulse" style={{ animationDelay: '1s' }} />
      
      <div className="relative z-10 p-6">
        <div className="max-w-4xl mx-auto">
          {/* Progress indicator */}
          <div className="flex justify-center mb-8">
            <div className="flex items-center space-x-4">
              {[1, 2, 3].map((stepNum) => (
                <div key={stepNum} className="flex items-center">
                  <div className={`w-10 h-10 rounded-full flex items-center justify-center text-sm font-medium transition-all duration-300 ${
                    step >= stepNum 
                      ? 'bg-gradient-to-r from-purple-600 to-pink-600 text-white' 
                      : 'bg-muted text-muted-foreground'
                  }`}>
                    {stepNum}
                  </div>
                  {stepNum < 3 && (
                    <div className={`w-16 h-0.5 mx-2 transition-all duration-300 ${
                      step > stepNum ? 'bg-gradient-to-r from-purple-600 to-pink-600' : 'bg-muted'
                    }`} />
                  )}
                </div>
              ))}
            </div>
          </div>

          {step === 1 && (
            <Card className="border-2 border-purple-100">
              <CardHeader className="text-center">
                <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-gradient-to-r from-purple-100 to-pink-100 border-2 border-purple-200 mb-4 mx-auto">
                  <Search className="w-8 h-8 text-purple-600" />
                </div>
                <CardTitle className="text-2xl font-medium">Find New Fragrances</CardTitle>
                <p className="text-muted-foreground">
                  Tell us what you love, discover what's next
                </p>
              </CardHeader>
              <CardContent className="space-y-6">
                <div className="relative">
                  <Input
                    type="text"
                    placeholder="Search for a fragrance (e.g., Tom Ford Oud Wood, Chanel No. 5)"
                    value={searchQuery}
                    onChange={handleSearchInput}
                    className="pl-10"
                  />
                  <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-muted-foreground" />
                  
                  {searchLoading && (
                    <div className="absolute right-3 top-1/2 transform -translate-y-1/2">
                      <div className="w-4 h-4 border-2 border-purple-600 border-t-transparent rounded-full animate-spin" />
                    </div>
                  )}
                </div>
                
                {/* Search Results */}
                {searchResults.length > 0 && (
                  <div className="border border-muted rounded-lg max-h-60 overflow-y-auto">
                    {searchResults.map((fragrance) => (
                      <div
                        key={fragrance.id}
                        onClick={() => addFragrance(fragrance)}
                        className="p-3 hover:bg-purple-50 cursor-pointer border-b border-muted last:border-b-0"
                      >
                        <div className="flex justify-between items-start">
                          <div>
                            <h4 className="font-medium">{fragrance.name}</h4>
                            <p className="text-sm text-muted-foreground">{fragrance.brand}</p>
                            {fragrance.avg_rating && (
                              <div className="flex items-center mt-1">
                                <Star className="w-3 h-3 text-yellow-500 fill-current" />
                                <span className="text-xs text-muted-foreground ml-1">
                                  {fragrance.avg_rating}/5
                                </span>
                              </div>
                            )}
                          </div>
                          <Button size="sm" variant="ghost" className="text-purple-600">
                            Add
                          </Button>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
                
                {/* Selected Fragrances */}
                {selectedFragrances.length > 0 && (
                  <div className="space-y-4">
                    <h3 className="font-medium text-foreground">Your Selected Fragrances:</h3>
                    <div className="grid grid-cols-1 gap-3">
                      {selectedFragrances.map((fragrance) => (
                        <Card key={fragrance.id} className="border border-purple-200">
                          <CardContent className="p-4">
                            <div className="flex justify-between items-start">
                              <div>
                                <h4 className="font-medium">{fragrance.name}</h4>
                                <p className="text-sm text-muted-foreground">{fragrance.brand}</p>
                                <div className="flex items-center mt-2">
                                  <Heart className="w-4 h-4 text-red-500 fill-current" />
                                  <span className="text-sm text-muted-foreground ml-1">In your collection</span>
                                </div>
                              </div>
                              <Button
                                variant="ghost"
                                size="sm"
                                onClick={() => removeFragrance(fragrance.id)}
                                className="text-red-500 hover:bg-red-50"
                              >
                                <X className="w-4 h-4" />
                              </Button>
                            </div>
                          </CardContent>
                        </Card>
                      ))}
                    </div>
                  </div>
                )}

                <div className="flex justify-between pt-6">
                  <Button variant="ghost" disabled>
                    <ArrowLeft className="w-4 h-4 mr-2" />
                    Back
                  </Button>
                  <Button 
                    onClick={() => setStep(2)}
                    disabled={selectedFragrances.length === 0}
                    className="bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700"
                  >
                    Continue
                    <ArrowRight className="w-4 h-4 ml-2" />
                  </Button>
                </div>
              </CardContent>
            </Card>
          )}

          {step === 2 && (
            <Card className="border-2 border-purple-100">
              <CardHeader className="text-center">
                <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-gradient-to-r from-purple-100 to-pink-100 border-2 border-purple-200 mb-4 mx-auto">
                  <Sparkles className="w-8 h-8 text-purple-600" />
                </div>
                <CardTitle className="text-2xl font-medium">Review Your Selection</CardTitle>
                <p className="text-muted-foreground">
                  {selectedFragrances.length === 1 
                    ? "We'll find fragrances similar to your favorite"
                    : `We'll analyze your collection of ${selectedFragrances.length} fragrances`
                  }
                </p>
              </CardHeader>
              <CardContent className="space-y-6">
                <div className="grid grid-cols-1 gap-4">
                  {selectedFragrances.map((fragrance) => (
                    <Card key={fragrance.id} className="border border-purple-200 bg-purple-50/30">
                      <CardContent className="p-4">
                        <div className="flex justify-between items-center">
                          <div>
                            <h4 className="font-medium">{fragrance.name}</h4>
                            <p className="text-sm text-muted-foreground">{fragrance.brand}</p>
                          </div>
                          <div className="text-right">
                            <Heart className="w-5 h-5 text-red-500 fill-current mx-auto" />
                            <p className="text-xs text-muted-foreground mt-1">Loved</p>
                          </div>
                        </div>
                      </CardContent>
                    </Card>
                  ))}
                </div>

                <div className="text-center pt-6">
                  <Button 
                    onClick={getSimilarRecommendations}
                    size="lg"
                    className="px-8 py-3 text-lg rounded-full bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700"
                  >
                    {selectedFragrances.length === 1 ? 'Find Similar Fragrances' : 'Analyze My Collection'}
                    <Sparkles className="w-5 h-5 ml-2" />
                  </Button>
                </div>

                <div className="flex justify-between pt-4">
                  <Button variant="ghost" onClick={() => setStep(1)}>
                    <ArrowLeft className="w-4 h-4 mr-2" />
                    Back
                  </Button>
                </div>
              </CardContent>
            </Card>
          )}
        </div>
      </div>
    </div>
  );
};

export default ExperiencedQuiz;