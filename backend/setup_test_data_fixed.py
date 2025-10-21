#!/usr/bin/env python3
"""
Setup sample data for LOGI-BOT testing
"""
import os
import sys
import django

# Add the parent directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'main.settings')
django.setup()

from django.contrib.auth.models import User, Group
from app.models import Company, Product, AgentConfiguration, Category
from decimal import Decimal

def create_sample_data():
    """Create sample companies, products, and configurations for testing"""
    
    print("🏗️  Setting up sample data for LOGI-BOT testing...")
    
    # Get or create admin user first
    admin_user, user_created = User.objects.get_or_create(
        username='admin',
        defaults={
            'email': 'admin@test.com',
            'first_name': 'Admin',
            'last_name': 'User'
        }
    )
    if user_created:
        admin_user.set_password('password123')
        admin_user.save()
        print("✅ Created admin user")
    else:
        print("✅ Using existing admin user: admin")
    
    # Create a manufacturer group user if doesn't exist
    manufacturer_group, created = Group.objects.get_or_create(name='Manufacturer')
    if created:
        print("✅ Created Manufacturer group")
    
    # Create sample company
    company, created = Company.objects.get_or_create(
        name="Acme Manufacturing Co.",
        defaults={
            'user': admin_user,  # Add the required user field
            'gstin': '27AAACI1234L1ZQ',  # Add required GSTIN
            'description': 'Leading manufacturer of construction materials',
            'is_public': True,
            'email': 'contact@acme-manufacturing.com',
            'phone': '+1-555-0123',
            'address': '123 Industrial Ave, Manufacturing City, MC 12345',
            'state': 'Manufacturing State',
            'city': 'Manufacturing City',
            'pincode': '12345'
        }
    )
    if created:
        print("✅ Created sample company: Acme Manufacturing Co.")
    else:
        print("ℹ️  Company already exists: Acme Manufacturing Co.")
    
    # Create sample categories
    cement_category, created = Category.objects.get_or_create(
        name="Cement Products",
        company=company
    )
    if created:
        print("✅ Created category: Cement Products")
    
    raw_materials_category, created = Category.objects.get_or_create(
        name="Raw Materials", 
        company=company
    )
    if created:
        print("✅ Created category: Raw Materials")
    
    # Create sample products with low inventory to trigger alerts
    products_data = [
        {
            'name': 'LIMESTONE',
            'price': 125.50,
            'quantity': 8,  # Critical - below threshold (10)
            'category': cement_category
        },
        {
            'name': 'CEMENT',
            'price': 95.75,
            'quantity': 15,  # Low inventory - below warning (20) 
            'category': cement_category
        },
        {
            'name': 'SAND',
            'price': 45.00,
            'quantity': 12,  # Low inventory
            'category': raw_materials_category
        },
        {
            'name': 'GRAVEL',
            'price': 55.25,
            'quantity': 25,  # Adequate inventory
            'category': raw_materials_category
        }
    ]
    
    products_created = 0
    for product_data in products_data:
        product, created = Product.objects.get_or_create(
            name=product_data['name'],
            company=company,
            defaults={
                'available_quantity': product_data['quantity'],
                'category': product_data['category'],
                'price': Decimal(str(product_data['price'])),
                'unit': 'KGS',
                'hsn_code': '2517',
                'created_by': admin_user
            }
        )
        if created:
            products_created += 1
            print(f"✅ Created product: {product_data['name']} (Stock: {product_data['quantity']})")
        else:
            # Update quantity to ensure we have the test scenario
            product.available_quantity = product_data['quantity']
            product.save()
            print(f"ℹ️  Updated product: {product_data['name']} (Stock: {product_data['quantity']})")
    
    print(f"✅ {products_created} new products created, {len(products_data) - products_created} updated")
    
    # Create agent configuration for the company
    agent_config, created = AgentConfiguration.objects.get_or_create(
        company=company,
        defaults={
            'critical_inventory_level': 10,
            'warning_inventory_level': 20,
            'reorder_point': 15,
            'safety_stock': 5,
            'auto_resolution_enabled': True,
            'require_approval': True,
            'check_interval_minutes': 5,
            'notification_emails': ['manager@acme-manufacturing.com', 'procurement@acme-manufacturing.com']
        }
    )
    if created:
        print("✅ Created agent configuration for Acme Manufacturing Co.")
        print(f"   - Critical level: {agent_config.critical_inventory_level}")
        print(f"   - Warning level: {agent_config.warning_inventory_level}")
        print(f"   - Auto-resolution: {agent_config.auto_resolution_enabled}")
    else:
        print("ℹ️  Agent configuration already exists")
    
    print("\n🎯 Test Scenario Setup Complete!")
    print("=" * 50)
    print("Products with LOW INVENTORY (will trigger alerts):")
    low_inventory_products = Product.objects.filter(
        company=company,
        available_quantity__lte=agent_config.warning_inventory_level
    )
    for product in low_inventory_products:
        status = "🔴 CRITICAL" if product.available_quantity <= agent_config.critical_inventory_level else "🟡 WARNING"
        print(f"   {status} {product.name}: {product.available_quantity} units")
    
    print(f"\n🤖 Ready to test LOGI-BOT agent!")
    print(f"   Use: python test_agent.py")
    print(f"   Or API: POST /api/agent/check-inventory/ with product_id and company_id")
    
    return company, admin_user

if __name__ == "__main__":
    create_sample_data()