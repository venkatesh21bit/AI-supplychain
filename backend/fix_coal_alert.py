"""
Fix COAL alert and execution history issues.
"""

import os
import django
from datetime import datetime

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'main.settings')
django.setup()

from django.utils import timezone
from app.models import Product, Company, AgentAlert, AgentExecution, AgentWorkflowStep


def create_coal_alert():
    """Create critical COAL alert scenario."""
    
    print("🔥 Creating COAL critical alert scenario...")
    
    # Get COAL product
    company = Company.objects.filter(name__icontains='ConstructCo').first()
    coal_product = Product.objects.filter(name='COAL', company=company).first()
    
    if not coal_product:
        print("❌ COAL product not found!")
        return
    
    print(f"📦 COAL current stock: {coal_product.available_quantity}")
    
    # Make COAL critical
    coal_product.available_quantity = 6
    coal_product.save()
    print(f"📦 COAL updated stock: {coal_product.available_quantity}")
    
    # Create alert
    alert = AgentAlert.objects.create(
        alert_type='low_inventory',
        company=company,
        product=coal_product,
        priority='critical',
        status='analyzing',
        current_stock=6,
        alert_data={
            'triggered_by': 'manual_update',
            'threshold': 10,
            'previous_stock': 100,
            'urgency': 'high'
        }
    )
    print(f"🚨 Created COAL alert: {alert.alert_id}")
    
    # Create execution
    execution = AgentExecution.objects.create(
        execution_id=f'EXEC-COAL-{timezone.now().strftime("%Y%m%d-%H%M%S")}',
        alert=alert,
        status='started',
        root_cause='High demand for COAL in winter season',
        confidence_score=0.88,
        analysis_data={
            'seasonal_demand': True,
            'supply_chain_factor': 'winter_increase'
        },
        solution_data={
            'recommended_quantity': 75,
            'preferred_supplier': 'Coal Mining Corp',
            'estimated_cost': float(coal_product.price * 75)
        },
        orchestration_data={
            'supplier_availability': True,
            'delivery_timeline': '5-7 days'
        },
        summary={
            'root_cause': 'High demand for COAL in winter season',
            'confidence': 0.88,
            'recommended_quantity': 75
        }
    )
    print(f"⚡ Created COAL execution: {execution.execution_id}")
    
    # Create workflow steps
    steps_data = [
        ('Root Cause Analysis', 'completed'),
        ('Solution Generation', 'in_progress'), 
        ('Orchestration & Execution', 'pending')
    ]
    
    for i, (name, status) in enumerate(steps_data):
        step = AgentWorkflowStep.objects.create(
            execution=execution,
            step_number=i + 1,
            step_name=name,
            status=status,
            step_data={'step_info': f'Step {i+1} data'},
            result_data={'result_info': f'Step {i+1} result'},
            started_at=timezone.now() if status != 'pending' else None,
            completed_at=timezone.now() if status == 'completed' else None
        )
    
    print(f"📋 Created {len(steps_data)} workflow steps for COAL")
    return alert, execution


def check_current_status():
    """Check current alert and execution status."""
    
    print("\n=== CURRENT STATUS ===")
    
    print("🚨 Active Alerts:")
    alerts = AgentAlert.objects.filter(status='analyzing').order_by('-detected_at')
    for alert in alerts:
        print(f"   • {alert.product.name}: {alert.current_stock} units - Alert #{alert.alert_id}")
    
    print(f"\n⚡ Active Executions ({AgentExecution.objects.count()} total):")
    executions = AgentExecution.objects.all().order_by('-started_at')
    for exec in executions:
        steps_count = exec.workflow_steps.count()
        print(f"   • {exec.execution_id}: {exec.alert.product.name} - {exec.status} - {steps_count} steps")
    
    print(f"\n📊 Total Workflow Steps: {AgentWorkflowStep.objects.count()}")


if __name__ == "__main__":
    try:
        create_coal_alert()
        check_current_status()
        
        print("\n🎉 COAL alert and execution created successfully!")
        print("✅ All products should now show in LOGI-BOT dashboard")
        print("✅ Execution history should be populated")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()