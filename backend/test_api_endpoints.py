"""
Test LOGI-BOT API endpoints
"""

import os
import django
import requests

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'main.settings')
django.setup()

from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import RefreshToken


def test_api_endpoints():
    """Test the LOGI-BOT API endpoints."""
    
    # Get token for superuser
    user = User.objects.filter(is_superuser=True).first()
    refresh = RefreshToken.for_user(user)
    token = str(refresh.access_token)
    
    print("🧪 Testing LOGI-BOT API endpoints...")
    print(f"👤 User: {user.username} (superuser: {user.is_superuser})")
    
    endpoints = {
        "Agent Status": "http://127.0.0.1:8000/api/agent/status/",
        "Agent Alerts": "http://127.0.0.1:8000/api/agent/alerts/", 
        "Agent Executions": "http://127.0.0.1:8000/api/agent/executions/"
    }
    
    headers = {'Authorization': f'Bearer {token}'}
    
    for name, url in endpoints.items():
        try:
            print(f"\n🔍 Testing {name}...")
            response = requests.get(url, headers=headers, timeout=5)
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                
                if name == "Agent Executions":
                    count = data.get('count', 0)
                    executions = data.get('executions', [])
                    print(f"   ✅ Count: {count}")
                    print(f"   ✅ Executions returned: {len(executions)}")
                    
                    if executions:
                        exec_sample = executions[0]
                        exec_id = exec_sample.get('execution_id', 'N/A')
                        product = exec_sample.get('product_name', 'N/A')
                        total_steps = exec_sample.get('total_steps', 0)
                        completed_steps = exec_sample.get('steps_completed', 0)
                        print(f"   📊 Sample: {exec_id} - {product}")
                        print(f"   📋 Steps: {completed_steps}/{total_steps}")
                        
                elif name == "Agent Alerts":
                    alerts = data.get('alerts', [])
                    print(f"   ✅ Alerts: {len(alerts)}")
                    
                    if alerts:
                        alert_sample = alerts[0]
                        product = alert_sample.get('product', 'N/A')
                        status = alert_sample.get('status', 'N/A')
                        stock = alert_sample.get('current_stock', 0)
                        print(f"   🚨 Sample: {product} - {status} ({stock} units)")
                        
                elif name == "Agent Status":
                    active = data.get('active', False)
                    stats = data.get('statistics', {})
                    print(f"   ✅ Active: {active}")
                    print(f"   📊 Stats: {stats}")
                    
            else:
                error_text = response.text[:200]
                print(f"   ❌ Error: {error_text}")
                
        except Exception as e:
            print(f"   💥 Exception: {str(e)}")
    
    print(f"\n🎯 API Test Complete!")


if __name__ == "__main__":
    test_api_endpoints()