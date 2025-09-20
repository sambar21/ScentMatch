'use client';

import { ReactNode } from 'react';
import { Progress } from "@/components/ui/progress";
import { Button } from "@/components/ui/button";
import { ChevronLeft } from "lucide-react";
import { useRouter } from 'next/navigation';

interface QuizLayoutProps {
  children: ReactNode;
  currentStep: number;
  totalSteps: number;
  title: string;
  onBack?: () => void;
  showBackButton?: boolean;
}

export function QuizLayout({ 
  children, 
  currentStep, 
  totalSteps, 
  title, 
  onBack, 
  showBackButton = true 
}: QuizLayoutProps) {
  const router = useRouter();
  const progress = (currentStep / totalSteps) * 100;

  return (
    <div className="min-h-screen bg-gradient-to-br from-pink-50 via-rose-50 to-orange-50">
      {/* Header with Progress */}
      <div className="glass border-b border-pink-200/30 sticky top-0 z-10 backdrop-blur-lg">
        <div className="max-w-4xl mx-auto px-4 py-4">
          <div className="flex items-center justify-between mb-4">
            {showBackButton && (
              <Button 
                variant="ghost" 
                onClick={onBack || (() => router.back())}
                className="text-pink-600"
              >
                <ChevronLeft className="w-4 h-4 mr-1" />
                Back
              </Button>
            )}
            <div className="text-sm text-muted-foreground">
              Step {currentStep} of {totalSteps}
            </div>
          </div>
          <h1 className="text-xl font-semibold text-center mb-4">{title}</h1>
          <Progress value={progress} className="h-2" />
        </div>
      </div>

      {/* Content */}
      <main className="max-w-4xl mx-auto px-4 py-8">
        {children}
      </main>
    </div>
  );
}