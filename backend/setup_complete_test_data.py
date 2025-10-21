#!/usr/bin/env python3
"""
Comprehensive LOGI-BOT Test Data Setup Script
Creates realistic data that matches across all dashboard components
"""

import os
import sys
import django
from datetime import datetime, timedelta
from decimal import Decimal

# Add the project directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'main.settings')
django.setup()

from django.contrib.auth.models import User, Group
from app.models import (
    Company, Product, Category, Retailer, Order, OrderItem,
    AgentAlert, AgentExecution, AgentWorkflowStep, AgentConfiguration
)

def create_test_data():
    print("🚀 Creating comprehensive LOGI-BOT test data...")
    
    # Clear existing data
    print("🧹 Clearing existing data...")
    AgentWorkflowStep.objects.all().delete()
    AgentExecution.objects.all().delete()
    AgentAlert.objects.all().delete()
    AgentConfiguration.objects.all().delete()
    OrderItem.objects.all().delete()
    Order.objects.all().delete()
    Product.objects.all().delete()
    Category.objects.all().delete()
    Retailer.objects.all().delete()
    Company.objects.all().delete()
    User.objects.filter(username__in=['admin', 'manufacturer1', 'retailer1', 'employee1']).delete()
    
    # Create Groups
    print("👥 Creating user groups...")
    manufacturer_group, _ = Group.objects.get_or_create(name='Manufacturer')
    retailer_group, _ = Group.objects.get_or_create(name='Retailer')
    employee_group, _ = Group.objects.get_or_create(name='Employee')
    
    # Create Users
    print("👤 Creating users...")
    
    # Admin user for API access
    admin_user = User.objects.create_user(
        username='admin',
        email='admin@logibot.com',
        password='password123',
        first_name='System',
        last_name='Administrator',
        is_staff=True,
        is_superuser=True
    )
    
    # Manufacturer user
    manufacturer_user = User.objects.create_user(
        username='manufacturer1',
        email='manager@constructco.com',
        password='manu123',
        first_name='John',
        last_name='Manufacturing'
    )
    manufacturer_user.groups.add(manufacturer_group)
    
    # Retailer user
    retailer_user = User.objects.create_user(
        username='retailer1',
        email='orders@buildmart.com',
        password='retail123',
        first_name='Sarah',
        last_name='Retail'
    )
    retailer_user.groups.add(retailer_group)
    
    # Employee user
    employee_user = User.objects.create_user(
        username='employee1',
        email='warehouse@constructco.com',
        password='emp123',
        first_name='Mike',
        last_name='Warehouse'
    )
    employee_user.groups.add(employee_group)
    
    # Create Companies
    print("🏢 Creating companies...")
    
    # Manufacturer Company
    manufacturer_company = Company.objects.create(
        user=manufacturer_user,
        name="ConstructCo Materials Ltd",
        gstin="29ABCDE1234F1Z5",
        address="123 Industrial Park, Manufacturing District",
        state="Karnataka",
        city="Bangalore",
        pincode="560001",
        phone="+91-80-12345678",
        email="contact@constructco.com",
        description="Leading manufacturer of construction materials and industrial supplies",
        is_public=True
    )
    
    # Retailer Company
    retailer_company = Company.objects.create(
        user=retailer_user,
        name="BuildMart Retail Chain",
        gstin="29FGHIJ5678K2L9",
        address="456 Commerce Boulevard, Retail Center",
        state="Karnataka",
        city="Bangalore",
        pincode="560002",
        phone="+91-80-87654321",
        email="info@buildmart.com",
        description="Premier retail chain for construction and building materials",
        is_public=True
    )
    
    # Create Categories
    print("� Creating categories...")
    
    raw_materials = Category.objects.create(
        company=manufacturer_company,
        name="Raw Materials"
    )
    
    metal_products = Category.objects.create(
        company=manufacturer_company,
        name="Metal Products"
    )
    
    building_materials = Category.objects.create(
        company=manufacturer_company,
        name="Building Materials"
    )
    
    # Create Retailers (as suppliers)
    print("🚚 Creating supplier retailers...")
    
    primary_supplier = Retailer.objects.create(
        company=manufacturer_company,
        name="RockSolid Quarries Inc",
        contact_person="David Stone",
        email="orders@rocksolid.com",
        contact="+91-80-11111111",
        address_line1="789 Quarry Road",
        city="Stone Valley",
        state="Karnataka",
        pincode="560050",
        gstin="29ROCKSOLID1F1Z5",
        distance_from_warehouse=15.5,
        is_active=True
    )
    
    backup_supplier = Retailer.objects.create(
        company=manufacturer_company,
        name="Mountain Materials Co",
        contact_person="Lisa Peak",
        email="supply@mountainmaterials.com",
        contact="+91-80-22222222",
        address_line1="321 Peak Drive",
        city="Highland City",
        state="Karnataka",
        pincode="560060",
        gstin="29MOUNTAIN1F1Z5",
        distance_from_warehouse=22.3,
        is_active=True
    )
    
    # Create Products with stock levels
    print("📦 Creating products...")
    
    limestone = Product.objects.create(
        company=manufacturer_company,
        name="LIMESTONE",
        category=raw_materials,
        available_quantity=8,  # CRITICAL LOW - triggers LOGI-BOT
        total_required_quantity=50,
        unit='TON',
        price=Decimal('45.50'),
        hsn_code='2521',
        cgst_rate=Decimal('9.00'),
        sgst_rate=Decimal('9.00'),
        igst_rate=Decimal('18.00'),
        created_by=manufacturer_user
    )
    
    steel_rods = Product.objects.create(
        company=manufacturer_company,
        name="STEEL_RODS",
        category=metal_products,
        available_quantity=245,  # Good stock
        total_required_quantity=200,
        unit='PCS',
        price=Decimal('125.75'),
        hsn_code='7213',
        cgst_rate=Decimal('9.00'),
        sgst_rate=Decimal('9.00'),
        igst_rate=Decimal('18.00'),
        created_by=manufacturer_user
    )
    
    cement = Product.objects.create(
        company=manufacturer_company,
        name="CEMENT",
        category=building_materials,
        available_quantity=15,  # Low but not critical
        total_required_quantity=25,
        unit='BAG',
        price=Decimal('32.90'),
        hsn_code='2523',
        cgst_rate=Decimal('9.00'),
        sgst_rate=Decimal('9.00'),
        igst_rate=Decimal('18.00'),
        created_by=manufacturer_user
    )
    
    concrete_blocks = Product.objects.create(
        company=manufacturer_company,
        name="CONCRETE_BLOCKS",
        category=building_materials,
        available_quantity=500,  # Good stock
        total_required_quantity=300,
        unit='PCS',
        price=Decimal('8.25'),
        hsn_code='6810',
        cgst_rate=Decimal('9.00'),
        sgst_rate=Decimal('9.00'),
        igst_rate=Decimal('18.00'),
        created_by=manufacturer_user
    )
    
    # Create Agent Configuration
    print("🤖 Creating LOGI-BOT configuration...")
    
    agent_config = AgentConfiguration.objects.create(
        company=manufacturer_company,
        critical_inventory_level=5,
        warning_inventory_level=10,
        reorder_point=15,
        safety_stock=5,
        auto_resolution_enabled=True,
        require_approval=False,  # For demo purposes
        check_interval_minutes=5,
        notification_emails=["manager@constructco.com", "procurement@constructco.com"]
    )
    
    # Create Historical Orders for realistic data
    print("📋 Creating historical orders...")
    
    # Recent order from 1 week ago
    recent_order = Order.objects.create(
        retailer=primary_supplier,
        status="delivered"
    )
    
    OrderItem.objects.create(
        order=recent_order,
        product=limestone,
        quantity=100
    )
    
    # Create Agent Alerts (Historical)
    print("🚨 Creating agent alerts...")
    
    # Historical resolved alert
    resolved_alert = AgentAlert.objects.create(
        alert_type="low_inventory",
        product=cement,
        company=manufacturer_company,
        priority="high",
        status="resolved",
        current_stock=12,
        alert_data={"threshold_value": 15, "message": "Low inventory detected for CEMENT - 12 units remaining"},
        resolved_at=datetime.now() - timedelta(days=1)
    )
    
    # Current critical alert for LIMESTONE
    current_alert = AgentAlert.objects.create(
        alert_type="low_inventory",
        product=limestone,
        company=manufacturer_company,
        priority="critical",
        status="detected",
        current_stock=8,
        alert_data={"threshold_value": 10, "message": "CRITICAL: LIMESTONE inventory below threshold - immediate action required"}
    )
    
    # Create Agent Execution (Historical)
    print("⚡ Creating agent execution history...")
    
    execution = AgentExecution.objects.create(
        execution_id="EXEC-2024-001",
        alert=current_alert,
        status="completed",
        root_cause="Increased demand spike",
        confidence_score=0.85,
        completed_at=datetime.now() - timedelta(hours=1, minutes=15),
        analysis_data={
            "consumption_rate": "15.2 units/day",
            "supplier_performance": "98.5% on-time delivery",
            "demand_forecast": "High seasonal demand detected"
        },
        solution_data={
            "replenishment_qty": 160,
            "lead_time_days": 3,
            "sourcing_strategy": "Emergency dual-supplier"
        },
        orchestration_data={
            "asana_project_created": True,
            "meeting_scheduled": True,
            "orders_drafted": 2
        },
        summary={
            "product": "LIMESTONE",
            "execution_status": "COMPLETED",
            "steps_completed": "3/3",
            "actions_taken": [
                "Root cause analysis completed",
                "Replenishment plan generated: 160 units",
                "External systems orchestrated"
            ],
            "root_cause": "Increased demand spike",
            "confidence": "85%",
            "replenishment_qty": 160
        }
    )
    
    # Create Workflow Steps
    print("🔄 Creating workflow steps...")
    
    # Step 1: Root Cause Analysis
    step1 = AgentWorkflowStep.objects.create(
        execution=execution,
        step_number=1,
        step_name="root_cause_analysis",
        status="completed",
        started_at=datetime.now() - timedelta(hours=1, minutes=30),
        completed_at=datetime.now() - timedelta(hours=1, minutes=30) + timedelta(seconds=30),
        step_data={
            "analysis_type": "Deep Learning Analysis",
            "timeframe": "2.3 seconds"
        },
        result_data={
            "root_cause": "Increased demand spike",
            "confidence": 0.85,
            "current_inventory": 8,
            "consumption_rate": "15.2 units/day",
            "supplier_performance": "98.5% on-time delivery",
            "demand_forecast": "High seasonal demand detected"
        }
    )
    
    # Step 2: Solution Formulation
    step2 = AgentWorkflowStep.objects.create(
        execution=execution,
        step_number=2,
        step_name="solution_formulation",
        status="completed",
        started_at=step1.completed_at,
        completed_at=step1.completed_at + timedelta(seconds=45),
        step_data={
            "optimization_method": "AI-powered planning",
            "suppliers_evaluated": 2
        },
        result_data={
            "recommendation": {
                "total_replenishment_qty": 160,
                "net_requirement": 152,
                "priority_level": "CRITICAL",
                "timeline": {
                    "expected_delivery": (datetime.now() + timedelta(days=3)).isoformat(),
                    "lead_time_days": 3,
                    "order_placement": "Immediate"
                },
                "sourcing_strategy": {
                    "primary_supplier": "RockSolid Quarries Inc",
                    "backup_supplier": "Mountain Materials Co",
                    "split_order": True,
                    "shipping_method": "Express"
                }
            },
            "action_items": [
                {
                    "description": "Place emergency order with RockSolid Quarries (80 units)",
                    "priority": "CRITICAL",
                    "assigned_to": "Procurement Team",
                    "due_date": datetime.now().isoformat()
                },
                {
                    "description": "Backup order with Mountain Materials (80 units)",
                    "priority": "HIGH",
                    "assigned_to": "Supply Chain Manager",
                    "due_date": (datetime.now() + timedelta(hours=4)).isoformat()
                },
                {
                    "description": "Coordinate expedited shipping",
                    "priority": "HIGH",
                    "assigned_to": "Logistics Team",
                    "due_date": (datetime.now() + timedelta(hours=2)).isoformat()
                }
            ]
        }
    )
    
    # Step 3: Workflow Orchestration
    step3 = AgentWorkflowStep.objects.create(
        execution=execution,
        step_number=3,
        step_name="workflow_orchestration",
        status="completed",
        started_at=step2.completed_at,
        completed_at=step2.completed_at + timedelta(seconds=60),
        step_data={
            "external_tools": ["Asana", "Outlook", "ERP"],
            "integration_method": "Composio API"
        },
        result_data={
            "steps": [
                {
                    "step": "create_asana_project",
                    "status": "success",
                    "data": {
                        "success": True,
                        "project_name": "EMERGENCY_REPLENISHMENT_LIMESTONE_1",
                        "project_id": "ASN-1234567890",
                        "tasks_created": 5,
                        "team_members": ["procurement@constructco.com", "logistics@constructco.com"],
                        "due_date": (datetime.now() + timedelta(days=3)).isoformat()
                    }
                },
                {
                    "step": "schedule_meeting",
                    "status": "success",
                    "data": {
                        "success": True,
                        "meeting_id": "MTG-EMERGENCY-001",
                        "meeting_start": (datetime.now() + timedelta(hours=2)).isoformat(),
                        "attendees": ["manager@constructco.com", "procurement@constructco.com"],
                        "subject": "Emergency LIMESTONE Replenishment Briefing"
                    }
                },
                {
                    "step": "create_draft_orders",
                    "status": "success",
                    "data": {
                        "success": True,
                        "orders_created": 2,
                        "total_quantity": 160,
                        "primary_order": {
                            "vendor": "RockSolid Quarries Inc",
                            "quantity": 80,
                            "estimated_cost": "$3,640.00"
                        },
                        "backup_order": {
                            "vendor": "Mountain Materials Co",
                            "quantity": 80,
                            "estimated_cost": "$3,640.00"
                        }
                    }
                }
            ]
        }
    )
    
    print("\n✅ Test data creation completed successfully!")
    print("\n" + "="*60)
    print("🔐 USER CREDENTIALS")
    print("="*60)
    print(f"🔧 ADMIN USER:")
    print(f"   Username: admin")
    print(f"   Password: password123")
    print(f"   Email: admin@logibot.com")
    print(f"   Role: System Administrator")
    print()
    print(f"🏭 MANUFACTURER USER:")
    print(f"   Username: manufacturer1")
    print(f"   Password: manu123")
    print(f"   Email: manager@constructco.com")
    print(f"   Company: ConstructCo Materials Ltd")
    print(f"   Role: Manufacturing Manager")
    print()
    print(f"🏪 RETAILER USER:")
    print(f"   Username: retailer1")
    print(f"   Password: retail123")
    print(f"   Email: orders@buildmart.com")
    print(f"   Company: BuildMart Retail Chain")
    print(f"   Role: Retail Manager")
    print()
    print(f"👷 EMPLOYEE USER:")
    print(f"   Username: employee1")
    print(f"   Password: emp123")
    print(f"   Email: warehouse@constructco.com")
    print(f"   Role: Warehouse Employee")
    print()
    print("="*60)
    print("📊 DASHBOARD DATA")
    print("="*60)
    print(f"🏢 Companies: {Company.objects.count()}")
    print(f"📦 Products: {Product.objects.count()}")
    print(f"� Categories: {Category.objects.count()}")
    print(f"🚚 Suppliers (Retailers): {Retailer.objects.count()}")
    print(f"🚨 Agent Alerts: {AgentAlert.objects.count()}")
    print(f"⚡ Agent Executions: {AgentExecution.objects.count()}")
    print(f"🔄 Workflow Steps: {AgentWorkflowStep.objects.count()}")
    print()
    print("🎯 CRITICAL ALERT STATUS:")
    print(f"   Product: LIMESTONE")
    print(f"   Current Stock: 8 units")
    print(f"   Threshold: 10 units")
    print(f"   Status: CRITICAL - Ready for LOGI-BOT demo!")
    print()
    print("🚀 Ready to test LOGI-BOT dashboard with real data!")
    print("="*60)

if __name__ == "__main__":
    create_test_data()