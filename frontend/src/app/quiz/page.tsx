'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Sparkles, User, Package, ArrowRight, Brain, Target } from "lucide-react";

export default function QuizEntry() {
  const router = useRouter();

  return (
    <div className="min-h-screen relative overflow-hidden bg-background">
      {/* Background Effects */}
      <div className="absolute inset-0 bg-gradient-primary opacity-5" />
      <div className="absolute top-20 left-20 w-96 h-96 bg-primary/10 rounded-full blur-3xl animate-pulse" />
      <div className="absolute bottom-20 right-20 w-96 h-96 bg-secondary/10 rounded-full blur-3xl animate-pulse" style={{ animationDelay: '1s' }} />
      
      <div className="relative z-10 flex items-center justify-center min-h-screen p-6">
        <div className="max-w-4xl mx-auto">
          {/* Header */}
          <div className="text-center mb-12">
            <div className="inline-flex items-center justify-center w-20 h-20 rounded-full bg-gradient-primary mb-8 animate-glow">
              <Sparkles className="w-10 h-10 text-primary-foreground" />
            </div>
            <h1 className="text-4xl md:text-5xl font-light mb-6 text-foreground">
              Discover Your <span className="bg-gradient-primary bg-clip-text text-transparent font-medium">Perfect Fragrance</span>
            </h1>
            <p className="text-lg text-muted-foreground max-w-2xl mx-auto leading-relaxed">
              Choose your personalized path to fragrance discovery
            </p>
          </div>

          {/* Collection Status Selection */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-12">
            <Card 
              className="glass border-primary/20 hover:shadow-luxury transition-luxury cursor-pointer group relative overflow-hidden"
              onClick={() => router.push('/quiz/beginner')}
            >
              {/* Card background effect */}
              <div className="absolute inset-0 bg-gradient-primary/5 opacity-0 group-hover:opacity-100 transition-luxury" />
              
              <CardHeader className="relative z-10 text-center py-10 px-8">
                <div className="inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-gradient-primary/10 border border-primary/20 mb-6 mx-auto group-hover:bg-gradient-primary/20 group-hover:scale-110 transition-luxury">
                  <User className="w-8 h-8 text-primary" />
                </div>
                <CardTitle className="text-2xl font-medium mb-3 text-foreground">I'm New to Fragrances</CardTitle>
                <p className="text-sm text-muted-foreground mb-6">
                  Perfect if you're just starting your fragrance journey
                </p>
                <CardContent className="px-0">
                  <p className="text-muted-foreground mb-6 leading-relaxed">
                    Help us understand your scent preferences through notes and aromas you love
                  </p>
                  <div className="space-y-3 text-left">
                    <div className="flex items-center gap-3 text-sm text-muted-foreground">
                      <div className="w-2 h-2 bg-primary rounded-full" />
                      Rate different fragrance notes and families
                    </div>
                    <div className="flex items-center gap-3 text-sm text-muted-foreground">
                      <div className="w-2 h-2 bg-secondary rounded-full" />
                      Explore scent profiles you're drawn to
                    </div>
                    <div className="flex items-center gap-3 text-sm text-muted-foreground">
                      <div className="w-2 h-2 bg-accent rounded-full" />
                      Get beginner-friendly recommendations
                    </div>
                  </div>
                  <div className="mt-6 flex items-center justify-center">
                    <Button variant="ghost" size="sm" className="group-hover:bg-primary/10 transition-luxury">
                      Start Quiz
                      <ArrowRight className="w-4 h-4 ml-2 group-hover:translate-x-1 transition-transform" />
                    </Button>
                  </div>
                </CardContent>
              </CardHeader>
            </Card>

            <Card 
              className="glass border-primary/20 hover:shadow-luxury transition-luxury cursor-pointer group relative overflow-hidden"
              onClick={() => router.push('/quiz/experienced')}
            >
              {/* Card background effect */}
              <div className="absolute inset-0 bg-gradient-primary/5 opacity-0 group-hover:opacity-100 transition-luxury" />
              
              <CardHeader className="relative z-10 text-center py-10 px-8">
                <div className="inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-gradient-primary/10 border border-primary/20 mb-6 mx-auto group-hover:bg-gradient-primary/20 group-hover:scale-110 transition-luxury">
                  <Package className="w-8 h-8 text-primary" />
                </div>
                <CardTitle className="text-2xl font-medium mb-3 text-foreground">I Own Fragrances</CardTitle>
                <p className="text-sm text-muted-foreground mb-6">
                  Ideal if you want to expand your current collection
                </p>
                <CardContent className="px-0">
                  <p className="text-muted-foreground mb-6 leading-relaxed">
                    Share your current collection so we can recommend complementary scents
                  </p>
                  <div className="space-y-3 text-left">
                    <div className="flex items-center gap-3 text-sm text-muted-foreground">
                      <div className="w-2 h-2 bg-primary rounded-full" />
                      Input your existing fragrance collection
                    </div>
                    <div className="flex items-center gap-3 text-sm text-muted-foreground">
                      <div className="w-2 h-2 bg-secondary rounded-full" />
                      Discover gaps in your collection
                    </div>
                    <div className="flex items-center gap-3 text-sm text-muted-foreground">
                      <div className="w-2 h-2 bg-accent rounded-full" />
                      Find complementary fragrances
                    </div>
                  </div>
                  <div className="mt-6 flex items-center justify-center">
                    <Button variant="ghost" size="sm" className="group-hover:bg-primary/10 transition-luxury">
                      Start Quiz
                      <ArrowRight className="w-4 h-4 ml-2 group-hover:translate-x-1 transition-transform" />
                    </Button>
                  </div>
                </CardContent>
              </CardHeader>
            </Card>
          </div>

          {/* Additional Info Section */}
          <div className="glass rounded-3xl p-8 mb-8">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-8 text-center">
              <div className="flex flex-col items-center">
                <div className="inline-flex items-center justify-center w-12 h-12 rounded-2xl bg-gradient-primary/10 border border-primary/20 mb-4">
                  <Brain className="w-6 h-6 text-primary" />
                </div>
                <h3 className="font-medium text-foreground mb-2">AI-Powered</h3>
                <p className="text-sm text-muted-foreground">Advanced algorithms analyze your preferences</p>
              </div>
              <div className="flex flex-col items-center">
                <div className="inline-flex items-center justify-center w-12 h-12 rounded-2xl bg-gradient-primary/10 border border-primary/20 mb-4">
                  <Target className="w-6 h-6 text-primary" />
                </div>
                <h3 className="font-medium text-foreground mb-2">Personalized</h3>
                <p className="text-sm text-muted-foreground">Tailored recommendations just for you</p>
              </div>
              <div className="flex flex-col items-center">
                <div className="inline-flex items-center justify-center w-12 h-12 rounded-2xl bg-gradient-primary/10 border border-primary/20 mb-4">
                  <Sparkles className="w-6 h-6 text-primary" />
                </div>
                <h3 className="font-medium text-foreground mb-2">Instant Results</h3>
                <p className="text-sm text-muted-foreground">Get recommendations in minutes</p>
              </div>
            </div>
          </div>

          <div className="text-center">
            <Button 
              variant="glass" 
              onClick={() => router.push('/dashboard')}
              className="rounded-full px-8"
            >
              Back to Dashboard
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
}