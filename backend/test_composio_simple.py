#!/usr/bin/env python3
"""
Simple Composio Test Script
"""
import os
import asyncio
from datetime import datetime

# Setup Django
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'main.settings')
django.setup()

from logibot.enhanced_composio_orchestrator import EnhancedComposioOrchestrator

async def test_composio_integration():
    print('🚀 Testing Composio Integration')
    print('=' * 40)
    
    orchestrator = EnhancedComposioOrchestrator()
    status = orchestrator.get_status()
    
    print(f'Composio Available: {status["composio_available"]}')
    print(f'API Key Configured: {status["api_key_configured"]}')
    print(f'Connected Apps: {len(status["connected_apps"])}')
    print(f'Total Tools: {status["total_tools"]}')
    
    if status['composio_available'] and status['api_key_configured']:
        print('\n🧪 Testing workflow execution...')
        test_alert = {
            'product_name': 'Steel Rods',
            'current_stock': 150,
            'minimum_threshold': 500,
            'urgency': 'high'
        }
        
        result = await orchestrator.execute_comprehensive_workflow(test_alert)
        print(f'✅ Workflow ID: {result["workflow_id"]}')
        print(f'✅ Success Rate: {result["success_rate"]:.1f}%')
        
        for platform, platform_result in result["platforms"].items():
            status_icon = "✅" if platform_result.get("success") else "❌"
            message = platform_result.get("message", platform_result.get("error", "Unknown"))
            print(f'  {status_icon} {platform.title()}: {message}')
    
    else:
        print('\n⚠️ Composio not fully configured')
        print('Using mock responses for demonstration...')
        
        # Mock successful workflow
        mock_result = {
            'workflow_id': f'mock_workflow_{datetime.now().strftime("%Y%m%d_%H%M%S")}',
            'success_rate': 85.0,
            'platforms': {
                'asana': {'success': True, 'message': 'Task created: Steel Rods restocking'},
                'slack': {'success': True, 'message': 'Alert sent to #supply-chain'},
                'gmail': {'success': True, 'message': 'Email sent to manager'},
                'sheets': {'success': False, 'error': 'Sheet ID not configured'},
                'calendar': {'success': True, 'message': 'Meeting scheduled for review'}
            }
        }
        
        print(f'✅ Mock Workflow ID: {mock_result["workflow_id"]}')
        print(f'✅ Mock Success Rate: {mock_result["success_rate"]:.1f}%')
        
        for platform, platform_result in mock_result["platforms"].items():
            status_icon = "✅" if platform_result.get("success") else "❌"
            message = platform_result.get("message", platform_result.get("error", "Unknown"))
            print(f'  {status_icon} {platform.title()}: {message}')
    
    print('\n🎉 Composio Test Complete!')

if __name__ == '__main__':
    asyncio.run(test_composio_integration())