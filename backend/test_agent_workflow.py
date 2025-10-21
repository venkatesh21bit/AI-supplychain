#!/usr/bin/env python3

import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'main.settings')
django.setup()

from logibot.agent import LogiBot
from logibot.config import AgentConfig
import traceback

def test_agent_workflow():
    """Test agent workflow execution manually."""
    
    print("🧪 Testing LOGI-BOT Agent Workflow...")
    
    try:
        # Initialize agent
        config = AgentConfig()
        agent = LogiBot(config)
        
        # Test data from our COAL alert
        alert_data = {
            'product_id': 1,  # COAL product ID
            'product_name': 'COAL',
            'current_stock': 6,
            'company_id': 1,
            'alert_id': 28
        }
        
        print(f"🎯 Testing with alert data: {alert_data}")
        
        # Execute workflow
        result = agent.handle_alert('low_inventory', alert_data)
        
        print(f"\n📊 WORKFLOW RESULT:")
        print(f"  Execution ID: {result.get('execution_id')}")
        print(f"  Status: {result.get('status')}")
        print(f"  Steps: {len(result.get('steps', []))}")
        
        for i, step in enumerate(result.get('steps', [])):
            print(f"    Step {i+1}: {step.get('name')} - {step.get('status')}")
            if step.get('status') == 'failed':
                print(f"      Error: {step.get('error')}")
        
        if result.get('error'):
            print(f"  ❌ Error: {result.get('error')}")
            
        if result.get('summary'):
            summary = result.get('summary')
            print(f"  📋 Summary:")
            print(f"    Root Cause: {summary.get('root_cause')}")
            print(f"    Confidence: {summary.get('confidence')}")
        
        # Now test database saving like the API does
        print(f"\n💾 Testing Database Save...")
        from app.models import AgentAlert, AgentExecution, AgentWorkflowStep
        from app.agent_views import _save_execution_to_db
        
        try:
            # Get the alert that should exist
            alert = AgentAlert.objects.get(alert_id=alert_data['alert_id'])
            print(f"  Found Alert: {alert}")
            
            # Save execution to DB like the API does
            execution = _save_execution_to_db(result, alert)
            
            if execution:
                print(f"  ✅ Saved Execution: {execution.execution_id}")
                print(f"  Status: {execution.status}")
                
                # Check workflow steps
                steps = AgentWorkflowStep.objects.filter(execution=execution)
                print(f"  Steps in DB: {steps.count()}")
                for step in steps:
                    print(f"    - Step {step.step_number}: {step.step_name}: {step.status}")
            else:
                print(f"  ❌ Failed to save execution")
                
        except Exception as db_e:
            print(f"  ❌ Database error: {str(db_e)}")
            
        return result
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        print(traceback.format_exc())
        return None

if __name__ == "__main__":
    test_agent_workflow()