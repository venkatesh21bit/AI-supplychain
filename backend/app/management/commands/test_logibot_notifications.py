"""
Management command to test LOGI-BOT email notifications and workflow execution.
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from app.models import Product, Company, AgentAlert, AgentExecution, AgentWorkflowStep, AgentConfiguration
from app.email_service import email_service
import json


class Command(BaseCommand):
    help = 'Test LOGI-BOT email notifications and workflow execution'

    def add_arguments(self, parser):
        parser.add_argument(
            '--product-id',
            type=int,
            help='Product ID to test with',
        )
        parser.add_argument(
            '--company-id', 
            type=int,
            help='Company ID to test with',
        )
        parser.add_argument(
            '--test-email',
            type=str,
            help='Email address to send test notifications to',
            default='test@constructco.com'
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Testing LOGI-BOT Email Notifications'))
        
        # Get test data
        product_id = options.get('product_id')
        company_id = options.get('company_id')
        test_email = options['test_email']
        
        if not product_id or not company_id:
            # Find test data automatically
            try:
                company = Company.objects.filter(name__icontains='ConstructCo').first()
                if not company:
                    company = Company.objects.first()
                
                product = Product.objects.filter(
                    company=company,
                    available_quantity__lte=10
                ).first()
                
                if not product:
                    product = Product.objects.filter(company=company).first()
                
                if not company or not product:
                    self.stdout.write(self.style.ERROR('No test data found. Run setup_complete_test_data.py first.'))
                    return
                
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Error finding test data: {str(e)}'))
                return
        else:
            try:
                product = Product.objects.get(product_id=product_id)
                company = Company.objects.get(pk=company_id)
            except (Product.DoesNotExist, Company.DoesNotExist) as e:
                self.stdout.write(self.style.ERROR(f'Error: {str(e)}'))
                return
        
        self.stdout.write(f'Testing with Product: {product.name} (Stock: {product.available_quantity})')
        self.stdout.write(f'Company: {company.name}')
        
        # Get or create agent config
        agent_config, created = AgentConfiguration.objects.get_or_create(
            company=company,
            defaults={
                'critical_inventory_level': 10,
                'warning_inventory_level': 20,
                'auto_resolution_enabled': True,
                'require_approval': True,
                'notification_emails': json.dumps([test_email])
            }
        )
        
        if created:
            self.stdout.write(f'Created new AgentConfiguration for {company.name}')
        
        # Test 1: Low Stock Alert Email
        self.stdout.write('\nTesting Low Stock Alert Email...')
        
        low_stock_success = email_service.send_low_stock_alert(
            product_name=product.name,
            current_stock=product.available_quantity,
            threshold=agent_config.critical_inventory_level,
            company_name=company.name,
            recipient_emails=[test_email]
        )
        
        if low_stock_success:
            self.stdout.write(self.style.SUCCESS('Low stock alert email sent successfully'))
        else:
            self.stdout.write(self.style.WARNING('Low stock alert email simulated (check logs)'))
        
        # Test 2: Create Mock Execution and Workflow
        self.stdout.write('\nCreating test workflow execution...')
        
        # Create alert
        alert = AgentAlert.objects.create(
            alert_type='low_inventory',
            company=company,
            product=product,
            priority='critical',
            status='resolved',
            current_stock=product.available_quantity,
            alert_data={
                'triggered_by': 'test_command',
                'threshold': agent_config.critical_inventory_level,
                'test': True
            }
        )
        
        # Create execution
        execution = AgentExecution.objects.create(
            execution_id=f'test-exec-{timezone.now().strftime("%Y%m%d-%H%M%S")}',
            alert=alert,
            status='completed',
            root_cause='High demand from construction projects',
            confidence_score=0.95,
            analysis_data={
                'demand_spike': True,
                'seasonal_factor': 'Q4 construction rush',
                'supplier_reliability': 'high'
            },
            solution_data={
                'recommended_quantity': 50,
                'preferred_supplier': 'BuildMart Supplies',
                'estimated_delivery': '2-3 business days'
            },
            orchestration_data={
                'purchase_order_generated': True,
                'supplier_notified': True,
                'delivery_scheduled': True
            },
            summary={
                'root_cause': 'High demand from construction projects',
                'confidence': 0.95,
                'recommended_quantity': 50,
                'actions_completed': 5
            },
            completed_at=timezone.now()
        )
        
        # Create workflow steps
        steps = [
            {
                'step_name': 'Root Cause Analysis',
                'status': 'completed',
                'data': {
                    'analysis_type': 'demand_pattern',
                    'findings': 'Unexpected surge in construction activity',
                    'confidence': 0.95
                }
            },
            {
                'step_name': 'Solution Generation',
                'status': 'completed', 
                'data': {
                    'solution_type': 'emergency_procurement',
                    'quantity': 50,
                    'supplier': 'BuildMart Supplies'
                }
            },
            {
                'step_name': 'Orchestration',
                'status': 'completed',
                'data': {
                    'actions': ['Purchase order sent', 'Delivery scheduled', 'Stakeholders notified'],
                    'eta': '2-3 business days'
                }
            }
        ]
        
        for i, step_data in enumerate(steps):
            AgentWorkflowStep.objects.create(
                execution=execution,
                step_number=i + 1,
                step_name=step_data['step_name'],
                status=step_data['status'],
                step_data=step_data['data'],
                result_data=step_data['data'],
                started_at=timezone.now(),
                completed_at=timezone.now()
            )
        
        self.stdout.write(f'Created execution {execution.execution_id} with {len(steps)} workflow steps')
        
        # Test 3: Workflow Completion Email
        self.stdout.write('\nTesting Workflow Completion Email...')
        
        execution_data = {
            'execution_id': execution.execution_id,
            'product': product.name,
            'status': 'COMPLETED',
            'steps_completed': f'{len(steps)}/{len(steps)}',
            'root_cause': execution.root_cause,
            'replenishment_qty': execution.summary.get('recommended_quantity', 50),
            'actions_taken': [
                'Performed comprehensive root cause analysis',
                'Generated optimal replenishment strategy based on demand patterns',
                'Coordinated with preferred suppliers for immediate procurement',
                'Initiated automated purchase order workflow',
                'Set up real-time delivery tracking and stakeholder notifications'
            ]
        }
        
        workflow_success = email_service.send_workflow_completion_notification(
            execution_data=execution_data,
            recipient_emails=[test_email]
        )
        
        if workflow_success:
            self.stdout.write(self.style.SUCCESS('Workflow completion email sent successfully'))
        else:
            self.stdout.write(self.style.WARNING('Workflow completion email simulated (check logs)'))
        
        # Summary
        self.stdout.write('\nTest Summary:')
        self.stdout.write(f'   Alert ID: {alert.alert_id}')
        self.stdout.write(f'   Execution ID: {execution.execution_id}')
        self.stdout.write(f'   Workflow Steps: {len(steps)}')
        self.stdout.write(f'   Email Recipient: {test_email}')
        self.stdout.write(f'   Company: {company.name}')
        self.stdout.write(f'   Product: {product.name} ({product.available_quantity} units)')
        
        self.stdout.write(self.style.SUCCESS('\nLOGI-BOT email notification test completed!'))
        self.stdout.write('Check the LOGI-BOT dashboard to see the new execution data.')