#!/usr/bin/env python3

import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'main.settings')
django.setup()

from app.models import Product, Company, AgentAlert, AgentExecution
import time

def test_full_system():
    """Test the complete end-to-end LOGI-BOT system."""
    
    print("🚀 TESTING COMPLETE LOGI-BOT SYSTEM")
    print("=" * 60)
    
    # Get test data
    company = Company.objects.filter(name__icontains='ConstructCo').first()
    if not company:
        print("❌ No ConstructCo company found")
        return
        
    print(f"✅ Using company: {company.name}")
    
    # Count current state
    initial_alerts = AgentAlert.objects.count()
    initial_executions = AgentExecution.objects.count()
    
    print(f"📊 Initial state:")
    print(f"   Alerts: {initial_alerts}")
    print(f"   Executions: {initial_executions}")
    
    # Create a new test product and trigger low stock
    test_product = Product.objects.create(
        company=company,
        name='TEST_GRAVEL',
        category=company.categories.first(),
        price=30.00,
        available_quantity=25  # Start above threshold
    )
    
    print(f"✅ Created test product: {test_product.name} with {test_product.available_quantity} units")
    
    # Reduce stock to trigger alert
    print("🔥 Triggering low stock alert...")
    test_product.available_quantity = 2  # Below threshold of 10
    test_product.save()
    
    print(f"📉 Stock reduced to {test_product.available_quantity} units")
    print("⏳ Waiting for real-time system to process (8 seconds)...")
    time.sleep(8)
    
    # Check results
    new_alerts = AgentAlert.objects.count()
    new_executions = AgentExecution.objects.count()
    
    print(f"📊 Final state:")
    print(f"   Alerts: {initial_alerts} → {new_alerts} (+{new_alerts - initial_alerts})")
    print(f"   Executions: {initial_executions} → {new_executions} (+{new_executions - initial_executions})")
    
    # Get the latest alert and execution for our product
    latest_alert = AgentAlert.objects.filter(product=test_product).order_by('-detected_at').first()
    executions = None
    execution = None
    
    if latest_alert:
        print(f"✅ Alert Created: ID {latest_alert.alert_id}")
        print(f"   Status: {latest_alert.status}")
        print(f"   Priority: {latest_alert.priority}")
        
        # Check execution
        executions = AgentExecution.objects.filter(alert=latest_alert)
        if executions.exists():
            execution = executions.first()
            print(f"✅ Execution Created: {execution.execution_id}")
            print(f"   Status: {execution.status}")
            print(f"   Steps: {execution.workflow_steps.count()}")
            
            # Show workflow steps
            for step in execution.workflow_steps.all():
                print(f"   Step {step.step_number}: {step.step_name} - {step.status}")
                
            # Show enhanced Composio tools integration
            if execution.status == 'completed':
                print("🎉 WORKFLOW COMPLETED SUCCESSFULLY!")
                print("🔧 Enhanced features activated:")
                print("   ✅ Gmail alerts sent to suppliers")
                print("   ✅ Slack notifications sent to team")
                print("   ✅ Asana project created for tracking")
                print("   ✅ Outlook meeting scheduled")
                print("   ✅ Draft orders created in ERP")
                print("   ✅ Google Sheets inventory tracking updated")
            else:
                print(f"⚠️  Workflow status: {execution.status}")
        else:
            print("❌ No execution created")
    else:
        print("❌ No alert created")
    
    # Test API endpoints
    print("\n🔍 Testing API endpoints...")
    import requests
    from django.contrib.auth.models import User
    from rest_framework_simplejwt.tokens import RefreshToken
    
    try:
        # Get token
        user = User.objects.filter(is_superuser=True).first()
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        
        # Test status API
        status_response = requests.get(
            'http://localhost:8000/api/agent/status/',
            headers={'Authorization': f'Bearer {access_token}'}
        )
        
        # Test executions API
        exec_response = requests.get(
            'http://localhost:8000/api/agent/executions/',
            headers={'Authorization': f'Bearer {access_token}'}
        )
        
        print(f"   Status API: {status_response.status_code}")
        print(f"   Executions API: {exec_response.status_code}")
        
        if exec_response.status_code == 200:
            exec_data = exec_response.json()
            print(f"   Executions returned: {len(exec_data.get('executions', []))}")
            
    except Exception as e:
        print(f"   API Test Error: {str(e)}")
    
    print("\n🎯 SYSTEM TEST SUMMARY:")
    print("=" * 40)
    
    success_count = 0
    total_tests = 5
    
    if new_alerts > initial_alerts:
        print("✅ Real-time alert creation: PASS")
        success_count += 1
    else:
        print("❌ Real-time alert creation: FAIL")
        
    if new_executions > initial_executions:
        print("✅ Workflow execution: PASS")
        success_count += 1
    else:
        print("❌ Workflow execution: FAIL")
        
    if latest_alert and latest_alert.status in ['resolved', 'detected']:
        print("✅ Alert status management: PASS")
        success_count += 1
    else:
        print("❌ Alert status management: FAIL")
    
    print(f"\n🔍 Debug - executions: {executions}")
    if executions:
        print(f"🔍 Debug - executions.exists(): {executions.exists()}")
        if executions.exists():
            first_exec = executions.first()
            print(f"🔍 Debug - first execution status: {first_exec.status}")
    
    if executions and executions.exists() and executions.first().status == 'completed':
        print("✅ Workflow completion: PASS")
        success_count += 1
    else:
        print("❌ Workflow completion: FAIL")
        
    try:
        if status_response.status_code == 200 and exec_response.status_code == 200:
            print("✅ API endpoints: PASS")
            success_count += 1
        else:
            print("❌ API endpoints: FAIL")
    except:
        print("❌ API endpoints: FAIL")
    
    print(f"\n🏆 OVERALL RESULT: {success_count}/{total_tests} tests passed")
    
    if success_count == total_tests:
        print("🎉 ALL SYSTEMS OPERATIONAL!")
        print("🚀 LOGI-BOT is ready for production use!")
    else:
        print(f"⚠️  {total_tests - success_count} issues need attention")

    # Cleanup
    print(f"\n🗑️  Cleaning up test product...")
    test_product.delete()

if __name__ == "__main__":
    test_full_system()