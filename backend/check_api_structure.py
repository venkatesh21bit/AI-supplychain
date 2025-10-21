#!/usr/bin/env python3

import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'main.settings')
django.setup()

import requests
from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import RefreshToken

def check_api_structure():
    """Check the current API response structure for executions."""
    
    # Get token
    user = User.objects.filter(is_superuser=True).first()
    refresh = RefreshToken.for_user(user)
    access_token = str(refresh.access_token)

    # Test executions API
    response = requests.get(
        'http://localhost:8000/api/agent/executions/',
        headers={'Authorization': f'Bearer {access_token}'}
    )

    if response.status_code == 200:
        data = response.json()
        print('🔍 API Response Structure:')
        print(f'Response keys: {list(data.keys())}')
        
        if 'results' in data and len(data['results']) > 0:
            execution = data['results'][0]
            print(f'First execution keys: {list(execution.keys())}')
            print(f'Execution ID: {execution.get("execution_id")}')
            print(f'Has workflow_steps: {"workflow_steps" in execution}')
            
            if 'workflow_steps' in execution:
                steps = execution['workflow_steps']
                print(f'Workflow steps type: {type(steps)}')
                print(f'Workflow steps length: {len(steps) if steps else "None"}')
                if steps and len(steps) > 0:
                    print(f'First step keys: {list(steps[0].keys()) if isinstance(steps[0], dict) else "Not dict"}')
                    print(f'First step: {steps[0]}')
            else:
                print('❌ workflow_steps field missing!')
                
        elif 'executions' in data and len(data['executions']) > 0:
            execution = data['executions'][0]
            print(f'First execution (from executions key): {list(execution.keys())}')
        else:
            print('❌ No executions found in response')
            print(f'Full response: {data}')
    else:
        print(f'❌ API Error: {response.status_code} - {response.text}')

if __name__ == "__main__":
    check_api_structure()