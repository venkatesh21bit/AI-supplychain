#!/usr/bin/env python
"""
Test script to verify the UI -> API -> Database -> Signal flow
This script tests if stock edits from the UI properly trigger Django signals
"""

import os
import sys
import django
import requests
import json
from datetime import datetime

# Add the project root to the Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.append(project_root)

# Configure Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'main.settings')
django.setup()

from django.test import Client
from django.contrib.auth.models import User, Group
from app.models import Product, Company, AgentAlert, AgentExecution
from rest_framework_simplejwt.tokens import RefreshToken

def get_auth_token():
    """Get JWT token for testing"""
    try:
        user = User.objects.first()
        if not user:
            print("❌ No users found in database")
            return None
        
        refresh = RefreshToken.for_user(user)
        return str(refresh.access_token)
    except Exception as e:
        print(f"❌ Error getting auth token: {e}")
        return None

def test_direct_product_update():
    """Test direct product model update (bypasses API)"""
    print("=== Testing Direct Product Model Update ===")
    
    try:
        # Get a product to test with
        product = Product.objects.first()
        if not product:
            print("❌ No products found in database")
            return False
        
        print(f"🧪 Testing with product: {product.name}")
        print(f"📦 Current stock: {product.available_quantity}")
        
        # Store initial execution count
        initial_executions = AgentExecution.objects.count()
        print(f"📊 Initial executions in DB: {initial_executions}")
        
        # Update stock to a low level (should trigger signal)
        old_quantity = product.available_quantity
        product.available_quantity = 5  # Very low stock
        product.save()
        
        # Check if execution was created
        new_executions = AgentExecution.objects.count()
        print(f"📊 Executions after update: {new_executions}")
        
        if new_executions > initial_executions:
            print("✅ Direct model update successfully triggered signal!")
            latest_execution = AgentExecution.objects.latest('started_at')
            print(f"📋 Execution ID: {latest_execution.execution_id}")
            print(f"🎯 Product: {latest_execution.alert.product.name}")
            return True
        else:
            print("❌ Direct model update did not trigger signal")
            return False
            
    except Exception as e:
        print(f"❌ Error in direct product update test: {e}")
        return False

def test_api_product_update():
    """Test product update via API (simulates UI behavior)"""
    print("\n=== Testing API Product Update ===")
    
    try:
        token = get_auth_token()
        if not token:
            return False
        
        # Get a product to test with
        product = Product.objects.first()
        if not product:
            print("❌ No products found in database")
            return False
        
        print(f"🧪 Testing API update with product: {product.name}")
        print(f"📦 Current stock: {product.available_quantity}")
        
        # Store initial execution count
        initial_executions = AgentExecution.objects.count()
        print(f"📊 Initial executions in DB: {initial_executions}")
        
        # Prepare API request (simulate what the UI does)
        client = Client()
        headers = {'HTTP_AUTHORIZATION': f'Bearer {token}'}
        
        # Update data
        update_data = {
            'available_quantity': 3,  # Very low stock
            'price': str(product.price),  # Keep other fields
            'name': product.name,
            'category': product.category.category_id if product.category else None,
            'company': product.company.pk
        }
        
        # Make PATCH request to API
        response = client.patch(
            f'/products/{product.product_id}/',
            data=json.dumps(update_data),
            content_type='application/json',
            **headers
        )
        
        print(f"📡 API Response Status: {response.status_code}")
        
        if response.status_code == 200:
            # Refresh product from database
            product.refresh_from_db()
            print(f"📦 Updated stock in DB: {product.available_quantity}")
            
            # Check if execution was created
            new_executions = AgentExecution.objects.count()
            print(f"📊 Executions after API update: {new_executions}")
            
            if new_executions > initial_executions:
                print("✅ API update successfully triggered signal!")
                latest_execution = AgentExecution.objects.latest('started_at')
                print(f"📋 Execution ID: {latest_execution.execution_id}")
                print(f"🎯 Product: {latest_execution.alert.product.name}")
                return True
            else:
                print("❌ API update did not trigger signal")
                return False
        else:
            print(f"❌ API update failed with status: {response.status_code}")
            if response.content:
                print(f"Response: {response.content.decode()}")
            return False
            
    except Exception as e:
        print(f"❌ Error in API product update test: {e}")
        return False

def check_database_state():
    """Check current database state"""
    print("\n=== Database State Check ===")
    
    try:
        # Count products
        product_count = Product.objects.count()
        print(f"📦 Total products: {product_count}")
        
        # Count low stock products
        low_stock_products = Product.objects.filter(available_quantity__lte=10)
        print(f"⚠️  Low stock products (≤10): {low_stock_products.count()}")
        
        for product in low_stock_products[:5]:  # Show first 5
            print(f"   - {product.name}: {product.available_quantity} units")
        
        # Count executions
        execution_count = AgentExecution.objects.count()
        print(f"🚀 Total executions: {execution_count}")
        
        # Show recent executions
        recent_executions = AgentExecution.objects.order_by('-started_at')[:3]
        print(f"📋 Recent executions:")
        for execution in recent_executions:
            print(f"   - {execution.started_at.strftime('%Y-%m-%d %H:%M:%S')}: {execution.alert.product.name} (Status: {execution.status})")
        
        return True
        
    except Exception as e:
        print(f"❌ Error checking database state: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 Testing UI -> API -> Database -> Signal Flow")
    print("=" * 50)
    
    # Check initial database state
    check_database_state()
    
    # Test direct model update
    direct_test_passed = test_direct_product_update()
    
    # Test API update
    api_test_passed = test_api_product_update()
    
    # Final summary
    print("\n" + "=" * 50)
    print("📊 Test Results Summary:")
    print(f"✅ Direct Model Update: {'PASSED' if direct_test_passed else 'FAILED'}")
    print(f"✅ API Update: {'PASSED' if api_test_passed else 'FAILED'}")
    
    if direct_test_passed and api_test_passed:
        print("🎉 All tests passed! UI edits should trigger signals correctly.")
    elif direct_test_passed and not api_test_passed:
        print("⚠️  Signals work for direct updates but not API updates. Check API implementation.")
    elif not direct_test_passed and not api_test_passed:
        print("❌ Signals are not working. Check signal configuration.")
    else:
        print("🤔 Mixed results. Further investigation needed.")

if __name__ == "__main__":
    main()