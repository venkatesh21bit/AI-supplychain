#!/usr/bin/env python3
"""
Check database state for alerts and executions
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'main.settings')
django.setup()

from app.models import AgentAlert, AgentExecution, AgentWorkflowStep

def main():
    alerts = AgentAlert.objects.all().order_by('-detected_at')
    executions = AgentExecution.objects.all().order_by('-started_at')

    print('🚨 ALERTS:')
    for i, alert in enumerate(alerts[:10], 1):
        print(f'{i}. {alert.alert_type} - {alert.product.name} - {alert.status} - {alert.detected_at}')

    print(f'\nTotal Alerts: {AgentAlert.objects.count()}')
    print(f'Active Alerts: {AgentAlert.objects.filter(status="active").count()}')
    print(f'Detected Alerts: {AgentAlert.objects.filter(status="detected").count()}')

    print('\n🤖 EXECUTIONS:')
    for i, exec in enumerate(executions, 1):
        steps_count = AgentWorkflowStep.objects.filter(execution=exec).count()
        print(f'{i}. {exec.execution_id} - {exec.alert.product.name} - {exec.status} - Steps: {steps_count} - {exec.started_at}')

    print(f'\nTotal Executions: {AgentExecution.objects.count()}')
    print(f'Completed Executions: {AgentExecution.objects.filter(status="completed").count()}')
    print(f'Total Workflow Steps: {AgentWorkflowStep.objects.count()}')

    # Check if there are executions without proper alerts
    print('\n🔍 ANALYSIS:')
    alerts_with_executions = AgentAlert.objects.filter(executions__isnull=False).distinct().count()
    print(f'Alerts with executions: {alerts_with_executions}')
    
    executions_without_proper_alert = AgentExecution.objects.filter(alert__isnull=True).count()
    print(f'Executions without alert: {executions_without_proper_alert}')

if __name__ == '__main__':
    main()