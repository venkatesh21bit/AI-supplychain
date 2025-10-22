"use client";

import React, { useState, useEffect } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { 
  Mail, MessageSquare, CheckSquare, Calendar, Sheet, Github, 
  Trello, MessageCircle, Users, FileText, Upload, Send,
  Activity, Settings, Zap, AlertCircle, CheckCircle2, XCircle
} from "lucide-react";
import { fetchWithAuth, API_URL } from "../../utils/auth_fn";

interface Integration {
  id: string;
  name: string;
  icon: React.ReactNode;
  description: string;
  connected: boolean;
  color: string;
}

interface IntegrationResult {
  success: boolean;
  message: string;
  data?: any;
}

export default function ComposioIntegrationsDashboard() {
  const [activeTab, setActiveTab] = useState("overview");
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState<IntegrationResult[]>([]);
  const [stats, setStats] = useState<any>(null);

  const [integrations, setIntegrations] = useState<Integration[]>([
    { id: "gmail", name: "Gmail", icon: <Mail className="h-5 w-5" />, description: "Send automated stock alerts via email", connected: false, color: "bg-red-500" },
    { id: "slack", name: "Slack", icon: <MessageSquare className="h-5 w-5" />, description: "Real-time team notifications for critical stock levels", connected: false, color: "bg-purple-500" },
    { id: "sheets", name: "Google Sheets", icon: <Sheet className="h-5 w-5" />, description: "Log and track inventory data automatically", connected: false, color: "bg-green-500" },
    { id: "calendar", name: "Google Calendar", icon: <Calendar className="h-5 w-5" />, description: "Schedule supplier meetings & inventory audits", connected: false, color: "bg-blue-500" },
    { id: "drive", name: "Google Drive", icon: <Upload className="h-5 w-5" />, description: "Store invoices, reports & documents", connected: false, color: "bg-yellow-500" },
  ]);

  useEffect(() => {
    fetchIntegrationStats();
    fetchAvailableIntegrations();
  }, []);

  const fetchIntegrationStats = async () => {
    try {
      const token = localStorage.getItem("access_token");
      const response = await fetch("http://127.0.0.1:8000/api/agent/composio/stats/", {
        headers: {
          "Authorization": `Bearer ${token}`,
        },
      });
      
      if (response.ok) {
        const data = await response.json();
        setStats(data.stats);
      }
    } catch (error) {
      console.error("Failed to fetch stats:", error);
    }
  };

  const fetchAvailableIntegrations = async () => {
    try {
      const token = localStorage.getItem("access_token");
      const response = await fetch("http://127.0.0.1:8000/api/integrations/available/", {
        headers: {
          "Authorization": `Bearer ${token}`,
        },
      });
      
      if (response.ok) {
        const data = await response.json();
        console.log("API Response:", data); // Debug log
        // Handle the API response format: {success: true, integrations: [...]}
        if (data.success && Array.isArray(data.integrations)) {
          setIntegrations(prevIntegrations => 
            prevIntegrations.map(integration => {
              const apiIntegration = data.integrations.find((i: any) => i.type === integration.id);
              if (apiIntegration) {
                return {
                  ...integration,
                  connected: apiIntegration.configured
                };
              }
              return integration;
            })
          );
        } else {
          console.error("API response format unexpected:", data);
        }
      } else {
        console.error("Failed to fetch integrations:", response.status, response.statusText);
      }
    } catch (error) {
      console.error("Error fetching integrations:", error);
    }
  };

  const sendGmail = async (formData: any) => {
    setLoading(true);
    try {
      const response = await fetchWithAuth(`${API_URL}/agent/composio/gmail-send/`, {
        method: "POST",
        body: JSON.stringify(formData),
      });
      
      const data = await response.json();
      setResults([...results, { success: data.success, message: data.message, data }]);
    } catch (error) {
      setResults([...results, { success: false, message: String(error) }]);
    } finally {
      setLoading(false);
    }
  };

  const sendSlackNotification = async (formData: any) => {
    setLoading(true);
    try {
      const response = await fetchWithAuth(`${API_URL}/agent/composio/slack-notify/`, {
        method: "POST",
        body: JSON.stringify(formData),
      });
      
      const data = await response.json();
      setResults([...results, { success: data.success, message: data.message, data }]);
    } catch (error) {
      setResults([...results, { success: false, message: String(error) }]);
    } finally {
      setLoading(false);
    }
  };

  const updateGoogleSheet = async (formData: any) => {
    setLoading(true);
    try {
      const response = await fetchWithAuth(`${API_URL}/agent/composio/sheets-update/`, {
        method: "POST",
        body: JSON.stringify(formData),
      });
      
      const data = await response.json();
      setResults([...results, { 
        success: data.success, 
        message: data.success 
          ? `✅ Google Sheet updated! ${data.rows_updated} row(s) added.`
          : `❌ Sheet update failed: ${data.message}`,
        data 
      }]);
    } catch (error) {
      setResults([...results, { success: false, message: `Sheet update error: ${String(error)}` }]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-900 text-white p-8">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center gap-3 mb-2">
            <Zap className="h-8 w-8 text-yellow-400" />
            <h1 className="text-3xl font-bold">Composio Integrations</h1>
          </div>
          <p className="text-gray-400">
            Automate your supply chain workflow across 12+ platforms
          </p>
        </div>

        {/* Stats Overview */}
        {stats && (
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
            <Card className="bg-gray-800 border-gray-700">
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-400">Total Integrations</p>
                    <p className="text-3xl font-bold text-white">{stats.total_integrations}</p>
                  </div>
                  <Activity className="h-8 w-8 text-blue-400" />
                </div>
              </CardContent>
            </Card>
            
            <Card className="bg-gray-800 border-gray-700">
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-400">Gmail Status</p>
                    <p className="text-sm font-medium text-white">
                      {stats.gmail_configured ? (
                        <Badge className="bg-green-600">Configured</Badge>
                      ) : (
                        <Badge className="bg-red-600">Not Setup</Badge>
                      )}
                    </p>
                  </div>
                  <Mail className="h-8 w-8 text-red-400" />
                </div>
              </CardContent>
            </Card>

            <Card className="bg-gray-800 border-gray-700">
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-400">API Status</p>
                    <p className="text-sm font-medium">
                      <Badge className="bg-green-600">{stats.api_key_status}</Badge>
                    </p>
                  </div>
                  <Settings className="h-8 w-8 text-gray-400" />
                </div>
              </CardContent>
            </Card>

            <Card className="bg-gray-800 border-gray-700">
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-400">Connected Apps</p>
                    <p className="text-3xl font-bold text-white">
                      {stats.connected_apps?.length || 0}
                    </p>
                  </div>
                  <CheckCircle2 className="h-8 w-8 text-green-400" />
                </div>
              </CardContent>
            </Card>
          </div>
        )}

        {/* Main Content */}
        <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
          <TabsList className="bg-gray-800 border-gray-700">
            <TabsTrigger value="overview">Overview</TabsTrigger>
            <TabsTrigger value="gmail">Gmail</TabsTrigger>
            <TabsTrigger value="slack">Slack</TabsTrigger>
            <TabsTrigger value="sheets">Google Sheets</TabsTrigger>
            <TabsTrigger value="calendar">Google Calendar</TabsTrigger>
            <TabsTrigger value="drive">Google Drive</TabsTrigger>
            <TabsTrigger value="results">Results</TabsTrigger>
          </TabsList>

          {/* Overview Tab */}
          <TabsContent value="overview">
            <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-4 gap-4">
              {integrations.map((integration) => (
                <Card
                  key={integration.id}
                  className="bg-gray-800 border-gray-700 hover:border-gray-600 transition-colors cursor-pointer"
                  onClick={() => setActiveTab(integration.id)}
                >
                  <CardContent className="p-6">
                    <div className="flex items-start justify-between mb-4">
                      <div className={`p-3 rounded-lg ${integration.color}`}>
                        {integration.icon}
                      </div>
                      {integration.connected ? (
                        <CheckCircle2 className="h-5 w-5 text-green-400" />
                      ) : (
                        <XCircle className="h-5 w-5 text-gray-600" />
                      )}
                    </div>
                    <h3 className="text-lg font-semibold text-white mb-1">
                      {integration.name}
                    </h3>
                    <p className="text-sm text-gray-400">{integration.description}</p>
                  </CardContent>
                </Card>
              ))}
            </div>
          </TabsContent>

          {/* Gmail Tab */}
          <TabsContent value="gmail">
            <GmailForm onSubmit={sendGmail} loading={loading} />
          </TabsContent>

          {/* Slack Tab */}
          <TabsContent value="slack">
            <SlackForm onSubmit={sendSlackNotification} loading={loading} />
          </TabsContent>

          {/* Google Sheets Tab */}
          <TabsContent value="sheets">
            <Card className="bg-gray-800 border-gray-700">
              <CardHeader>
                <CardTitle className="text-white">Google Sheets Integration</CardTitle>
                <p className="text-gray-400">Automatically log inventory alerts and actions to your tracking spreadsheet</p>
              </CardHeader>
              <CardContent className="space-y-6">
                
                {/* Demo Sheet Info */}
                <div className="bg-blue-900/20 border border-blue-700 rounded-lg p-4">
                  <h3 className="text-blue-400 font-medium mb-2">📊 Demo Sheet Template</h3>
                  <p className="text-gray-300 text-sm mb-3">
                    Create a Google Sheet with these headers for the demo:
                  </p>
                  <div className="bg-gray-900 rounded p-3 text-xs font-mono">
                    <div className="grid grid-cols-7 gap-2 text-gray-400">
                      <span>Timestamp</span>
                      <span>Product</span>
                      <span>Current</span>
                      <span>Min Stock</span>
                      <span>Status</span>
                      <span>Alert Type</span>
                      <span>Action</span>
                    </div>
                  </div>
                  <p className="text-gray-400 text-xs mt-2">
                    Sheet ID: 1qcdOOAGJ50HfWJFlrQ3WUcrq0kjSUauVt5eBQAtGkHw (configured)
                  </p>
                </div>

                {/* Test Sheet Update */}
                <div className="space-y-4">
                  <h3 className="text-white font-medium">🧪 Test Sheet Update</h3>
                  <form onSubmit={(e) => {
                    e.preventDefault();
                    const formData = new FormData(e.target as HTMLFormElement);
                    const testData = {
                      sheet_id: "1qcdOOAGJ50HfWJFlrQ3WUcrq0kjSUauVt5eBQAtGkHw",
                      range: "A4:G4",
                      data: [[
                        new Date().toLocaleString(),
                        formData.get('product') || "Steel Rods",
                        formData.get('current_stock') || "75",
                        formData.get('min_stock') || "100",
                        "LOW STOCK",
                        "Demo Alert",
                        "LOGI-BOT Response"
                      ]]
                    };
                    updateGoogleSheet(testData);
                  }} className="space-y-4">
                    
                    <div className="grid grid-cols-3 gap-4">
                      <div>
                        <label className="block text-sm font-medium text-gray-300 mb-2">Product Name</label>
                        <input
                          type="text"
                          name="product"
                          defaultValue="Steel Rods"
                          className="w-full bg-gray-700 border border-gray-600 rounded-lg px-3 py-2 text-white"
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-gray-300 mb-2">Current Stock</label>
                        <input
                          type="number"
                          name="current_stock"
                          defaultValue="75"
                          className="w-full bg-gray-700 border border-gray-600 rounded-lg px-3 py-2 text-white"
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-gray-300 mb-2">Min Stock</label>
                        <input
                          type="number"
                          name="min_stock"
                          defaultValue="100"
                          className="w-full bg-gray-700 border border-gray-600 rounded-lg px-3 py-2 text-white"
                        />
                      </div>
                    </div>

                    <Button 
                      type="submit" 
                      disabled={loading}
                      className="w-full bg-green-600 hover:bg-green-700"
                    >
                      {loading ? (
                        <>
                          <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                          Updating Sheet...
                        </>
                      ) : (
                        <>
                          <Sheet className="h-4 w-4 mr-2" />
                          Update Demo Sheet
                        </>
                      )}
                    </Button>
                  </form>
                </div>

                {/* Live Demo Preview */}
                <div className="bg-gray-900 border border-gray-700 rounded-lg p-4">
                  <h3 className="text-white font-medium mb-3">📈 Live Sheet Preview</h3>
                  <div className="text-xs space-y-2">
                    <div className="grid grid-cols-7 gap-2 font-mono text-gray-400 border-b border-gray-700 pb-2">
                      <span>Timestamp</span>
                      <span>Product</span>
                      <span>Current</span>
                      <span>Min</span>
                      <span>Status</span>
                      <span>Alert</span>
                      <span>Action</span>
                    </div>
                    <div className="grid grid-cols-7 gap-2 font-mono text-green-400">
                      <span>2024-10-22 09:00</span>
                      <span>Steel Rods</span>
                      <span>75</span>
                      <span>100</span>
                      <span>LOW</span>
                      <span>Inventory</span>
                      <span>Email Sent</span>
                    </div>
                    <div className="grid grid-cols-7 gap-2 font-mono text-gray-500">
                      <span>2024-10-22 08:30</span>
                      <span>Aluminum</span>
                      <span>250</span>
                      <span>200</span>
                      <span>OK</span>
                      <span>Monitor</span>
                      <span>None</span>
                    </div>
                  </div>
                  <p className="text-gray-400 text-xs mt-3">
                    🔗 <a href="https://docs.google.com/spreadsheets/d/1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms/edit" 
                         target="_blank" rel="noopener noreferrer" 
                         className="text-blue-400 hover:text-blue-300">
                      Open Live Sheet →
                    </a>
                  </p>
                </div>

              </CardContent>
            </Card>
          </TabsContent>

          {/* Google Calendar Tab */}
          <TabsContent value="calendar">
            <Card className="bg-gray-800 border-gray-700">
              <CardHeader>
                <CardTitle className="text-white">Configure Google Calendar</CardTitle>
                <p className="text-gray-400">Schedule supplier meetings and inventory audits</p>
              </CardHeader>
              <CardContent>
                <p className="text-gray-300">Configuration form coming soon. Use Settings page for now.</p>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Google Drive Tab */}
          <TabsContent value="drive">
            <Card className="bg-gray-800 border-gray-700">
              <CardHeader>
                <CardTitle className="text-white">Configure Google Drive</CardTitle>
                <p className="text-gray-400">Store invoices, reports and documents automatically</p>
              </CardHeader>
              <CardContent>
                <p className="text-gray-300">Configuration form coming soon. Use Settings page for now.</p>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Results Tab */}
          <TabsContent value="results">
            <Card className="bg-gray-800 border-gray-700">
              <CardHeader>
                <CardTitle>Execution Results</CardTitle>
                <CardDescription>Recent integration actions and their outcomes</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {results.length === 0 ? (
                    <div className="text-center py-8 text-gray-400">
                      <AlertCircle className="h-12 w-12 mx-auto mb-4" />
                      <p>No results yet. Execute an integration to see results here.</p>
                    </div>
                  ) : (
                    results.map((result, idx) => (
                      <div
                        key={idx}
                        className={`p-4 rounded-lg border ${
                          result.success
                            ? "bg-green-900/20 border-green-700"
                            : "bg-red-900/20 border-red-700"
                        }`}
                      >
                        <div className="flex items-start gap-3">
                          {result.success ? (
                            <CheckCircle2 className="h-5 w-5 text-green-400 mt-0.5" />
                          ) : (
                            <XCircle className="h-5 w-5 text-red-400 mt-0.5" />
                          )}
                          <div className="flex-1">
                            <p className="text-white font-medium">{result.message}</p>
                            {result.data && (
                              <pre className="mt-2 text-xs text-gray-400 overflow-auto">
                                {JSON.stringify(result.data, null, 2)}
                              </pre>
                            )}
                          </div>
                        </div>
                      </div>
                    ))
                  )}
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
}

// Form Components
function GmailForm({ onSubmit, loading }: { onSubmit: (data: any) => void; loading: boolean }) {
  const [formData, setFormData] = useState({
    to_email: "",
    subject: "",
    body: "",
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSubmit(formData);
  };

  return (
    <Card className="bg-gray-800 border-gray-700">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Mail className="h-5 w-5 text-red-400" />
          Send Gmail
        </CardTitle>
        <CardDescription>Send automated email notifications</CardDescription>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <Label htmlFor="to_email">Recipient Email</Label>
            <Input
              id="to_email"
              type="email"
              placeholder="recipient@example.com"
              value={formData.to_email}
              onChange={(e) => setFormData({ ...formData, to_email: e.target.value })}
              className="bg-gray-900 border-gray-700 text-white"
              required
            />
          </div>
          <div>
            <Label htmlFor="subject">Subject</Label>
            <Input
              id="subject"
              placeholder="Stock Alert: Low Inventory"
              value={formData.subject}
              onChange={(e) => setFormData({ ...formData, subject: e.target.value })}
              className="bg-gray-900 border-gray-700 text-white"
              required
            />
          </div>
          <div>
            <Label htmlFor="body">Message Body</Label>
            <textarea
              id="body"
              placeholder="Current stock for Steel Rods: 150 units..."
              value={formData.body}
              onChange={(e) => setFormData({ ...formData, body: e.target.value })}
              className="w-full h-32 px-3 py-2 bg-gray-900 border border-gray-700 rounded-md text-white"
              required
            />
          </div>
          <Button type="submit" disabled={loading} className="w-full bg-red-600 hover:bg-red-700">
            {loading ? "Sending..." : "Send Email"}
          </Button>
        </form>
      </CardContent>
    </Card>
  );
}

function SlackForm({ onSubmit, loading }: { onSubmit: (data: any) => void; loading: boolean }) {
  const [formData, setFormData] = useState({
    channel: "#general",
    message: "",
    urgency: "normal",
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSubmit(formData);
  };

  return (
    <Card className="bg-gray-800 border-gray-700">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <MessageSquare className="h-5 w-5 text-purple-400" />
          Send Slack Message
        </CardTitle>
        <CardDescription>Post notifications to Slack channels</CardDescription>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <Label htmlFor="channel">Channel</Label>
            <Input
              id="channel"
              placeholder="#supply-chain-alerts"
              value={formData.channel}
              onChange={(e) => setFormData({ ...formData, channel: e.target.value })}
              className="bg-gray-900 border-gray-700 text-white"
              required
            />
          </div>
          <div>
            <Label htmlFor="message">Message</Label>
            <textarea
              id="message"
              placeholder="Urgent: Stock levels are critically low..."
              value={formData.message}
              onChange={(e) => setFormData({ ...formData, message: e.target.value })}
              className="w-full h-32 px-3 py-2 bg-gray-900 border border-gray-700 rounded-md text-white"
              required
            />
          </div>
          <div>
            <Label htmlFor="urgency">Urgency</Label>
            <select
              id="urgency"
              value={formData.urgency}
              onChange={(e) => setFormData({ ...formData, urgency: e.target.value })}
              className="w-full px-3 py-2 bg-gray-900 border border-gray-700 rounded-md text-white"
            >
              <option value="low">Low</option>
              <option value="normal">Normal</option>
              <option value="high">High</option>
            </select>
          </div>
          <Button type="submit" disabled={loading} className="w-full bg-purple-600 hover:bg-purple-700">
            {loading ? "Sending..." : "Send to Slack"}
          </Button>
        </form>
      </CardContent>
    </Card>
  );
}
