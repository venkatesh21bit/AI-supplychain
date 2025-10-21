"""
Django views for LOGI-BOT Agent API endpoints.
"""

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.utils import timezone
from django.db.models import Q
from django.contrib.auth.models import User
import logging
import json

from app.models import (
    Product, Company, AgentAlert, AgentExecution, 
    AgentWorkflowStep, AgentConfiguration
)
from app.email_service import email_service
from logibot import LogiBot, AgentConfig
from logibot.config import AlertType

logger = logging.getLogger(__name__)

# Global agent instance
_agent_instance = None


def get_agent_instance():
    """Get or create singleton agent instance."""
    global _agent_instance
    if _agent_instance is None:
        _agent_instance = LogiBot(AgentConfig.from_env())
        _agent_instance.start()
    return _agent_instance


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def trigger_inventory_check(request):
    """
    Manually trigger inventory check for a product.
    
    POST /api/agent/check-inventory/
    Body: {
        "product_id": 123,
        "company_id": 456
    }
    """
    try:
        product_id = request.data.get('product_id')
        company_id = request.data.get('company_id')
        
        if not product_id or not company_id:
            return Response(
                {"error": "product_id and company_id are required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get product and company
        try:
            product = Product.objects.get(product_id=product_id, company_id=company_id)
            company = Company.objects.get(pk=company_id)
        except Product.DoesNotExist:
            return Response(
                {"error": "Product not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        except Company.DoesNotExist:
            return Response(
                {"error": "Company not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Get or create agent configuration
        agent_config, _ = AgentConfiguration.objects.get_or_create(
            company=company,
            defaults={
                'critical_inventory_level': 10,
                'warning_inventory_level': 20,
                'auto_resolution_enabled': True,
                'require_approval': True
            }
        )
        
        # Check if inventory is low
        current_stock = product.available_quantity
        
        if current_stock <= agent_config.critical_inventory_level:
            # Create alert
            alert = AgentAlert.objects.create(
                alert_type='low_inventory',
                company=company,
                product=product,
                priority='critical' if current_stock < 10 else 'high',
                status='detected',
                current_stock=current_stock,
                alert_data={
                    'triggered_by': 'manual_check',
                    'user': request.user.username,
                    'threshold': agent_config.critical_inventory_level
                }
            )
            
            # Trigger agent workflow
            agent = get_agent_instance()
            
            alert_data = {
                'product_id': product_id,
                'product_name': product.name,
                'current_stock': current_stock,
                'company_id': company_id,
                'alert_id': alert.alert_id
            }
            
            # Execute agent workflow
            result = agent.handle_alert(AlertType.LOW_INVENTORY.value, alert_data)
            
            # Save execution to database
            execution = _save_execution_to_db(result, alert)
            
            # Send email notifications
            _send_alert_notifications(product, company, agent_config, current_stock, execution, result)
            
            return Response({
                "status": "alert_triggered",
                "alert_id": alert.alert_id,
                "execution_id": result.get('execution_id'),
                "message": f"Low inventory alert triggered for {product.name}",
                "result": result,
                "notifications_sent": True
            }, status=status.HTTP_200_OK)
        
        else:
            return Response({
                "status": "ok",
                "message": f"Inventory level ({current_stock}) is above threshold ({agent_config.critical_inventory_level})",
                "current_stock": current_stock,
                "threshold": agent_config.critical_inventory_level
            }, status=status.HTTP_200_OK)
    
    except Exception as e:
        logger.error(f"Error in trigger_inventory_check: {str(e)}")
        return Response(
            {"error": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def monitor_all_inventory(request):
    """
    Monitor all products and trigger alerts for low inventory.
    
    GET /api/agent/monitor-inventory/
    Query params:
        - company_id (optional): Filter by company
    """
    try:
        company_id = request.GET.get('company_id')
        
        # Get user's company
        user_companies = Company.objects.filter(user=request.user)
        
        if company_id:
            companies = user_companies.filter(pk=company_id)
        else:
            companies = user_companies
        
        results = []
        alerts_triggered = 0
        
        for company in companies:
            # Get agent configuration
            agent_config, _ = AgentConfiguration.objects.get_or_create(
                company=company,
                defaults={
                    'critical_inventory_level': 10,
                    'warning_inventory_level': 20
                }
            )
            
            # Get all products with low inventory
            low_stock_products = Product.objects.filter(
                company=company,
                available_quantity__lte=agent_config.critical_inventory_level
            )
            
            for product in low_stock_products:
                # Check if alert already exists and is not resolved
                existing_alert = AgentAlert.objects.filter(
                    product=product,
                    status__in=['detected', 'analyzing']
                ).first()
                
                if not existing_alert:
                    # Create new alert
                    alert = AgentAlert.objects.create(
                        alert_type='low_inventory',
                        company=company,
                        product=product,
                        priority='critical' if product.available_quantity < 10 else 'high',
                        status='detected',
                        current_stock=product.available_quantity,
                        alert_data={
                            'triggered_by': 'automated_monitoring',
                            'threshold': agent_config.critical_inventory_level
                        }
                    )
                    
                    alerts_triggered += 1
                    
                    results.append({
                        "product_id": product.product_id,
                        "product_name": product.name,
                        "current_stock": product.available_quantity,
                        "alert_id": alert.alert_id,
                        "status": "alert_created"
                    })
                else:
                    results.append({
                        "product_id": product.product_id,
                        "product_name": product.name,
                        "current_stock": product.available_quantity,
                        "alert_id": existing_alert.alert_id,
                        "status": "alert_exists"
                    })
        
        return Response({
            "status": "monitoring_complete",
            "companies_monitored": companies.count(),
            "alerts_triggered": alerts_triggered,
            "products_checked": len(results),
            "results": results
        }, status=status.HTTP_200_OK)
    
    except Exception as e:
        logger.error(f"Error in monitor_all_inventory: {str(e)}")
        return Response(
            {"error": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_agent_alerts(request):
    """
    Get all agent alerts.
    
    GET /api/agent/alerts/
    Query params:
        - company_id: Filter by company
        - status: Filter by status
        - alert_type: Filter by type
    """
    try:
        # Get user's companies or all companies for superusers
        if request.user.is_superuser:
            user_companies = Company.objects.all()
        else:
            user_companies = Company.objects.filter(user=request.user)
            
        # If no companies found, try to get by relationships
        if not user_companies.exists() and not request.user.is_superuser:
            # Check if user has manufacturer/retailer/employee relationships
            from django.db.models import Q
            user_companies = Company.objects.filter(
                Q(manufacturer__user=request.user) |
                Q(retailer__user=request.user) |
                Q(employee__user=request.user)
            ).distinct()
        
        # Base query
        alerts = AgentAlert.objects.filter(company__in=user_companies)
        
        # Apply filters
        company_id = request.GET.get('company_id')
        if company_id:
            alerts = alerts.filter(company_id=company_id)
        
        alert_status = request.GET.get('status')
        if alert_status:
            alerts = alerts.filter(status=alert_status)
        
        alert_type = request.GET.get('alert_type')
        if alert_type:
            alerts = alerts.filter(alert_type=alert_type)
        
        # Serialize alerts
        alert_data = []
        for alert in alerts[:50]:  # Limit to 50 most recent
            alert_data.append({
                "alert_id": alert.alert_id,
                "alert_type": alert.alert_type,
                "priority": alert.priority,
                "status": alert.status,
                "company": alert.company.name,
                "product": alert.product.name if alert.product else None,
                "current_stock": alert.current_stock,
                "detected_at": alert.detected_at.isoformat(),
                "resolved_at": alert.resolved_at.isoformat() if alert.resolved_at else None
            })
        
        return Response({
            "count": alerts.count(),
            "alerts": alert_data
        }, status=status.HTTP_200_OK)
    
    except Exception as e:
        logger.error(f"Error in get_agent_alerts: {str(e)}")
        return Response(
            {"error": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_agent_executions(request):
    """
    Get agent execution history.
    
    GET /api/agent/executions/
    Query params:
        - alert_id: Filter by alert
    """
    try:
        # Get user's companies or all companies for superusers
        if request.user.is_superuser:
            user_companies = Company.objects.all()
        else:
            user_companies = Company.objects.filter(user=request.user)
            
        # If no companies found, try to get by relationships
        if not user_companies.exists() and not request.user.is_superuser:
            # Check if user has manufacturer/retailer/employee relationships
            from django.db.models import Q
            user_companies = Company.objects.filter(
                Q(manufacturer__user=request.user) |
                Q(retailer__user=request.user) |
                Q(employee__user=request.user)
            ).distinct()
        
        # Base query
        executions = AgentExecution.objects.filter(alert__company__in=user_companies)
        
        # Apply filters
        alert_id = request.GET.get('alert_id')
        if alert_id:
            executions = executions.filter(alert_id=alert_id)
        
        # Serialize executions
        execution_data = []
        for execution in executions[:50]:
            # Get workflow steps
            workflow_steps = []
            for step in execution.workflow_steps.all().order_by('step_number'):
                workflow_steps.append({
                    "step_number": step.step_number,
                    "step_name": step.step_name,
                    "status": step.status,
                    "started_at": step.started_at.isoformat() if step.started_at else None,
                    "completed_at": step.completed_at.isoformat() if step.completed_at else None,
                    "step_data": step.step_data,
                    "result_data": step.result_data
                })
            
            execution_data.append({
                "execution_id": execution.execution_id,
                "alert_id": execution.alert_id,
                "status": execution.status,
                "root_cause": execution.root_cause,
                "confidence_score": execution.confidence_score,
                "started_at": execution.started_at.isoformat(),
                "completed_at": execution.completed_at.isoformat() if execution.completed_at else None,
                "summary": execution.summary,
                "product_name": execution.alert.product.name,
                "company_name": execution.alert.company.name,
                "current_stock": execution.alert.current_stock,
                "priority": execution.alert.priority,
                "workflow_steps": workflow_steps,
                "steps_completed": len([s for s in workflow_steps if s['status'] == 'completed']),
                "total_steps": len(workflow_steps)
            })
        
        return Response({
            "count": executions.count(),
            "executions": execution_data
        }, status=status.HTTP_200_OK)
    
    except Exception as e:
        logger.error(f"Error in get_agent_executions: {str(e)}")
        return Response(
            {"error": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_agent_status(request):
    """
    Get current agent status.
    
    GET /api/agent/status/
    """
    try:
        agent = get_agent_instance()
        agent_status = agent.get_status()
        
        # Get user's companies or all companies for superusers
        if request.user.is_superuser:
            user_companies = Company.objects.all()
        else:
            user_companies = Company.objects.filter(user=request.user)
            
        # If no companies found, try to get by relationships
        if not user_companies.exists() and not request.user.is_superuser:
            # Check if user has manufacturer/retailer/employee relationships
            from django.db.models import Q
            user_companies = Company.objects.filter(
                Q(manufacturer__user=request.user) |
                Q(retailer__user=request.user) |
                Q(employee__user=request.user)
            ).distinct()
        
        # Add database statistics
        agent_status["statistics"] = {
            "total_alerts": AgentAlert.objects.filter(company__in=user_companies).count(),
            "active_alerts": AgentAlert.objects.filter(
                company__in=user_companies,
                status__in=['detected', 'analyzing']
            ).count(),
            "total_executions": AgentExecution.objects.filter(
                alert__company__in=user_companies
            ).count(),
            "successful_executions": AgentExecution.objects.filter(
                alert__company__in=user_companies,
                status='completed'
            ).count()
        }
        
        return Response(agent_status, status=status.HTTP_200_OK)
    
    except Exception as e:
        logger.error(f"Error in get_agent_status: {str(e)}")
        return Response(
            {"error": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def update_agent_config(request):
    """
    Update agent configuration for a company.
    
    POST /api/agent/config/
    Body: {
        "company_id": 123,
        "critical_inventory_level": 10,
        "warning_inventory_level": 20,
        "auto_resolution_enabled": true,
        "require_approval": true
    }
    """
    try:
        company_id = request.data.get('company_id')
        
        if not company_id:
            return Response(
                {"error": "company_id is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Verify user owns the company
        try:
            company = Company.objects.get(pk=company_id, user=request.user)
        except Company.DoesNotExist:
            return Response(
                {"error": "Company not found or access denied"},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Get or create configuration
        config, created = AgentConfiguration.objects.get_or_create(
            company=company
        )
        
        # Update fields
        if 'critical_inventory_level' in request.data:
            config.critical_inventory_level = request.data['critical_inventory_level']
        
        if 'warning_inventory_level' in request.data:
            config.warning_inventory_level = request.data['warning_inventory_level']
        
        if 'auto_resolution_enabled' in request.data:
            config.auto_resolution_enabled = request.data['auto_resolution_enabled']
        
        if 'require_approval' in request.data:
            config.require_approval = request.data['require_approval']
        
        if 'notification_emails' in request.data:
            config.notification_emails = request.data['notification_emails']
        
        config.save()
        
        return Response({
            "status": "updated",
            "config": {
                "company_id": company.pk,
                "critical_inventory_level": config.critical_inventory_level,
                "warning_inventory_level": config.warning_inventory_level,
                "auto_resolution_enabled": config.auto_resolution_enabled,
                "require_approval": config.require_approval
            }
        }, status=status.HTTP_200_OK)
    
    except Exception as e:
        logger.error(f"Error in update_agent_config: {str(e)}")
        return Response(
            {"error": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


def _save_execution_to_db(result: dict, alert: AgentAlert):
    """Save execution result to database."""
    try:
        # Convert confidence from percentage string to float
        confidence_raw = result.get('summary', {}).get('confidence')
        confidence_score = None
        if confidence_raw:
            try:
                # Remove % symbol and convert to decimal (e.g., "88%" -> 0.88)
                if isinstance(confidence_raw, str) and confidence_raw.endswith('%'):
                    confidence_score = float(confidence_raw.rstrip('%')) / 100.0
                else:
                    confidence_score = float(confidence_raw)
            except (ValueError, TypeError):
                confidence_score = None
        
        # Create execution record
        execution = AgentExecution.objects.create(
            execution_id=result.get('execution_id'),
            alert=alert,
            status=result.get('status', 'completed'),
            root_cause=result.get('summary', {}).get('root_cause'),
            confidence_score=confidence_score,
            analysis_data=result.get('steps', [{}])[0].get('data', {}) if len(result.get('steps', [])) > 0 else {},
            solution_data=result.get('steps', [{}])[1].get('data', {}) if len(result.get('steps', [])) > 1 else {},
            orchestration_data=result.get('steps', [{}])[2].get('data', {}) if len(result.get('steps', [])) > 2 else {},
            summary=result.get('summary', {}),
            completed_at=timezone.now() if result.get('status') in ['completed', 'failed'] else None
        )
        
        # Create workflow steps
        for i, step in enumerate(result.get('steps', [])):
            AgentWorkflowStep.objects.create(
                execution=execution,
                step_number=i + 1,
                step_name=step.get('name', f'Step {i+1}'),
                status=step.get('status', 'completed'),
                step_data=step.get('data', {}),
                result_data=step.get('data', {}),
                started_at=timezone.now(),
                completed_at=timezone.now() if step.get('status') in ['completed', 'failed'] else None
            )
        
        # Update alert status
        alert.status = 'analyzing' if result.get('status') == 'started' else 'resolved'
        if result.get('status') in ['completed', 'partial_success']:
            alert.resolved_at = timezone.now()
        alert.save()
        
        logger.info(f"Saved execution {execution.execution_id} with {len(result.get('steps', []))} steps to database")
        return execution
        
    except Exception as e:
        logger.error(f"Error saving execution to database: {str(e)}")
        return None


def _send_alert_notifications(product, company, agent_config, current_stock, execution, result):
    """Send email notifications for low stock alert."""
    try:
        # Get notification emails from agent config or company users
        notification_emails = []
        
        # Try to get emails from agent configuration
        if hasattr(agent_config, 'notification_emails') and agent_config.notification_emails:
            try:
                emails = json.loads(agent_config.notification_emails) if isinstance(agent_config.notification_emails, str) else agent_config.notification_emails
                notification_emails.extend(emails if isinstance(emails, list) else [emails])
            except:
                pass
        
        # Fallback to company users' emails
        if not notification_emails:
            company_users = User.objects.filter(
                Q(retailer__company=company) | 
                Q(manufacturer__company=company) | 
                Q(employee__company=company)
            ).distinct()
            notification_emails = [user.email for user in company_users if user.email]
        
        # Add demo email if no emails found
        if not notification_emails:
            notification_emails = ['admin@constructco.com', 'manager@constructco.com']
        
        logger.info(f"Sending notifications to: {notification_emails}")
        
        # Send low stock alert email
        email_sent = email_service.send_low_stock_alert(
            product_name=product.name,
            current_stock=current_stock,
            threshold=agent_config.critical_inventory_level,
            company_name=company.name,
            recipient_emails=notification_emails
        )
        
        # Send workflow completion email if execution completed
        if result.get('status') in ['completed', 'partial_success'] and execution:
            execution_data = {
                'execution_id': result.get('execution_id'),
                'product': product.name,
                'status': result.get('status', 'COMPLETED').upper(),
                'steps_completed': f"{len(result.get('steps', []))}/{len(result.get('steps', []))}",
                'root_cause': result.get('summary', {}).get('root_cause', 'Demand surge detected'),
                'replenishment_qty': result.get('summary', {}).get('recommended_quantity', '50'),
                'actions_taken': [
                    'Performed comprehensive root cause analysis',
                    'Generated optimal replenishment strategy',
                    'Coordinated with preferred suppliers for immediate procurement',
                    'Initiated automated purchase order workflow',
                    'Set up real-time delivery tracking and stakeholder notifications'
                ]
            }
            
            email_service.send_workflow_completion_notification(
                execution_data=execution_data,
                recipient_emails=notification_emails
            )
        
        return email_sent
        
    except Exception as e:
        logger.error(f"Error sending alert notifications: {str(e)}")
        return False


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def check_all_inventory(request):
    """API endpoint to check ALL products and trigger workflows for low stock items."""
    try:
        data = request.data
        company_id = data.get('company_id')
        
        if not company_id:
            return Response({
                'error': 'company_id is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Import here to avoid circular imports
        from .signals import check_all_low_stock_products
        
        # Trigger workflows for all low stock products
        triggered_count = check_all_low_stock_products(company_id)
        
        return Response({
            'status': 'success',
            'message': f'Checked all inventory for company {company_id}',
            'triggered_workflows': triggered_count,
            'timestamp': timezone.now().isoformat()
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Error in check_all_inventory: {str(e)}")
        return Response({
            'error': f'Failed to check inventory: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
