#!/usr/bin/env python3
"""
Test AI Features with Live Django Server
"""
import os
import django
import requests
import json
from datetime import datetime

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'main.settings')
django.setup()

from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken

def get_auth_token():
    """Get JWT token for API authentication"""
    User = get_user_model()
    user = User.objects.filter(username='admin_constructco').first()
    if not user:
        user = User.objects.filter(is_superuser=True).first()
    
    refresh = RefreshToken.for_user(user)
    return str(refresh.access_token), user

def test_multilingual_alert(token):
    """Test multilingual alert translation"""
    print('🌍 Testing Multilingual Alert...')
    try:
        response = requests.post(
            'http://localhost:8000/api/agent/ai/multilingual-alert/',
            json={
                'message': 'URGENT: Critical stock shortage - Steel Rods need immediate restocking',
                'target_language': 'spanish',
                'supplier_name': 'Acero Internacional SA'
            },
            headers={
                'Authorization': f'Bearer {token}',
                'Content-Type': 'application/json'
            },
            timeout=30
        )
        if response.status_code == 200:
            result = response.json()
            print('✅ Translation Success!')
            print(f'Original: {result.get("original_message", "N/A")}')
            print(f'Spanish: {result.get("translated_message", "N/A")}')
            print(f'Supplier: {result.get("supplier_name", "N/A")}')
        else:
            print(f'❌ Error {response.status_code}: {response.text}')
    except Exception as e:
        print(f'❌ Request failed: {str(e)}')
    print()

def test_voice_command(token):
    """Test voice command processing"""
    print('🎤 Testing Voice Command Processing...')
    try:
        response = requests.post(
            'http://localhost:8000/api/agent/ai/voice-command/',
            json={
                'command_text': 'Check current stock levels for all steel products and create alert if any are below minimum threshold',
                'user_context': 'manufacturer_dashboard'
            },
            headers={
                'Authorization': f'Bearer {token}',
                'Content-Type': 'application/json'
            },
            timeout=30
        )
        if response.status_code == 200:
            result = response.json()
            print('✅ Voice Command Processed!')
            print(f'Action: {result.get("action", "N/A")}')
            print(f'Parameters: {result.get("parameters", "N/A")}')
            print(f'Response: {result.get("response", "N/A")}')
        else:
            print(f'❌ Error {response.status_code}: {response.text}')
    except Exception as e:
        print(f'❌ Request failed: {str(e)}')
    print()

def test_enhanced_status(token):
    """Test enhanced AI status"""
    print('⚡ Testing Enhanced AI Status...')
    try:
        response = requests.get(
            'http://localhost:8000/api/agent/ai/enhanced-status/',
            headers={
                'Authorization': f'Bearer {token}',
                'Content-Type': 'application/json'
            },
            timeout=30
        )
        if response.status_code == 200:
            result = response.json()
            print('✅ AI Status Retrieved!')
            print(f'Overall Status: {result.get("status", "N/A")}')
            print(f'Features Available: {len(result.get("features", []))}')
            print(f'Active Workflows: {result.get("active_workflows", 0)}')
            print(f'System Health: {result.get("system_health", "N/A")}')
        else:
            print(f'❌ Error {response.status_code}: {response.text}')
    except Exception as e:
        print(f'❌ Request failed: {str(e)}')
    print()

def test_document_analysis(token):
    """Test document analysis"""
    print('📄 Testing Document Analysis...')
    try:
        # Create a simple test document (base64 encoded)
        test_document = {
            'document_data': 'VGVzdCBJbnZvaWNlDQpTdXBwbGllcjogU3RlZWwgU3VwcGx5IENvcnANCkl0ZW06IFN0ZWVsIFJvZHMNCkFtb3VudDogMTAwMCB1bml0cw0KUHJpY2U6ICQ1MDAwDQpUb3RhbDogJDUwMDAwMA==',
            'document_type': 'invoice'
        }
        response = requests.post(
            'http://localhost:8000/api/agent/ai/analyze-document/',
            json=test_document,
            headers={
                'Authorization': f'Bearer {token}',
                'Content-Type': 'application/json'
            },
            timeout=30
        )
        if response.status_code == 200:
            result = response.json()
            print('✅ Document Analysis Success!')
            print(f'Document Type: {result.get("document_type", "N/A")}')
            print(f'Key Information: {result.get("key_information", "N/A")}')
        else:
            print(f'❌ Error {response.status_code}: {response.text}')
    except Exception as e:
        print(f'❌ Request failed: {str(e)}')
    print()

def test_predictive_analytics(token):
    """Test predictive analytics"""
    print('📈 Testing Predictive Analytics...')
    try:
        response = requests.post(
            'http://localhost:8000/api/agent/ai/predictive-analytics/',
            json={
                'analysis_type': 'demand_forecast',
                'timeframe': '30_days',
                'product_categories': ['steel', 'concrete']
            },
            headers={
                'Authorization': f'Bearer {token}',
                'Content-Type': 'application/json'
            },
            timeout=30
        )
        if response.status_code == 200:
            result = response.json()
            print('✅ Predictive Analytics Success!')
            print(f'Forecast Period: {result.get("forecast_period", "N/A")}')
            print(f'Predicted Trends: {len(result.get("predictions", []))} items')
            print(f'Confidence Level: {result.get("confidence_level", "N/A")}')
        else:
            print(f'❌ Error {response.status_code}: {response.text}')
    except Exception as e:
        print(f'❌ Request failed: {str(e)}')
    print()

def main():
    """Main test function"""
    print('🚀 LIVE AI FEATURES TESTING')
    print('=' * 60)
    
    # Get authentication token
    token, user = get_auth_token()
    print(f'User: {user.username}')
    
    # Check API key
    api_key = os.getenv('GOOGLE_CLOUD_API_KEY')
    print(f'API Key Available: {bool(api_key)}')
    if api_key:
        print(f'API Key Length: {len(api_key)} characters')
    print()
    
    # Run all tests
    test_multilingual_alert(token)
    test_voice_command(token)
    test_enhanced_status(token)
    test_document_analysis(token)
    test_predictive_analytics(token)
    
    print('🎉 ALL AI FEATURES TESTING COMPLETE!')
    print('=' * 60)

if __name__ == '__main__':
    main()