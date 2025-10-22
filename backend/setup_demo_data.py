#!/usr/bin/env python3
"""
Demo Database Setup Script
Creates the necessary data for the LOGI-BOT demo video
"""

import os
import sys
import django
from datetime import datetime, timedelta

# Add the parent directory to the path to find Django settings
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'main.settings')
django.setup()

from app.models import (
    Company, Product, Order, IntegrationConfig, IntegrationLog, AgentConfiguration
)
from django.contrib.auth.models import User as AuthUser
from django.db import transaction

def setup_demo_data():
    """Setup all demo data for LOGI-BOT video"""
    
    print("🚀 Setting up LOGI-BOT Demo Database...")
    
    with transaction.atomic():
        # 1. Get or create demo user first
        auth_user, created = AuthUser.objects.get_or_create(
            username='demo_manager',
            defaults={
                'email': 'manager@steelworks.com',
                'first_name': 'Demo',
                'last_name': 'Manager'
            }
        )
        # Set password for authentication
        auth_user.set_password('demo123456')
        auth_user.save()
        print(f"✅ User: {auth_user.username} {'(created)' if created else '(updated)'} - Password: demo123456")
        
        # 2. Get or create demo company
        company, created = Company.objects.get_or_create(
            name="Steel Works Manufacturing Co.",
            defaults={
                'user': auth_user,
                'gstin': '29STEELWORKS001Z1',
                'description': 'Demo manufacturing company for LOGI-BOT showcase',
                'address': '123 Industrial Ave, Detroit, MI 48201',
                'state': 'Michigan',
                'city': 'Detroit',
                'pincode': '48201',
                'email': 'demo@steelworks.com',
                'phone': '+1-555-STEEL-01',
                'is_public': False
            }
        )
        print(f"✅ Company: {company.name} {'(created)' if created else '(exists)'}")
        
        # 3. Create Steel Rods product with low stock
        steel_rods, created = Product.objects.get_or_create(
            name="Steel Rods",
            company=company,
            defaults={
                'available_quantity': 75,  # Below required threshold!
                'total_required_quantity': 100,  # This acts as minimum threshold
                'unit': 'KGS',
                'price': 150.00,
                'hsn_code': '7308',
                'created_by': auth_user,
                'status': 'on_demand'  # Will be calculated on save
            }
        )
        
        if not created:
            # Update existing product to demo values
            steel_rods.available_quantity = 75
            steel_rods.total_required_quantity = 100
            steel_rods.price = 150.00
            steel_rods.unit = 'KGS'
            steel_rods.hsn_code = '7308'
            steel_rods.created_by = auth_user
            steel_rods.save()  # This will trigger status calculation
        
        print(f"✅ Product: {steel_rods.name} - Stock: {steel_rods.available_quantity}/{steel_rods.total_required_quantity} ({steel_rods.status})")
        
        # 4. Create additional products for context
        products_data = [
            {'name': 'Aluminum Sheets', 'stock': 250, 'min': 200, 'price': 120.00, 'hsn': '7606'},
            {'name': 'Copper Wire', 'stock': 180, 'min': 150, 'price': 85.50, 'hsn': '7408'},
            {'name': 'Plastic Pellets', 'stock': 450, 'min': 300, 'price': 32.25, 'hsn': '3901'},
            {'name': 'Rubber Gaskets', 'stock': 95, 'min': 100, 'price': 45.00, 'hsn': '4016'},  # Also low!
        ]
        
        for prod_data in products_data:
            product, created = Product.objects.get_or_create(
                name=prod_data['name'],
                company=company,
                defaults={
                    'available_quantity': prod_data['stock'],
                    'total_required_quantity': prod_data['min'],
                    'unit': 'KGS',
                    'price': prod_data['price'],
                    'hsn_code': prod_data['hsn'],
                    'created_by': auth_user
                }
            )
            
            if not created:
                product.available_quantity = prod_data['stock']
                product.total_required_quantity = prod_data['min']
                product.price = prod_data['price']
                product.hsn_code = prod_data['hsn']
                product.save()
        
        print(f"✅ Created {len(products_data)} additional products")
        
        # 5. Setup Integration Configurations for Demo
        integrations_data = [
            {
                'type': 'google_sheets',
                'name': 'LOGI-BOT Inventory Tracker',
                'config': {
                    'sheet_id': '1qcdOOAGJ50HfWJFlrQ3WUcrq0kjSUauVt5eBQAtGkHw',
                    'sheet_name': 'Inventory Log',
                    'range': 'A:F',
                    'headers': ['Timestamp', 'Product', 'Current Stock', 'Min Stock', 'Status', 'Action Taken']
                }
            },
            {
                'type': 'slack',
                'name': 'Supply Chain Alerts',
                'config': {
                    'webhook_url': 'https://hooks.slack.com/services/T07RXXX/B07RXXX/demo_webhook',
                    'channel': '#supply-chain-alerts'
                }
            },
            {
                'type': 'gmail',
                'name': 'Supplier Communications',
                'config': {
                    'email_from': 'alerts@steelworks.com',
                    'smtp_server': 'smtp.gmail.com',
                    'smtp_port': 587
                }
            },
            {
                'type': 'google_calendar',
                'name': 'Supply Chain Meetings',
                'config': {
                    'calendar_id': 'supply-chain@steelworks.com'
                }
            },
            {
                'type': 'google_drive',
                'name': 'Document Storage',
                'config': {
                    'folder_id': '1abcd1234-5678-90ef-ghij-klmnopqrstuv',
                    'folder_name': 'Supply Chain Documents'
                }
            }
        ]
        
        for int_data in integrations_data:
            integration, created = IntegrationConfig.objects.get_or_create(
                company=company,
                integration_type=int_data['type'],
                defaults={
                    'user': auth_user,
                    'integration_name': int_data['name'],
                    'status': 'active',
                    'config_data': int_data['config'],
                    'created_at': datetime.now(),
                    'updated_at': datetime.now()
                }
            )
            
            if not created:
                integration.config_data = int_data['config']
                integration.status = 'active'
                integration.save()
        
        print(f"✅ Configured {len(integrations_data)} integrations")
        
        # 6. Setup Agent Configuration for threshold monitoring
        agent_config, created = AgentConfiguration.objects.get_or_create(
            company=company,
            defaults={
                'critical_inventory_level': 50,
                'warning_inventory_level': 100,  # Steel Rods at 75 will trigger warning
                'reorder_point': 80,
                'safety_stock': 25,
                'auto_resolution_enabled': True,
                'require_approval': False,  # For demo, auto-resolve
                'check_interval_minutes': 5,
                'notification_emails': ['manager@steelworks.com', 'supply@steelworks.com']
            }
        )
        
        if not created:
            agent_config.warning_inventory_level = 100
            agent_config.critical_inventory_level = 50
            agent_config.reorder_point = 80
            agent_config.safety_stock = 25
            agent_config.auto_resolution_enabled = True
            agent_config.require_approval = False
            agent_config.save()
        
        print(f"✅ Agent Configuration: Warning at {agent_config.warning_inventory_level} units")
        
        # 7. Log the demo setup completion
        print("✅ Demo data setup completed successfully")
        
    print("\n🎯 Demo Database Setup Complete!")
    print("\n📊 Demo Scenario Ready:")
    print(f"   • Steel Rods: {steel_rods.available_quantity} units (below {steel_rods.total_required_quantity} required)")
    print(f"   • Status: {steel_rods.status}")
    print(f"   • Daily usage: ~15 units/day")
    print(f"   • Days until stockout: ~5 days")
    print(f"   • Urgency: HIGH")
    print(f"   • All 5 integrations configured and active")
    print("\n🚀 Ready for LOGI-BOT demo recording!")

if __name__ == '__main__':
    setup_demo_data()