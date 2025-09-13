import { MessageSquare, Brain, Gift } from "lucide-react";

const steps = [
  {
    icon: MessageSquare,
    title: "Tell Us About You",
    description: "Share your fragrance preferences, lifestyle, and the occasions you're shopping for through our intuitive questionnaire."
  },
  {
    icon: Brain,
    title: "AI Analysis",
    description: "Our advanced AI processes your responses, analyzing patterns from thousands of fragrance profiles and user preferences."
  },
  {
    icon: Gift,
    title: "Perfect Matches",
    description: "Receive personalized recommendations with detailed notes, occasion suggestions, and where to find your perfect scents."
  }
];

export const HowItWorksSection = () => {
  return (
    <section className="py-32 px-6 relative">
      {/* Background decoration */}
      <div className="absolute inset-0 bg-gradient-accent opacity-5" />

      <div className="max-w-6xl mx-auto relative z-10">
        <div className="text-center mb-20">
          <h2 className="text-4xl md:text-5xl font-light mb-6 text-foreground">
            How It <span className="bg-gradient-primary bg-clip-text text-transparent font-medium">Works</span>
          </h2>
          <p className="text-lg text-muted-foreground max-w-2xl mx-auto leading-relaxed">
            Three simple steps to discover your perfect fragrance match
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-12">
          {steps.map((step, index) => {
            const Icon = step.icon;
            return (
              <div key={index} className="text-center relative">
                {/* Connection line */}
                {index < steps.length - 1 && (
                  <div className="hidden lg:block absolute top-16 left-full w-full h-0.5 bg-gradient-primary opacity-30 transform translate-x-6" />
                )}

                {/* Step content */}
                <div className="glass rounded-3xl p-8 transition-luxury hover:shadow-luxury group animate-float"
                     style={{ animationDelay: `${index * 1}s` }}>
                  <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-gradient-primary/10 border border-primary/20 mb-6 group-hover:bg-gradient-primary/20 transition-luxury">
                    <Icon className="h-8 w-8 text-primary" />
                  </div>

                  <div className="text-4xl font-light text-primary/40 mb-4">
                    {String(index + 1).padStart(2, '0')}
                  </div>

                  <h3 className="text-xl font-medium mb-3 text-foreground">
                    {step.title}
                  </h3>

                  <p className="text-muted-foreground leading-relaxed">
                    {step.description}
                  </p>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </section>
  );
};
