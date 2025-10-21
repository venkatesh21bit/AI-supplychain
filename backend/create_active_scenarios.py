"""
Script to set up multiple critical stock situations for LOGI-BOT demo.
This will create realistic low stock scenarios and active workflows.
"""

import os
import sys
import django
from datetime import datetime, timedelta

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'main.settings')
django.setup()

from django.utils import timezone
from app.models import (
    Product, Company, AgentAlert, AgentExecution, 
    AgentWorkflowStep, AgentConfiguration
)
from app.email_service import email_service
import json


def create_critical_stock_scenarios():
    """Create multiple critical stock scenarios for demo."""
    
    print("🚨 Setting up critical stock scenarios for LOGI-BOT demo...")
    
    # Get the company
    company = Company.objects.filter(name__icontains='ConstructCo').first()
    if not company:
        print("❌ ConstructCo company not found!")
        return
    
    # Get or create agent config
    agent_config, _ = AgentConfiguration.objects.get_or_create(
        company=company,
        defaults={
            'critical_inventory_level': 10,
            'warning_inventory_level': 20,
            'auto_resolution_enabled': True,
            'require_approval': True,
            'notification_emails': json.dumps(['admin@constructco.com', 'manager@constructco.com'])
        }
    )
    
    # Critical stock scenarios
    critical_scenarios = [
        {'name': 'CEMENT', 'new_stock': 5, 'priority': 'critical'},
        {'name': 'STEEL_RODS', 'new_stock': 7, 'priority': 'critical'},
        {'name': 'CONCRETE_BLOCKS', 'new_stock': 3, 'priority': 'critical'},
        {'name': 'LIMESTONE', 'new_stock': 2, 'priority': 'critical'},  # Make even more critical
    ]
    
    created_alerts = []
    
    for scenario in critical_scenarios:
        try:
            # Update product stock
            product = Product.objects.filter(name=scenario['name'], company=company).first()
            if not product:
                print(f"⚠️ Product {scenario['name']} not found, skipping...")
                continue
            
            old_stock = product.available_quantity
            product.available_quantity = scenario['new_stock']
            product.save()
            
            print(f"📦 {product.name}: {old_stock} → {scenario['new_stock']} units")
            
            # Create active alert
            alert = AgentAlert.objects.create(
                alert_type='low_inventory',
                company=company,
                product=product,
                priority=scenario['priority'],
                status='analyzing',  # Active status
                current_stock=scenario['new_stock'],
                alert_data={
                    'triggered_by': 'demo_setup',
                    'threshold': agent_config.critical_inventory_level,
                    'previous_stock': old_stock,
                    'urgency_level': 'high',
                    'supplier_lead_time': '2-3 days'
                }
            )
            created_alerts.append(alert)
            
            # Create active execution
            execution = AgentExecution.objects.create(
                execution_id=f'EXEC-{datetime.now().strftime("%Y%m%d-%H%M%S")}-{product.name[:4]}',
                alert=alert,
                status='started',  # Use valid status
                root_cause=f'Unexpected demand surge for {product.name}',
                confidence_score=0.92,
                analysis_data={
                    'demand_pattern': 'surge_detected',
                    'seasonal_factor': 'Q4_construction_boom',
                    'supplier_status': 'available',
                    'lead_time_days': 3
                },
                solution_data={
                    'recommended_quantity': max(50, scenario['new_stock'] * 5),
                    'preferred_supplier': 'BuildMart Supplies',
                    'estimated_cost': float(product.price * max(50, scenario['new_stock'] * 5)),
                    'delivery_priority': 'express'
                },
                orchestration_data={
                    'purchase_order_status': 'generating',
                    'supplier_contacted': True,
                    'approval_required': True,
                    'estimated_delivery': (datetime.now() + timedelta(days=3)).strftime('%Y-%m-%d')
                },
                summary={
                    'root_cause': f'Unexpected demand surge for {product.name}',
                    'confidence': 0.92,
                    'recommended_quantity': max(50, scenario['new_stock'] * 5),
                    'status': 'analyzing_and_coordinating'
                },
                completed_at=None  # Not completed yet
            )
            
            # Create workflow steps (some completed, some in progress)
            steps_data = [
                {
                    'step_name': 'Root Cause Analysis',
                    'status': 'completed',
                    'step_data': {
                        'analysis_type': 'demand_surge_detection',
                        'confidence': 0.95,
                        'contributing_factors': ['seasonal_demand', 'supply_chain_delay', 'new_projects']
                    },
                    'result_data': {
                        'primary_cause': f'High demand for {product.name} due to construction projects',
                        'recommendation': 'immediate_replenishment'
                    }
                },
                {
                    'step_name': 'Solution Generation',
                    'status': 'in_progress',
                    'step_data': {
                        'solution_type': 'emergency_procurement',
                        'suppliers_contacted': 3,
                        'best_option': 'BuildMart Supplies'
                    },
                    'result_data': {
                        'selected_supplier': 'BuildMart Supplies',
                        'quantity': max(50, scenario['new_stock'] * 5),
                        'estimated_cost': float(product.price * max(50, scenario['new_stock'] * 5))
                    }
                },
                {
                    'step_name': 'Orchestration & Execution',
                    'status': 'pending',
                    'step_data': {
                        'next_actions': ['generate_purchase_order', 'coordinate_delivery', 'notify_stakeholders']
                    },
                    'result_data': {}
                }
            ]
            
            for i, step_data in enumerate(steps_data):
                AgentWorkflowStep.objects.create(
                    execution=execution,
                    step_number=i + 1,
                    step_name=step_data['step_name'],
                    status=step_data['status'],
                    step_data=step_data['step_data'],
                    result_data=step_data['result_data'],
                    started_at=timezone.now() if step_data['status'] != 'pending' else None,
                    completed_at=timezone.now() if step_data['status'] == 'completed' else None
                )
            
            print(f"✅ Created active alert and workflow for {product.name}")
            
            # Send email notification
            email_service.send_low_stock_alert(
                product_name=product.name,
                current_stock=scenario['new_stock'],
                threshold=agent_config.critical_inventory_level,
                company_name=company.name,
                recipient_emails=['admin@constructco.com', 'manager@constructco.com']
            )
            
        except Exception as e:
            print(f"❌ Error creating scenario for {scenario['name']}: {str(e)}")
    
    print(f"\n🎉 Created {len(created_alerts)} active critical stock alerts!")
    print("📊 Summary:")
    for alert in created_alerts:
        print(f"   • {alert.product.name}: {alert.current_stock} units - {alert.status.upper()}")
    
    print("\n🚀 LOGI-BOT Dashboard should now show:")
    print("   • Multiple active alerts in Alert Monitor")
    print("   • Live animated workflows in progress")
    print("   • Real-time execution updates")
    print("   • Email notifications sent")


if __name__ == "__main__":
    create_critical_stock_scenarios()