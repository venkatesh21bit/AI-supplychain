"use client";

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { 
  Activity, 
  AlertTriangle, 
  Bot, 
  Wifi, 
  WifiOff,
  Zap,
  Clock,
  TrendingUp,
  CheckCircle2,
  Play,
  RefreshCw
} from 'lucide-react';

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000/api";

interface RealTimeUpdate {
  id: string;
  type: 'alert' | 'execution' | 'workflow_step' | 'system';
  title: string;
  message: string;
  timestamp: string;
  severity: 'info' | 'warning' | 'error' | 'success';
  data?: any;
}

interface NotificationProps {
  onTriggerDemo: () => void;
  isExecuting: boolean;
  currentLowStockProduct?: any;
}

export default function RealTimeNotifications({ onTriggerDemo, isExecuting, currentLowStockProduct }: NotificationProps) {
  const [updates, setUpdates] = useState<RealTimeUpdate[]>([]);
  const [isConnected, setIsConnected] = useState(true);
  const [token, setToken] = useState<string | null>(null);

  // Mock real-time connection
  useEffect(() => {
    const getToken = async () => {
      try {
        const response = await fetch(`${API_URL}/token/`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ username: 'admin', password: 'password123' })
        });
        const data = await response.json();
        setToken(data.access);
      } catch (err) {
        console.error('Auth failed');
      }
    };
    getToken();
  }, []);

  // Simulate real-time updates
  useEffect(() => {
    if (!token) return;

    const interval = setInterval(() => {
      // Simulate receiving real-time updates
      if (Math.random() > 0.7) { // 30% chance of update
        const updateTypes = ['alert', 'execution', 'workflow_step', 'system'];
        const type = updateTypes[Math.floor(Math.random() * updateTypes.length)] as any;
        
        const newUpdate: RealTimeUpdate = {
          id: Date.now().toString(),
          type,
          title: getUpdateTitle(type),
          message: getUpdateMessage(type),
          timestamp: new Date().toISOString(),
          severity: getUpdateSeverity(type),
        };

        setUpdates(prev => [newUpdate, ...prev.slice(0, 9)]); // Keep last 10 updates
      }
    }, 3000);

    return () => clearInterval(interval);
  }, [token]);

  // Add demo workflow updates using current product data
  const addDemoUpdates = () => {
    let productName = 'current inventory';
    let stockLevel = 'optimal';
    let stockMessage = 'LOGI-BOT has detected inventory optimization opportunity';
    let severity: 'info' | 'warning' = 'info';

    // Use real product data if available
    if (currentLowStockProduct) {
      productName = currentLowStockProduct.name;
      stockLevel = currentLowStockProduct.available_quantity.toString();
      
      if (currentLowStockProduct.available_quantity <= 10) {
        stockMessage = `LOGI-BOT has detected critically low inventory for ${productName} (${stockLevel} units < 10 threshold)`;
        severity = 'warning';
      } else {
        stockMessage = `LOGI-BOT monitoring ${productName} (${stockLevel} units - optimal replenishment timing)`;
        severity = 'info';
      }
    }

    // Generate unique IDs using timestamp to avoid key conflicts
    const timestamp = Date.now();
    const demoUpdates: RealTimeUpdate[] = [
      {
        id: `demo-${timestamp}-1`,
        type: 'execution',
        title: 'Workflow Initiated',
        message: stockMessage,
        timestamp: new Date().toISOString(),
        severity: severity
      },
      {
        id: `demo-${timestamp}-2`,
        type: 'workflow_step',
        title: 'Root Cause Analysis Started',
        message: `Analyzing consumption patterns and supplier performance for ${productName}...`,
        timestamp: new Date(Date.now() + 2000).toISOString(),
        severity: 'info'
      },
      {
        id: `demo-${timestamp}-3`,
        type: 'workflow_step',
        title: 'AI Optimization Complete',
        message: `Generated replenishment plan for ${productName}: optimized quantity with 3-day delivery timeline`,
        timestamp: new Date(Date.now() + 5000).toISOString(),
        severity: 'success'
      },
      {
        id: `demo-${timestamp}-4`,
        type: 'workflow_step',
        title: 'External Tools Orchestrated',
        message: `Created Asana project for ${productName}, scheduled emergency meeting, generated draft orders`,
        timestamp: new Date(Date.now() + 8000).toISOString(),
        severity: 'success'
      }
    ];

    // Add updates with delays
    demoUpdates.forEach((update, index) => {
      setTimeout(() => {
        setUpdates(prev => [update, ...prev.slice(0, 9)]);
      }, index * 3000);
    });
  };

  useEffect(() => {
    if (isExecuting) {
      addDemoUpdates();
    }
  }, [isExecuting, currentLowStockProduct]);

  const getUpdateTitle = (type: string) => {
    switch (type) {
      case 'alert': return 'New Alert Detected';
      case 'execution': return 'Workflow Execution';
      case 'workflow_step': return 'Step Completed';
      case 'system': return 'System Status';
      default: return 'Update';
    }
  };

  const getUpdateMessage = (type: string) => {
    const messages = {
      alert: [
        'Low inventory detected for critical products',
        'Critical threshold breached for essential materials',
        'Supplier delivery delay reported'
      ],
      execution: [
        'Emergency replenishment workflow initiated',
        'Automated analysis completed successfully',
        'All orchestration tasks completed'
      ],
      workflow_step: [
        'Root cause analysis in progress...',
        'AI optimization engine processing...',
        'External integrations executing...'
      ],
      system: [
        'All monitoring systems operational',
        'Database connection stable',
        'API endpoints responding normally'
      ]
    };
    
    const typeMessages = messages[type as keyof typeof messages] || ['System update'];
    return typeMessages[Math.floor(Math.random() * typeMessages.length)];
  };

  const getUpdateSeverity = (type: string): 'info' | 'warning' | 'error' | 'success' => {
    switch (type) {
      case 'alert': return 'warning';
      case 'execution': return 'info';
      case 'workflow_step': return 'success';
      case 'system': return 'info';
      default: return 'info';
    }
  };

  const getSeverityIcon = (severity: string) => {
    switch (severity) {
      case 'warning': return <AlertTriangle className="h-4 w-4 text-yellow-400" />;
      case 'error': return <AlertTriangle className="h-4 w-4 text-red-400" />;
      case 'success': return <CheckCircle2 className="h-4 w-4 text-green-400" />;
      default: return <Activity className="h-4 w-4 text-blue-400" />;
    }
  };

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'warning': return 'border-l-yellow-500 bg-yellow-900 bg-opacity-30';
      case 'error': return 'border-l-red-500 bg-red-900 bg-opacity-30';
      case 'success': return 'border-l-green-500 bg-green-900 bg-opacity-30';
      default: return 'border-l-blue-500 bg-blue-900 bg-opacity-30';
    }
  };

  return (
    <div className="space-y-6">
      {/* Connection Status */}
      <Card className="bg-gray-800 border-gray-700">
        <CardHeader>
          <CardTitle className="flex items-center justify-between text-white">
            <div className="flex items-center space-x-2">
              <Bot className="h-5 w-5 text-blue-400" />
              <span>LOGI-BOT Real-Time Monitor</span>
            </div>
            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-2">
                {isConnected ? (
                  <Wifi className="h-4 w-4 text-green-400" />
                ) : (
                  <WifiOff className="h-4 w-4 text-red-400" />
                )}
                <span className="text-sm text-gray-300">
                  {isConnected ? 'Connected' : 'Disconnected'}
                </span>
              </div>
              <Button 
                onClick={onTriggerDemo} 
                disabled={isExecuting}
                size="sm"
                className="bg-blue-600 hover:bg-blue-700 text-white border-0"
              >
                {isExecuting ? (
                  <>
                    <RefreshCw className="h-4 w-4 mr-2 animate-spin" />
                    Running...
                  </>
                ) : (
                  <>
                    <Play className="h-4 w-4 mr-2" />
                    Demo Workflow
                  </>
                )}
              </Button>
            </div>
          </CardTitle>
          <CardDescription className="text-gray-400">
            Live updates from the autonomous supply chain agent
          </CardDescription>
        </CardHeader>
      </Card>

      {/* Live Updates Feed */}
      <Card className="bg-gray-800 border-gray-700">
        <CardHeader>
          <CardTitle className="flex items-center space-x-2 text-white">
            <Zap className="h-5 w-5 text-yellow-400" />
            <span>Live Activity Feed</span>
          </CardTitle>
        </CardHeader>
        <CardContent>
          {updates.length === 0 ? (
            <div className="text-center py-8">
              <Activity className="h-12 w-12 text-gray-500 mx-auto mb-4" />
              <p className="text-gray-300">Monitoring for updates...</p>
              <p className="text-sm text-gray-500">Real-time notifications will appear here</p>
            </div>
          ) : (
            <div className="space-y-3 max-h-96 overflow-y-auto">
              {updates.map((update) => (
                <div 
                  key={update.id}
                  className={`border-l-4 pl-4 py-2 rounded-r ${getSeverityColor(update.severity)} transition-all duration-300 hover:bg-opacity-70`}
                >
                  <div className="flex items-start justify-between">
                    <div className="flex items-start space-x-3">
                      {getSeverityIcon(update.severity)}
                      <div className="min-w-0 flex-1">
                        <div className="flex items-center space-x-2 mb-1">
                          <p className="font-semibold text-sm text-white">{update.title}</p>
                          <Badge variant="outline" className="text-xs border-gray-500 text-gray-300">
                            {update.type}
                          </Badge>
                        </div>
                        <p className="text-sm text-gray-300">{update.message}</p>
                      </div>
                    </div>
                    <div className="flex items-center space-x-2 text-xs text-gray-500">
                      <Clock className="h-3 w-3" />
                      <span>{new Date(update.timestamp).toLocaleTimeString()}</span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Quick Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card className="bg-gray-800 border-gray-700">
          <CardContent className="p-4">
            <div className="flex items-center space-x-3">
              <div className="p-2 bg-blue-900 rounded-lg border border-blue-700">
                <Activity className="h-6 w-6 text-blue-400" />
              </div>
              <div>
                <p className="text-sm text-gray-400">Updates Today</p>
                <p className="text-xl font-bold text-white">{updates.length}</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="bg-gray-800 border-gray-700">
          <CardContent className="p-4">
            <div className="flex items-center space-x-3">
              <div className="p-2 bg-green-900 rounded-lg border border-green-700">
                <TrendingUp className="h-6 w-6 text-green-400" />
              </div>
              <div>
                <p className="text-sm text-gray-400">Success Rate</p>
                <p className="text-xl font-bold text-white">98.5%</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="bg-gray-800 border-gray-700">
          <CardContent className="p-4">
            <div className="flex items-center space-x-3">
              <div className="p-2 bg-yellow-900 rounded-lg border border-yellow-700">
                <AlertTriangle className="h-6 w-6 text-yellow-400" />
              </div>
              <div>
                <p className="text-sm text-gray-400">Active Alerts</p>
                <p className="text-xl font-bold text-white">
                  {updates.filter(u => u.severity === 'warning').length}
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}