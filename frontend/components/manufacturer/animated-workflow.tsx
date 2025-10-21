"use client";

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Button } from '@/components/ui/button';
import { 
  AlertTriangle, 
  Bot, 
  CheckCircle2, 
  Zap,
  ArrowRight,
  Clock,
  TrendingUp,
  Users,
  Package,
  Calendar,
  FileText
} from 'lucide-react';

interface AnimatedWorkflowProps {
  isActive: boolean;
  onComplete?: () => void;
}

interface WorkflowStep {
  id: number;
  title: string;
  description: string;
  icon: React.ReactNode;
  status: 'pending' | 'active' | 'completed';
  duration: number; // in seconds
  details?: string[];
}

export default function AnimatedWorkflow({ isActive, onComplete }: AnimatedWorkflowProps) {
  const [currentStep, setCurrentStep] = useState(0);
  const [progress, setProgress] = useState(0);
  const [steps, setSteps] = useState<WorkflowStep[]>([
    {
      id: 1,
      title: "Alert Detection",
      description: "LOGI-BOT detects critical inventory shortage",
      icon: <AlertTriangle className="h-6 w-6" />,
      status: 'pending',
      duration: 2,
      details: [
        "Monitoring inventory levels across all products",
        "Detecting critical stock thresholds",
        "Alert severity: CRITICAL"
      ]
    },
    {
      id: 2,
      title: "Root Cause Analysis",
      description: "AI analyzes consumption patterns and supplier performance",
      icon: <Bot className="h-6 w-6" />,
      status: 'pending',
      duration: 4,
      details: [
        "Analyzing recent consumption: 45% increase",
        "Checking supplier performance metrics",
        "Evaluating external market factors",
        "Root cause identified: Demand spike + supplier delay"
      ]
    },
    {
      id: 3,
      title: "Solution Generation",
      description: "AI formulates optimal replenishment strategy",
      icon: <TrendingUp className="h-6 w-6" />,
      status: 'pending',
      duration: 3,
      details: [
        "Calculating optimal order quantity: 160 units",
        "Selecting dual-supplier strategy",
        "Primary: 80 units (3-day delivery)",
        "Backup: 80 units (5-day delivery)"
      ]
    },
    {
      id: 4,
      title: "Autonomous Orchestration",
      description: "Coordinates external tools and stakeholders",
      icon: <Zap className="h-6 w-6" />,
      status: 'pending',
      duration: 3,
      details: [
        "Creating Asana project with 5 tasks",
        "Scheduling emergency stakeholder meeting",
        "Generating supplier order drafts",
        "Sending notifications to procurement team"
      ]
    },
    {
      id: 5,
      title: "Workflow Complete",
      description: "All emergency response actions executed successfully",
      icon: <CheckCircle2 className="h-6 w-6" />,
      status: 'pending',
      duration: 1,
      details: [
        "Emergency response plan activated",
        "All stakeholders notified",
        "Supplier orders pending approval",
        "Expected resolution: 3-5 business days"
      ]
    }
  ]);

  useEffect(() => {
    if (!isActive) {
      setCurrentStep(0);
      setProgress(0);
      setSteps(prev => prev.map(step => ({ ...step, status: 'pending' })));
      return;
    }

    let stepTimer: NodeJS.Timeout;
    let progressTimer: NodeJS.Timeout;
    
    const runWorkflow = () => {
      setSteps(prev => prev.map((step, index) => ({
        ...step,
        status: index === currentStep ? 'active' : index < currentStep ? 'completed' : 'pending'
      })));

      if (currentStep < steps.length) {
        const currentStepData = steps[currentStep];
        let stepProgress = 0;
        
        // Progress animation within current step
        progressTimer = setInterval(() => {
          stepProgress += 100 / (currentStepData.duration * 10); // Update every 100ms
          setProgress(Math.min(stepProgress, 100));
        }, 100);

        // Move to next step
        stepTimer = setTimeout(() => {
          clearInterval(progressTimer);
          setProgress(100);
          
          setTimeout(() => {
            setCurrentStep(prev => prev + 1);
            setProgress(0);
          }, 500);
        }, currentStepData.duration * 1000);
      } else {
        // Workflow complete
        setProgress(100);
        onComplete?.();
      }
    };

    runWorkflow();

    return () => {
      clearTimeout(stepTimer);
      clearInterval(progressTimer);
    };
  }, [isActive, currentStep, onComplete]);

  const getStepColor = (status: string) => {
    switch (status) {
      case 'completed': return 'bg-green-900/30 text-green-300 border-green-500/30';
      case 'active': return 'bg-blue-900/30 text-blue-300 border-blue-500/30';
      default: return 'bg-gray-700/50 text-gray-400 border-gray-600/50';
    }
  };

  const getStepBadgeVariant = (status: string) => {
    switch (status) {
      case 'completed': return 'default';
      case 'active': return 'default';
      default: return 'secondary';
    }
  };

  return (
    <div className="space-y-6">
      {/* Workflow Overview */}
      <Card className="bg-gray-800/80 backdrop-blur border-gray-700">
        <CardHeader>
          <CardTitle className="flex items-center justify-between text-white">
            <div className="flex items-center space-x-3">
              <div className="p-2 bg-blue-600 rounded-lg">
                <Bot className="h-6 w-6 text-white" />
              </div>
              <div>
                <span>LOGI-BOT Autonomous Workflow</span>
                <div className="text-sm text-gray-300 font-normal">
                  Emergency Supply Chain Response System
                </div>
              </div>
            </div>
            <Badge variant={isActive ? 'default' : 'secondary'} className={isActive ? 'bg-green-600 text-white' : 'bg-gray-600 text-gray-300'}>
              {isActive ? 'ACTIVE' : 'READY'}
            </Badge>
          </CardTitle>
          <CardDescription className="text-gray-300">
            Real-time visualization of autonomous supply chain resilience in action
          </CardDescription>
        </CardHeader>
        <CardContent>
          {/* Overall Progress */}
          <div className="mb-6">
            <div className="flex justify-between text-sm mb-2 text-gray-300">
              <span>Overall Progress</span>
              <span>{currentStep}/{steps.length} steps completed</span>
            </div>
            <Progress 
              value={(currentStep / steps.length) * 100} 
              className="h-2 bg-gray-700"
            />
          </div>

          {/* Current Step Highlight */}
          {isActive && currentStep < steps.length && (
            <div className="mb-6 p-4 bg-blue-900/30 rounded-lg border border-blue-500/30">
              <div className="flex items-center justify-between mb-2">
                <h4 className="font-semibold text-blue-300">
                  Currently Executing: {steps[currentStep].title}
                </h4>
                <div className="flex items-center space-x-2">
                  <Clock className="h-4 w-4 text-blue-400" />
                  <span className="text-sm text-blue-400">
                    {steps[currentStep].duration}s
                  </span>
                </div>
              </div>
              <p className="text-blue-200 mb-3">{steps[currentStep].description}</p>
              <Progress value={progress} className="h-1 mb-3 bg-gray-700" />
              
              {/* Step Details */}
              <div className="space-y-1">
                {steps[currentStep].details?.map((detail, index) => (
                  <div key={index} className="flex items-center space-x-2 text-sm">
                    <div className="w-2 h-2 bg-blue-400 rounded-full" />
                    <span className="text-blue-200">{detail}</span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Workflow Steps */}
      <div className="space-y-4">
        {steps.map((step, index) => (
          <Card 
            key={step.id} 
            className={`transition-all duration-500 border-2 ${
              step.status === 'active' 
                ? 'bg-gray-800/90 border-blue-500/50 shadow-lg shadow-blue-500/20 scale-105' 
                : step.status === 'completed'
                ? 'bg-gray-800/80 border-green-500/50'
                : 'bg-gray-800/60 border-gray-600/50'
            }`}
          >
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-4">
                  <div className={`p-3 rounded-full border-2 transition-all duration-300 ${getStepColor(step.status)}`}>
                    {step.icon}
                  </div>
                  <div className="flex-1">
                    <div className="flex items-center space-x-3 mb-1">
                      <h3 className="font-semibold text-lg text-white">
                        Step {step.id}: {step.title}
                      </h3>
                      <Badge 
                        variant={getStepBadgeVariant(step.status)}
                        className={
                          step.status === 'completed' ? 'bg-green-600 text-white' :
                          step.status === 'active' ? 'bg-blue-600 text-white' :
                          'bg-gray-600 text-gray-300'
                        }
                      >
                        {step.status.toUpperCase()}
                      </Badge>
                    </div>
                    <p className="text-gray-300">{step.description}</p>
                  </div>
                </div>
                
                <div className="flex items-center space-x-2">
                  {step.status === 'completed' && (
                    <CheckCircle2 className="h-6 w-6 text-green-400" />
                  )}
                  {step.status === 'active' && (
                    <div className="animate-pulse">
                      <div className="h-3 w-3 bg-blue-400 rounded-full" />
                    </div>
                  )}
                  {index < steps.length - 1 && (
                    <ArrowRight className="h-5 w-5 text-gray-400" />
                  )}
                </div>
              </div>

              {/* Step Progress */}
              {step.status === 'active' && (
                <div className="mt-4 ml-16">
                  <Progress value={progress} className="h-1 bg-gray-700" />
                </div>
              )}

              {/* Step Results */}
              {step.status === 'completed' && step.details && (
                <div className="mt-4 ml-16">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
                    {step.details.slice(0, 4).map((detail, idx) => (
                      <div key={idx} className="flex items-center space-x-2 text-sm text-green-400">
                        <CheckCircle2 className="h-3 w-3" />
                        <span>{detail}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Completion Summary */}
      {currentStep >= steps.length && isActive && (
        <Card className="bg-gradient-to-r from-gray-800 to-gray-700 border-green-500 border-2">
          <CardContent className="p-6">
            <div className="text-center">
              <div className="inline-flex items-center justify-center w-16 h-16 bg-green-900/30 rounded-full mb-4">
                <CheckCircle2 className="h-8 w-8 text-green-400" />
              </div>
              <h3 className="text-xl font-bold text-green-300 mb-2">
                Workflow Successfully Completed!
              </h3>
              <p className="text-green-200 mb-4">
                LOGI-BOT has autonomously managed the entire emergency response cycle from detection to resolution coordination.
              </p>
              
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-6">
                <div className="text-center p-3 bg-gray-700/50 rounded-lg border border-gray-600">
                  <Package className="h-6 w-6 text-blue-400 mx-auto mb-2" />
                  <div className="font-semibold text-white">160 Units</div>
                  <div className="text-xs text-gray-300">Replenishment Planned</div>
                </div>
                <div className="text-center p-3 bg-gray-700/50 rounded-lg border border-gray-600">
                  <Calendar className="h-6 w-6 text-purple-400 mx-auto mb-2" />
                  <div className="font-semibold text-white">3-5 Days</div>
                  <div className="text-xs text-gray-300">Expected Resolution</div>
                </div>
                <div className="text-center p-3 bg-gray-700/50 rounded-lg border border-gray-600">
                  <Users className="h-6 w-6 text-green-400 mx-auto mb-2" />
                  <div className="font-semibold text-white">5 Tasks</div>
                  <div className="text-xs text-gray-300">Created & Assigned</div>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}