#!/usr/bin/env python3
"""
Test script to verify the low stock alert triggering logic is working correctly.
"""

import os
import sys
import django

# Setup Django
sys.path.append('/c/Users/91902/Documents/startup/latest-vendor/Vendor-backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'main.settings')
django.setup()

from app.models import Product, Company, AgentAlert, AgentExecution
from django.contrib.auth.models import User

def test_alert_logic():
    """Test different scenarios for alert triggering"""
    
    print("🧪 TESTING LOGI-BOT ALERT TRIGGERING LOGIC")
    print("=" * 50)
    
    # Get test company
    company = Company.objects.filter(name__icontains='ConstructCo').first()
    if not company:
        print("❌ No test company found")
        return
    
    print(f"✅ Using company: {company.name}")
    
    # Clear old alerts to start fresh
    old_alerts = AgentAlert.objects.filter(company=company)
    old_executions = AgentExecution.objects.filter(alert__company=company)
    
    print(f"🗑️  Clearing {old_alerts.count()} old alerts and {old_executions.count()} old executions")
    old_executions.delete()
    old_alerts.delete()
    
    # Test 1: Create new product with low stock (should trigger)
    print("\n📝 TEST 1: Creating new product with low stock")
    test_product = Product.objects.create(
        name="TEST_LOW_STOCK_ITEM",
        company=company,
        available_quantity=5,  # Below threshold of 10
        price=100.0,
        unit="KG"
    )
    
    # Check if alert was created
    alerts = AgentAlert.objects.filter(product=test_product)
    print(f"   Result: {alerts.count()} alert(s) created")
    if alerts.exists():
        alert = alerts.first()
        print(f"   ✅ Alert ID: {alert.alert_id}, Status: {alert.status}, Priority: {alert.priority}")
        trigger_reason = alert.alert_data.get('trigger_reason', 'unknown')
        print(f"   ✅ Trigger reason: {trigger_reason}")
    else:
        print("   ❌ No alert created for new low stock product")
    
    # Test 2: Update existing product to increase stock (should NOT trigger)
    print("\n📝 TEST 2: Increasing stock from low to sufficient")
    test_product.available_quantity = 25  # Above threshold
    test_product.save()
    
    new_alerts = AgentAlert.objects.filter(product=test_product).count()
    print(f"   Result: Total alerts for product: {new_alerts}")
    if new_alerts == 1:
        print("   ✅ No new alert created when stock increased (correct behavior)")
    else:
        print("   ❌ Unexpected alert created when stock increased")
    
    # Test 3: Update product to decrease stock below threshold (should trigger)  
    print("\n📝 TEST 3: Decreasing stock from sufficient to low")
    
    # First resolve existing alert
    if alerts.exists():
        alerts.update(status='resolved')
    
    # Wait a moment to ensure pre_save signal captures the current state
    import time
    time.sleep(0.1)
    
    test_product.available_quantity = 3  # Below threshold of 5 
    test_product.save()
    
    # Check if new alert was created (might be resolved already if workflow completed)
    all_alerts = AgentAlert.objects.filter(product=test_product).order_by('detected_at')
    
    print(f"   Result: Total alerts for product: {all_alerts.count()}")
    if all_alerts.count() >= 2:  # Should have original + new alert
        latest_alert = all_alerts.last()
        trigger_reason = latest_alert.alert_data.get('trigger_reason', 'unknown')
        print(f"   ✅ New alert created with reason: {trigger_reason}, Status: {latest_alert.status}")
        
        # Check if execution was created
        executions = AgentExecution.objects.filter(alert=latest_alert)
        if executions.exists():
            print(f"   ✅ Workflow execution created: {executions.first().execution_id}")
        else:
            print("   ⚠️  No execution found for the alert")
    else:
        print("   ❌ No new alert created when stock decreased below threshold")
    
    # Test 4: Check if LIMESTONE triggers correctly
    print("\n📝 TEST 4: Testing existing LIMESTONE product")
    limestone = Product.objects.filter(name='LIMESTONE', company=company).first()
    if limestone:
        old_stock = limestone.available_quantity
        print(f"   LIMESTONE current stock: {old_stock}")
        
        # Clear existing alerts for limestone
        AgentAlert.objects.filter(product=limestone).update(status='resolved')
        
        # Set stock to low value
        limestone.available_quantity = 3
        limestone.save()
        
        all_limestone_alerts = AgentAlert.objects.filter(product=limestone)
        limestone_executions = AgentExecution.objects.filter(alert__product=limestone)
        
        print(f"   Result: Total LIMESTONE alerts: {all_limestone_alerts.count()}")
        print(f"   Result: Total LIMESTONE executions: {limestone_executions.count()}")
        
        if limestone_executions.exists():
            latest_execution = limestone_executions.last()
            print(f"   ✅ LIMESTONE workflow executed: {latest_execution.execution_id}, Status: {latest_execution.status}")
        else:
            print("   ❌ LIMESTONE workflow not executed")
        
        # Restore original stock
        limestone.available_quantity = old_stock
        limestone.save()
    else:
        print("   ⚠️  LIMESTONE product not found")
    
    # Summary
    print("\n📊 SUMMARY:")
    total_alerts = AgentAlert.objects.filter(company=company).count()
    active_alerts = AgentAlert.objects.filter(
        company=company, 
        status__in=['detected', 'analyzing']
    ).count()
    total_executions = AgentExecution.objects.filter(alert__company=company).count()
    
    print(f"   Total alerts created: {total_alerts}")
    print(f"   Active alerts: {active_alerts}")
    print(f"   Total executions: {total_executions}")
    
    # Cleanup test product
    print(f"\n🗑️  Cleaning up test product...")
    test_product.delete()
    
    print("\n✅ Test completed!")

if __name__ == "__main__":
    test_alert_logic()