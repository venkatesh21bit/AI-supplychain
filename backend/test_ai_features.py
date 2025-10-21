"""
Test script for Advanced LOGI-BOT AI Features

This script demonstrates and tests all the new AI-powered capabilities.
"""

import os
import sys
import django
import json
import base64
import requests
import asyncio
from datetime import datetime

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'main.settings')
django.setup()

from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
from app.models import Product, Company

# Import AI configuration
sys.path.append(os.path.dirname(__file__))
from ai_config import validate_ai_configuration, GOOGLE_CLOUD_API_KEY

User = get_user_model()

class AIFeaturesDemo:
    """Demonstration of Advanced LOGI-BOT AI Features."""
    
    def __init__(self):
        """Initialize demo with authentication."""
        self.base_url = "http://localhost:8000/api"
        self.token = self._get_auth_token()
        self.headers = {
            'Authorization': f'Bearer {self.token}',
            'Content-Type': 'application/json'
        }
        
        # Check AI configuration
        self.config = validate_ai_configuration()
        print("🤖 Advanced LOGI-BOT AI Features Demo")
        print("=" * 50)
        print(f"Configuration Valid: {self.config['valid']}")
        print(f"Available Features: {self.config['features_available']}")
        if self.config['errors']:
            print(f"⚠️ Errors: {self.config['errors']}")
        if self.config['warnings']:
            print(f"⚠️ Warnings: {self.config['warnings']}")
        print()
    
    def _get_auth_token(self):
        """Get authentication token."""
        user = User.objects.filter(username='admin_constructco').first()
        if not user:
            user = User.objects.filter(is_superuser=True).first()
        
        refresh = RefreshToken.for_user(user)
        return str(refresh.access_token)
    
    def run_all_demos(self):
        """Run all AI feature demonstrations."""
        print("🚀 Starting AI Features Demonstration...")
        print()
        
        # 1. Enhanced Agent Status
        self.demo_enhanced_status()
        
        # 2. Multilingual Communication
        if self.config['features_available']['multilingual']:
            self.demo_multilingual_communication()
        
        # 3. Document Intelligence
        if self.config['features_available']['document_ai']:
            self.demo_document_intelligence()
        
        # 4. Voice Commands
        if self.config['features_available']['voice_commands']:
            self.demo_voice_commands()
        
        # 5. Predictive Analytics
        if self.config['features_available']['predictive_analytics']:
            self.demo_predictive_analytics()
        
        # 6. Smart Document Generation
        self.demo_smart_document_generation()
        
        # 7. Intelligent Workflows
        self.demo_intelligent_workflows()
        
        print("✅ All AI Features Demo Completed!")
    
    def demo_enhanced_status(self):
        """Demo: Enhanced agent status with AI capabilities."""
        print("📊 ENHANCED AGENT STATUS")
        print("-" * 30)
        
        try:
            response = requests.get(
                f"{self.base_url}/agent/ai/enhanced-status/",
                headers=self.headers,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                status = data.get('agent_status', {})
                
                print(f"Agent: {status.get('agent', 'LOGI-BOT')}")
                print(f"Version: {status.get('version', 'Unknown')}")
                print(f"Total Executions: {status.get('total_executions', 0)}")
                
                ai_features = status.get('ai_features', {})
                if ai_features:
                    print("🤖 AI Features:")
                    print(f"  Google Cloud: {ai_features.get('google_cloud_integration', False)}")
                    print(f"  Enabled Features: {len(ai_features.get('advanced_features_enabled', []))}")
                    print(f"  Supported Languages: {len(ai_features.get('ai_capabilities', {}).get('languages_supported', []))}")
            else:
                print(f"❌ Status check failed: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Error: {str(e)}")
        
        print()
    
    def demo_multilingual_communication(self):
        """Demo: Multilingual supplier alerts."""
        print("🌍 MULTILINGUAL SUPPLIER COMMUNICATION")
        print("-" * 40)
        
        # Get a test product
        product = Product.objects.filter(available_quantity__lt=50).first()
        if not product:
            print("❌ No products with low stock found for demo")
            return
        
        try:
            payload = {
                "product_id": product.product_id,
                "alert_type": "critical_shortage",
                "target_languages": ["es", "fr", "de", "zh"],
                "custom_message": "DEMO: Testing multilingual AI communication"
            }
            
            print(f"Sending multilingual alert for: {product.name}")
            print(f"Target languages: {payload['target_languages']}")
            
            response = requests.post(
                f"{self.base_url}/agent/ai/multilingual-alert/",
                headers=self.headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                result = data.get('multilingual_result', {})
                
                print(f"✅ Alert sent successfully!")
                print(f"Languages processed: {result.get('successful_languages', 0)}")
                print(f"Total suppliers contacted: {data.get('total_suppliers_contacted', 0)}")
                
                # Show translation samples
                translations = result.get('translations', [])
                for trans in translations[:2]:  # Show first 2
                    if trans.get('translation_success'):
                        print(f"  📧 {trans['language'].upper()}: Alert sent to {trans.get('suppliers_contacted', 0)} suppliers")
            else:
                print(f"❌ Multilingual alert failed: {response.status_code}")
                print(f"Response: {response.text}")
                
        except Exception as e:
            print(f"❌ Error: {str(e)}")
        
        print()
    
    def demo_document_intelligence(self):
        """Demo: Document intelligence and OCR."""
        print("📄 DOCUMENT INTELLIGENCE & OCR")  
        print("-" * 35)
        
        try:
            # Create a simple test image (simulated invoice)
            test_image_data = self._create_test_invoice_image()
            
            payload = {
                "image_data": test_image_data,
                "document_type": "invoice",
                "metadata": {
                    "supplier_name": "Demo Steel Supplier",
                    "upload_source": "ai_demo_test"
                }
            }
            
            print("Analyzing test invoice document...")
            print("Document type: Invoice")
            print("Supplier: Demo Steel Supplier")
            
            response = requests.post(
                f"{self.base_url}/agent/ai/analyze-document/",
                headers=self.headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                analysis = data.get('document_analysis', {})
                
                print(f"✅ Document analyzed successfully!")
                print(f"Status: {analysis.get('status', 'Unknown')}")
                print(f"Confidence: {analysis.get('confidence', 0):.2%}")
                
                extracted_data = analysis.get('extracted_data', {})
                if extracted_data:
                    print(f"📊 Extracted Data: {len(extracted_data)} fields found")
                
                insights = analysis.get('insights', [])
                if insights:
                    print(f"💡 AI Insights: {len(insights)} insights generated")
            else:
                print(f"❌ Document analysis failed: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Error: {str(e)}")
        
        print()
    
    def demo_voice_commands(self):
        """Demo: Voice command processing."""
        print("🎤 VOICE COMMAND PROCESSING")
        print("-" * 30)
        
        try:
            # Create simulated audio data (in real implementation, this would be recorded audio)
            test_audio_data = self._create_test_audio_data()
            
            payload = {
                "audio_data": test_audio_data,
                "context": {
                    "location": "warehouse_demo",
                    "department": "inventory_management"
                }
            }
            
            print("Processing voice command: 'Check stock for steel products'")
            
            response = requests.post(
                f"{self.base_url}/agent/ai/voice-command/",
                headers=self.headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                result = data.get('voice_command_result', {})
                
                print(f"✅ Voice command processed!")
                print(f"Transcript: {result.get('transcript', 'N/A')}")
                
                command_executed = result.get('command_executed', {})
                if command_executed:
                    print(f"Action: {command_executed.get('action', 'Unknown')}")
                    print(f"Message: {command_executed.get('message', 'No message')}")
                
                voice_response = result.get('voice_response', {})
                if voice_response and voice_response.get('success'):
                    print("🔊 Voice response generated successfully")
            else:
                print(f"❌ Voice command failed: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Error: {str(e)}")
        
        print()
    
    def demo_predictive_analytics(self):
        """Demo: Predictive analytics report."""
        print("📈 PREDICTIVE ANALYTICS")
        print("-" * 25)
        
        try:
            params = {
                'timeframe_days': 30,
                'report_type': 'full'
            }
            
            print("Generating predictive analytics report...")
            print(f"Timeframe: {params['timeframe_days']} days")
            
            response = requests.get(
                f"{self.base_url}/agent/ai/predictive-analytics/",
                headers=self.headers,
                params=params,
                timeout=45
            )
            
            if response.status_code == 200:
                data = response.json()
                report = data.get('predictive_report', {})
                
                print(f"✅ Predictive report generated!")
                print(f"Status: {report.get('status', 'Unknown')}")
                print(f"Generated at: {report.get('generated_at', 'N/A')}")
                
                predictions = report.get('predictions', {})
                if predictions:
                    print(f"📊 Predictions Available:")
                    for pred_type, pred_data in predictions.items():
                        print(f"  • {pred_type.replace('_', ' ').title()}")
                
                ai_insights = report.get('ai_insights', {})
                if ai_insights:
                    high_priority = ai_insights.get('high_priority_actions', [])
                    print(f"⚡ High Priority Actions: {len(high_priority)}")
                
                recommendations = report.get('recommendations', [])
                if recommendations:
                    print(f"💡 Recommendations: {len(recommendations)}")
                    for rec in recommendations[:2]:  # Show first 2
                        print(f"  • {rec.get('action', 'Unknown action')}")
            else:
                print(f"❌ Predictive analytics failed: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Error: {str(e)}")
        
        print()
    
    def demo_smart_document_generation(self):
        """Demo: Smart document generation."""
        print("📋 SMART DOCUMENT GENERATION")
        print("-" * 32)
        
        try:
            # Get a test product for the document
            product = Product.objects.first()
            
            payload = {
                "document_type": "executive_summary",
                "data": {
                    "product_id": product.product_id if product else "DEMO_001",
                    "report_period": "2025-Q1",
                    "summary_type": "inventory_status",
                    "include_predictions": True
                },
                "output_formats": ["html", "pdf"]
            }
            
            print("Generating executive summary document...")
            print(f"Document type: {payload['document_type']}")
            print(f"Output formats: {payload['output_formats']}")
            
            response = requests.post(
                f"{self.base_url}/agent/ai/generate-document/",
                headers=self.headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                doc_generation = data.get('document_generation', {})
                
                print(f"✅ Document generated successfully!")
                print(f"Status: {doc_generation.get('status', 'Unknown')}")
                
                available_formats = data.get('available_formats', [])
                if available_formats:
                    print(f"📄 Available formats: {', '.join(available_formats)}")
                
                download_links = data.get('download_links', {})
                if download_links:
                    print(f"🔗 Download links: {len(download_links)} formats ready")
            else:
                print(f"❌ Document generation failed: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Error: {str(e)}")
        
        print()
    
    def demo_intelligent_workflows(self):
        """Demo: Intelligent workflow creation."""
        print("⚡ INTELLIGENT WORKFLOWS")
        print("-" * 25)
        
        try:
            payload = {
                "trigger_conditions": {
                    "type": "inventory_threshold_demo",
                    "conditions": {
                        "product_categories": ["STEEL", "CEMENT"],
                        "threshold_percentage": 20,
                        "time_sensitive": True
                    }
                },
                "workflow_config": {
                    "auto_adapt": True,
                    "intelligence_level": "high",
                    "cross_platform": True,
                    "approval_required": False
                }
            }
            
            print("Creating intelligent workflow...")
            print(f"Trigger: {payload['trigger_conditions']['type']}")
            print(f"Intelligence level: {payload['workflow_config']['intelligence_level']}")
            
            response = requests.post(
                f"{self.base_url}/agent/ai/create-workflow/",
                headers=self.headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                workflow = data.get('workflow', {})
                
                print(f"✅ Workflow created successfully!")
                print(f"Workflow ID: {data.get('workflow_id', 'N/A')}")
                print(f"Status: {workflow.get('status', 'Unknown')}")
                
                deployment_status = data.get('deployment_status', 'Unknown')
                print(f"Deployment: {deployment_status}")
                
                workflow_design = workflow.get('workflow_design', {})
                if workflow_design:
                    print(f"🔧 Workflow designed with AI optimization")
            else:
                print(f"❌ Workflow creation failed: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Error: {str(e)}")
        
        print()
    
    def _create_test_invoice_image(self):
        """Create a test invoice image as base64."""
        # This would be a real image in production
        # For demo, we'll create a small placeholder
        test_data = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
        return test_data
    
    def _create_test_audio_data(self):
        """Create test audio data as base64."""
        # This would be real audio data in production
        # For demo, we'll create a placeholder
        test_audio = base64.b64encode(b"test_audio_data_placeholder").decode()
        return test_audio

def main():
    """Run the AI features demonstration."""
    demo = AIFeaturesDemo()
    
    if not demo.config['valid']:
        print("❌ AI Configuration is invalid!")
        print("Please check ai_config.py and set your Google Cloud API key.")
        print()
        print("Setup Instructions:")
        print("1. Get Google Cloud API key from: https://console.cloud.google.com/")
        print("2. Enable required APIs (Translation, Vision, Speech, etc.)")
        print("3. Set environment variable: GOOGLE_CLOUD_API_KEY")
        print("4. Run this demo again")
        return
    
    try:
        demo.run_all_demos()
    except KeyboardInterrupt:
        print("\n🛑 Demo interrupted by user")
    except Exception as e:
        print(f"\n❌ Demo failed with error: {str(e)}")

if __name__ == "__main__":
    main()