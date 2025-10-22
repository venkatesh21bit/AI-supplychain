#!/usr/bin/env python3
"""
Demo Login Script
Get authentication tokens for testing Composio integrations
"""

import requests
import json

# Demo user credentials (from our setup_demo_data.py)
DEMO_CREDENTIALS = {
    "username": "demo_manager",
    "password": "demo123456"  # You'll need to set this
}

API_BASE = "http://127.0.0.1:8000/api"

def get_demo_token():
    """Get authentication token for demo user"""
    
    try:
        print("🔐 Attempting to login with demo credentials...")
        
        response = requests.post(
            f"{API_BASE}/token/",
            headers={"Content-Type": "application/json"},
            json=DEMO_CREDENTIALS
        )
        
        if response.status_code == 200:
            tokens = response.json()
            print("✅ Login successful!")
            print(f"Access Token: {tokens.get('access', 'N/A')}")
            print(f"Refresh Token: {tokens.get('refresh', 'N/A')}")
            
            # Save tokens to a file for easy copying
            with open('demo_tokens.json', 'w') as f:
                json.dump(tokens, f, indent=2)
            
            print("\n📋 Tokens saved to 'demo_tokens.json'")
            print("\n🌐 To use in browser:")
            print("1. Open browser developer tools (F12)")
            print("2. Go to Console tab")
            print("3. Run these commands:")
            print(f'   localStorage.setItem("access_token", "{tokens.get("access", "")}");')
            print(f'   localStorage.setItem("refresh_token", "{tokens.get("refresh", "")}");')
            print("4. Refresh the page")
            
            return tokens
            
        else:
            print(f"❌ Login failed: {response.status_code}")
            print(f"Response: {response.text}")
            
            if response.status_code == 400:
                print("\n💡 The demo user might not exist or need a password.")
                print("   Run: python manage.py shell")
                print("   Then: from django.contrib.auth.models import User")
                print("         user = User.objects.get(username='demo_manager')")
                print("         user.set_password('demo123456')")
                print("         user.save()")
            
            return None
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection failed. Make sure the backend server is running:")
        print("   cd backend && python manage.py runserver")
        return None
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

if __name__ == "__main__":
    get_demo_token()