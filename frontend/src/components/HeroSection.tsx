'use client';
import { Button } from "@/components/ui/button";
import { Sparkles, Heart, Flower } from "lucide-react";
import heroImage from "@/assets/hero-luxury-perfume.jpg";
export const HeroSection = () => {
  return (
    <section className="relative min-h-screen flex items-center justify-center overflow-hidden">
      {/* Background Image with Overlay */}
      <div
        className="absolute inset-0 bg-cover bg-center bg-no-repeat"
        style={{ backgroundImage: `url(${heroImage})` }}
      />
      <div className="absolute inset-0 bg-gradient-to-br from-background/90 via-background/70 to-background/50" />

      {/* Floating Elements */}
      <div className="absolute top-20 left-20 animate-float">
        <div className="glass rounded-full p-4">
          <Sparkles className="h-8 w-8 text-primary" />
        </div>
      </div>
      <div className="absolute top-32 right-32 animate-float" style={{ animationDelay: '2s' }}>
        <div className="glass rounded-full p-4">
          <Heart className="h-8 w-8 text-accent" />
        </div>
      </div>
      <div className="absolute bottom-32 left-32 animate-float" style={{ animationDelay: '4s' }}>
        <div className="glass rounded-full p-4">
          <Flower className="h-8 w-8 text-primary" />
        </div>
      </div>

      {/* Main Content */}
      <div className="relative z-10 text-center max-w-4xl mx-auto px-6">
        <h1 className="text-5xl md:text-7xl font-light mb-6 text-foreground leading-tight">
          Find Your <span className="bg-gradient-primary bg-clip-text text-transparent font-medium">Signature Scent</span>
        </h1>
        <p className="text-xl md:text-2xl mb-8 text-muted-foreground font-light max-w-2xl mx-auto leading-relaxed">
          Discover fragrances that perfectly match your personality through AI-powered recommendations
        </p>

        <div className="flex flex-col sm:flex-row gap-4 justify-center items-center mb-16">
          <Button variant="hero" size="lg" className="text-lg px-10 py-4 h-auto rounded-full">
            Start Quiz
          </Button>
          <Button variant="glass" size="lg" className="text-lg px-8 py-4 h-auto rounded-full">
            Browse Scents
          </Button>
           <Button variant="outline" size="lg" onClick={() => window.location.href = '/login'} className="text-lg px-8 py-4 h-auto rounded-full border-pink-300/50 text-pink-600 hover:bg-pink-50">
                Login
           </Button>
        </div>

        {/* Stats */}
        <div className="mt-16 grid grid-cols-1 md:grid-cols-3 gap-8">
          <div className="glass rounded-2xl p-6 transition-luxury hover:shadow-luxury">
            <div className="text-3xl font-bold text-primary mb-2">10,000+</div>
            <div className="text-muted-foreground">Fragrances Analyzed</div>
          </div>
          <div className="glass rounded-2xl p-6 transition-luxury hover:shadow-luxury">
            <div className="text-3xl font-bold text-secondary mb-2">98%</div>
            <div className="text-muted-foreground">Match Accuracy</div>
          </div>
          <div className="glass rounded-2xl p-6 transition-luxury hover:shadow-luxury">
            <div className="text-3xl font-bold text-accent mb-2">50K+</div>
            <div className="text-muted-foreground">Happy Users</div>
          </div>
        </div>
      </div>
    </section>
  );
};
