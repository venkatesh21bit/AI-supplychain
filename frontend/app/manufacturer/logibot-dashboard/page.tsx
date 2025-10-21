"use client";

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Alert, AlertDescription } from '@/components/ui/alert';
import RealTimeNotifications from '@/components/manufacturer/real-time-notifications';
import AnimatedWorkflow from '@/components/manufacturer/animated-workflow';
import { API_URL, fetchWithAuth, getAuthToken } from '@/utils/auth_fn';
import { 
  Activity, 
  AlertTriangle, 
  Bot, 
  CheckCircle, 
  Clock, 
  Package, 
  TrendingUp, 
  Zap,
  Eye,
  Play,
  RefreshCw,
  Calendar,
  FileText,
  ShoppingCart,
  Users
} from 'lucide-react';

// Utility functions
const getPriorityColor = (priority: string) => {
  switch (priority.toLowerCase()) {
    case 'critical': return 'destructive';
    case 'high': return 'destructive';
    case 'medium': return 'default';
    case 'low': return 'secondary';
    default: return 'default';
  }
};

const getStatusColor = (status: string) => {
  switch (status.toLowerCase()) {
    case 'completed': return 'text-green-600';
    case 'failed': return 'text-red-600';
    case 'running': return 'text-blue-600';
    default: return 'text-gray-600';
  }
};

interface AgentStatus {
  agent: string;
  version: string;
  active: boolean;
  total_executions: number;
  active_workflows: number;
  last_execution: string | null;
  statistics: {
    total_alerts: number;
    active_alerts: number;
    total_executions: number;
    successful_executions: number;
  };
}

interface Alert {
  alert_id: number;
  alert_type: string;
  priority: string;
  status: string;
  company: string;
  product: string;
  current_stock: number;
  detected_at: string;
  resolved_at: string | null;
}

interface WorkflowExecution {
  execution_id: string;
  alert_type: string;
  product_id: number;
  product_name: string;
  started_at: string;
  status: string;
  workflow_steps: WorkflowStep[];
  summary?: {
    product: string;
    execution_status: string;
    steps_completed: string;
    actions_taken: string[];
    root_cause: string;
    confidence: string;
    replenishment_qty: number;
  };
}

interface WorkflowStep {
  step_number: number;
  step_name: string;
  status: string;
  started_at?: string;
  completed_at?: string;
  step_data?: any;
  result_data?: any;
}

export default function LogiBotDashboard() {
  const [agentStatus, setAgentStatus] = useState<AgentStatus | null>(null);
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [executions, setExecutions] = useState<WorkflowExecution[]>([]);
  const [selectedExecution, setSelectedExecution] = useState<WorkflowExecution | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isExecuting, setIsExecuting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [currentLowStockProduct, setCurrentLowStockProduct] = useState<any>(null);

  // Fetch data with proper authentication
  const fetchData = async () => {
    try {
      const companyId = localStorage.getItem('company_id');
      const [statusRes, alertsRes, executionsRes, productsRes] = await Promise.all([
        fetchWithAuth(`${API_URL}/agent/status/`),
        fetchWithAuth(`${API_URL}/agent/alerts/`),
        fetchWithAuth(`${API_URL}/agent/executions/`),
        companyId ? fetchWithAuth(`${API_URL}/products/?company=${companyId}`) : Promise.resolve({ ok: false })
      ]);

      if (statusRes.ok) {
        const statusData = await statusRes.json();
        console.log('Status API Response:', statusData);
        setAgentStatus(statusData);
      } else {
        console.error('Status API Error:', statusRes.status, statusRes.statusText);
      }
      
      if (alertsRes.ok) {
        const alertsData = await alertsRes.json();
        console.log('Alerts API Response:', alertsData);
        setAlerts(alertsData.alerts || alertsData.results || alertsData || []);
      } else {
        console.error('Alerts API Error:', alertsRes.status, alertsRes.statusText);
      }
      
      if (executionsRes.ok) {
        const execData = await executionsRes.json();
        console.log('Executions API Response:', execData);
        const executionsArray = execData.results || execData.executions || execData || [];
        console.log('Executions Array Length:', executionsArray.length);
        console.log('First execution sample:', executionsArray[0]);
        
        // Enhanced logging for workflow steps
        if (executionsArray.length > 0) {
          const latestExecution = executionsArray[0];
          console.log('Latest execution workflow_steps:', latestExecution.workflow_steps);
          if (latestExecution.workflow_steps) {
            latestExecution.workflow_steps.forEach((step: any, index: number) => {
              console.log(`Step ${index + 1}: ${step.step_name} - Status: ${step.status}`);
            });
          }
        }
        
        setExecutions(executionsArray);
      } else {
        console.error('Executions API Error:', executionsRes.status, executionsRes.statusText);
      }

      // Process products to find current low stock product
      if (productsRes.ok && 'json' in productsRes) {
        const products = await productsRes.json();
        const productsArray = Array.isArray(products) ? products : [];
        
        if (productsArray.length > 0) {
          // Find products with low stock (available_quantity <= 10)
          const lowStockProducts = productsArray.filter((p: any) => p.available_quantity <= 10);
          
          let targetProduct;
          if (lowStockProducts.length > 0) {
            // Use the product with lowest stock
            targetProduct = lowStockProducts.reduce((lowest: any, product: any) => 
              product.available_quantity < lowest.available_quantity ? product : lowest
            );
          } else {
            // Use the product with lowest stock overall
            targetProduct = productsArray.reduce((lowest: any, product: any) => 
              product.available_quantity < lowest.available_quantity ? product : lowest
            );
          }
          setCurrentLowStockProduct(targetProduct);
        }
      } else if ('status' in productsRes) {
        console.error('Products API Error:', productsRes.status, productsRes.statusText);
      }
    } catch (err) {
      console.error('Error fetching data:', err);
      setError('Failed to fetch data');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    // Check if user is authenticated
    const token = getAuthToken();
    if (token) {
      fetchData();
      const interval = setInterval(fetchData, 2000); // Refresh every 2 seconds for better real-time updates
      return () => clearInterval(interval);
    } else {
      setError('Please log in to access LOGI-BOT dashboard');
      setIsLoading(false);
    }
  }, []);

  // Trigger manual inventory check
  const triggerInventoryCheck = async () => {
    const companyId = localStorage.getItem('company_id');
    if (!companyId) {
      setError('No company selected');
      return;
    }
    
    setIsExecuting(true);
    try {
      // Get all products for the company
      const productsRes = await fetchWithAuth(`${API_URL}/products/?company=${companyId}`);
      if (!productsRes.ok) throw new Error('Failed to get products');
      
      const products = await productsRes.json();
      const productsArray = Array.isArray(products) ? products : [];
      
      if (productsArray.length === 0) {
        setError('No products found to check');
        return;
      }

      // Find products with low stock (available_quantity <= 10)
      const lowStockProducts = productsArray.filter(p => p.available_quantity <= 10);
      
      let targetProduct;
      if (lowStockProducts.length > 0) {
        // Use the product with lowest stock
        targetProduct = lowStockProducts.reduce((lowest, product) => 
          product.available_quantity < lowest.available_quantity ? product : lowest
        );
        console.log(`Found low stock product: ${targetProduct.name} with ${targetProduct.available_quantity} units`);
      } else {
        // No low stock products, use the product with lowest stock overall
        targetProduct = productsArray.reduce((lowest, product) => 
          product.available_quantity < lowest.available_quantity ? product : lowest
        );
        console.log(`No critically low stock found. Using lowest stock product: ${targetProduct.name} with ${targetProduct.available_quantity} units`);
      }

      const response = await fetchWithAuth(`${API_URL}/agent/check-all-inventory/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ 
          company_id: parseInt(companyId) 
        })
      });
      
      if (response.ok) {
        const result = await response.json();
        console.log('All inventory check result:', result);
        console.log(`✅ Triggered ${result.triggered_workflows || 0} workflows for low stock products`);
        
        if (result.result) {
          setSelectedExecution(result.result);
        }
        await fetchData(); // Refresh data
        setError(null);
      } else {
        const errorText = await response.text();
        console.error('All inventory check failed:', errorText);
        setError(`Failed to check all inventory: ${errorText}`);
      }
    } catch (err) {
      setError('Failed to trigger inventory check');
    } finally {
      setIsExecuting(false);
    }
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-900 flex items-center justify-center">
        <div className="text-center">
          <Bot className="h-16 w-16 text-blue-400 animate-pulse mx-auto mb-4" />
          <p className="text-lg text-gray-300">Loading LOGI-BOT Dashboard...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-900 p-6">
      <div className="max-w-7xl mx-auto space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <div className="bg-blue-600 p-3 rounded-xl">
              <Bot className="h-8 w-8 text-white" />
            </div>
            <div>
              <h1 className="text-3xl font-bold text-white">LOGI-BOT Dashboard</h1>
              <p className="text-gray-400">Autonomous Supply Chain Resilience Agent</p>
            </div>
          </div>
          <div className="flex items-center space-x-4">
            <Badge variant={agentStatus?.active ? "default" : "destructive"} className="bg-gray-800 text-white border-gray-700">
              {agentStatus?.active ? "Active" : "Inactive"}
            </Badge>
            <Button 
              onClick={() => {
                setIsLoading(true);
                fetchData();
              }}
              className="bg-gray-600 hover:bg-gray-700 text-white border-0"
            >
              <RefreshCw className="h-4 w-4 mr-2" />
              Refresh
            </Button>
            <Button 
              onClick={triggerInventoryCheck} 
              disabled={isExecuting}
              className="bg-blue-600 hover:bg-blue-700 text-white border-0"
            >
              {isExecuting ? (
                <>
                  <RefreshCw className="h-4 w-4 mr-2 animate-spin" />
                  Executing...
                </>
              ) : (
                <>
                  <Play className="h-4 w-4 mr-2" />
                  Demo Workflow
                </>
              )}
            </Button>
          </div>
        </div>

        {error && (
          <Alert variant="destructive" className="bg-red-900 border-red-700">
            <AlertTriangle className="h-4 w-4 text-red-400" />
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        )}

        {/* Agent Status Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          <Card className="bg-gray-800 border-gray-700">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-gray-300">Total Executions</CardTitle>
              <Activity className="h-4 w-4 text-blue-400" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-white">{agentStatus?.statistics.total_executions || 0}</div>
              <p className="text-xs text-gray-400">
                {agentStatus?.statistics.successful_executions || 0} successful
              </p>
            </CardContent>
          </Card>

          <Card className="bg-gray-800 border-gray-700">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-gray-300">Active Alerts</CardTitle>
              <AlertTriangle className="h-4 w-4 text-red-400" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-white">{agentStatus?.statistics.active_alerts || 0}</div>
              <p className="text-xs text-gray-400">
                {agentStatus?.statistics.total_alerts || 0} total alerts
              </p>
            </CardContent>
          </Card>

          <Card className="bg-gray-800 border-gray-700">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-gray-300">Active Workflows</CardTitle>
              <Zap className="h-4 w-4 text-yellow-400" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-white">{agentStatus?.active_workflows || 0}</div>
              <p className="text-xs text-gray-400">Currently running</p>
            </CardContent>
          </Card>

          <Card className="bg-gray-800 border-gray-700">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-gray-300">Success Rate</CardTitle>
              <TrendingUp className="h-4 w-4 text-green-400" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-white">
                {agentStatus?.statistics.total_executions ? 
                  Math.round((agentStatus.statistics.successful_executions / agentStatus.statistics.total_executions) * 100) : 0}%
              </div>
              <p className="text-xs text-gray-400">Execution success</p>
            </CardContent>
          </Card>
        </div>

        {/* Main Content Tabs */}
        <Tabs defaultValue="realtime" className="space-y-6">
          <TabsList className="grid w-full grid-cols-5 bg-gray-800 border-gray-700">
            <TabsTrigger value="realtime" className="data-[state=active]:bg-blue-600 data-[state=active]:text-white text-gray-400">Real-Time Monitor</TabsTrigger>
            <TabsTrigger value="animated" className="data-[state=active]:bg-blue-600 data-[state=active]:text-white text-gray-400">Animated Demo</TabsTrigger>
            <TabsTrigger value="workflow" className="data-[state=active]:bg-blue-600 data-[state=active]:text-white text-gray-400">Live Workflow</TabsTrigger>
            <TabsTrigger value="alerts" className="data-[state=active]:bg-blue-600 data-[state=active]:text-white text-gray-400">Alerts Monitor</TabsTrigger>
            <TabsTrigger value="history" className="data-[state=active]:bg-blue-600 data-[state=active]:text-white text-gray-400">Execution History</TabsTrigger>
          </TabsList>

          <TabsContent value="realtime">
            <RealTimeNotifications 
              onTriggerDemo={triggerInventoryCheck} 
              isExecuting={isExecuting} 
              currentLowStockProduct={currentLowStockProduct}
            />
          </TabsContent>

          <TabsContent value="animated">
            <AnimatedWorkflow isActive={isExecuting} onComplete={() => setIsExecuting(false)} />
          </TabsContent>

          <TabsContent value="workflow">
            <WorkflowVisualization execution={selectedExecution} />
          </TabsContent>

          <TabsContent value="alerts">
            <AlertsMonitor alerts={alerts} />
          </TabsContent>

          <TabsContent value="history">
            <ExecutionHistory executions={executions} onSelect={setSelectedExecution} />
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
}

// Workflow Visualization Component
function WorkflowVisualization({ execution }: { execution: WorkflowExecution | null }) {
  if (!execution) {
    return (
      <Card className="bg-gray-800 border-gray-700">
        <CardHeader>
          <CardTitle className="flex items-center space-x-2 text-white">
            <Zap className="h-5 w-5 text-blue-400" />
            <span>LOGI-BOT Autonomous Workflow</span>
          </CardTitle>
          <CardDescription className="text-gray-400">
            Click "Demo Workflow" to see LOGI-BOT in action - from alert detection to complete resolution
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="text-center p-6 border-2 border-dashed border-gray-600 rounded-lg bg-gray-800">
              <AlertTriangle className="h-12 w-12 text-blue-400 mx-auto mb-4" />
              <h3 className="font-semibold mb-2 text-white">1. Alert Detection</h3>
              <p className="text-sm text-gray-400">Monitors inventory levels and detects critical shortages</p>
            </div>
            <div className="text-center p-6 border-2 border-dashed border-gray-600 rounded-lg bg-gray-800">
              <Bot className="h-12 w-12 text-purple-400 mx-auto mb-4" />
              <h3 className="font-semibold mb-2 text-white">2. AI Analysis & Planning</h3>
              <p className="text-sm text-gray-400">Root cause analysis and optimal solution generation</p>
            </div>
            <div className="text-center p-6 border-2 border-dashed border-gray-600 rounded-lg bg-gray-800">
              <CheckCircle className="h-12 w-12 text-green-400 mx-auto mb-4" />
              <h3 className="font-semibold mb-2 text-white">3. Autonomous Execution</h3>
              <p className="text-sm text-gray-400">Creates tasks, schedules meetings, and generates orders</p>
            </div>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="space-y-6">
      {/* Execution Summary */}
      <Card className="bg-gray-800 border-gray-700">
        <CardHeader>
          <CardTitle className="flex items-center justify-between text-white">
            <span>Workflow Execution: {execution.product_name}</span>
            <Badge variant={execution.status === 'completed' ? 'default' : 'destructive'} className="bg-blue-600 text-white">
              {execution.status}
            </Badge>
          </CardTitle>
          <CardDescription className="text-gray-400">
            Execution ID: {execution.execution_id}
          </CardDescription>
        </CardHeader>
        <CardContent>
          {execution.summary && (
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
              <div className="text-center p-4 bg-blue-900 rounded-lg border border-blue-700">
                <Package className="h-8 w-8 text-blue-400 mx-auto mb-2" />
                <div className="text-lg font-semibold text-white">{execution.summary.replenishment_qty}</div>
                <div className="text-sm text-gray-400">Units Planned</div>
              </div>
              <div className="text-center p-4 bg-purple-900 rounded-lg border border-purple-700">
                <Bot className="h-8 w-8 text-purple-400 mx-auto mb-2" />
                <div className="text-lg font-semibold text-white">{execution.summary.root_cause}</div>
                <div className="text-sm text-gray-400">Root Cause</div>
              </div>
              <div className="text-center p-4 bg-green-900 rounded-lg border border-green-700">
                <CheckCircle className="h-8 w-8 text-green-400 mx-auto mb-2" />
                <div className="text-lg font-semibold text-white">{execution.summary.steps_completed}</div>
                <div className="text-sm text-gray-400">Completed</div>
              </div>
            </div>
          )}

          {/* Progress bar */}
          <div className="mb-6">
            <div className="flex justify-between text-sm mb-2 text-gray-300">
              <span>Workflow Progress</span>
              <span>{(execution.workflow_steps || []).filter(s => s.status === 'completed').length}/{(execution.workflow_steps || []).length} steps</span>
            </div>
            <Progress 
              value={execution.workflow_steps && execution.workflow_steps.length > 0 ? 
                ((execution.workflow_steps.filter(s => s.status === 'completed').length / execution.workflow_steps.length) * 100) : 0
              } 
              className="h-2 bg-gray-700"
            />
          </div>
        </CardContent>
      </Card>

      {/* Workflow Steps */}
      <div className="space-y-4">
        {(execution.workflow_steps || []).map((step, index) => (
          <WorkflowStepCard key={index} step={step} />
        ))}
      </div>
    </div>
  );
}

// Workflow Step Card Component
function WorkflowStepCard({ step }: { step: WorkflowStep }) {
  const getStepIcon = (name: string) => {
    switch (name.toLowerCase()) {
      case 'root_cause_analysis': return <AlertTriangle className="h-5 w-5" />;
      case 'solution_formulation': return <Bot className="h-5 w-5" />;
      case 'workflow_orchestration': return <Zap className="h-5 w-5" />;
      default: return <Activity className="h-5 w-5" />;
    }
  };

  const getStepTitle = (name: string) => {
    switch (name.toLowerCase()) {
      case 'root_cause_analysis': return 'Root Cause Analysis';
      case 'solution_formulation': return 'AI Solution Generation';
      case 'workflow_orchestration': return 'Autonomous Orchestration';
      default: return name.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
    }
  };

  return (
    <Card className="bg-gray-800 border-gray-700">
      <CardHeader>
        <CardTitle className="flex items-center justify-between text-lg text-white">
          <div className="flex items-center space-x-3">
            <div className={`p-2 rounded-lg ${
              step.status === 'completed' 
                ? 'bg-green-900 text-green-400 border border-green-700' 
                : step.status === 'running' 
                  ? 'bg-blue-900 text-blue-400 border border-blue-700' 
                  : step.status === 'failed' 
                    ? 'bg-red-900 text-red-400 border border-red-700'
                    : 'bg-gray-700 text-gray-400 border border-gray-600'
            }`}>
              {step.status === 'running' ? (
                <div className="animate-spin h-5 w-5 border-2 border-blue-400 border-t-transparent rounded-full"></div>
              ) : (
                getStepIcon(step.step_name)
              )}
            </div>
            <span>Step {step.step_number}: {getStepTitle(step.step_name)}</span>
            {step.completed_at && (
              <span className="text-xs text-gray-500">
                Completed: {new Date(step.completed_at).toLocaleTimeString()}
              </span>
            )}
          </div>
          <Badge variant={
            step.status === 'completed' ? 'default' : 
            step.status === 'running' ? 'secondary' : 
            step.status === 'failed' ? 'destructive' : 'outline'
          } className={
            step.status === 'completed' ? 'bg-green-600 text-white' :
            step.status === 'running' ? 'bg-blue-600 text-white' :
            step.status === 'failed' ? 'bg-red-600 text-white' :
            'bg-gray-600 text-white'
          }>
            {step.status.charAt(0).toUpperCase() + step.status.slice(1)}
          </Badge>
        </CardTitle>
      </CardHeader>
      <CardContent>
        <StepDetails step={step} />
      </CardContent>
    </Card>
  );
}

// Step Details Component  
function StepDetails({ step }: { step: WorkflowStep }) {
  // Handle both old and new data structures
  const stepData = step.result_data || step.step_data || (step as any).data || {};
  
  if (step.step_name === 'root_cause_analysis') {
    return (
      <div className="space-y-4">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="text-center p-3 bg-blue-900 rounded border border-blue-700">
            <div className="font-semibold text-white">{stepData.root_cause || 'N/A'}</div>
            <div className="text-sm text-gray-400">Root Cause</div>
          </div>
          <div className="text-center p-3 bg-purple-900 rounded border border-purple-700">
            <div className="font-semibold text-white">{Math.round((stepData.confidence || 0) * 100)}%</div>
            <div className="text-sm text-gray-400">Confidence</div>
          </div>
          <div className="text-center p-3 bg-green-900 rounded border border-green-700">
            <div className="font-semibold text-white">{stepData.current_inventory || 0}</div>
            <div className="text-sm text-gray-400">Current Stock</div>
          </div>
          <div className="text-center p-3 bg-yellow-900 rounded border border-yellow-700">
            <div className="font-semibold text-white">Critical</div>
            <div className="text-sm text-gray-400">Priority</div>
          </div>
        </div>
        {stepData.error && (
          <Alert variant="destructive" className="bg-red-900 border-red-700">
            <AlertTriangle className="h-4 w-4 text-red-400" />
            <AlertDescription>Analysis Error: {stepData.error}</AlertDescription>
          </Alert>
        )}
      </div>
    );
  }

  if (step.step_name === 'solution_formulation') {
    return (
      <div className="space-y-4">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <h4 className="font-semibold mb-3 flex items-center text-white">
              <ShoppingCart className="h-4 w-4 mr-2 text-blue-400" />
              Replenishment Plan
            </h4>
            <div className="space-y-2">
              <div className="flex justify-between text-gray-300">
                <span>Total Quantity:</span>
                <span className="font-semibold text-white">{stepData.recommendation?.total_replenishment_qty || 0} units</span>
              </div>
              <div className="flex justify-between text-gray-300">
                <span>Net Requirement:</span>
                <span className="font-semibold text-white">{stepData.recommendation?.net_requirement || 0} units</span>
              </div>
              <div className="flex justify-between text-gray-300">
                <span>Priority:</span>
                <Badge variant="destructive" className="bg-red-600 text-white">{stepData.recommendation?.priority_level || 'High'}</Badge>
              </div>
            </div>
          </div>
          <div>
            <h4 className="font-semibold mb-3 flex items-center text-white">
              <Clock className="h-4 w-4 mr-2 text-blue-400" />
              Timeline
            </h4>
            <div className="space-y-2">
              <div className="flex justify-between text-gray-300">
                <span>Expected Delivery:</span>
                <span className="font-semibold text-white">
                  {stepData.recommendation?.timeline?.expected_delivery ? 
                    new Date(stepData.recommendation.timeline.expected_delivery).toLocaleDateString() : 'TBD'}
                </span>
              </div>
              <div className="flex justify-between text-gray-300">
                <span>Lead Time:</span>
                <span className="font-semibold text-white">{stepData.recommendation?.timeline?.lead_time_days || 0} days</span>
              </div>
              <div className="flex justify-between text-gray-300">
                <span>Shipping:</span>
                <span className="font-semibold text-white">{stepData.recommendation?.sourcing_strategy?.shipping_method || 'Standard'}</span>
              </div>
            </div>
          </div>
        </div>

        {stepData.action_items && (
          <div>
            <h4 className="font-semibold mb-3 flex items-center text-white">
              <FileText className="h-4 w-4 mr-2 text-blue-400" />
              Action Items ({stepData.action_items.length})
            </h4>
            <div className="space-y-2">
              {stepData.action_items.slice(0, 3).map((item: any, idx: number) => (
                <div key={idx} className="flex items-center justify-between p-2 bg-gray-700 rounded border border-gray-600">
                  <span className="text-sm text-gray-300">{item.description}</span>
                  <Badge variant="outline" className="border-gray-500 text-gray-300">{item.priority}</Badge>
                </div>
              ))}
              {stepData.action_items.length > 3 && (
                <div className="text-sm text-gray-400 text-center">
                  +{stepData.action_items.length - 3} more actions
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    );
  }

  if (step.step_name === 'workflow_orchestration') {
    return (
      <div className="space-y-4">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {stepData.steps?.map((orchStep: any, idx: number) => (
            <div key={idx} className="p-4 border border-gray-600 rounded-lg bg-gray-700">
              <div className="flex items-center justify-between mb-2">
                <h5 className="font-semibold text-sm text-white">
                  {orchStep.step.replace(/_/g, ' ').replace(/\b\w/g, (l: string) => l.toUpperCase())}
                </h5>
                <Badge variant={orchStep.status === 'success' ? 'default' : 'destructive'} className="text-xs bg-blue-600 text-white">
                  {orchStep.status}
                </Badge>
              </div>
              
              {orchStep.step === 'create_asana_project' && orchStep.success && (
                <div className="space-y-1 text-sm">
                  <div className="flex items-center text-gray-300">
                    <Users className="h-3 w-3 mr-1 text-blue-400" />
                    <span>{orchStep.tasks_created || 0} tasks created</span>
                  </div>
                  <div className="text-xs text-gray-400 truncate">
                    Project: {orchStep.project_name || 'N/A'}
                  </div>
                </div>
              )}
              
              {orchStep.step === 'schedule_meeting' && orchStep.success && (
                <div className="space-y-1 text-sm">
                  <div className="flex items-center text-gray-300">
                    <Calendar className="h-3 w-3 mr-1 text-blue-400" />
                    <span>Meeting scheduled</span>
                  </div>
                  <div className="text-xs text-gray-400">
                    {orchStep.meeting_start ? 
                      new Date(orchStep.meeting_start).toLocaleString() : 'TBD'}
                  </div>
                </div>
              )}
              
              {orchStep.step === 'create_draft_orders' && orchStep.success && (
                <div className="space-y-1 text-sm">
                  <div className="flex items-center text-gray-300">
                    <ShoppingCart className="h-3 w-3 mr-1 text-blue-400" />
                    <span>{orchStep.orders_created || 0} orders created</span>
                  </div>
                  <div className="text-xs text-gray-400">
                    Total: {orchStep.total_quantity || 0} units
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="text-sm text-gray-400">
      <pre className="bg-gray-700 p-4 rounded overflow-auto text-gray-300 border border-gray-600">
        {JSON.stringify(stepData, null, 2)}
      </pre>
    </div>
  );
}

// Alerts Monitor Component
function AlertsMonitor({ alerts }: { alerts: Alert[] }) {
  return (
    <Card className="bg-gray-800 border-gray-700">
      <CardHeader>
        <CardTitle className="flex items-center space-x-2 text-white">
          <AlertTriangle className="h-5 w-5 text-red-400" />
          <span>Active Alerts Monitor</span>
        </CardTitle>
        <CardDescription className="text-gray-400">
          Real-time monitoring of supply chain alerts and inventory issues
        </CardDescription>
      </CardHeader>
      <CardContent>
        {alerts.length === 0 ? (
          <div className="text-center py-8">
            <CheckCircle className="h-12 w-12 text-green-400 mx-auto mb-4" />
            <p className="text-lg font-semibold text-gray-300">No Active Alerts</p>
            <p className="text-sm text-gray-500">All inventory levels are within acceptable ranges</p>
          </div>
        ) : (
          <div className="space-y-4">
            {alerts.map((alert) => (
              <div key={alert.alert_id} className="flex items-center justify-between p-4 border border-gray-600 rounded-lg bg-gray-700">
                <div className="flex items-center space-x-4">
                  <div className="flex flex-col items-center">
                    <Package className="h-8 w-8 text-blue-400" />
                    <Badge variant={getPriorityColor(alert.priority)} className="mt-1 text-xs bg-red-600 text-white">
                      {alert.priority}
                    </Badge>
                  </div>
                  <div>
                    <h4 className="font-semibold text-white">{alert.product}</h4>
                    <p className="text-sm text-gray-400">{alert.company}</p>
                    <p className="text-xs text-gray-500">
                      Detected: {new Date(alert.detected_at).toLocaleString()}
                    </p>
                  </div>
                </div>
                <div className="text-right">
                  <div className="text-2xl font-bold text-red-400">{alert.current_stock}</div>
                  <div className="text-sm text-gray-400">units remaining</div>
                  <Badge variant={alert.status === 'detected' ? 'destructive' : 'default'} className="mt-1 bg-blue-600 text-white">
                    {alert.status}
                  </Badge>
                </div>
              </div>
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  );
}

// Execution History Component
function ExecutionHistory({ executions, onSelect }: { executions: WorkflowExecution[], onSelect: (exec: WorkflowExecution) => void }) {
  return (
    <Card className="bg-gray-800 border-gray-700">
      <CardHeader>
        <CardTitle className="flex items-center space-x-2 text-white">
          <Clock className="h-5 w-5 text-blue-400" />
          <span>Execution History</span>
        </CardTitle>
        <CardDescription className="text-gray-400">
          Complete history of LOGI-BOT workflow executions and results
        </CardDescription>
      </CardHeader>
      <CardContent>
        {executions.length === 0 ? (
          <div className="text-center py-8">
            <Activity className="h-12 w-12 text-gray-500 mx-auto mb-4" />
            <p className="text-lg font-semibold text-gray-300">No Executions Yet</p>
            <p className="text-sm text-gray-500">Trigger a workflow to see execution history</p>
          </div>
        ) : (
          <div className="space-y-4">
            {executions.map((execution) => (
              <div 
                key={execution.execution_id} 
                className="flex items-center justify-between p-4 border border-gray-600 rounded-lg bg-gray-700 hover:bg-gray-600 cursor-pointer transition-colors"
                onClick={() => onSelect(execution)}
              >
                <div className="flex items-center space-x-4">
                  <div className="flex flex-col items-center">
                    <Bot className="h-8 w-8 text-blue-400" />
                    <Badge variant={execution.status === 'completed' ? 'default' : 'destructive'} className="mt-1 text-xs bg-blue-600 text-white">
                      {execution.status}
                    </Badge>
                  </div>
                  <div>
                    <h4 className="font-semibold text-white">{execution.product_name}</h4>
                    <p className="text-sm text-gray-400">
                      {(execution.workflow_steps || []).length} steps • {(execution.workflow_steps || []).filter(s => s.status === 'completed').length} completed
                    </p>
                    <p className="text-xs text-gray-500">
                      {new Date(execution.started_at).toLocaleString()}
                    </p>
                  </div>
                </div>
                <div className="flex items-center space-x-2">
                  <Eye className="h-4 w-4 text-gray-400" />
                  <span className="text-sm text-gray-400">View Details</span>
                </div>
              </div>
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  );
}
