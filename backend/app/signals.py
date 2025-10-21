from django.db.models.signals import post_save, post_delete, pre_save
from django.db.models import F
from django.db import models
from django.dispatch import receiver
from django.contrib.auth.models import User, Group
from .models import Order,OrderItem, Product, Shipment, Truck, Employee,OdooCredentials
from .odoo_connector import add_product_to_odoo, authenticate_with_odoo

# ===================== EMPLOYEE SIGNAL =====================

@receiver(post_save, sender=User)
def create_employee_for_user(sender, instance, created, **kwargs):
    """Automatically create Employee when a user is added to the 'Employee' group."""
    if created and instance.groups.filter(name="Employee").exists():
        truck = Truck.objects.filter(is_available=True).first()
        if truck:
            truck.is_available = False  
            truck.save()
        Employee.objects.create(user=instance, contact="Not Provided", truck=truck)


@receiver(post_save, sender=User)
def update_employee_for_user(sender, instance, **kwargs):
    """Ensure Employee model is updated when user is added to Employee group."""
    if instance.groups.filter(name="Employee").exists():
        employee, created = Employee.objects.get_or_create(user=instance)
        if created or not employee.truck:
            truck = Truck.objects.filter(is_available=True).first()
            if truck:
                truck.is_available = False
                truck.save()
                employee.truck = truck
            employee.save()


@receiver(post_delete, sender=Employee)
def make_truck_available(sender, instance, **kwargs):
    """Mark the truck as available when an Employee is deleted."""
    if instance.truck:
        instance.truck.is_available = True
        instance.truck.save()


# ===================== ORDER SIGNALS =====================

@receiver(pre_save, sender=Order)
def store_old_order_status(sender, instance, **kwargs):
    """Stores the old order status and quantity before saving."""
    try:
        old_order = Order.objects.get(pk=instance.pk)
        instance._old_status = old_order.status
        instance._old_required_qty = old_order.required_qty
    except Order.DoesNotExist:
        instance._old_status = None
        instance._old_required_qty = None



@receiver(post_save, sender=OrderItem)
def update_product_required_quantity_on_save(sender, instance, created, **kwargs):
    """
    Update the product's total_required_quantity and status when an OrderItem is created or updated.
    """
    product = instance.product
    # Recalculate total required quantity for this product across all order items
    total_required = OrderItem.objects.filter(product=product).aggregate(
        total=models.Sum('quantity')
    )['total'] or 0
    product.total_required_quantity = total_required
    # Update product status
    product.status = "on_demand" if product.total_required_quantity > product.available_quantity else "sufficient"
    product.save(update_fields=["total_required_quantity", "status"])

@receiver(post_delete, sender=OrderItem)
def update_product_required_quantity_on_delete(sender, instance, **kwargs):
    """
    Update the product's total_required_quantity and status when an OrderItem is deleted.
    """
    product = instance.product
    total_required = OrderItem.objects.filter(product=product).aggregate(
        total=models.Sum('quantity')
    )['total'] or 0
    product.total_required_quantity = total_required
    product.status = "on_demand" if product.total_required_quantity > product.available_quantity else "sufficient"
    product.save(update_fields=["total_required_quantity", "status"])


# ===================== SHIPMENT SIGNALS =====================

@receiver(post_save, sender=Shipment)
def update_truck_availability_on_shipment(sender, instance, created, **kwargs):
    truck = getattr(instance.employee, 'truck', None)

    if truck:
        if created and instance.status == 'in_transit':
            truck.is_available = False
        elif instance.status == 'delivered':
            all_delivered = not Shipment.objects.filter(employee=instance.employee, status='in_transit').exists()
            if all_delivered:
                truck.is_available = True
        truck.save()

    # ✅ Ensure product's total_required_quantity never goes negative
    if instance.status == "delivered":
        product = instance.order.product
        product.update_status()
        product.save(update_fields=["total_required_quantity", "total_shipped", "status"])




@receiver(post_save, sender=Product)
def sync_product_to_odoo(sender, instance, created, **kwargs):
    """Sync product to Odoo when a new product is created."""
    if created:
        try:
            # Get the Odoo credentials for the user who created the product
            user = instance.created_by
            if not user:
                print("No user associated with the product. Skipping Odoo sync.")
                return

            credentials = OdooCredentials.objects.get(user=user)

            # Authenticate with Odoo
            uid, models = authenticate_with_odoo(credentials.db, credentials.username, credentials.password)

            # Add product to Odoo
            product_id = add_product_to_odoo(
                uid=uid,
                models=models,
                db=credentials.db,
                password=credentials.password,
                name=instance.name,
                price=instance.price,
                quantity=instance.available_quantity
            )

            print(f"Product synced to Odoo with ID: {product_id}")
        except OdooCredentials.DoesNotExist:
            print(f"No Odoo credentials found for user {user.username}.")
        except Exception as e:
            print(f"Failed to sync product to Odoo: {e}")


# ===================== LOGI-BOT AUTOMATIC TRIGGERS =====================

def trigger_workflow_for_product(product, reason="low_stock_detected"):
    """Helper function to trigger LOGI-BOT workflow for a specific product."""
    from .models import AgentConfiguration, AgentAlert, Company
    from .email_service import email_service
    from django.utils import timezone
    import logging
    
    logger = logging.getLogger(__name__)
    
    try:
        # Get the company
        company = product.company
        if not company:
            return False
        
        # Get agent configuration for the company
        try:
            agent_config = AgentConfiguration.objects.get(company=company)
        except AgentConfiguration.DoesNotExist:
            # Create default configuration if none exists
            agent_config = AgentConfiguration.objects.create(
                company=company,
                critical_inventory_level=10,
                warning_inventory_level=20,
                auto_resolution_enabled=True,
                require_approval=True
            )
        
        # Check if there's already an active alert for this product
        existing_alert = AgentAlert.objects.filter(
            product=product,
            company=company,
            status__in=['detected', 'analyzing']
        ).first()
        
        if existing_alert:
            logger.info(f"Active alert already exists for {product.name} (Alert ID: {existing_alert.alert_id})")
            return False
        
        # Determine alert type and priority based on conditions
        is_low_stock = product.available_quantity <= agent_config.critical_inventory_level
        is_high_demand = product.status == 'on_demand'
        
        if is_low_stock and is_high_demand:
            alert_type = 'critical_inventory'
            priority = 'critical'
        elif is_high_demand:
            alert_type = 'high_demand'
            priority = 'high'
        else:
            alert_type = 'low_inventory'
            priority = 'high'
        
        # Create new alert
        alert_data = {
            'current_stock': product.available_quantity,
            'required_quantity': product.total_required_quantity,
            'threshold': agent_config.critical_inventory_level,
            'reason': reason,
            'trigger_time': timezone.now().isoformat(),
            'is_low_stock': is_low_stock,
            'is_high_demand': is_high_demand,
            'demand_gap': max(0, product.total_required_quantity - product.available_quantity)
        }
        
        alert = AgentAlert.objects.create(
            alert_type=alert_type,
            company=company,
            product=product,
            priority=priority,
            alert_data=alert_data,
            status='detected',
            current_stock=product.available_quantity
        )
        
        logger.info(f"Created alert {alert.alert_id} for {product.name} ({product.available_quantity} units)")
        
        # Trigger LOGI-BOT workflow
        try:
            from .agent_views import get_agent_instance, _save_execution_to_db, _send_alert_notifications
            from logibot.config import AlertType
            
            # Get agent instance
            agent = get_agent_instance()
            
            alert_data = {
                'product_id': product.product_id,
                'product_name': product.name,
                'current_stock': product.available_quantity,
                'company_id': company.pk,
                'alert_id': alert.alert_id
            }
            
            # Execute agent workflow
            result = agent.handle_alert(AlertType.LOW_INVENTORY.value, alert_data)
            
            # Save execution to database
            execution = _save_execution_to_db(result, alert)
            
            # Send email notifications  
            _send_alert_notifications(product, company, agent_config, product.available_quantity, execution, result)
            
            success = True
        except Exception as e:
            logger.error(f"Error executing LOGI-BOT workflow: {str(e)}")
            success = False
        
        if success:
            logger.info(f"LOGI-BOT workflow triggered successfully for {product.name}")
            
            # Send immediate notification
            notification_emails = ['manager@company.com', 'operations@company.com']
            email_service.send_low_stock_alert(
                product_name=product.name,
                current_stock=product.available_quantity,
                threshold=agent_config.critical_inventory_level,
                company_name=company.name,
                recipient_emails=notification_emails
            )
            logger.info(f"Sent immediate low stock alert for {product.name} to {len(notification_emails)} recipients")
            return True
        else:
            logger.error(f"Failed to trigger LOGI-BOT workflow for {product.name}")
            return False
            
    except Exception as e:
        logger.error(f"Error in trigger_workflow_for_product for {product.name}: {str(e)}")
        return False

@receiver(post_save, sender=Product)
def auto_trigger_logibot_on_low_stock(sender, instance, created, **kwargs):
    """Automatically trigger LOGI-BOT when product stock drops below threshold."""
    from .models import AgentConfiguration, AgentAlert, Company
    from .email_service import email_service
    import logging
    
    logger = logging.getLogger(__name__)
    
    try:
        # Get the company (assuming product has company relationship)
        company = instance.company
        if not company:
            return
        
        # Get agent configuration for the company
        try:
            agent_config = AgentConfiguration.objects.get(company=company)
        except AgentConfiguration.DoesNotExist:
            # Create default configuration if none exists
            agent_config = AgentConfiguration.objects.create(
                company=company,
                critical_inventory_level=10,
                warning_inventory_level=20,
                auto_resolution_enabled=True,
                require_approval=True
            )
        
        # Check current stock level
        current_stock = instance.available_quantity
        old_stock = getattr(instance, '_old_available_quantity', None)
        
        # Determine if we should trigger alert
        should_trigger = False
        trigger_reason = ""
        
        # Check current conditions
        is_low_stock = current_stock <= agent_config.critical_inventory_level
        is_high_demand = instance.status == 'on_demand'  # available < total_required
        
        if created:
            # For new products, trigger if stock is low OR high demand
            if is_low_stock or is_high_demand:
                should_trigger = True
                if is_low_stock and is_high_demand:
                    trigger_reason = "new_product_critical_state"
                elif is_high_demand:
                    trigger_reason = "new_product_high_demand"
                else:
                    trigger_reason = "new_product_low_stock"
                logger.info(f"New product {instance.name} created - Stock: {current_stock}, Required: {instance.total_required_quantity}, Status: {instance.status}")
        else:
            # For existing products, trigger if conditions are met and auto-resolution is enabled
            if agent_config.auto_resolution_enabled:
                
                # High demand condition: trigger if status changed to on_demand or stock decreased while on_demand
                if is_high_demand:
                    should_trigger = True
                    if is_low_stock:
                        trigger_reason = "critical_high_demand_low_stock"
                    else:
                        trigger_reason = "high_demand_detected"
                    logger.info(f"High demand detected for {instance.name}: {current_stock} available vs {instance.total_required_quantity} required")
                
                # Low stock condition (traditional logic)
                elif is_low_stock:
                    if old_stock is None:
                        should_trigger = True
                        trigger_reason = "low_stock_no_history"
                    elif old_stock > agent_config.critical_inventory_level:
                        should_trigger = True
                        trigger_reason = "stock_dropped_below_threshold"
                        logger.info(f"Stock for {instance.name} dropped from {old_stock} to {current_stock}")
                    elif old_stock > current_stock:
                        should_trigger = True  
                        trigger_reason = "low_stock_decreased_further"
                        logger.info(f"Low stock for {instance.name} decreased further from {old_stock} to {current_stock}")
                    else:
                        logger.info(f"Stock for {instance.name} is {current_stock} (low) but increased from {old_stock}, not triggering")
        
        if should_trigger:
            # Check if there's already an active alert for this product
            existing_alert = AgentAlert.objects.filter(
                product=instance,
                status__in=['detected', 'analyzing'],
                alert_type='low_inventory'
            ).first()
            
            if existing_alert:
                logger.info(f"Active alert already exists for {instance.name}, skipping auto-trigger")
                return
            
            # Create new alert
            alert = AgentAlert.objects.create(
                alert_type='low_inventory',
                company=company,
                product=instance,
                priority='critical' if current_stock < 5 else 'high',
                status='detected',
                current_stock=current_stock,
                alert_data={
                    'triggered_by': 'auto_detection',
                    'trigger_reason': trigger_reason,
                    'threshold': agent_config.critical_inventory_level,
                    'previous_stock': old_stock,
                    'stock_change': (current_stock - old_stock) if old_stock else 0,
                    'is_new_product': created
                }
            )
            
            logger.info(f"LOGI-BOT Auto-trigger: {trigger_reason} for {instance.name} ({current_stock} units)")
            
            # **🔥 Trigger full LOGI-BOT workflow**
            try:
                from . import agent_views
                
                # Prepare alert data for agent
                alert_data = {
                    'product_id': instance.product_id,
                    'product_name': instance.name,
                    'current_stock': current_stock,
                    'company_id': company.pk,
                    'alert_id': alert.alert_id
                }
                
                # Get agent instance and trigger workflow
                agent = agent_views.get_agent_instance()
                
                # Execute workflow asynchronously to avoid blocking
                import threading
                def run_workflow():
                    try:
                        # Fix: Pass alert_type as first argument
                        workflow_result = agent.handle_alert('low_inventory', alert_data)
                        
                        # Save execution to database
                        if workflow_result:
                            agent_views._save_execution_to_db(workflow_result, alert)
                            logger.info(f"LOGI-BOT workflow completed for {instance.name}: {workflow_result.get('execution_id')}")
                        else:
                            logger.error(f"LOGI-BOT workflow failed for {instance.name}")
                            
                    except Exception as e:
                        logger.error(f"LOGI-BOT workflow error for {instance.name}: {str(e)}")
                
                # Start workflow in background thread
                workflow_thread = threading.Thread(target=run_workflow)
                workflow_thread.daemon = True
                workflow_thread.start()
                
                logger.info(f"Started LOGI-BOT workflow for {instance.name}")
                
            except Exception as e:
                logger.error(f"Failed to trigger LOGI-BOT workflow: {str(e)}")            # Send immediate email notification
            from django.contrib.auth.models import User
            from django.db.models import Q
            
            # Get notification emails
            notification_emails = []
            
            # Try to get emails from agent configuration
            if hasattr(agent_config, 'notification_emails') and agent_config.notification_emails:
                try:
                    import json
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
            
            # Send immediate low stock alert
            email_service.send_low_stock_alert(
                product_name=instance.name,
                current_stock=current_stock,
                threshold=agent_config.critical_inventory_level,
                company_name=company.name,
                recipient_emails=notification_emails
            )
            
            logger.info(f"📧 Sent immediate low stock alert for {instance.name} to {len(notification_emails)} recipients")
            
    except Exception as e:
        logger.error(f"Error in auto_trigger_logibot_on_low_stock: {str(e)}")


def check_all_low_stock_products(company_id):
    """Check all products for a company and trigger workflows for low stock items AND high demand items."""
    from .models import Product, AgentConfiguration
    from django.db.models import Q
    import logging
    
    logger = logging.getLogger(__name__)
    
    try:
        # Get all products for the company
        products = Product.objects.filter(company_id=company_id)
        
        # Get agent configuration
        try:
            agent_config = AgentConfiguration.objects.get(company_id=company_id)
            threshold = agent_config.critical_inventory_level
        except AgentConfiguration.DoesNotExist:
            threshold = 10  # Default threshold
        
        # Find products that need workflow triggers:
        # 1. Low stock products (available_quantity <= threshold)
        # 2. High demand products (status = 'on_demand', meaning available < total_required)
        # 3. Critical products (both conditions)
        trigger_products = products.filter(
            Q(available_quantity__lte=threshold) |  # Low stock
            Q(status='on_demand')  # High demand (available < required)
        ).distinct()
        
        logger.info(f"Checking {products.count()} products for company {company_id}")
        logger.info(f"Found {trigger_products.count()} products requiring workflow triggers")
        
        successful_triggers = 0
        
        for product in trigger_products:
            # Determine trigger reason
            is_low_stock = product.available_quantity <= threshold
            is_high_demand = product.status == 'on_demand'
            
            if is_low_stock and is_high_demand:
                reason = "critical_low_stock_high_demand"
                priority = "critical"
            elif is_high_demand:
                reason = "high_demand_detected"
                priority = "high"
            else:
                reason = "low_stock_detected"
                priority = "high"
            
            logger.info(f"Processing {product.name}: {product.available_quantity} available, {product.total_required_quantity} required, Status: {product.status}, Reason: {reason}")
            
            if trigger_workflow_for_product(product, reason):
                successful_triggers += 1
        
        logger.info(f"Successfully triggered {successful_triggers} workflows out of {trigger_products.count()} products requiring attention")
        return successful_triggers
        
    except Exception as e:
        logger.error(f"Error in check_all_low_stock_products: {str(e)}")
        return 0


@receiver(pre_save, sender=Product)
def store_old_product_quantity(sender, instance, **kwargs):
    """Store old available_quantity before saving to detect changes."""
    try:
        old_product = Product.objects.get(pk=instance.pk)
        instance._old_available_quantity = old_product.available_quantity
    except Product.DoesNotExist:
        instance._old_available_quantity = None