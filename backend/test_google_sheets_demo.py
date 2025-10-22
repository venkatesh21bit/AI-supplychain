#!/usr/bin/env python3
"""
Google Sheets Demo Test Script
Tests the Google Sheets integration with actual demo data
"""

import os
import sys
import django
import json
from datetime import datetime

# Add the parent directory to the path to find Django settings
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'main.settings')
django.setup()

from app.models import IntegrationConfig, Company
from django.contrib.auth.models import User as AuthUser
import requests

def test_google_sheets_integration():
    """Test Google Sheets integration with demo data"""
    
    print("🔗 Testing Google Sheets Integration...")
    
    try:
        # Get demo company and user
        company = Company.objects.get(name="Steel Works Manufacturing Co.")
        user = AuthUser.objects.get(username='demo_manager')
        
        # Get Google Sheets integration
        sheets_integration = IntegrationConfig.objects.get(
            company=company,
            integration_type='google_sheets'
        )
        
        print(f"✅ Found integration: {sheets_integration.integration_name}")
        print(f"📋 Current Sheet ID: {sheets_integration.get_config_value('sheet_id')}")
        
        # Test data for demo
        demo_data = [
            [
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "Steel Rods",
                "75",
                "100", 
                "LOW STOCK",
                "Inventory Alert",
                "LOGI-BOT Multi-tool Response Initiated"
            ]
        ]
        
        print("\n📊 Demo Data to Send:")
        headers = ["Timestamp", "Product", "Current", "Min", "Status", "Alert Type", "Action"]
        for i, header in enumerate(headers):
            print(f"   {header}: {demo_data[0][i]}")
        
        # Prepare API call
        api_url = "http://localhost:8000/api/agent/composio/sheets-update/"
        payload = {
            "sheet_id": sheets_integration.get_config_value('sheet_id'),
            "range": f"A{4}:G{4}",  # Add to row 4 (assuming headers in row 1, sample data in rows 2-3)
            "data": demo_data
        }
        
        print(f"\n🌐 API Call Details:")
        print(f"   URL: {api_url}")
        print(f"   Range: {payload['range']}")
        print(f"   Rows: {len(payload['data'])}")
        
        print("\n🚀 To test manually:")
        print("1. Create a Google Sheet with headers:")
        print("   A1: Timestamp | B1: Product | C1: Current | D1: Min | E1: Status | F1: Alert Type | G1: Action")
        print("\n2. Make it public with 'Editor' permissions")
        print("\n3. Update the Sheet ID in database:")
        print(f"   Current ID: {sheets_integration.get_config_value('sheet_id')}")
        print("   Replace with your actual sheet ID")
        
        print("\n4. Test with curl:")
        curl_command = f'''curl -X POST {api_url} \\
  -H "Content-Type: application/json" \\
  -d '{json.dumps(payload, indent=2)}\''''
        print(curl_command)
        
        print("\n📋 Expected Result:")
        print("   - New row added to your Google Sheet")
        print("   - Timestamp: Current time")
        print("   - Product: Steel Rods")
        print("   - Status: LOW STOCK")
        print("   - Action: LOGI-BOT Multi-tool Response Initiated")
        
        return True
        
    except Company.DoesNotExist:
        print("❌ Demo company not found. Run setup_demo_data.py first")
        return False
    except IntegrationConfig.DoesNotExist:
        print("❌ Google Sheets integration not found. Run setup_demo_data.py first") 
        return False
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

def update_sheet_id_for_demo():
    """Helper function to update sheet ID with a real one"""
    
    print("\n🔧 Sheet ID Update Helper")
    print("=" * 50)
    
    new_sheet_id = input("Enter your Google Sheet ID: ").strip()
    
    if not new_sheet_id:
        print("❌ No Sheet ID provided")
        return False
    
    try:
        company = Company.objects.get(name="Steel Works Manufacturing Co.")
        sheets_integration = IntegrationConfig.objects.get(
            company=company,
            integration_type='google_sheets'
        )
        
        # Update the config
        config_data = sheets_integration.config_data.copy()
        config_data['sheet_id'] = new_sheet_id
        sheets_integration.config_data = config_data
        sheets_integration.save()
        
        print(f"✅ Updated Sheet ID to: {new_sheet_id}")
        print(f"🔗 Sheet URL: https://docs.google.com/spreadsheets/d/{new_sheet_id}/edit")
        
        return True
        
    except Exception as e:
        print(f"❌ Error updating Sheet ID: {str(e)}")
        return False

if __name__ == '__main__':
    print("📊 Google Sheets Demo Test Script")
    print("=" * 50)
    
    # Test current integration
    success = test_google_sheets_integration()
    
    if success:
        print("\n🔧 Want to update the Sheet ID with your own?")
        response = input("Update Sheet ID? (y/n): ").lower().strip()
        
        if response == 'y':
            update_sheet_id_for_demo()
            print("\n🔄 Testing with new Sheet ID...")
            test_google_sheets_integration()
    
    print("\n✅ Demo test complete!")
    print("\n📝 Next Steps:")
    print("1. Create your Google Sheet using GOOGLE_SHEETS_DEMO_SETUP.md")
    print("2. Update Sheet ID using this script")
    print("3. Start backend: python manage.py runserver")
    print("4. Test the integration via the frontend")
    print("5. Record your demo video!")