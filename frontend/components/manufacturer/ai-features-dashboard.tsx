/**
 * Advanced AI Features Dashboard for LOGI-BOT
 * 
 * This component provides a comprehensive interface for all AI-powered features:
 * - Multilingual Communication
 * - Document Intelligence & OCR
 * - Voice Commands  
 * - Predictive Analytics
 * - Smart Document Generation
 * - Intelligent Workflows
 */

'use client'

import React, { useState, useEffect, useRef } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Textarea } from '@/components/ui/textarea'
import { Badge } from '@/components/ui/badge'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { 
  Mic, MicOff, Upload, FileText, Globe, BarChart3, 
  Workflow, Brain, Zap, MessageSquare, Camera,
  Play, Pause, Download, Eye, Sparkles
} from 'lucide-react'

interface AIFeature {
  id: string
  name: string
  description: string
  icon: React.ElementType
  available: boolean
  category: 'communication' | 'intelligence' | 'automation' | 'analytics'
}

interface VoiceCommandResult {
  transcript: string
  command_executed: {
    action: string
    message: string
  }
  voice_response?: {
    audio_content: string
    text: string
  }
}

interface DocumentAnalysisResult {
  status: string
  confidence: number
  extracted_data: Record<string, any>
  insights: string[]
}

export default function AIFeaturesPanel() {
  // State management
  const [activeFeature, setActiveFeature] = useState<string>('overview')
  const [isRecording, setIsRecording] = useState(false)
  const [voiceResult, setVoiceResult] = useState<VoiceCommandResult | null>(null)
  const [documentResult, setDocumentResult] = useState<DocumentAnalysisResult | null>(null)
  const [predictiveData, setPredictiveData] = useState<any>(null)
  const [loading, setLoading] = useState<Record<string, boolean>>({})
  const [aiStatus, setAiStatus] = useState<any>(null)

  // Refs
  const mediaRecorderRef = useRef<MediaRecorder | null>(null)
  const audioChunksRef = useRef<Blob[]>([])
  const fileInputRef = useRef<HTMLInputElement>(null)

  // Available AI Features
  const aiFeatures: AIFeature[] = [
    {
      id: 'multilingual',
      name: 'Multilingual Communication',
      description: 'Send supplier alerts in multiple languages instantly',
      icon: Globe,
      available: true,
      category: 'communication'
    },
    {
      id: 'document_ai',
      name: 'Document Intelligence',
      description: 'OCR and AI analysis for invoices, contracts, and documents',
      icon: FileText,
      available: true,
      category: 'intelligence'
    },
    {
      id: 'voice_commands',
      name: 'Voice Commands',
      description: 'Control LOGI-BOT with natural voice commands',
      icon: Mic,
      available: true,
      category: 'intelligence'
    },
    {
      id: 'predictive_analytics',
      name: 'Predictive Analytics',
      description: 'AI-powered demand forecasting and risk analysis',
      icon: BarChart3,
      available: true,
      category: 'analytics'
    },
    {
      id: 'smart_documents',
      name: 'Smart Document Generation',
      description: 'Auto-generate contracts, reports, and summaries',
      icon: Brain,
      available: true,
      category: 'automation'
    },
    {
      id: 'intelligent_workflows',
      name: 'Intelligent Workflows',
      description: 'Self-adapting automation with AI decision-making',
      icon: Workflow,
      available: true,
      category: 'automation'
    }
  ]

  // Load AI status on component mount
  useEffect(() => {
    loadAIStatus()
  }, [])

  const loadAIStatus = async () => {
    try {
      setLoading(prev => ({ ...prev, status: true }))
      const token = localStorage.getItem('token')
      
      const response = await fetch('/api/agent/ai/enhanced-status/', {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      })
      
      if (response.ok) {
        const data = await response.json()
        setAiStatus(data.agent_status)
      }
    } catch (error) {
      console.error('Failed to load AI status:', error)
    } finally {
      setLoading(prev => ({ ...prev, status: false }))
    }
  }

  // ===================== VOICE COMMANDS =====================

  const startVoiceRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
      
      const mediaRecorder = new MediaRecorder(stream, {
        mimeType: 'audio/webm;codecs=opus'
      })
      
      mediaRecorderRef.current = mediaRecorder
      audioChunksRef.current = []
      
      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunksRef.current.push(event.data)
        }
      }
      
      mediaRecorder.onstop = processVoiceCommand
      
      mediaRecorder.start()
      setIsRecording(true)
      
    } catch (error) {
      console.error('Voice recording failed:', error)
      alert('Voice recording not supported or permission denied')
    }
  }

  const stopVoiceRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop()
      setIsRecording(false)
      
      // Stop all tracks
      mediaRecorderRef.current.stream?.getTracks().forEach(track => track.stop())
    }
  }

  const processVoiceCommand = async () => {
    try {
      setLoading(prev => ({ ...prev, voice: true }))
      
      const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/webm' })
      const audioBase64 = await blobToBase64(audioBlob)
      
      const token = localStorage.getItem('token')
      const response = await fetch('/api/agent/ai/voice-command/', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          audio_data: audioBase64,
          context: {
            location: 'dashboard',
            user_interface: 'web_app'
          }
        })
      })
      
      if (response.ok) {
        const data = await response.json()
        setVoiceResult(data.voice_command_result)
        
        // Play voice response if available
        if (data.voice_command_result?.voice_response?.audio_content) {
          playAudioResponse(data.voice_command_result.voice_response.audio_content)
        }
      } else {
        throw new Error('Voice command processing failed')
      }
    } catch (error) {
      console.error('Voice processing error:', error)
      alert('Failed to process voice command')
    } finally {
      setLoading(prev => ({ ...prev, voice: false }))
    }
  }

  const playAudioResponse = (audioBase64: string) => {
    try {
      const audioData = atob(audioBase64)
      const audioArray = new Uint8Array(audioData.length)
      for (let i = 0; i < audioData.length; i++) {
        audioArray[i] = audioData.charCodeAt(i)
      }
      
      const audioBlob = new Blob([audioArray], { type: 'audio/mp3' })
      const audioUrl = URL.createObjectURL(audioBlob)
      const audio = new Audio(audioUrl)
      audio.play()
    } catch (error) {
      console.error('Audio playback failed:', error)
    }
  }

  // ===================== DOCUMENT INTELLIGENCE =====================

  const handleDocumentUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (file) {
      processDocument(file)
    }
  }

  const processDocument = async (file: File) => {
    try {
      setLoading(prev => ({ ...prev, document: true }))
      
      const imageBase64 = await fileToBase64(file)
      const token = localStorage.getItem('token')
      
      const response = await fetch('/api/agent/ai/analyze-document/', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          image_data: imageBase64,
          document_type: detectDocumentType(file.name),
          metadata: {
            filename: file.name,
            size: file.size,
            upload_source: 'ai_dashboard'
          }
        })
      })
      
      if (response.ok) {
        const data = await response.json()
        setDocumentResult(data.document_analysis)
      } else {
        throw new Error('Document analysis failed')
      }
    } catch (error) {
      console.error('Document processing error:', error)
      alert('Failed to process document')
    } finally {
      setLoading(prev => ({ ...prev, document: false }))
    }
  }

  // ===================== MULTILINGUAL COMMUNICATION =====================

  const sendMultilingualAlert = async (productId: string, languages: string[]) => {
    try {
      setLoading(prev => ({ ...prev, multilingual: true }))
      const token = localStorage.getItem('token')
      
      const response = await fetch('/api/agent/ai/multilingual-alert/', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          product_id: productId,
          alert_type: 'critical_shortage',
          target_languages: languages,
          custom_message: 'AI-powered multilingual alert from dashboard'
        })
      })
      
      if (response.ok) {
        const data = await response.json()
        alert(`Multilingual alert sent to ${data.total_suppliers_contacted} suppliers in ${languages.length} languages!`)
      } else {
        throw new Error('Multilingual alert failed')
      }
    } catch (error) {
      console.error('Multilingual alert error:', error)
      alert('Failed to send multilingual alert')
    } finally {
      setLoading(prev => ({ ...prev, multilingual: false }))
    }
  }

  // ===================== PREDICTIVE ANALYTICS =====================

  const generatePredictiveReport = async () => {
    try {
      setLoading(prev => ({ ...prev, analytics: true }))
      const token = localStorage.getItem('token')
      
      const response = await fetch('/api/agent/ai/predictive-analytics/?timeframe_days=30', {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      })
      
      if (response.ok) {
        const data = await response.json()
        setPredictiveData(data.predictive_report)
      } else {
        throw new Error('Predictive analytics failed')
      }
    } catch (error) {
      console.error('Predictive analytics error:', error)
      alert('Failed to generate predictive report')
    } finally {
      setLoading(prev => ({ ...prev, analytics: false }))
    }
  }

  // ===================== UTILITY FUNCTIONS =====================

  const blobToBase64 = (blob: Blob): Promise<string> => {
    return new Promise((resolve, reject) => {
      const reader = new FileReader()
      reader.onloadend = () => {
        const base64String = reader.result as string
        resolve(base64String.split(',')[1]) // Remove data URL prefix
      }
      reader.onerror = reject
      reader.readAsDataURL(blob)
    })
  }

  const fileToBase64 = (file: File): Promise<string> => {
    return new Promise((resolve, reject) => {
      const reader = new FileReader()
      reader.onloadend = () => {
        const base64String = reader.result as string
        resolve(base64String.split(',')[1]) // Remove data URL prefix
      }
      reader.onerror = reject
      reader.readAsDataURL(file)
    })
  }

  const detectDocumentType = (filename: string): string => {
    const lower = filename.toLowerCase()
    if (lower.includes('invoice')) return 'invoice'
    if (lower.includes('contract')) return 'contract'
    if (lower.includes('order')) return 'purchase_order'
    if (lower.includes('ship')) return 'shipping_document'
    return 'communication'
  }

  return (
    <div className="min-h-screen bg-gray-900 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center space-x-3 mb-4">
            <div className="p-2 bg-gradient-to-r from-purple-600 to-blue-600 rounded-lg">
              <Sparkles className="h-8 w-8 text-white" />
            </div>
            <div>
              <h1 className="text-3xl font-bold text-white">LOGI-BOT AI Features</h1>
              <p className="text-gray-400">Advanced AI-powered supply chain automation</p>
            </div>
          </div>
          
          {/* AI Status */}
          {aiStatus && (
            <Card className="mb-6 bg-gray-800 border-gray-700">
              <CardHeader>
                <CardTitle className="flex items-center space-x-2 text-white">
                  <Brain className="h-5 w-5 text-purple-400" />
                  <span>AI System Status</span>
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                  <div className="text-center">
                    <div className="text-2xl font-bold text-green-400">
                      {aiStatus.total_executions || 0}
                    </div>
                    <div className="text-sm text-gray-400">Total Executions</div>
                  </div>
                  <div className="text-center">
                    <div className="text-2xl font-bold text-blue-400">
                      {aiStatus.ai_features?.advanced_features_enabled?.length || 0}
                    </div>
                    <div className="text-sm text-gray-400">AI Features</div>
                  </div>
                  <div className="text-center">
                    <div className="text-2xl font-bold text-purple-400">
                      {aiStatus.ai_features?.ai_capabilities?.languages_supported?.length || 0}
                    </div>
                    <div className="text-sm text-gray-400">Languages</div>
                  </div>
                  <div className="text-center">
                    <Badge variant={aiStatus.ai_features?.google_cloud_integration ? 'default' : 'secondary'} className="bg-blue-600 text-white">
                      {aiStatus.ai_features?.google_cloud_integration ? 'Google Cloud Active' : 'Local Mode'}
                    </Badge>
                  </div>
                </div>
              </CardContent>
            </Card>
          )}
        </div>

        {/* AI Features Tabs */}
        <Tabs value={activeFeature} onValueChange={setActiveFeature}>
          <TabsList className="grid w-full grid-cols-6 bg-gray-800 border-gray-700">
            <TabsTrigger value="overview" className="data-[state=active]:bg-blue-600 data-[state=active]:text-white text-gray-400">Overview</TabsTrigger>
            <TabsTrigger value="voice" className="data-[state=active]:bg-blue-600 data-[state=active]:text-white text-gray-400">Voice</TabsTrigger>
            <TabsTrigger value="documents" className="data-[state=active]:bg-blue-600 data-[state=active]:text-white text-gray-400">Documents</TabsTrigger>
            <TabsTrigger value="multilingual" className="data-[state=active]:bg-blue-600 data-[state=active]:text-white text-gray-400">Multilingual</TabsTrigger>
            <TabsTrigger value="analytics" className="data-[state=active]:bg-blue-600 data-[state=active]:text-white text-gray-400">Analytics</TabsTrigger>
            <TabsTrigger value="workflows" className="data-[state=active]:bg-blue-600 data-[state=active]:text-white text-gray-400">Workflows</TabsTrigger>
          </TabsList>

          {/* Overview Tab */}
          <TabsContent value="overview" className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {aiFeatures.map((feature) => {
                const Icon = feature.icon
                return (
                  <Card key={feature.id} className="hover:shadow-lg transition-shadow bg-gray-800 border-gray-700">
                    <CardHeader>
                      <CardTitle className="flex items-center space-x-2 text-white">
                        <Icon className="h-5 w-5 text-blue-400" />
                        <span>{feature.name}</span>
                      </CardTitle>
                      <CardDescription className="text-gray-400">{feature.description}</CardDescription>
                    </CardHeader>
                    <CardContent>
                      <div className="flex items-center justify-between">
                        <Badge variant={feature.available ? 'default' : 'secondary'} className="bg-blue-600 text-white">
                          {feature.available ? 'Available' : 'Coming Soon'}
                        </Badge>
                        <Badge variant="outline" className="border-gray-600 text-gray-300">
                          {feature.category}
                        </Badge>
                      </div>
                    </CardContent>
                  </Card>
                )
              })}
            </div>
          </TabsContent>

          {/* Voice Commands Tab */}
          <TabsContent value="voice" className="space-y-6">
            <Card className="bg-gray-800 border-gray-700">
              <CardHeader>
                <CardTitle className="flex items-center space-x-2 text-white">
                  <Mic className="h-5 w-5 text-green-400" />
                  <span>Voice Command Center</span>
                </CardTitle>
                <CardDescription className="text-gray-400">
                  Control LOGI-BOT with natural voice commands
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex items-center space-x-4">
                  <Button
                    onClick={isRecording ? stopVoiceRecording : startVoiceRecording}
                    disabled={loading.voice}
                    variant={isRecording ? "destructive" : "default"}
                    size="lg"
                    className={isRecording ? "" : "bg-blue-600 hover:bg-blue-700 text-white"}
                  >
                    {isRecording ? (
                      <>
                        <MicOff className="h-5 w-5 mr-2" />
                        Stop Recording
                      </>
                    ) : (
                      <>
                        <Mic className="h-5 w-5 mr-2" />
                        Start Voice Command
                      </>
                    )}
                  </Button>
                  
                  {isRecording && (
                    <div className="flex items-center space-x-2 text-red-400">
                      <div className="w-3 h-3 bg-red-500 rounded-full animate-pulse"></div>
                      <span>Listening...</span>
                    </div>
                  )}
                </div>

                {/* Voice Command Examples */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-6">
                  <div>
                    <h4 className="font-semibold mb-2 text-white">Try these commands:</h4>
                    <ul className="space-y-1 text-sm text-gray-400">
                      <li>• "Check stock for steel rods"</li>
                      <li>• "Create alert for limestone shortage"</li>
                      <li>• "Schedule emergency meeting"</li>
                      <li>• "Show me recent orders"</li>
                    </ul>
                  </div>
                  
                  {voiceResult && (
                    <div>
                      <h4 className="font-semibold mb-2 text-white">Last Command:</h4>
                      <div className="bg-gray-700 p-3 rounded-lg text-sm text-gray-300">
                        <p><strong>You said:</strong> {voiceResult.transcript}</p>
                        <p><strong>Action:</strong> {voiceResult.command_executed?.action}</p>
                        <p><strong>Response:</strong> {voiceResult.command_executed?.message}</p>
                      </div>
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Document Intelligence Tab */}
          <TabsContent value="documents" className="space-y-6">
            <Card className="bg-gray-800 border-gray-700">
              <CardHeader>
                <CardTitle className="flex items-center space-x-2 text-white">
                  <FileText className="h-5 w-5 text-blue-400" />
                  <span>Document Intelligence & OCR</span>
                </CardTitle>
                <CardDescription className="text-gray-400">
                  Upload and analyze invoices, contracts, and shipping documents
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="border-2 border-dashed border-gray-600 rounded-lg p-8 text-center bg-gray-700">
                  <input
                    type="file"
                    ref={fileInputRef}
                    onChange={handleDocumentUpload}
                    accept="image/*,.pdf"
                    className="hidden"
                  />
                  
                  <Camera className="h-12 w-12 mx-auto mb-4 text-gray-500" />
                  <p className="text-gray-400 mb-4">
                    Upload a document for AI analysis
                  </p>
                  <Button
                    onClick={() => fileInputRef.current?.click()}
                    disabled={loading.document}
                    className="bg-blue-600 hover:bg-blue-700 text-white"
                  >
                    <Upload className="h-4 w-4 mr-2" />
                    Choose Document
                  </Button>
                </div>

                {documentResult && (
                  <div className="bg-green-900 border border-green-700 rounded-lg p-4">
                    <h4 className="font-semibold text-green-400 mb-2">Analysis Complete</h4>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm text-gray-300">
                      <div>
                        <p><strong>Status:</strong> {documentResult.status}</p>
                        <p><strong>Confidence:</strong> {(documentResult.confidence * 100).toFixed(1)}%</p>
                      </div>
                      <div>
                        <p><strong>Data Extracted:</strong> {Object.keys(documentResult.extracted_data).length} fields</p>
                        <p><strong>AI Insights:</strong> {documentResult.insights.length} insights</p>
                      </div>
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>
          </TabsContent>

          {/* Multilingual Tab */}
          <TabsContent value="multilingual" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <Globe className="h-5 w-5 text-green-500" />
                  <span>Multilingual Supplier Communication</span>
                </CardTitle>
                <CardDescription>
                  Send alerts to international suppliers in their native languages
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid grid-cols-2 md:grid-cols-4 gap-2">
                  {['🇪🇸 Spanish', '🇫🇷 French', '🇩🇪 German', '🇨🇳 Chinese', 
                    '🇯🇵 Japanese', '🇮🇹 Italian', '🇵🇹 Portuguese', '🇰🇷 Korean'].map((lang) => (
                    <Badge key={lang} variant="outline" className="justify-center p-2">
                      {lang}
                    </Badge>
                  ))}
                </div>
                
                <Button
                  onClick={() => sendMultilingualAlert('STEEL_001', ['es', 'fr', 'de', 'zh'])}
                  disabled={loading.multilingual}
                  className="w-full"
                >
                  <MessageSquare className="h-4 w-4 mr-2" />
                  Send Demo Multilingual Alert
                </Button>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Predictive Analytics Tab */}
          <TabsContent value="analytics" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <BarChart3 className="h-5 w-5 text-purple-500" />
                  <span>Predictive Analytics</span>
                </CardTitle>
                <CardDescription>
                  AI-powered demand forecasting and supply chain risk analysis
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <Button
                  onClick={generatePredictiveReport}
                  disabled={loading.analytics}
                  size="lg"
                >
                  <Zap className="h-4 w-4 mr-2" />
                  Generate Predictive Report
                </Button>

                {predictiveData && (
                  <div className="bg-purple-50 border border-purple-200 rounded-lg p-4">
                    <h4 className="font-semibold text-purple-800 mb-2">Predictive Report Generated</h4>
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
                      <div>
                        <p><strong>Status:</strong> {predictiveData.status}</p>
                        <p><strong>Timeframe:</strong> {predictiveData.timeframe_days} days</p>
                      </div>
                      <div>
                        <p><strong>Predictions:</strong> {Object.keys(predictiveData.predictions || {}).length}</p>
                        <p><strong>Recommendations:</strong> {predictiveData.recommendations?.length || 0}</p>
                      </div>
                      <div>
                        <p><strong>Generated:</strong> {new Date(predictiveData.generated_at).toLocaleString()}</p>
                      </div>
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>
          </TabsContent>

          {/* Intelligent Workflows Tab */}
          <TabsContent value="workflows" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <Workflow className="h-5 w-5 text-orange-500" />
                  <span>Intelligent Workflows</span>
                </CardTitle>
                <CardDescription>
                  Create self-adapting automation with AI decision-making
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <h4 className="font-semibold mb-2">Workflow Types:</h4>
                    <ul className="space-y-1 text-sm text-gray-600">
                      <li>• Emergency Replenishment</li>
                      <li>• Supplier Communication</li>
                      <li>• Risk Mitigation</li>
                      <li>• Demand Response</li>
                    </ul>
                  </div>
                  <div>
                    <h4 className="font-semibold mb-2">AI Capabilities:</h4>
                    <ul className="space-y-1 text-sm text-gray-600">
                      <li>• Self-adaptation</li>
                      <li>• Cross-platform orchestration</li>
                      <li>• Intelligent routing</li>
                      <li>• Predictive triggers</li>
                    </ul>
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  )
}