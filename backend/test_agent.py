#!/usr/bin/env python3
"""
Simple script to test LOGI-BOT agent API endpoints
"""
import requests
import json

# API Configuration
API_URL = "http://127.0.0.1:8000/api"
USERNAME = "admin"
PASSWORD = "password123"

def get_auth_token():
    """Get JWT authentication token"""
    response = requests.post(f"{API_URL}/token/", json={
        "username": USERNAME,
        "password": PASSWORD
    })
    if response.status_code == 200:
        return response.json()["access"]
    else:
        print(f"Failed to get token: {response.status_code}")
        print(response.text)
        return None

def test_agent_status(token):
    """Test agent status endpoint"""
    headers = {"Authorization": f"Bearer {token}"}
    
    print("🤖 Testing LOGI-BOT Agent Status...")
    response = requests.get(f"{API_URL}/agent/status/", headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        print("✅ Agent Status Response:")
        print(json.dumps(data, indent=2))
        return True
    else:
        print(f"❌ Failed: {response.status_code}")
        print(response.text)
        return False

def test_monitor_inventory(token):
    """Test inventory monitoring endpoint"""
    headers = {"Authorization": f"Bearer {token}"}
    
    print("\n📦 Testing Inventory Monitoring...")
    response = requests.get(f"{API_URL}/agent/monitor-inventory/", headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        print("✅ Monitor Inventory Response:")
        print(json.dumps(data, indent=2))
        return True
    else:
        print(f"❌ Failed: {response.status_code}")
        print(response.text)
        return False

def test_get_alerts(token):
    """Test get alerts endpoint"""
    headers = {"Authorization": f"Bearer {token}"}
    
    print("\n🚨 Testing Get Alerts...")
    response = requests.get(f"{API_URL}/agent/alerts/", headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        print("✅ Get Alerts Response:")
        print(json.dumps(data, indent=2))
        return True
    else:
        print(f"❌ Failed: {response.status_code}")
        print(response.text)
        return False

def main():
    print("🚀 LOGI-BOT Agent API Test Suite")
    print("=" * 50)
    
    # Get authentication token
    token = get_auth_token()
    if not token:
        print("❌ Could not authenticate. Exiting.")
        return
    
    print(f"✅ Got authentication token: {token[:20]}...")
    
    # Test endpoints
    success_count = 0
    total_tests = 3
    
    if test_agent_status(token):
        success_count += 1
    
    if test_monitor_inventory(token):
        success_count += 1
        
    if test_get_alerts(token):
        success_count += 1
    
    print(f"\n📊 Test Results: {success_count}/{total_tests} tests passed")
    
    if success_count == total_tests:
        print("🎉 All LOGI-BOT agent endpoints are working!")
    else:
        print("⚠️  Some endpoints need attention.")

if __name__ == "__main__":
    main()