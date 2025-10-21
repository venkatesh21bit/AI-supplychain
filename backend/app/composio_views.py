#!/usr/bin/env python3
"""
Enhanced Composio Views for LOGI-BOT
Cross-platform automation endpoints using Composio tools
"""
import os
import asyncio
import json
from datetime import datetime
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.http import JsonResponse
import logging

# Import the enhanced orchestrator
from logibot.enhanced_composio_orchestrator import EnhancedComposioOrchestrator

logger = logging.getLogger(__name__)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_cross_platform_workflow(request):
    """
    Create comprehensive workflow across multiple platforms
    
    POST /api/agent/composio/create-workflow/
    {
        "alert_data": {
            "product_name": "Steel Rods",
            "current_stock": 150,
            "minimum_threshold": 500,
            "urgency": "high"
        },
        "platforms": ["asana", "slack", "gmail", "sheets", "calendar"]
    }
    """
    try:
        data = request.data
        alert_data = data.get('alert_data', {})
        platforms = data.get('platforms', ['asana', 'slack', 'gmail'])
        
        orchestrator = EnhancedComposioOrchestrator()
        
        # Execute workflow asynchronously
        workflow_result = asyncio.run(
            orchestrator.execute_comprehensive_workflow(alert_data)
        )
        
        return Response({
            'success': True,
            'workflow_id': workflow_result['workflow_id'],
            'platforms_executed': list(workflow_result['platforms'].keys()),
            'success_rate': workflow_result['success_rate'],
            'results': workflow_result['platforms'],
            'message': f"Cross-platform workflow executed with {workflow_result['success_rate']:.1f}% success rate"
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Cross-platform workflow failed: {str(e)}")
        return Response({
            'success': False,
            'error': str(e),
            'message': 'Failed to execute cross-platform workflow'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def send_slack_notification(request):
    """
    Send notification to Slack channel
    
    POST /api/agent/composio/slack-notify/
    {
        "channel": "#supply-chain-alerts",
        "message": "Urgent stock alert for Steel Rods",
        "urgency": "high"
    }
    """
    try:
        data = request.data
        channel = data.get('channel', '#general')
        message = data.get('message', '')
        urgency = data.get('urgency', 'normal')
        
        orchestrator = EnhancedComposioOrchestrator()
        
        result = asyncio.run(
            orchestrator.send_slack_alert(channel, message, urgency)
        )
        
        if result['success']:
            return Response({
                'success': True,
                'channel': channel,
                'message_id': result.get('message_id'),
                'message': 'Slack notification sent successfully'
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'success': False,
                'error': result.get('error'),
                'message': 'Failed to send Slack notification'
            }, status=status.HTTP_400_BAD_REQUEST)
            
    except Exception as e:
        logger.error(f"Slack notification failed: {str(e)}")
        return Response({
            'success': False,
            'error': str(e),
            'message': 'Slack notification error'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_asana_task(request):
    """
    Create task in Asana
    
    POST /api/agent/composio/asana-task/
    {
        "title": "Urgent: Restock Steel Rods",
        "description": "Current stock: 150 units, Required: 500 units",
        "priority": "High"
    }
    """
    try:
        data = request.data
        title = data.get('title', 'LOGI-BOT Task')
        description = data.get('description', '')
        priority = data.get('priority', 'Medium')
        
        orchestrator = EnhancedComposioOrchestrator()
        
        result = asyncio.run(
            orchestrator.create_asana_task(title, description, priority)
        )
        
        if result['success']:
            return Response({
                'success': True,
                'task_id': result.get('task_id'),
                'task_url': result.get('task_url'),
                'message': f'Asana task created: {title}'
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'success': False,
                'error': result.get('error'),
                'message': 'Failed to create Asana task'
            }, status=status.HTTP_400_BAD_REQUEST)
            
    except Exception as e:
        logger.error(f"Asana task creation failed: {str(e)}")
        return Response({
            'success': False,
            'error': str(e),
            'message': 'Asana task creation error'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def send_email_notification(request):
    """
    Send email notification via Gmail
    
    POST /api/agent/composio/email-notify/
    {
        "to_email": "manager@company.com",
        "subject": "Critical Stock Alert",
        "body": "Immediate action required for Steel Rods inventory"
    }
    """
    try:
        data = request.data
        to_email = data.get('to_email', '')
        subject = data.get('subject', 'LOGI-BOT Alert')
        body = data.get('body', '')
        
        if not to_email:
            return Response({
                'success': False,
                'error': 'Email address is required',
                'message': 'Please provide recipient email address'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        orchestrator = EnhancedComposioOrchestrator()
        
        result = asyncio.run(
            orchestrator.send_gmail_notification(to_email, subject, body)
        )
        
        if result['success']:
            return Response({
                'success': True,
                'message_id': result.get('message_id'),
                'recipient': to_email,
                'message': f'Email sent successfully to {to_email}'
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'success': False,
                'error': result.get('error'),
                'message': 'Failed to send email notification'
            }, status=status.HTTP_400_BAD_REQUEST)
            
    except Exception as e:
        logger.error(f"Email notification failed: {str(e)}")
        return Response({
            'success': False,
            'error': str(e),
            'message': 'Email notification error'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def update_tracking_sheet(request):
    """
    Update Google Sheets with inventory tracking data
    
    POST /api/agent/composio/update-sheet/
    {
        "sheet_id": "your-google-sheet-id",
        "data": [
            ["2024-10-19 14:30:00", "Steel Rods", "150", "high", "Alert Generated"]
        ],
        "range": "A:E"
    }
    """
    try:
        data = request.data
        sheet_id = data.get('sheet_id', '')
        sheet_data = data.get('data', [])
        range_name = data.get('range', 'A1')
        
        if not sheet_id:
            return Response({
                'success': False,
                'error': 'Google Sheet ID is required',
                'message': 'Please provide valid Google Sheet ID'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        orchestrator = EnhancedComposioOrchestrator()
        
        result = asyncio.run(
            orchestrator.update_google_sheet(sheet_id, sheet_data, range_name)
        )
        
        if result['success']:
            return Response({
                'success': True,
                'updated_cells': result.get('updated_cells', 0),
                'rows_updated': len(sheet_data),
                'message': f'Google Sheet updated: {len(sheet_data)} rows'
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'success': False,
                'error': result.get('error'),
                'message': 'Failed to update Google Sheet'
            }, status=status.HTTP_400_BAD_REQUEST)
            
    except Exception as e:
        logger.error(f"Google Sheets update failed: {str(e)}")
        return Response({
            'success': False,
            'error': str(e),
            'message': 'Google Sheets update error'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def schedule_meeting(request):
    """
    Schedule calendar meeting
    
    POST /api/agent/composio/schedule-meeting/
    {
        "title": "Emergency Stock Review",
        "start_time": "2024-10-19T16:00:00Z",
        "duration_hours": 1,
        "attendees": ["manager@company.com", "procurement@company.com"]
    }
    """
    try:
        data = request.data
        title = data.get('title', 'LOGI-BOT Meeting')
        start_time_str = data.get('start_time', '')
        duration_hours = data.get('duration_hours', 1)
        attendees = data.get('attendees', [])
        
        if not start_time_str:
            return Response({
                'success': False,
                'error': 'Start time is required',
                'message': 'Please provide meeting start time'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            start_time = datetime.fromisoformat(start_time_str.replace('Z', '+00:00'))
        except ValueError:
            return Response({
                'success': False,
                'error': 'Invalid date format',
                'message': 'Please use ISO format: YYYY-MM-DDTHH:MM:SSZ'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        orchestrator = EnhancedComposioOrchestrator()
        
        result = asyncio.run(
            orchestrator.create_calendar_event(title, start_time, duration_hours, attendees)
        )
        
        if result['success']:
            return Response({
                'success': True,
                'event_id': result.get('event_id'),
                'event_link': result.get('event_link'),
                'attendees_count': len(attendees),
                'message': f'Meeting scheduled: {title}'
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'success': False,
                'error': result.get('error'),
                'message': 'Failed to schedule meeting'
            }, status=status.HTTP_400_BAD_REQUEST)
            
    except Exception as e:
        logger.error(f"Meeting scheduling failed: {str(e)}")
        return Response({
            'success': False,
            'error': str(e),
            'message': 'Meeting scheduling error'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_github_issue(request):
    """
    Create GitHub issue for technical problems
    
    POST /api/agent/composio/github-issue/
    {
        "repo": "company/supply-chain-system",
        "title": "Inventory Sync Error",
        "body": "Automated detection of inventory synchronization issues",
        "labels": ["bug", "inventory", "urgent"]
    }
    """
    try:
        data = request.data
        repo = data.get('repo', '')
        title = data.get('title', 'LOGI-BOT Issue')
        body = data.get('body', '')
        labels = data.get('labels', [])
        
        if not repo:
            return Response({
                'success': False,
                'error': 'Repository name is required',
                'message': 'Please provide GitHub repository (format: owner/repo)'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        orchestrator = EnhancedComposioOrchestrator()
        
        result = asyncio.run(
            orchestrator.create_github_issue(repo, title, body, labels)
        )
        
        if result['success']:
            return Response({
                'success': True,
                'issue_number': result.get('issue_number'),
                'issue_url': result.get('issue_url'),
                'labels_count': len(labels),
                'message': f'GitHub issue created: #{result.get("issue_number")}'
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'success': False,
                'error': result.get('error'),
                'message': 'Failed to create GitHub issue'
            }, status=status.HTTP_400_BAD_REQUEST)
            
    except Exception as e:
        logger.error(f"GitHub issue creation failed: {str(e)}")
        return Response({
            'success': False,
            'error': str(e),
            'message': 'GitHub issue creation error'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_composio_status(request):
    """
    Get Composio integration status and available tools
    
    GET /api/agent/composio/status/
    """
    try:
        orchestrator = EnhancedComposioOrchestrator()
        status_info = orchestrator.get_status()
        
        return Response({
            'success': True,
            'composio_available': status_info['composio_available'],
            'api_key_configured': status_info['api_key_configured'],
            'connected_apps': status_info['connected_apps'],
            'total_tools': status_info['total_tools'],
            'available_platforms': status_info['available_platforms'],
            'features': {
                'cross_platform_workflows': True,
                'slack_notifications': True,
                'asana_task_management': True,
                'gmail_notifications': True,
                'google_sheets_tracking': True,
                'calendar_scheduling': True,
                'github_issue_tracking': True
            },
            'message': f"Composio integration active with {len(status_info['connected_apps'])} connected apps"
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Composio status check failed: {str(e)}")
        return Response({
            'success': False,
            'error': str(e),
            'message': 'Failed to get Composio status'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)