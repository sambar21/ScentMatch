import { Button } from "@/components/ui/button";
import { ArrowRight, Sparkles } from "lucide-react";

export const CTASection = () => {
  return (
    <section className="py-32 px-6 relative overflow-hidden">
      {/* Background Effects */}
      <div className="absolute inset-0 bg-gradient-primary opacity-10" />
      <div className="absolute top-20 left-20 w-96 h-96 bg-primary/20 rounded-full blur-3xl animate-pulse" />
      <div className="absolute bottom-20 right-20 w-96 h-96 bg-secondary/20 rounded-full blur-3xl animate-pulse" style={{ animationDelay: '1s' }} />

      <div className="max-w-4xl mx-auto text-center relative z-10">
        <div className="glass rounded-3xl p-12 md:p-16 shadow-luxury">
          <div className="inline-flex items-center justify-center w-20 h-20 rounded-full bg-gradient-primary mb-8 animate-glow">
            <Sparkles className="h-10 w-10 text-primary-foreground" />
          </div>

          <h2 className="text-3xl md:text-5xl font-light mb-6 text-foreground">
            Ready to Find Your <span className="bg-gradient-primary bg-clip-text text-transparent font-medium">Signature Scent?</span>
          </h2>

          <p className="text-lg text-muted-foreground mb-12 max-w-2xl mx-auto leading-relaxed">
            Join thousands who&apos;ve discovered their perfect fragrance match through AI
          </p>

          <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
            <Button variant="hero" size="lg" className="text-lg px-10 py-4 h-auto rounded-full group">
              Start Your Journey
              <ArrowRight className="h-5 w-5 group-hover:translate-x-1 transition-transform" />
            </Button>
            <Button variant="glass" size="lg" className="text-lg px-8 py-4 h-auto rounded-full">
              Browse Collection
            </Button>
          </div>

          <div className="mt-12 flex items-center justify-center gap-8 text-sm text-muted-foreground">
            <div className="flex items-center gap-2">
              <div className="w-2 h-2 bg-secondary rounded-full animate-pulse" />
              Free to start
            </div>
            <div className="flex items-center gap-2">
              <div className="w-2 h-2 bg-accent rounded-full animate-pulse" />
              No credit card required
            </div>
            <div className="flex items-center gap-2">
              <div className="w-2 h-2 bg-primary rounded-full animate-pulse" />
              Instant results
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};
