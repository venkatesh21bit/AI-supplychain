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
        print(f"✅ Created admin user: {admin_user.username}")
    else:
        print(f"✅ Using existing admin user: {admin_user.username}")
    
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
    
    # Create sample products with low inventory to trigger alerts
    products_data = [
        {
            'name': 'LIMESTONE',
            'description': 'High-quality limestone for construction',
            'price': 25.00,
            'quantity': 8,  # Below critical threshold (10)
            'sku': 'LM-001',
            'category': 'Raw Materials'
        },
        {
            'name': 'CEMENT BAGS',
            'description': 'Premium Portland cement, 50kg bags',
            'price': 12.50,
            'quantity': 15,  # Below warning threshold (20)
            'sku': 'CB-002',
            'category': 'Building Materials'
        },
        {
            'name': 'SAND',
            'description': 'Fine construction sand',
            'price': 18.00,
            'quantity': 45,  # Above threshold (adequate stock)
            'sku': 'SD-003',
            'category': 'Raw Materials'
        },
        {
            'name': 'STEEL REBAR',
            'description': 'Reinforcement steel bars, various sizes',
            'price': 85.00,
            'quantity': 5,  # Critical - very low stock
            'sku': 'SR-004',
            'category': 'Steel Products'
        }
    ]
    
    products_created = 0
    for product_data in products_data:
        product, created = Product.objects.get_or_create(
            name=product_data['name'],
            company=company,
            defaults={
                'available_quantity': product_data['quantity'],
                'category': category,
                'price': Decimal(str(product_data['price'])),
                'unit': 'KGS',
                'hsn_code': '2517',
                'created_by': user
            }
        )
        if created:
            products_created += 1
            print(f"✅ Created product: {product_data['name']} (Stock: {product_data['quantity']})")
        else:
            # Update quantity to ensure we have the test scenario
            product.quantity = product_data['quantity']
            product.save()
            print(f"ℹ️  Updated product: {product_data['name']} (Stock: {product_data['quantity']})")
    
    print(f"✅ {products_created} new products created, {len(products_data) - products_created} updated")
    
    # Create agent configuration for the company
    config, created = AgentConfiguration.objects.get_or_create(
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
        print("✅ Created agent configuration for company")
    else:
        print("ℹ️  Agent configuration already exists")
    
    print("\n📊 Current Inventory Status:")
    print("=" * 50)
    
    critical_products = Product.objects.filter(
        company=company, 
        quantity__lte=config.critical_inventory_level
    )
    warning_products = Product.objects.filter(
        company=company,
        quantity__lte=config.warning_inventory_level,
        quantity__gt=config.critical_inventory_level
    )
    
    if critical_products.exists():
        print("🚨 CRITICAL - Products below critical threshold:")
        for product in critical_products:
            print(f"   - {product.name}: {product.quantity} units (threshold: {config.critical_inventory_level})")
    
    if warning_products.exists():
        print("⚠️  WARNING - Products below warning threshold:")
        for product in warning_products:
            print(f"   - {product.name}: {product.quantity} units (threshold: {config.warning_inventory_level})")
    
    adequate_products = Product.objects.filter(
        company=company,
        quantity__gt=config.warning_inventory_level
    )
    if adequate_products.exists():
        print("✅ ADEQUATE - Products with sufficient stock:")
        for product in adequate_products:
            print(f"   - {product.name}: {product.quantity} units")
    
    print(f"\n🎯 Ready for LOGI-BOT testing!")
    print(f"   - Company ID: {company.id}")
    print(f"   - Products with critical alerts: {critical_products.count()}")
    print(f"   - Products with warning alerts: {warning_products.count()}")
    print(f"   - Total products: {Product.objects.filter(company=company).count()}")
    
    return company, list(critical_products) + list(warning_products)

if __name__ == "__main__":
    create_sample_data()