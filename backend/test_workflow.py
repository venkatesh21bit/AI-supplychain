#!/usr/bin/env python3
"""
Enhanced LOGI-BOT Agent Workflow Test Script
Tests the complete workflow: Alert Detection → Root Cause Analysis → Optimization → Orchestration
"""
import requests
import json
import time

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

def test_manual_inventory_check(token, product_id, company_id, product_name):
    """Test manual inventory check for a specific product"""
    headers = {"Authorization": f"Bearer {token}"}
    
    print(f"\n🔍 Testing Manual Inventory Check for {product_name}...")
    print(f"   Product ID: {product_id}, Company ID: {company_id}")
    
    response = requests.post(f"{API_URL}/agent/check-inventory/", 
                           headers=headers,
                           json={
                               "product_id": product_id,
                               "company_id": company_id
                           })
    
    if response.status_code == 200:
        data = response.json()
        print("✅ Manual Check Response:")
        print(json.dumps(data, indent=2))
        
        # Check if alert was generated
        if data.get("alert_generated"):
            print(f"🚨 ALERT GENERATED: {data['alert']['alert_type']} - {data['alert']['priority']}")
            
            # Check if execution was triggered
            if "execution" in data:
                execution = data["execution"]
                print(f"🤖 AGENT EXECUTION: {execution['status']} (ID: {execution['id']})")
                if execution['status'] == 'completed':
                    print(f"   ⏱️  Duration: {execution['duration_seconds']} seconds")
                    print(f"   🔍 Root Cause: {execution['root_cause']} ({execution['confidence']:.0%} confidence)")
                    if execution.get('actions_taken'):
                        print("   📋 Actions Taken:")
                        for action in execution['actions_taken']:
                            print(f"      • {action}")
                return execution.get('id')
        else:
            print(f"ℹ️  No alert needed: {data.get('message', 'Inventory adequate')}")
            
        return None
    else:
        print(f"❌ Failed: {response.status_code}")
        print(response.text)
        return None

def test_execution_details(token, execution_id):
    """Get detailed information about a specific execution"""
    if not execution_id:
        return
        
    headers = {"Authorization": f"Bearer {token}"}
    
    print(f"\n📊 Getting Execution Details (ID: {execution_id})...")
    
    response = requests.get(f"{API_URL}/agent/executions/?execution_id={execution_id}", 
                          headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        if data['count'] > 0:
            execution = data['results'][0]
            print("✅ Execution Details:")
            print(f"   📅 Started: {execution['started_at']}")
            print(f"   ⏰ Duration: {execution['duration_seconds']}s")
            print(f"   📊 Status: {execution['status']}")
            
            if execution.get('workflow_steps'):
                print("   🔄 Workflow Steps:")
                for step in execution['workflow_steps']:
                    print(f"      {step['step_number']}. {step['step_name']}: {step['status']} ({step['duration_seconds']}s)")
                    if step.get('output') and step['step_name'] == 'orchestration':
                        output = step['output']
                        if 'asana_project' in output:
                            print(f"         📋 Asana Project: {output['asana_project']['name']}")
                        if 'outlook_meeting' in output:
                            print(f"         📅 Meeting: {output['outlook_meeting']['subject']}")
                        if 'draft_orders' in output:
                            print(f"         📦 Draft Orders: {len(output['draft_orders'])} created")
    else:
        print(f"❌ Failed to get execution details: {response.status_code}")

def test_monitor_all_inventory(token):
    """Test the monitor all inventory endpoint"""
    headers = {"Authorization": f"Bearer {token}"}
    
    print(f"\n🔍 Testing Monitor All Inventory...")
    
    response = requests.get(f"{API_URL}/agent/monitor-inventory/?auto_resolve=true", 
                          headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        print("✅ Monitor All Response:")
        print(f"   📦 Products Checked: {data['products_checked']}")
        print(f"   🚨 Alerts Generated: {data['alerts_triggered']}")
        
        if data.get('alerts') and len(data['alerts']) > 0:
            print("   📋 Alert Details:")
            for alert in data['alerts']:
                print(f"      • {alert['product_name']}: {alert['current_inventory']} units "
                      f"(threshold: {alert['threshold']}) - {alert['priority']}")
                if alert.get('execution_initiated'):
                    print(f"        🤖 Execution started: ID {alert['execution_id']}")
        
        return data.get('alerts', [])
    else:
        print(f"❌ Failed: {response.status_code}")
        print(response.text)
        return []

def test_get_all_alerts(token):
    """Get all alerts from the system"""
    headers = {"Authorization": f"Bearer {token}"}
    
    print(f"\n🚨 Getting All System Alerts...")
    
    response = requests.get(f"{API_URL}/agent/alerts/", headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Total Alerts: {data['count']}")
        
        if data['count'] > 0:
            print("   📋 Alert Summary:")
            critical = high = medium = low = 0
            for alert in data['alerts']:
                priority = alert['priority']
                if priority == 'critical':
                    critical += 1
                elif priority == 'high':
                    high += 1
                elif priority == 'medium':
                    medium += 1
                else:
                    low += 1
                    
                print(f"      • [{alert['priority'].upper()}] {alert['product']}: "
                      f"{alert['current_stock']} units (Company: {alert['company']})")
            
            print(f"   📊 Priority Breakdown: 🔴{critical} Critical, 🟡{high} High, 🟠{medium} Medium, 🟢{low} Low")
        
        return data['alerts']
    else:
        print(f"❌ Failed: {response.status_code}")
        print(response.text)
        return []

def main():
    print("🚀 LOGI-BOT End-to-End Workflow Test")
    print("=" * 60)
    
    # Get authentication token
    token = get_auth_token()
    if not token:
        print("❌ Could not authenticate. Exiting.")
        return
    
    print(f"✅ Authenticated successfully")
    
    # Test scenarios with our sample data
    test_scenarios = [
        (1, 1, "LIMESTONE"),  # Critical - should trigger immediate response
        (2, 1, "CEMENT"),     # Warning - should trigger response
        (3, 1, "SAND"),       # Warning - should trigger response
    ]
    
    execution_ids = []
    
    print("\n" + "="*60)
    print("🧪 TESTING INDIVIDUAL PRODUCT CHECKS")
    print("="*60)
    
    # Test individual product checks
    for product_id, company_id, product_name in test_scenarios:
        execution_id = test_manual_inventory_check(token, product_id, company_id, product_name)
        if execution_id:
            execution_ids.append(execution_id)
            # Get detailed execution info
            test_execution_details(token, execution_id)
        
        print("\n" + "-"*40)
        time.sleep(1)  # Brief pause between tests
    
    print("\n" + "="*60)
    print("🔍 TESTING BULK MONITORING")
    print("="*60)
    
    # Test bulk monitoring
    alerts = test_monitor_all_inventory(token)
    
    print("\n" + "="*60)
    print("📊 FINAL SYSTEM STATUS")
    print("="*60)
    
    # Get all alerts
    all_alerts = test_get_all_alerts(token)
    
    # Final summary
    print(f"\n🎯 TEST SUMMARY:")
    print(f"   ✅ Individual checks completed: {len(test_scenarios)}")
    print(f"   🤖 Agent executions triggered: {len(execution_ids)}")
    print(f"   🚨 Total alerts in system: {len(all_alerts)}")
    
    if len(execution_ids) > 0:
        print(f"\n🎉 LOGI-BOT successfully demonstrated autonomous workflow!")
        print(f"   The agent detected low inventory, performed root cause analysis,")
        print(f"   generated optimization strategies, and orchestrated external actions.")
    else:
        print(f"\n⚠️  No executions were triggered. Check inventory levels and thresholds.")

if __name__ == "__main__":
    main()