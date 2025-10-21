"""
Script to simulate dynamic stock changes for testing LOGI-BOT auto-triggers.
This will gradually decrease stock levels to demonstrate real-time workflow triggering.
"""

import os
import sys
import django
import time
import random
from datetime import datetime

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'main.settings')
django.setup()

from app.models import Product, Company, AgentAlert


def simulate_stock_changes():
    """Simulate realistic stock decreases to trigger LOGI-BOT workflows."""
    
    print("🔄 Starting dynamic stock simulation for LOGI-BOT demo...")
    
    # Get the company
    company = Company.objects.filter(name__icontains='ConstructCo').first()
    if not company:
        print("❌ ConstructCo company not found!")
        return
    
    # Get products to simulate
    products = Product.objects.filter(company=company)
    
    print(f"📦 Found {products.count()} products to simulate")
    for product in products:
        print(f"   • {product.name}: {product.available_quantity} units")
    
    print("\n🎬 Starting simulation... (Press Ctrl+C to stop)")
    
    try:
        while True:
            # Pick a random product
            product = random.choice(list(products))
            
            if product.available_quantity > 0:
                # Simulate consumption (1-5 units)
                consumption = random.randint(1, min(5, product.available_quantity))
                old_stock = product.available_quantity
                product.available_quantity = max(0, product.available_quantity - consumption)
                product.save()  # This will trigger Django signals!
                
                print(f"📉 {product.name}: {old_stock} → {product.available_quantity} units (-{consumption})")
                
                # Check if this triggered an alert
                recent_alerts = AgentAlert.objects.filter(
                    product=product,
                    status='analyzing'
                ).order_by('-detected_at')[:1]
                
                if recent_alerts.exists():
                    alert = recent_alerts.first()
                    print(f"🚨 LOGI-BOT Alert triggered! Alert ID: {alert.alert_id}")
            
            # Wait before next change (3-8 seconds)
            wait_time = random.randint(3, 8)
            print(f"⏳ Waiting {wait_time} seconds...\n")
            time.sleep(wait_time)
    
    except KeyboardInterrupt:
        print("\n🛑 Simulation stopped by user")
    except Exception as e:
        print(f"❌ Error during simulation: {str(e)}")


def reset_stock_levels():
    """Reset stock levels for a fresh demo."""
    print("🔄 Resetting stock levels...")
    
    company = Company.objects.filter(name__icontains='ConstructCo').first()
    if not company:
        print("❌ ConstructCo company not found!")
        return
    
    # Reset to higher levels
    stock_resets = {
        'LIMESTONE': 50,
        'CEMENT': 45,
        'STEEL_RODS': 40,
        'CONCRETE_BLOCKS': 35,
        'COAL': 100,
    }
    
    for product_name, new_stock in stock_resets.items():
        try:
            product = Product.objects.get(name=product_name, company=company)
            old_stock = product.available_quantity
            product.available_quantity = new_stock
            product.save()
            print(f"📦 {product_name}: {old_stock} → {new_stock} units")
        except Product.DoesNotExist:
            print(f"⚠️ Product {product_name} not found")
    
    print("✅ Stock levels reset!")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == '--reset':
        reset_stock_levels()
    else:
        print("Options:")
        print("  python simulate_stock_changes.py          - Start dynamic simulation")
        print("  python simulate_stock_changes.py --reset  - Reset stock levels")
        print()
        
        choice = input("Start simulation? (y/n): ").lower().strip()
        if choice == 'y':
            simulate_stock_changes()
        else:
            print("Simulation cancelled.")