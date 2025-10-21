"""
Advanced AI API endpoints for LOGI-BOT.

This module provides API endpoints for advanced AI-powered features:
- Multilingual supplier communication
- Document intelligence and OCR  
- Voice command processing
- Predictive analytics
- Smart document generation
- Intelligent workflow automation
"""

try:
    from rest_framework.decorators import api_view, permission_classes
    from rest_framework.permissions import IsAuthenticated
    from rest_framework.response import Response
    from rest_framework import status
except ImportError:
    # Fallback for environments without DRF
    def api_view(methods):
        def decorator(func):
            return func
        return decorator
    
    def permission_classes(classes):
        def decorator(func):
            return func
        return decorator
    
    class IsAuthenticated:
        pass

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
import json
import logging
import asyncio
from typing import Dict, List
import base64
from io import BytesIO
from datetime import datetime

from .models import Company, Product, AgentAlert, AgentExecution
try:
    from .permissions import IsManufacturerOrEmployee
except ImportError:
    class IsManufacturerOrEmployee:
        pass

try:
    from logibot.agent import LogiBot
    from logibot.config import AgentConfig
    from logibot.advanced_features import GoogleCloudConfig, AdvancedLogiBotFeatures
except ImportError:
    # Mock for development
    class LogiBot:
        def __init__(self, config):
            pass
        def get_enhanced_status(self):
            return {}
    
    class AgentConfig:
        @classmethod
        def from_env(cls):
            return cls()

logger = logging.getLogger(__name__)


# ===================== VOICE COMMAND PROCESSING =====================

@api_view(['POST'])
@permission_classes([IsAuthenticated, IsManufacturerOrEmployee])
def process_voice_command(request):
    """
    Process voice commands for hands-free LOGI-BOT operations.
    
    POST /api/agent/voice-command/
    {
        "audio_data": "base64_encoded_audio",
        "context": {
            "user_id": 1,
            "company_id": 9,
            "location": "warehouse_A"
        }
    }
    """
    try:
        data = json.loads(request.body)
        audio_base64 = data.get('audio_data', '')
        context = data.get('context', {})
        
        if not audio_base64:
            return JsonResponse({
                'error': 'No audio data provided',
                'success': False
            }, status=400)
        
        # Decode audio data
        try:
            audio_data = base64.b64decode(audio_base64)
        except Exception as e:
            return JsonResponse({
                'error': f'Invalid audio data format: {str(e)}',
                'success': False
            }, status=400)
        
        # Add user context
        context.update({
            'user_id': request.user.id,
            'user_name': request.user.username,
            'permissions': [perm.codename for perm in request.user.user_permissions.all()]
        })
        
        # Process voice command
        agent = _get_agent_instance()
        
        # Run async function in sync context
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(
                agent.process_voice_command(audio_data, context)
            )
        finally:
            loop.close()
        
        return JsonResponse({
            'success': True,
            'voice_command_result': result,
            'processed_at': result.get('started_at')
        })
        
    except Exception as e:
        logger.error(f"Voice command processing failed: {str(e)}")
        return JsonResponse({
            'error': str(e),
            'success': False
        }, status=500)


# ===================== DOCUMENT INTELLIGENCE =====================

@api_view(['POST'])
@permission_classes([IsAuthenticated, IsManufacturerOrEmployee])
def analyze_document(request):
    """
    Analyze supplier documents using OCR and AI.
    
    POST /api/agent/analyze-document/
    {
        "image_data": "base64_encoded_image",
        "document_type": "invoice|contract|purchase_order|shipping_document",
        "metadata": {
            "supplier_name": "ABC Supply Co",
            "upload_source": "email_attachment"
        }
    }
    """
    try:
        data = json.loads(request.body)
        image_data = data.get('image_data', '')
        document_type = data.get('document_type', 'unknown')
        metadata = data.get('metadata', {})
        
        if not image_data:
            return JsonResponse({
                'error': 'No image data provided',
                'success': False
            }, status=400)
        
        # Validate document type
        valid_types = ['invoice', 'contract', 'purchase_order', 'shipping_document', 'communication']
        if document_type not in valid_types:
            return JsonResponse({
                'error': f'Invalid document type. Must be one of: {valid_types}',
                'success': False
            }, status=400)
        
        # Add user context to metadata
        metadata.update({
            'processed_by': request.user.username,
            'company_id': _get_user_company_id(request.user),
            'processed_at': metadata.get('processed_at')
        })
        
        # Analyze document
        agent = _get_agent_instance()
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(
                agent.analyze_supplier_document(image_data, document_type, metadata)
            )
        finally:
            loop.close()
        
        # Auto-create tasks if document analysis suggests actions
        if result.get('status') == 'completed' and result.get('tasks_created'):
            _create_document_follow_up_tasks(result, request.user)
        
        return JsonResponse({
            'success': True,
            'document_analysis': result,
            'analyzed_at': result.get('started_at')
        })
        
    except Exception as e:
        logger.error(f"Document analysis failed: {str(e)}")
        return JsonResponse({
            'error': str(e),
            'success': False
        }, status=500)


# ===================== MULTILINGUAL SUPPLIER COMMUNICATION =====================

@api_view(['POST'])
@permission_classes([IsAuthenticated, IsManufacturerOrEmployee])
def send_multilingual_alert(request):
    """
    Send supplier alerts in multiple languages.
    
    POST /api/agent/multilingual-alert/
    {
        "product_id": "STEEL_001",
        "alert_type": "critical_shortage",
        "target_languages": ["es", "fr", "de", "zh"],
        "custom_message": "Optional custom message override"
    }
    """
    try:
        data = json.loads(request.body)
        product_id = data.get('product_id')
        alert_type = data.get('alert_type', 'stock_shortage')
        target_languages = data.get('target_languages', ['es', 'fr'])
        custom_message = data.get('custom_message')
        
        if not product_id:
            return JsonResponse({
                'error': 'Product ID is required',
                'success': False
            }, status=400)
        
        # Get product and company info
        try:
            company_id = _get_user_company_id(request.user)
            product = Product.objects.get(product_id=product_id, company_id=company_id)
        except Product.DoesNotExist:
            return JsonResponse({
                'error': f'Product {product_id} not found',
                'success': False
            }, status=404)
        
        # Prepare alert data
        alert_data = {
            'product_id': product_id,
            'product_name': product.name,
            'current_stock': product.available_quantity,
            'required_quantity': product.total_required_quantity,
            'company_id': company_id,
            'alert_type': alert_type,
            'priority': 'critical' if product.available_quantity < 10 else 'high',
            'custom_message': custom_message,
            'initiated_by': request.user.username
        }
        
        # Send multilingual alerts
        agent = _get_agent_instance()
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(
                agent.advanced_features.send_multilingual_supplier_alerts(alert_data, target_languages)
            )
        finally:
            loop.close()
        
        # Log the multilingual communication
        _log_multilingual_communication(result, product, request.user)
        
        return JsonResponse({
            'success': True,
            'multilingual_result': result,
            'languages_sent': target_languages,
            'total_suppliers_contacted': sum(t.get('suppliers_contacted', 0) for t in result.get('translations', []))
        })
        
    except Exception as e:
        logger.error(f"Multilingual alert failed: {str(e)}")
        return JsonResponse({
            'error': str(e),
            'success': False
        }, status=500)


# ===================== PREDICTIVE ANALYTICS =====================

@api_view(['GET'])
@permission_classes([IsAuthenticated, IsManufacturerOrEmployee])  
def generate_predictive_report(request):
    """
    Generate predictive analytics report.
    
    GET /api/agent/predictive-analytics/?timeframe_days=30&report_type=full
    """
    try:
        timeframe_days = int(request.GET.get('timeframe_days', 30))
        report_type = request.GET.get('report_type', 'full')
        company_id = _get_user_company_id(request.user)
        
        if timeframe_days < 1 or timeframe_days > 365:
            return JsonResponse({
                'error': 'Timeframe must be between 1 and 365 days',
                'success': False
            }, status=400)
        
        # Generate predictive analytics report
        agent = _get_agent_instance()
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(
                agent.advanced_features.generate_predictive_analytics_report(company_id, timeframe_days)
            )
        finally:
            loop.close()
        
        # Create actionable tasks from high-priority predictions
        if result.get('ai_insights', {}).get('high_priority_actions'):
            _create_predictive_tasks(result['ai_insights']['high_priority_actions'], company_id, request.user)
        
        return JsonResponse({
            'success': True,
            'predictive_report': result,
            'generated_at': result.get('generated_at'),
            'company_id': company_id,
            'timeframe_days': timeframe_days
        })
        
    except Exception as e:
        logger.error(f"Predictive analytics failed: {str(e)}")
        return JsonResponse({
            'error': str(e),
            'success': False
        }, status=500)


# ===================== SMART DOCUMENT GENERATION =====================

@api_view(['POST'])
@permission_classes([IsAuthenticated, IsManufacturerOrEmployee])
def generate_smart_document(request):
    """
    Generate intelligent documents using AI.
    
    POST /api/agent/generate-document/
    {
        "document_type": "supplier_contract|purchase_order|compliance_report|executive_summary",
        "data": {
            "product_id": "STEEL_001",
            "supplier_info": {...},
            "terms": {...}
        },
        "output_formats": ["pdf", "docx", "html"]
    }
    """
    try:
        data = json.loads(request.body)
        document_type = data.get('document_type')
        document_data = data.get('data', {})
        output_formats = data.get('output_formats', ['html'])
        
        valid_types = ['supplier_contract', 'purchase_order', 'compliance_report', 'executive_summary']
        if document_type not in valid_types:
            return JsonResponse({
                'error': f'Invalid document type. Must be one of: {valid_types}',
                'success': False
            }, status=400)
        
        # Add user and company context
        document_data.update({
            'generated_by': request.user.username,
            'company_id': _get_user_company_id(request.user),
            'generation_timestamp': datetime.now().isoformat(),
            'requested_formats': output_formats
        })
        
        # Generate smart document
        agent = _get_agent_instance()
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(
                agent.advanced_features.generate_smart_documents(document_type, document_data)
            )
        finally:
            loop.close()
        
        return JsonResponse({
            'success': True,
            'document_generation': result,
            'available_formats': result.get('formats_available', []),
            'download_links': result.get('storage_result', {}).get('download_links', {})
        })
        
    except Exception as e:
        logger.error(f"Smart document generation failed: {str(e)}")
        return JsonResponse({
            'error': str(e),
            'success': False
        }, status=500)


# ===================== INTELLIGENT WORKFLOW CREATION =====================

@api_view(['POST'])
@permission_classes([IsAuthenticated, IsManufacturerOrEmployee])
def create_intelligent_workflow(request):
    """
    Create self-adapting intelligent workflows.
    
    POST /api/agent/create-workflow/
    {
        "trigger_conditions": {
            "type": "inventory_threshold",
            "conditions": {...}
        },
        "workflow_config": {
            "auto_adapt": true,
            "intelligence_level": "high",
            "cross_platform": true
        }
    }
    """
    try:
        data = json.loads(request.body)
        trigger_conditions = data.get('trigger_conditions', {})
        workflow_config = data.get('workflow_config', {})
        
        # Add user context
        trigger_conditions.update({
            'created_by': request.user.username,
            'company_id': _get_user_company_id(request.user)
        })
        
        # Create intelligent workflow
        agent = _get_agent_instance()
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(
                agent.create_smart_workflow(trigger_conditions, workflow_config)
            )
        finally:
            loop.close()
        
        return JsonResponse({
            'success': True,
            'workflow': result,
            'workflow_id': result.get('workflow_id'),
            'deployment_status': result.get('deployment', {}).get('status')
        })
        
    except Exception as e:
        logger.error(f"Intelligent workflow creation failed: {str(e)}")
        return JsonResponse({
            'error': str(e),
            'success': False
        }, status=500)


# ===================== ENHANCED AGENT STATUS =====================

@api_view(['GET'])
@permission_classes([IsAuthenticated, IsManufacturerOrEmployee])
def get_enhanced_agent_status(request):
    """
    Get comprehensive agent status including AI features.
    
    GET /api/agent/enhanced-status/
    """
    try:
        agent = _get_agent_instance()
        status = agent.get_enhanced_status()
        
        # Add real-time metrics
        company_id = _get_user_company_id(request.user)
        status['real_time_metrics'] = {
            'total_products': Product.objects.filter(company_id=company_id).count(),
            'active_alerts': AgentAlert.objects.filter(
                company_id=company_id, 
                status__in=['detected', 'analyzing']
            ).count(),
            'recent_executions': AgentExecution.objects.filter(
                alert__company_id=company_id
            ).count(),
            'ai_features_usage': _get_ai_features_usage_stats(company_id)
        }
        
        return JsonResponse({
            'success': True,
            'agent_status': status
        })
        
    except Exception as e:
        logger.error(f"Enhanced status retrieval failed: {str(e)}")
        return JsonResponse({
            'error': str(e),
            'success': False
        }, status=500)


# ===================== HELPER FUNCTIONS =====================

def _get_agent_instance():
    """Get LOGI-BOT agent instance."""
    config = AgentConfig.from_env()
    return LogiBot(config)

def _get_user_company_id(user):
    """Get company ID for user."""
    try:
        # Try manufacturer first
        if hasattr(user, 'manufacturer'):
            return user.manufacturer.company.pk
        # Then try retailer
        elif hasattr(user, 'retailer'):
            return user.retailer.company.pk
        # Then try employee
        elif hasattr(user, 'employee'):
            return user.employee.company.pk if user.employee.company else None
        else:
            # Fallback to first company
            company = Company.objects.first()
            return company.pk if company else None
    except Exception:
        return None

def _create_document_follow_up_tasks(analysis_result: Dict, user):
    """Create follow-up tasks based on document analysis."""
    try:
        # This would create Asana tasks or internal tasks
        # based on the document analysis results
        logger.info(f"Creating follow-up tasks for document analysis by {user.username}")
        pass
    except Exception as e:
        logger.error(f"Failed to create document follow-up tasks: {str(e)}")

def _log_multilingual_communication(result: Dict, product, user):
    """Log multilingual communication for tracking."""
    try:
        logger.info(f"Multilingual communication sent for {product.name} by {user.username}")
        logger.info(f"Languages: {[t.get('language') for t in result.get('translations', [])]}")
    except Exception as e:
        logger.error(f"Failed to log multilingual communication: {str(e)}")

def _create_predictive_tasks(high_priority_actions: List[Dict], company_id: int, user):
    """Create tasks from predictive analytics insights."""
    try:
        # This would create actionable tasks from AI predictions
        logger.info(f"Creating {len(high_priority_actions)} predictive tasks for company {company_id}")
        pass
    except Exception as e:
        logger.error(f"Failed to create predictive tasks: {str(e)}")

def _get_ai_features_usage_stats(company_id: int) -> Dict:
    """Get usage statistics for AI features."""
    return {
        'voice_commands_processed': 0,  # Would query usage logs
        'documents_analyzed': 0,
        'multilingual_alerts_sent': 0,
        'predictive_reports_generated': 0,
        'smart_documents_created': 0,
        'intelligent_workflows_active': 0
    }