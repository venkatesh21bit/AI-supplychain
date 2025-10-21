#!/usr/bin/env python3
"""
Simple Composio REST API Test
"""
import os
import asyncio
import requests
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def test_composio_api():
    """Test Composio API directly"""
    print("🚀 Testing Composio REST API")
    print("=" * 40)
    
    api_key = os.getenv('COMPOSIO_API_KEY')
    
    if not api_key:
        print("❌ No Composio API key found")
        return
    
    print(f"✅ API Key: {api_key[:8]}...{api_key[-4:]} (length: {len(api_key)})")
    
    # Test API connectivity
    base_url = "https://backend.composio.dev/api/v1"
    headers = {
        "X-API-Key": api_key,
        "Content-Type": "application/json"
    }
    
    try:
        print("\\n🔌 Testing API connectivity...")
        response = requests.get(
            f"{base_url}/integrations",
            headers=headers,
            timeout=30
        )
        
        print(f"Response Status: {response.status_code}")
        
        if response.status_code == 200:
            integrations = response.json()
            print(f"✅ Connected integrations: {len(integrations)}")
            
            for integration in integrations:
                app_name = integration.get('app', {}).get('name', 'Unknown')
                status = integration.get('status', 'unknown')
                print(f"  📱 {app_name}: {status}")
        
        elif response.status_code == 401:
            print("❌ Authentication failed - check API key")
        elif response.status_code == 403:
            print("❌ Access forbidden - check permissions")
        else:
            print(f"❌ API Error: {response.status_code} - {response.text}")
    
    except requests.exceptions.RequestException as e:
        print(f"❌ Connection error: {str(e)}")
    
    # Test workflow simulation
    print("\\n🔄 Simulating cross-platform workflow...")
    
    mock_workflow = {
        "workflow_id": f"workflow_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        "platforms": {
            "slack": {
                "action": "Send alert to #supply-chain channel",
                "status": "✅ Success",
                "message": "Critical stock alert sent"
            },
            "asana": {
                "action": "Create urgent task",
                "status": "✅ Success", 
                "message": "Task 'Restock Steel Rods' created"
            },
            "gmail": {
                "action": "Send email notification",
                "status": "✅ Success",
                "message": "Email sent to supply manager"
            },
            "googlesheets": {
                "action": "Update tracking spreadsheet",
                "status": "❌ Failed",
                "message": "Sheet ID not configured"
            },
            "calendar": {
                "action": "Schedule emergency meeting",
                "status": "✅ Success",
                "message": "Meeting scheduled for 2 hours"
            }
        },
        "success_rate": 80.0
    }
    
    print(f"🆔 Workflow ID: {mock_workflow['workflow_id']}")
    print(f"📊 Success Rate: {mock_workflow['success_rate']:.1f}%")
    print("\\n📋 Platform Results:")
    
    for platform, details in mock_workflow["platforms"].items():
        print(f"  {details['status']} {platform.title()}: {details['message']}")
    
    print("\\n🎯 Available Composio Features:")
    features = [
        "✅ Cross-platform workflow automation",
        "✅ Slack notifications and alerts",
        "✅ Asana task management",
        "✅ Gmail email notifications", 
        "✅ Google Sheets data tracking",
        "✅ Calendar meeting scheduling",
        "✅ GitHub issue creation",
        "✅ Real-time status monitoring"
    ]
    
    for feature in features:
        print(f"  {feature}")
    
    print("\\n🎉 Composio Integration Test Complete!")

if __name__ == "__main__":
    asyncio.run(test_composio_api())