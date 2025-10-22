#!/usr/bin/env python3
"""
Expanded Composio Integration Views
Additional tools: Trello, Discord, Teams, Notion, GitHub, Google Drive
"""
import os
import asyncio
import json
from datetime import datetime, timedelta
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
import logging

from logibot.composio_rest_orchestrator import ComposioRESTOrchestrator

logger = logging.getLogger(__name__)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_connected_integrations(request):
    """
    Get all connected Composio integrations
    
    GET /api/agent/composio/integrations/
    """
    try:
        orchestrator = ComposioRESTOrchestrator()
        integrations = asyncio.run(orchestrator.get_connected_integrations())
        
        return Response({
            'success': True,
            'count': len(integrations),
            'integrations': integrations,
            'message': f'Found {len(integrations)} connected integrations'
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Failed to get integrations: {str(e)}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_trello_card(request):
    """
    Create Trello card
    
    POST /api/agent/composio/trello-card/
    {
        "board_id": "board123",
        "list_id": "list456",
        "title": "Restock Steel Rods",
        "description": "Urgent restocking required",
        "labels": ["urgent", "inventory"]
    }
    """
    try:
        data = request.data
        orchestrator = ComposioRESTOrchestrator()
        
        parameters = {
            "name": data.get('title', 'New Task'),
            "desc": data.get('description', ''),
            "idList": data.get('list_id'),
            "labels": data.get('labels', [])
        }
        
        result = asyncio.run(
            orchestrator.execute_action("trello", "create_card", parameters)
        )
        
        return Response({
            'success': result.get('success', False),
            'card_id': result.get('data', {}).get('id'),
            'message': 'Trello card created successfully' if result.get('success') else 'Failed to create card'
        }, status=status.HTTP_200_OK if result.get('success') else status.HTTP_400_BAD_REQUEST)
        
    except Exception as e:
        logger.error(f"Trello card creation failed: {str(e)}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def send_discord_message(request):
    """
    Send Discord message
    
    POST /api/agent/composio/discord-message/
    {
        "channel_id": "123456789",
        "message": "Stock alert notification",
        "embed": {
            "title": "Low Stock Alert",
            "description": "Steel Rods: 150/500",
            "color": 16711680
        }
    }
    """
    try:
        data = request.data
        orchestrator = ComposioRESTOrchestrator()
        
        parameters = {
            "channel_id": data.get('channel_id'),
            "content": data.get('message', ''),
        }
        
        if data.get('embed'):
            parameters['embed'] = data['embed']
        
        result = asyncio.run(
            orchestrator.execute_action("discord", "send_message", parameters)
        )
        
        return Response({
            'success': result.get('success', False),
            'message_id': result.get('data', {}).get('id'),
            'message': 'Discord message sent successfully' if result.get('success') else 'Failed to send message'
        }, status=status.HTTP_200_OK if result.get('success') else status.HTTP_400_BAD_REQUEST)
        
    except Exception as e:
        logger.error(f"Discord message failed: {str(e)}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def send_teams_message(request):
    """
    Send Microsoft Teams message
    
    POST /api/agent/composio/teams-message/
    {
        "channel_id": "channel123",
        "message": "Stock alert for Steel Rods",
        "mention_users": ["user1@company.com"]
    }
    """
    try:
        data = request.data
        orchestrator = ComposioRESTOrchestrator()
        
        parameters = {
            "channelId": data.get('channel_id'),
            "message": data.get('message', ''),
            "mentions": data.get('mention_users', [])
        }
        
        result = asyncio.run(
            orchestrator.execute_action("teams", "send_message", parameters)
        )
        
        return Response({
            'success': result.get('success', False),
            'message': 'Teams message sent successfully' if result.get('success') else 'Failed to send message'
        }, status=status.HTTP_200_OK if result.get('success') else status.HTTP_400_BAD_REQUEST)
        
    except Exception as e:
        logger.error(f"Teams message failed: {str(e)}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_notion_page(request):
    """
    Create Notion page
    
    POST /api/agent/composio/notion-page/
    {
        "database_id": "db123",
        "title": "Stock Alert Log",
        "properties": {
            "Product": "Steel Rods",
            "Stock": 150,
            "Status": "Critical"
        }
    }
    """
    try:
        data = request.data
        orchestrator = ComposioRESTOrchestrator()
        
        parameters = {
            "parent": {"database_id": data.get('database_id')},
            "properties": {
                "Name": {
                    "title": [{"text": {"content": data.get('title', 'New Page')}}]
                }
            }
        }
        
        # Add custom properties
        for key, value in data.get('properties', {}).items():
            parameters['properties'][key] = {"rich_text": [{"text": {"content": str(value)}}]}
        
        result = asyncio.run(
            orchestrator.execute_action("notion", "create_page", parameters)
        )
        
        return Response({
            'success': result.get('success', False),
            'page_id': result.get('data', {}).get('id'),
            'message': 'Notion page created successfully' if result.get('success') else 'Failed to create page'
        }, status=status.HTTP_200_OK if result.get('success') else status.HTTP_400_BAD_REQUEST)
        
    except Exception as e:
        logger.error(f"Notion page creation failed: {str(e)}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_github_issue(request):
    """
    Create GitHub issue
    
    POST /api/agent/composio/github-issue/
    {
        "repo": "username/repo",
        "title": "Inventory System: Low Stock Alert",
        "body": "Steel Rods stock is critically low",
        "labels": ["bug", "urgent"],
        "assignees": ["username"]
    }
    """
    try:
        data = request.data
        orchestrator = ComposioRESTOrchestrator()
        
        repo_parts = data.get('repo', '/').split('/')
        
        parameters = {
            "owner": repo_parts[0],
            "repo": repo_parts[1] if len(repo_parts) > 1 else repo_parts[0],
            "title": data.get('title', 'New Issue'),
            "body": data.get('body', ''),
            "labels": data.get('labels', []),
            "assignees": data.get('assignees', [])
        }
        
        result = asyncio.run(
            orchestrator.execute_action("github", "create_issue", parameters)
        )
        
        return Response({
            'success': result.get('success', False),
            'issue_number': result.get('data', {}).get('number'),
            'issue_url': result.get('data', {}).get('html_url'),
            'message': 'GitHub issue created successfully' if result.get('success') else 'Failed to create issue'
        }, status=status.HTTP_200_OK if result.get('success') else status.HTTP_400_BAD_REQUEST)
        
    except Exception as e:
        logger.error(f"GitHub issue creation failed: {str(e)}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def upload_to_google_drive(request):
    """
    Upload file to Google Drive
    
    POST /api/agent/composio/drive-upload/
    {
        "file_name": "stock_report_2025.pdf",
        "file_content": "base64_encoded_content",
        "folder_id": "folder123",
        "mime_type": "application/pdf"
    }
    """
    try:
        data = request.data
        orchestrator = ComposioRESTOrchestrator()
        
        parameters = {
            "name": data.get('file_name'),
            "mimeType": data.get('mime_type', 'application/octet-stream'),
            "parents": [data.get('folder_id')] if data.get('folder_id') else []
        }
        
        result = asyncio.run(
            orchestrator.execute_action("googledrive", "upload_file", parameters)
        )
        
        return Response({
            'success': result.get('success', False),
            'file_id': result.get('data', {}).get('id'),
            'file_url': result.get('data', {}).get('webViewLink'),
            'message': 'File uploaded successfully' if result.get('success') else 'Failed to upload file'
        }, status=status.HTTP_200_OK if result.get('success') else status.HTTP_400_BAD_REQUEST)
        
    except Exception as e:
        logger.error(f"Drive upload failed: {str(e)}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def send_telegram_message(request):
    """
    Send Telegram message
    
    POST /api/agent/composio/telegram-message/
    {
        "chat_id": "123456789",
        "message": "Stock alert notification",
        "parse_mode": "Markdown"
    }
    """
    try:
        data = request.data
        orchestrator = ComposioRESTOrchestrator()
        
        parameters = {
            "chat_id": data.get('chat_id'),
            "text": data.get('message', ''),
            "parse_mode": data.get('parse_mode', 'Markdown')
        }
        
        result = asyncio.run(
            orchestrator.execute_action("telegram", "send_message", parameters)
        )
        
        return Response({
            'success': result.get('success', False),
            'message_id': result.get('data', {}).get('message_id'),
            'message': 'Telegram message sent successfully' if result.get('success') else 'Failed to send message'
        }, status=status.HTTP_200_OK if result.get('success') else status.HTTP_400_BAD_REQUEST)
        
    except Exception as e:
        logger.error(f"Telegram message failed: {str(e)}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_integration_stats(request):
    """
    Get statistics about Composio integrations usage
    
    GET /api/agent/composio/stats/
    """
    try:
        # For demo purposes, return mock stats to avoid API version issues
        stats = {
            'total_integrations': 5,
            'connected_apps': ['Gmail', 'Slack', 'Google Sheets', 'Google Calendar', 'Google Drive'],
            'gmail_configured': True,
            'api_key_status': 'configured',
            'demo_mode': True
        }
        
        return Response({
            'success': True,
            'stats': stats,
            'message': '✅ Demo: Integration statistics (simulated for demo)'
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Failed to get stats: {str(e)}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
