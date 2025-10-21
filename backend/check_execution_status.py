#!/usr/bin/env python3

import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'main.settings')
django.setup()

from app.models import AgentExecution, AgentWorkflowStep
from django.db.models import Count

print("=== CURRENT EXECUTIONS STATUS ===")
executions = AgentExecution.objects.all().order_by('-started_at')

for exec in executions:
    steps = AgentWorkflowStep.objects.filter(execution=exec)
    completed_steps = steps.filter(status='completed').count()
    total_steps = steps.count()
    
    print(f"ID: {exec.execution_id}")
    print(f"  Status: {exec.status}")
    print(f"  Alert: {exec.alert.alert_type} - {exec.alert.product.name if exec.alert.product else 'No Product'}")
    print(f"  Started: {exec.started_at}")
    print(f"  Completed: {exec.completed_at}")
    print(f"  Root Cause: {exec.root_cause}")
    print(f"  Confidence: {exec.confidence_score}")
    print(f"  Steps: {completed_steps}/{total_steps}")
    print(f"  Steps Details:")
    
    for step in steps:
        print(f"    - Step {step.step_number}: {step.step_name}: {step.status}")
        if step.error_message:
            print(f"      Error: {step.error_message}")
    print("---")

print(f"\nTotal Executions: {executions.count()}")
print(f"Started Status: {executions.filter(status='started').count()}")
print(f"Completed Status: {executions.filter(status='completed').count()}")
print(f"Failed Status: {executions.filter(status='failed').count()}")