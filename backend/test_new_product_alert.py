#!/usr/bin/env python3

import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'main.settings')
django.setup()

from app.models import Product, Company, Category, AgentAlert, AgentExecution
import time

def test_new_product_alert():
    """Test real-time alerts with a new product."""
    
    # Get company and category
    company = Company.objects.filter(name__icontains='ConstructCo').first()
    category = Category.objects.filter(company=company).first()

    print(f'Using company: {company.name}')
    print(f'Using category: {category.name}')

    # Count before
    initial_alerts = AgentAlert.objects.count()
    initial_executions = AgentExecution.objects.count()
    print(f'Initial alerts: {initial_alerts}')
    print(f'Initial executions: {initial_executions}')

    # Create a new test product with high stock first
    test_product = Product.objects.create(
        company=company,
        name='TEST_SAND',
        category=category,
        price=25.00,
        available_quantity=50  # Start with high stock
    )

    print(f'✅ Created product: {test_product.name} with {test_product.available_quantity} units')
    time.sleep(2)

    print('🔥 Reducing stock to trigger alert...')
    test_product.available_quantity = 3  # Below threshold of 10
    test_product.save()

    print(f'📉 Stock reduced to {test_product.available_quantity} units')
    print('⏳ Waiting for signal to trigger LOGI-BOT workflow (10 seconds)...')
    time.sleep(10)

    # Check results
    new_alerts = AgentAlert.objects.count()
    new_executions = AgentExecution.objects.count()

    print(f'🚨 Alerts: {initial_alerts} → {new_alerts} (+{new_alerts - initial_alerts})')
    print(f'🤖 Executions: {initial_executions} → {new_executions} (+{new_executions - initial_executions})')

    # Show latest alert for our product
    latest_alert = AgentAlert.objects.filter(product=test_product).order_by('-detected_at').first()
    if latest_alert:
        print(f'✅ New Alert Created: ID {latest_alert.alert_id}')
        print(f'   Product: {latest_alert.product.name}')
        print(f'   Status: {latest_alert.status}')
        print(f'   Priority: {latest_alert.priority}')
        try:
            trigger_by = latest_alert.alert_data.get('triggered_by', 'unknown')
            print(f'   Trigger: {trigger_by}')
        except:
            print('   Trigger: unknown')
        
        # Check if execution was created
        executions = AgentExecution.objects.filter(alert=latest_alert)
        if executions.exists():
            latest_exec = executions.first()
            print(f'✅ Execution Created: {latest_exec.execution_id}')
            print(f'   Status: {latest_exec.status}')
            print(f'   Steps: {latest_exec.workflow_steps.count()}')
            
            for step in latest_exec.workflow_steps.all():
                print(f'   Step {step.step_number}: {step.step_name} - {step.status}')
        else:
            print('❌ No execution created for this alert')
    else:
        print('❌ No alert created for test product')

    # Clean up
    test_product.delete()
    print('🗑️  Test product deleted')

if __name__ == "__main__":
    test_new_product_alert()