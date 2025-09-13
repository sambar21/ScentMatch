import { Brain, Heart, Target, Sparkles, TrendingUp, Shield } from "lucide-react";

const features = [
  {
    icon: Brain,
    title: "AI-Powered Analysis",
    description: "Advanced machine learning algorithms analyze thousands of fragrance profiles to understand complex scent relationships and preferences."
  },
  {
    icon: Heart,
    title: "Personalized Matching",
    description: "Our AI learns your unique preferences, lifestyle, and personality to create a custom fragrance profile just for you."
  },
  {
    icon: Target,
    title: "Precision Recommendations",
    description: "Get highly accurate suggestions based on your scent DNA, seasonal preferences, and occasion-specific needs."
  },
  {
    icon: Sparkles,
    title: "Discovery Engine",
    description: "Explore new fragrances outside your comfort zone with curated recommendations that expand your olfactory horizons."
  },
  {
    icon: TrendingUp,
    title: "Trend Insights",
    description: "Stay ahead with insights into fragrance trends, seasonal favorites, and emerging scent profiles in the market."
  },
  {
    icon: Shield,
    title: "Quality Assurance",
    description: "Every recommended fragrance is verified for authenticity and quality, ensuring you only discover premium scents."
  }
];

export const FeaturesSection = () => {
  return (
    <section className="py-32 px-6">
      <div className="max-w-7xl mx-auto">
        <div className="text-center mb-20">
          <h2 className="text-4xl md:text-5xl font-light mb-6 text-foreground">
            Why Choose <span className="bg-gradient-primary bg-clip-text text-transparent font-medium">ScentMatch</span>
          </h2>
          <p className="text-lg text-muted-foreground max-w-2xl mx-auto leading-relaxed">
            Discover fragrances through intelligent recommendations powered by advanced AI
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
          {features.map((feature, index) => {
            const Icon = feature.icon;
            return (
              <div
                key={index}
                className="glass rounded-3xl p-8 transition-luxury hover:shadow-luxury group animate-float"
                style={{ animationDelay: `${index * 0.5}s` }}
              >
                <div className="mb-6">
                  <div className="inline-flex items-center justify-center w-14 h-14 rounded-2xl bg-gradient-primary/10 border border-primary/20 group-hover:bg-gradient-primary/20 transition-luxury">
                    <Icon className="h-7 w-7 text-primary" />
                  </div>
                </div>
                <h3 className="text-xl font-medium mb-3 text-foreground">
                  {feature.title}
                </h3>
                <p className="text-muted-foreground leading-relaxed">
                  {feature.description}
                </p>
              </div>
            );
          })}
        </div>
      </div>
    </section>
  );
};
