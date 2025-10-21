#!/usr/bin/env python3

import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'main.settings')
django.setup()

import requests
from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import RefreshToken

def check_workflow_steps():
    """Check the actual workflow steps structure from the API."""
    
    # Get token
    user = User.objects.filter(is_superuser=True).first()
    refresh = RefreshToken.for_user(user)
    access_token = str(refresh.access_token)

    # Test executions API and show workflow steps structure
    response = requests.get(
        'http://localhost:8000/api/agent/executions/',
        headers={'Authorization': f'Bearer {access_token}'}
    )

    if response.status_code == 200:
        data = response.json()
        if 'executions' in data and len(data['executions']) > 0:
            execution = data['executions'][0]
            print(f'🔍 Execution ID: {execution.get("execution_id")}')
            
            if 'workflow_steps' in execution and execution['workflow_steps']:
                steps = execution['workflow_steps']
                print(f'📋 Number of workflow steps: {len(steps)}')
                print('🔧 First workflow step structure:')
                for key, value in steps[0].items():
                    print(f'  {key}: {value}')
                    
                print('\n📋 All step names and statuses:')
                for i, step in enumerate(steps):
                    step_name = step.get('step_name', 'Unknown')
                    status = step.get('status', 'Unknown')
                    step_num = step.get('step_number', i+1)
                    print(f'  Step {step_num}: {step_name} - {status}')
            else:
                print('❌ No workflow_steps found')
        else:
            print('❌ No executions found')
    else:
        print(f'❌ API Error: {response.status_code}')

if __name__ == "__main__":
    check_workflow_steps()