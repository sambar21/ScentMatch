'use client';
import { Slider } from "@/components/ui/slider"
import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Sparkles, Plus, X, ArrowRight, ArrowLeft, Lightbulb, Star } from "lucide-react";

const BeginnerQuiz = () => {
  const [step, setStep] = useState(1);
  const [notePreferences, setNotePreferences] = useState([]);
  const [accordPreferences, setAccordPreferences] = useState([]);
  const [currentNote, setCurrentNote] = useState('');
  const [currentAccord, setCurrentAccord] = useState('');
  const [recommendations, setRecommendations] = useState(null);
  const [loading, setLoading] = useState(false);

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
        // Don't show error to user - this is background initialization
      }
    };
    
    initializeRecommenders();
  }, []);

  // Common fragrance notes for suggestions
  const suggestedNotes = [
    'vanilla', 'bergamot', 'rose', 'jasmine', 'cedar', 'sandalwood', 'lavender',
    'lemon', 'orange', 'patchouli', 'musk', 'amber', 'oud', 'tobacco', 'vetiver',
    'iris', 'peony', 'ylang-ylang', 'cardamom', 'black pepper', 'ginger',
    'frankincense', 'oakmoss', 'tonka bean', 'white tea', 'mint', 'eucalyptus'
  ];

  // Common accords/fragrance families
  const suggestedAccords = [
    'woody', 'fresh', 'floral', 'oriental', 'citrus', 'spicy', 'aquatic',
    'fruity', 'gourmand', 'powdery', 'green', 'smoky', 'sweet', 'clean',
    'warm spicy', 'aromatic', 'earthy', 'musky', 'balsamic', 'herbal'
  ];

  const addNote = (note, importance) => {
    if (note.trim() && !notePreferences.find(p => p.name.toLowerCase() === note.toLowerCase())) {
      setNotePreferences([...notePreferences, { name: note.trim().toLowerCase(), importance }]);
      setCurrentNote('');
    }
  };

  const addAccord = (accord, importance) => {
    if (accord.trim() && !accordPreferences.find(p => p.name.toLowerCase() === accord.toLowerCase())) {
      setAccordPreferences([...accordPreferences, { name: accord.trim().toLowerCase(), importance }]);
      setCurrentAccord('');
    }
  };

  const removeNote = (index) => {
    setNotePreferences(notePreferences.filter((_, i) => i !== index));
  };

  const removeAccord = (index) => {
    setAccordPreferences(accordPreferences.filter((_, i) => i !== index));
  };

  const updateImportance = (type, index, importance) => {
    if (type === 'note') {
      const updated = [...notePreferences];
      updated[index].importance = importance;
      setNotePreferences(updated);
    } else {
      const updated = [...accordPreferences];
      updated[index].importance = importance;
      setAccordPreferences(updated);
    }
  };

  const getRecommendations = async () => {
    setLoading(true);
    try {
      const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
      console.log('Making request to:', `${API_URL}/recommendations/note-based`);
      console.log('Request body:', {
        preferred_notes: notePreferences,
        preferred_accords: accordPreferences,
        limit: 10
      });
      
      const response = await fetch(`${API_URL}/api/v1/recommendations/note-based`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          preferred_notes: notePreferences,
          preferred_accords: accordPreferences,
          limit: 10
        })
      });
      
      console.log('Response status:', response.status);
      console.log('Response ok:', response.ok);
      
      if (!response.ok) {
        const errorText = await response.text();
        console.error('Error response:', errorText);
        throw new Error(`API request failed: ${response.status} - ${errorText}`);
      }
      
      const data = await response.json();
      console.log('Success response:', data);
      setRecommendations(data);
      setStep(4);
    } catch (error) {
      console.error('Full error getting recommendations:', error);
      alert(`Error: ${error.message}`); // Temporary alert for debugging
      // Handle error state - for now just stay on current step
    } finally {
      setLoading(false);
    }
  };

  

  const ImportanceSlider = ({ value, onChange }) => (
    <div className="space-y-2">
      <div className="flex justify-between text-xs text-muted-foreground">
        <span>Dislike</span>
        <span className="font-medium">{value}/10</span>
        <span>Love</span>
      </div>

    <Slider
  value={[value]}
  min={1}
  max={10}
  step={1}
  onValueChange={(v) => onChange(v[0])}
/>
    </div>
  )


  const PreferenceCard = ({ item, index, type, onRemove, onUpdateImportance }) => (
    <Card className="glass border-primary/20 relative group">
      <CardContent className="p-4">
        <div className="flex justify-between items-start mb-3">
          <h4 className="font-medium capitalize text-foreground">{item.name}</h4>
          <Button
            variant="ghost"
            size="sm"
            onClick={() => onRemove(index)}
            className="opacity-0 group-hover:opacity-100 transition-opacity h-6 w-6 p-0 hover:bg-red-100"
          >
            <X className="h-3 w-3 text-red-500" />
          </Button>
        </div>
        <ImportanceSlider
          value={item.importance}
          onChange={(importance) => onUpdateImportance(type, index, importance)}
          label={item.name}
        />
      </CardContent>
    </Card>
  );

  if (loading) {
    return (
      <div className="min-h-screen bg-background relative overflow-hidden">
        <div className="absolute inset-0 bg-gradient-primary opacity-5" />
        <div className="relative z-10 flex items-center justify-center min-h-screen">
          <div className="text-center">
            <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-gradient-primary mb-6 animate-spin">
              <Sparkles className="w-8 h-8 text-primary-foreground" />
            </div>
            <h2 className="text-2xl font-medium text-foreground mb-2">Analyzing Your Preferences</h2>
            <p className="text-muted-foreground">Finding your perfect fragrance matches...</p>
          </div>
        </div>
      </div>
    );
  }

  if (step === 4 && recommendations) {
    return (
      <div className="min-h-screen bg-background relative overflow-hidden">
        <div className="absolute inset-0 bg-gradient-primary opacity-5" />
        <div className="relative z-10 p-6">
          <div className="max-w-4xl mx-auto">
            <div className="text-center mb-8">
              <h1 className="text-3xl font-medium mb-4 text-foreground">Your Fragrance Recommendations</h1>
              <p className="text-muted-foreground">Based on your preferences, here are your top matches</p>
            </div>
            
            <div className="grid gap-6">
              {recommendations.recommendations.map((rec) => (
                <Card key={rec.fragrance.id} className="glass border-primary/20 hover:shadow-luxury transition-luxury">
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
                        <div className="text-2xl font-bold text-primary">#{rec.rank}</div>
                        <div className="text-sm text-muted-foreground">{Math.round(rec.score * 100)}% match</div>
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
                            <span key={accord} className="px-3 py-1 bg-primary/10 text-primary rounded-full text-xs">
                              {accord}
                            </span>
                          ))}
                        </div>
                      </div>
                    )}
                  </CardContent>
                </Card>
              ))}
            </div>
            
            <div className="text-center mt-8">
              <Button onClick={() => setStep(1)} variant="glass" className="rounded-full">
                Try Different Preferences
              </Button>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background relative overflow-hidden">
      <div className="absolute inset-0 bg-gradient-primary opacity-5" />
      <div className="absolute top-20 left-20 w-96 h-96 bg-primary/10 rounded-full blur-3xl animate-pulse" />
      <div className="absolute bottom-20 right-20 w-96 h-96 bg-secondary/10 rounded-full blur-3xl animate-pulse" style={{ animationDelay: '1s' }} />
      
      <div className="relative z-10 p-6">
        <div className="max-w-4xl mx-auto">
          {/* Progress indicator */}
          <div className="flex justify-center mb-8">
            <div className="flex items-center space-x-4">
              {[1, 2, 3].map((stepNum) => (
                <div key={stepNum} className="flex items-center">
                  <div className={`w-10 h-10 rounded-full flex items-center justify-center text-sm font-medium transition-luxury ${
                    step >= stepNum 
                      ? 'bg-gradient-primary text-primary-foreground' 
                      : 'bg-muted text-muted-foreground'
                  }`}>
                    {stepNum}
                  </div>
                  {stepNum < 3 && (
                    <div className={`w-16 h-0.5 mx-2 transition-luxury ${
                      step > stepNum ? 'bg-primary' : 'bg-muted'
                    }`} />
                  )}
                </div>
              ))}
            </div>
          </div>

          {step === 1 && (
            <Card className="glass border-primary/20">
              <CardHeader className="text-center">
                <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-gradient-primary/10 border border-primary/20 mb-4 mx-auto">
                  <Lightbulb className="w-8 h-8 text-primary" />
                </div>
                <CardTitle className="text-2xl font-medium">Tell Us About Scents You Like</CardTitle>
                <p className="text-muted-foreground">
                  Add specific notes or ingredients you're drawn to. Think vanilla, rose, cedar, etc.
                </p>
              </CardHeader>
              <CardContent className="space-y-6">
                <div>
                  <div className="flex gap-2 mb-4">
                    <input
                      type="text"
                      placeholder="Type a fragrance note (e.g., vanilla, rose, cedar)"
                      value={currentNote}
                      onChange={(e) => setCurrentNote(e.target.value)}
                      onKeyPress={(e) => e.key === 'Enter' && addNote(currentNote, 7)}
                      className="flex-1 px-4 py-2 border border-primary/20 rounded-lg bg-background/50 focus:outline-none focus:border-primary"
                    />
                    <Button 
                      onClick={() => addNote(currentNote, 7)}
                      disabled={!currentNote.trim()}
                      className="px-6"
                    >
                      <Plus className="w-4 h-4" />
                    </Button>
                  </div>
                  
                  <div className="mb-4">
                    <p className="text-sm text-muted-foreground mb-2">Quick suggestions:</p>
                    <div className="flex flex-wrap gap-2">
                      {suggestedNotes.slice(0, 12).map((note) => (
                        <Button
                          key={note}
                          variant="ghost"
                          size="sm"
                          onClick={() => addNote(note, 7)}
                          className="text-xs border border-primary/20 hover:bg-primary/10"
                          disabled={notePreferences.find(p => p.name === note)}
                        >
                          {note}
                        </Button>
                      ))}
                    </div>
                  </div>
                </div>

                {notePreferences.length > 0 && (
                  <div className="space-y-4">
                    <h3 className="font-medium text-foreground">Your Note Preferences:</h3>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      {notePreferences.map((pref, index) => (
                        <PreferenceCard
                          key={`note-${index}`}
                          item={pref}
                          index={index}
                          type="note"
                          onRemove={removeNote}
                          onUpdateImportance={updateImportance}
                        />
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
                    disabled={notePreferences.length === 0}
                  >
                    Next: Fragrance Styles
                    <ArrowRight className="w-4 h-4 ml-2" />
                  </Button>
                </div>
              </CardContent>
            </Card>
          )}

          {step === 2 && (
            <Card className="glass border-primary/20">
              <CardHeader className="text-center">
                <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-gradient-primary/10 border border-primary/20 mb-4 mx-auto">
                  <Sparkles className="w-8 h-8 text-primary" />
                </div>
                <CardTitle className="text-2xl font-medium">What Fragrance Styles Appeal to You?</CardTitle>
                <p className="text-muted-foreground">
                  Add fragrance families or styles you enjoy. Think woody, fresh, floral, etc.
                </p>
              </CardHeader>
              <CardContent className="space-y-6">
                <div>
                  <div className="flex gap-2 mb-4">
                    <input
                      type="text"
                      placeholder="Type a fragrance style (e.g., woody, fresh, floral)"
                      value={currentAccord}
                      onChange={(e) => setCurrentAccord(e.target.value)}
                      onKeyPress={(e) => e.key === 'Enter' && addAccord(currentAccord, 7)}
                      className="flex-1 px-4 py-2 border border-primary/20 rounded-lg bg-background/50 focus:outline-none focus:border-primary"
                    />
                    <Button 
                      onClick={() => addAccord(currentAccord, 7)}
                      disabled={!currentAccord.trim()}
                      className="px-6"
                    >
                      <Plus className="w-4 h-4" />
                    </Button>
                  </div>
                  
                  <div className="mb-4">
                    <p className="text-sm text-muted-foreground mb-2">Popular styles:</p>
                    <div className="flex flex-wrap gap-2">
                      {suggestedAccords.slice(0, 12).map((accord) => (
                        <Button
                          key={accord}
                          variant="ghost"
                          size="sm"
                          onClick={() => addAccord(accord, 7)}
                          className="text-xs border border-primary/20 hover:bg-primary/10"
                          disabled={accordPreferences.find(p => p.name === accord)}
                        >
                          {accord}
                        </Button>
                      ))}
                    </div>
                  </div>
                </div>

                {accordPreferences.length > 0 && (
                  <div className="space-y-4">
                    <h3 className="font-medium text-foreground">Your Style Preferences:</h3>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      {accordPreferences.map((pref, index) => (
                        <PreferenceCard
                          key={`accord-${index}`}
                          item={pref}
                          index={index}
                          type="accord"
                          onRemove={removeAccord}
                          onUpdateImportance={updateImportance}
                        />
                      ))}
                    </div>
                  </div>
                )}

                <div className="flex justify-between pt-6">
                  <Button variant="ghost" onClick={() => setStep(1)}>
                    <ArrowLeft className="w-4 h-4 mr-2" />
                    Back
                  </Button>
                  <Button onClick={() => setStep(3)}>
                    Review & Get Recommendations
                    <ArrowRight className="w-4 h-4 ml-2" />
                  </Button>
                </div>
              </CardContent>
            </Card>
          )}

          {step === 3 && (
            <Card className="glass border-primary/20">
              <CardHeader className="text-center">
                <CardTitle className="text-2xl font-medium">Review Your Preferences</CardTitle>
                <p className="text-muted-foreground">
                  Ready to discover your perfect fragrance matches?
                </p>
              </CardHeader>
              <CardContent className="space-y-6">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                  <div>
                    <h3 className="font-medium text-foreground mb-4">Notes You Like ({notePreferences.length})</h3>
                    <div className="space-y-2">
                      {notePreferences.map((pref, index) => (
                        <div key={index} className="flex justify-between items-center p-2 bg-primary/5 rounded">
                          <span className="capitalize">{pref.name}</span>
                          <span className="text-sm text-muted-foreground">{pref.importance}/10</span>
                        </div>
                      ))}
                    </div>
                  </div>
                  
                  <div>
                    <h3 className="font-medium text-foreground mb-4">Styles You Like ({accordPreferences.length})</h3>
                    <div className="space-y-2">
                      {accordPreferences.map((pref, index) => (
                        <div key={index} className="flex justify-between items-center p-2 bg-primary/5 rounded">
                          <span className="capitalize">{pref.name}</span>
                          <span className="text-sm text-muted-foreground">{pref.importance}/10</span>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>

                <div className="text-center pt-6">
                  <Button 
                    onClick={getRecommendations}
                    size="lg"
                    className="px-8 py-3 text-lg rounded-full"
                    disabled={notePreferences.length === 0 && accordPreferences.length === 0}
                  >
                    Get My Fragrance Recommendations
                    <Sparkles className="w-5 h-5 ml-2" />
                  </Button>
                </div>

                <div className="flex justify-between pt-4">
                  <Button variant="ghost" onClick={() => setStep(2)}>
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

export default BeginnerQuiz;