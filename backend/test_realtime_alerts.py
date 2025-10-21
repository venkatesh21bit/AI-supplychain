#!/usr/bin/env python3

import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'main.settings')
django.setup()

from app.models import Product, Company, AgentAlert, AgentExecution
from django.contrib.auth.models import User
import time

def test_real_time_stock_alerts():
    """Test the real-time stock alert system with enhanced Composio tools."""
    
    print("🧪 Testing Real-Time Stock Alert System")
    print("=" * 60)
    
    # Get test data
    try:
        company = Company.objects.filter(name__icontains='ConstructCo').first()
        if not company:
            print("❌ No ConstructCo company found")
            return
            
        print(f"✅ Using company: {company.name}")
        
        # Find a product to test with
        test_product = Product.objects.filter(company=company, name='LIMESTONE').first()
        if not test_product:
            print("❌ No LIMESTONE product found")
            return
            
        print(f"✅ Using product: {test_product.name}")
        print(f"📦 Current stock: {test_product.available_quantity}")
        
        # Count current alerts and executions
        initial_alerts = AgentAlert.objects.count()
        initial_executions = AgentExecution.objects.count()
        
        print(f"📊 Initial alerts: {initial_alerts}")
        print(f"📊 Initial executions: {initial_executions}")
        print()
        
        # Simulate stock reduction to trigger low stock alert
        print("🔥 SIMULATING STOCK REDUCTION...")
        original_stock = test_product.available_quantity
        
        # Set stock to critical level (below 10)
        test_product.available_quantity = 3
        test_product.save()
        
        print(f"📉 Stock reduced from {original_stock} to {test_product.available_quantity}")
        print("🤖 Django signal should trigger LOGI-BOT workflow...")
        print()
        
        # Wait a moment for the signal to process
        print("⏳ Waiting for workflow to trigger (5 seconds)...")
        time.sleep(5)
        
        # Check results
        print("📊 CHECKING RESULTS:")
        print("-" * 30)
        
        new_alerts = AgentAlert.objects.count()
        new_executions = AgentExecution.objects.count()
        
        print(f"🚨 Alerts: {initial_alerts} → {new_alerts} (+{new_alerts - initial_alerts})")
        print(f"🤖 Executions: {initial_executions} → {new_executions} (+{new_executions - initial_executions})")
        
        # Show latest alert
        latest_alert = AgentAlert.objects.filter(product=test_product).order_by('-detected_at').first()
        if latest_alert:
            print(f"✅ Latest Alert: ID {latest_alert.alert_id} - {latest_alert.alert_type} - {latest_alert.status}")
            print(f"   Product: {latest_alert.product.name} ({latest_alert.current_stock} units)")
            print(f"   Priority: {latest_alert.priority}")
            print(f"   Detected: {latest_alert.detected_at}")
        
        # Show latest execution
        latest_execution = AgentExecution.objects.order_by('-started_at').first()
        if latest_execution:
            print(f"✅ Latest Execution: {latest_execution.execution_id}")
            print(f"   Status: {latest_execution.status}")
            print(f"   Alert: {latest_execution.alert.product.name}")
            print(f"   Started: {latest_execution.started_at}")
            print(f"   Steps: {latest_execution.workflow_steps.count()}")
            
            # Show workflow steps
            for step in latest_execution.workflow_steps.all():
                print(f"   Step {step.step_number}: {step.step_name} - {step.status}")
        
        print()
        print("🎯 TEST SUMMARY:")
        print("-" * 30)
        
        if new_alerts > initial_alerts:
            print("✅ Alert successfully created")
        else:
            print("❌ No new alert created")
            
        if new_executions > initial_executions:
            print("✅ Workflow execution triggered")
        else:
            print("❌ No workflow execution triggered")
            
        print()
        print("🔄 RESTORING ORIGINAL STOCK...")
        test_product.available_quantity = original_stock
        test_product.save()
        print(f"✅ Stock restored to {original_stock}")
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_real_time_stock_alerts()