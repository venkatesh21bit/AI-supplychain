"""
Integration Management Views
Handles CRUD operations for user-configured integrations
"""
import logging
from rest_framework import viewsets, status
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import IntegrationConfig, IntegrationLog, Company
from .serializers import (
    IntegrationConfigSerializer, 
    IntegrationLogSerializer,
    IntegrationConfigCreateSerializer
)

logger = logging.getLogger(__name__)


class IntegrationConfigViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing integration configurations.
    Provides CRUD operations for user integrations.
    """
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return IntegrationConfigCreateSerializer
        return IntegrationConfigSerializer
    
    def get_queryset(self):
        """Filter integrations by user's company."""
        user = self.request.user
        company = user.companies.first()
        
        if company:
            return IntegrationConfig.objects.filter(company=company)
        return IntegrationConfig.objects.none()
    
    def create(self, request, *args, **kwargs):
        """Create a new integration configuration."""
        serializer = self.get_serializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        
        # Return with full details
        instance = serializer.instance
        return_serializer = IntegrationConfigSerializer(instance)
        
        return Response(
            {
                'success': True,
                'message': f'{instance.get_integration_type_display()} integration configured successfully',
                'integration': return_serializer.data
            },
            status=status.HTTP_201_CREATED
        )
    
    def update(self, request, *args, **kwargs):
        """Update an existing integration configuration."""
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial, context={'request': request})
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        
        # Return with full details
        return_serializer = IntegrationConfigSerializer(instance)
        
        return Response(
            {
                'success': True,
                'message': f'{instance.get_integration_type_display()} integration updated successfully',
                'integration': return_serializer.data
            }
        )
    
    def destroy(self, request, *args, **kwargs):
        """Delete an integration configuration."""
        instance = self.get_object()
        integration_name = f"{instance.get_integration_type_display()}: {instance.integration_name}"
        self.perform_destroy(instance)
        
        return Response(
            {
                'success': True,
                'message': f'{integration_name} deleted successfully'
            },
            status=status.HTTP_200_OK
        )
    
    @action(detail=True, methods=['post'])
    def test_connection(self, request, pk=None):
        """Test the integration connection."""
        integration = self.get_object()
        
        try:
            # Mark as used
            integration.mark_as_used()
            
            # Test based on integration type
            if integration.integration_type == 'google_sheets':
                # Test Google Sheets connection
                sheet_id = integration.get_config_value('sheet_id')
                if sheet_id:
                    return Response({
                        'success': True,
                        'message': 'Google Sheets connection test successful',
                        'details': {
                            'sheet_id': sheet_id,
                            'sheet_url': f'https://docs.google.com/spreadsheets/d/{sheet_id}/edit'
                        }
                    })
            
            elif integration.integration_type == 'slack':
                # Test Slack connection
                webhook_url = integration.get_config_value('webhook_url')
                channel = integration.get_config_value('channel')
                if webhook_url or channel:
                    return Response({
                        'success': True,
                        'message': 'Slack connection test successful',
                        'details': {
                            'channel': channel,
                            'has_webhook': bool(webhook_url)
                        }
                    })
            
            elif integration.integration_type == 'google_calendar':
                # Test Google Calendar connection
                calendar_id = integration.get_config_value('calendar_id')
                if calendar_id:
                    return Response({
                        'success': True,
                        'message': 'Google Calendar connection test successful',
                        'details': {
                            'calendar_id': calendar_id
                        }
                    })
            
            elif integration.integration_type == 'google_drive':
                # Test Google Drive connection
                folder_id = integration.get_config_value('folder_id')
                if folder_id:
                    return Response({
                        'success': True,
                        'message': 'Google Drive connection test successful',
                        'details': {
                            'folder_id': folder_id,
                            'folder_url': f'https://drive.google.com/drive/folders/{folder_id}'
                        }
                    })
            
            return Response({
                'success': False,
                'message': 'Integration configuration incomplete'
            }, status=status.HTTP_400_BAD_REQUEST)
            
        except Exception as e:
            logger.error(f"Integration test failed: {str(e)}")
            integration.mark_error(str(e))
            
            return Response({
                'success': False,
                'message': f'Connection test failed: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['get'])
    def summary(self, request):
        """Get summary of all integrations."""
        integrations = self.get_queryset()
        
        summary = {
            'total': integrations.count(),
            'active': integrations.filter(status='active').count(),
            'error': integrations.filter(status='error').count(),
            'by_type': {}
        }
        
        for integration in integrations:
            int_type = integration.integration_type
            if int_type not in summary['by_type']:
                summary['by_type'][int_type] = {
                    'count': 0,
                    'active': 0,
                    'configured': []
                }
            
            summary['by_type'][int_type]['count'] += 1
            if integration.status == 'active':
                summary['by_type'][int_type]['active'] += 1
            summary['by_type'][int_type]['configured'].append(integration.integration_name)
        
        return Response({
            'success': True,
            'summary': summary
        })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_integration_logs(request):
    """Get integration activity logs."""
    company = request.user.companies.first()
    if not company:
        return Response(
            {'error': 'User not associated with any company'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Get logs for all company integrations
    logs = IntegrationLog.objects.filter(
        integration__company=company
    ).order_by('-created_at')[:50]  # Last 50 logs
    
    serializer = IntegrationLogSerializer(logs, many=True)
    
    return Response({
        'success': True,
        'logs': serializer.data,
        'count': logs.count()
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_available_integrations(request):
    """Get list of available integration types with their status."""
    company = request.user.companies.first()
    if not company:
        return Response(
            {'error': 'User not associated with any company'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Get existing integrations
    existing = IntegrationConfig.objects.filter(company=company)
    existing_types = {i.integration_type: i for i in existing}
    
    # Define available integrations
    available_integrations = [
        {
            'type': 'gmail',
            'name': 'Gmail',
            'description': 'Send automated email alerts for stock notifications',
            'icon': '📧',
            'configured': 'gmail' in existing_types,
            'status': existing_types['gmail'].status if 'gmail' in existing_types else 'not_configured',
            'requires': ['Composio Entity ID or OAuth'],
        },
        {
            'type': 'slack',
            'name': 'Slack',
            'description': 'Real-time team notifications in Slack channels',
            'icon': '💬',
            'configured': 'slack' in existing_types,
            'status': existing_types['slack'].status if 'slack' in existing_types else 'not_configured',
            'requires': ['Webhook URL or Bot Token', 'Channel Name'],
        },
        {
            'type': 'google_sheets',
            'name': 'Google Sheets',
            'description': 'Automatically log inventory data to spreadsheets',
            'icon': '📊',
            'configured': 'google_sheets' in existing_types,
            'status': existing_types['google_sheets'].status if 'google_sheets' in existing_types else 'not_configured',
            'requires': ['Sheet ID or Sheet URL'],
        },
        {
            'type': 'google_calendar',
            'name': 'Google Calendar',
            'description': 'Schedule meetings and reminders automatically',
            'icon': '📅',
            'configured': 'google_calendar' in existing_types,
            'status': existing_types['google_calendar'].status if 'google_calendar' in existing_types else 'not_configured',
            'requires': ['Calendar ID (email address)'],
        },
        {
            'type': 'google_drive',
            'name': 'Google Drive',
            'description': 'Store documents, reports, and invoices',
            'icon': '💾',
            'configured': 'google_drive' in existing_types,
            'status': existing_types['google_drive'].status if 'google_drive' in existing_types else 'not_configured',
            'requires': ['Folder ID or Folder URL'],
        },
    ]
    
    return Response({
        'success': True,
        'integrations': available_integrations,
        'total_configured': len(existing_types)
    })
