#!/usr/bin/env python3
"""
Trigger a workflow and track its completion
"""
import os
import django
import json

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'main.settings')
django.setup()

from app.models import Product, Company, AgentAlert, AgentExecution, AgentWorkflowStep
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
import requests

def main():
    # Get a product to trigger workflow on
    product = Product.objects.filter(name='STEEL_RODS').first()
    if not product:
        print("❌ STEEL_RODS product not found")
        return
    
    # Reduce stock to trigger alert
    original_stock = product.available_quantity
    print(f"📦 Original {product.name} stock: {original_stock}")
    
    # Set very low stock
    product.available_quantity = 3
    product.save()
    print(f"📦 Updated {product.name} stock to: {product.available_quantity}")
    
    # Get authentication
    User = get_user_model()
    user = User.objects.filter(username='admin').first()
    refresh = RefreshToken.for_user(user)
    access_token = str(refresh.access_token)
    
    # Trigger workflow
    print("🚀 Triggering workflow...")
    try:
        response = requests.post(
            'http://localhost:8000/api/agent/check-inventory/',
            json={
                'product_id': product.product_id,
                'company_id': product.company.pk
            },
            headers={
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json'
            },
            timeout=60  # Increase timeout for workflow completion
        )
        
        print(f"📡 API Response Status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Alert ID: {result.get('alert_id')}")
            print(f"✅ Execution ID: {result.get('execution_id')}")
            print(f"✅ Status: {result.get('status')}")
            print(f"✅ Message: {result.get('message')}")
            
            # Check database immediately after
            execution_id = result.get('execution_id')
            if execution_id:
                execution = AgentExecution.objects.filter(execution_id=execution_id).first()
                if execution:
                    steps = AgentWorkflowStep.objects.filter(execution=execution).order_by('step_number')
                    print(f"\n🔍 Database Check:")
                    print(f"   Execution Status: {execution.status}")
                    print(f"   Steps Created: {steps.count()}")
                    for step in steps:
                        print(f"   Step {step.step_number}: {step.step_name} - {step.status}")
                else:
                    print("❌ Execution not found in database!")
        else:
            print(f"❌ Error: {response.text}")
            
    except Exception as e:
        print(f"❌ Request failed: {str(e)}")
    
    # Restore original stock
    product.available_quantity = original_stock
    product.save()
    print(f"\n🔄 Restored {product.name} stock to: {product.available_quantity}")

if __name__ == '__main__':
    main()