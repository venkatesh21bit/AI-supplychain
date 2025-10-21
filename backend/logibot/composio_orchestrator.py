"""
Composio Tool Orchestrator for LOGI-BOT

Manages all external tool integrations via Composio Tool Router.
"""

from typing import Dict, List, Optional, Any
import requests
import json
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class ComposioOrchestrator:
    """Orchestrates external tool actions via Composio."""
    
    def __init__(self, config):
        """
        Initialize Composio orchestrator.
        
        Args:
            config: ComposioConfig instance
        """
        self.config = config
        self.base_url = config.base_url
        self.api_key = config.api_key
        self.session = requests.Session()
        self.session.headers.update({
            "X-API-Key": self.api_key,
            "Content-Type": "application/json"
        })
    
    def execute_workflow(self, workflow_type: str, workflow_data: Dict) -> Dict:
        """
        Execute a complete workflow.
        
        Args:
            workflow_type: Type of workflow ('emergency_replenishment', etc.)
            workflow_data: Data needed for the workflow
            
        Returns:
            Dict containing workflow execution results
        """
        if workflow_type == 'emergency_replenishment':
            return self._execute_emergency_replenishment_workflow(workflow_data)
        else:
            raise ValueError(f"Unknown workflow type: {workflow_type}")
    
    def _execute_emergency_replenishment_workflow(self, data: Dict) -> Dict:
        """
        Execute emergency replenishment workflow.
        
        Orchestrates:
        1. Send Gmail alerts to suppliers
        2. Create Asana project and tasks
        3. Send Slack notifications to team
        4. Schedule Outlook meeting
        5. Create draft orders in ERP system
        6. Update inventory tracking
        """
        results = {
            "workflow": "emergency_replenishment",
            "started_at": datetime.now().isoformat(),
            "steps": []
        }
        
        try:
            # Step 1: Send Gmail Alert to Suppliers
            logger.info("Sending Gmail alerts to suppliers...")
            gmail_result = self._send_supplier_gmail_alert(data)
            results["steps"].append({
                "step": "send_gmail_alert",
                "status": "success" if gmail_result.get("success") else "failed",
                "data": gmail_result
            })
            
            # Step 2: Send Slack Notification
            logger.info("Sending Slack notification to team...")
            slack_result = self._send_slack_notification(data)
            results["steps"].append({
                "step": "send_slack_notification",
                "status": "success" if slack_result.get("success") else "failed",
                "data": slack_result
            })
            
            # Step 3: Create Asana Project
            logger.info("Creating Asana project...")
            asana_result = self._create_asana_project(data)
            results["steps"].append({
                "step": "create_asana_project",
                "status": "success" if asana_result.get("success") else "failed",
                "data": asana_result
            })
            
            # Step 4: Schedule Outlook Meeting
            logger.info("Scheduling Outlook meeting...")
            meeting_result = self._schedule_outlook_meeting(data, asana_result)
            results["steps"].append({
                "step": "schedule_meeting",
                "status": "success" if meeting_result.get("success") else "failed",
                "data": meeting_result
            })
            
            # Step 5: Create Draft Orders
            logger.info("Creating draft orders...")
            order_result = self._create_draft_orders(data)
            results["steps"].append({
                "step": "create_draft_orders",
                "status": "success" if order_result.get("success") else "failed",
                "data": order_result
            })
            
            # Step 6: Update Google Sheets Inventory Tracking
            logger.info("Updating inventory tracking...")
            sheets_result = self._update_inventory_sheets(data)
            results["steps"].append({
                "step": "update_inventory_tracking",
                "status": "success" if sheets_result.get("success") else "failed",
                "data": sheets_result
            })
            
            results["status"] = "completed"
            results["completed_at"] = datetime.now().isoformat()
            results["summary"] = f"Emergency replenishment workflow completed for {data.get('product_name', 'unknown product')}. {len([s for s in results['steps'] if s['status'] == 'success'])}/{len(results['steps'])} steps successful."
            
        except Exception as e:
            logger.error(f"Workflow execution failed: {str(e)}")
            results["status"] = "failed"
            results["error"] = str(e)
            results["failed_at"] = datetime.now().isoformat()
        
        return results
    
    def _create_asana_project(self, data: Dict) -> Dict:
        """
        Create Asana project with tasks using Composio.
        
        Args:
            data: Workflow data including product info and solution
        """
        product_name = data.get('product_name', 'Unknown Product')
        product_id = data.get('product_id')
        solution = data.get('solution', {})
        
        project_name = f"EMERGENCY_REPLENISHMENT_{product_name.upper().replace(' ', '_')}_{product_id}"
        
        try:
            # Create project via Composio
            project_payload = {
                "tool": "asana",
                "action": "create_project",
                "parameters": {
                    "workspace": self.config.asana_workspace_id,
                    "name": project_name,
                    "notes": self._generate_project_description(data),
                    "color": "red",  # High priority
                    "public": True
                }
            }
            
            project_response = self._call_composio_api(project_payload)
            project_id = project_response.get("data", {}).get("gid")
            
            if not project_id:
                return {"success": False, "error": "Failed to create project"}
            
            # Create tasks
            action_items = solution.get('action_items', [])
            created_tasks = []
            
            for action in action_items:
                task_payload = {
                    "tool": "asana",
                    "action": "create_task",
                    "parameters": {
                        "project": project_id,
                        "name": action.get('description'),
                        "notes": json.dumps(action, indent=2),
                        "due_on": action.get('deadline', '').split('T')[0] if action.get('deadline') else None,
                        "assignee": None,  # To be assigned manually
                        "tags": [action.get('priority', 'medium')]
                    }
                }
                
                task_response = self._call_composio_api(task_payload)
                task_id = task_response.get("data", {}).get("gid")
                
                if task_id:
                    created_tasks.append({
                        "action_id": action.get('id'),
                        "task_id": task_id,
                        "name": action.get('description')
                    })
            
            return {
                "success": True,
                "project_id": project_id,
                "project_name": project_name,
                "project_url": f"https://app.asana.com/0/{project_id}",
                "tasks_created": len(created_tasks),
                "tasks": created_tasks
            }
            
        except Exception as e:
            logger.error(f"Asana project creation failed: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "fallback_data": {
                    "project_name": project_name,
                    "description": self._generate_project_description(data)
                }
            }
    
    def _schedule_outlook_meeting(self, data: Dict, asana_result: Dict) -> Dict:
        """
        Schedule emergency briefing meeting via Outlook using Composio.
        
        Args:
            data: Workflow data
            asana_result: Result from Asana project creation
        """
        product_name = data.get('product_name', 'Unknown Product')
        solution = data.get('solution', {})
        
        # Schedule meeting for next business day at 9 AM
        meeting_start = self._get_next_business_day()
        meeting_start = meeting_start.replace(hour=9, minute=0, second=0)
        meeting_end = meeting_start + timedelta(minutes=30)
        
        try:
            meeting_payload = {
                "tool": "outlook",
                "action": "create_meeting",
                "parameters": {
                    "subject": f"URGENT: Emergency Briefing - {product_name} Stock Shortage",
                    "body": self._generate_meeting_body(data, asana_result),
                    "start": meeting_start.isoformat(),
                    "end": meeting_end.isoformat(),
                    "attendees": [
                        {"email": "procurement@company.com", "type": "required"},
                        {"email": "logistics@company.com", "type": "required"},
                        {"email": "planning@company.com", "type": "optional"}
                    ],
                    "location": "Virtual (Teams)",
                    "is_online_meeting": True,
                    "importance": "high"
                }
            }
            
            response = self._call_composio_api(meeting_payload)
            meeting_id = response.get("data", {}).get("id")
            
            if meeting_id:
                return {
                    "success": True,
                    "meeting_id": meeting_id,
                    "meeting_start": meeting_start.isoformat(),
                    "meeting_url": response.get("data", {}).get("onlineMeeting", {}).get("joinUrl")
                }
            else:
                return {"success": False, "error": "Failed to create meeting"}
                
        except Exception as e:
            logger.error(f"Outlook meeting scheduling failed: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "fallback_data": {
                    "suggested_time": meeting_start.isoformat(),
                    "duration_minutes": 30,
                    "subject": f"URGENT: Emergency Briefing - {product_name} Stock Shortage"
                }
            }
    
    def _create_draft_orders(self, data: Dict) -> Dict:
        """
        Create draft replenishment orders in ERP system.
        
        Args:
            data: Workflow data including solution
        """
        solution = data.get('solution', {})
        recommendation = solution.get('recommendation', {})
        product_id = data.get('product_id')
        company_id = data.get('company_id')
        
        try:
            # In this system, we'll create pending orders in our own database
            # In a real scenario, this would interact with external ERP via Composio
            
            orders = []
            net_requirement = recommendation.get('net_requirement', 0)
            sourcing = recommendation.get('sourcing_strategy', {})
            
            # Primary order
            if sourcing.get('split_order'):
                primary_qty = net_requirement // 2
                backup_qty = net_requirement - primary_qty
            else:
                primary_qty = net_requirement
                backup_qty = 0
            
            orders.append({
                "type": "primary_order",
                "product_id": product_id,
                "company_id": company_id,
                "quantity": primary_qty,
                "source": sourcing.get('primary_source'),
                "shipping_method": sourcing.get('shipping_method'),
                "status": "draft_pending_approval",
                "priority": "high",
                "notes": "Auto-generated by LOGI-BOT emergency replenishment"
            })
            
            if backup_qty > 0:
                orders.append({
                    "type": "backup_order",
                    "product_id": product_id,
                    "company_id": company_id,
                    "quantity": backup_qty,
                    "source": "alternative_supplier",
                    "shipping_method": "standard",
                    "status": "draft_pending_approval",
                    "priority": "medium",
                    "notes": "Backup order - Auto-generated by LOGI-BOT"
                })
            
            return {
                "success": True,
                "orders_created": len(orders),
                "orders": orders,
                "total_quantity": net_requirement,
                "approval_required": True
            }
            
        except Exception as e:
            logger.error(f"Draft order creation failed: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _call_composio_api(self, payload: Dict) -> Dict:
        """
        Make API call to Composio.
        
        Args:
            payload: Request payload
            
        Returns:
            Response from Composio API
        """
        try:
            # In production, this would call actual Composio API
            # For now, we'll simulate the response
            
            tool = payload.get("tool")
            action = payload.get("action")
            
            logger.info(f"Calling Composio API: {tool}.{action}")
            
            # Simulate API response
            return {
                "success": True,
                "data": {
                    "gid": f"simulated_{tool}_{action}_{datetime.now().timestamp()}",
                    "id": f"simulated_{tool}_{action}_{datetime.now().timestamp()}"
                }
            }
            
            # Real implementation would be:
            # response = self.session.post(
            #     f"{self.base_url}/tools/execute",
            #     json=payload,
            #     timeout=(self.config.connection_timeout, self.config.read_timeout)
            # )
            # response.raise_for_status()
            # return response.json()
            
        except requests.RequestException as e:
            logger.error(f"Composio API call failed: {str(e)}")
            raise
    
    def _generate_project_description(self, data: Dict) -> str:
        """Generate Asana project description."""
        product_name = data.get('product_name')
        current_stock = data.get('current_stock')
        root_cause = data.get('root_cause')
        solution = data.get('solution', {})
        
        description = f"""
# Emergency Replenishment: {product_name}

## Alert Summary
- **Product**: {product_name}
- **Current Stock**: {current_stock} units
- **Root Cause**: {root_cause}
- **Priority**: CRITICAL
- **Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M')}

## Recommended Action
{json.dumps(solution.get('recommendation', {}), indent=2)}

## Action Items
See individual tasks below. Each task has been assigned appropriate priority and deadline.

---
*This project was automatically created by LOGI-BOT Agent*
"""
        return description
    
    def _generate_meeting_body(self, data: Dict, asana_result: Dict) -> str:
        """Generate meeting invitation body."""
        product_name = data.get('product_name')
        solution = data.get('solution', {})
        project_url = asana_result.get('project_url', 'N/A')
        
        body = f"""
<h2>Emergency Stock Shortage - Immediate Action Required</h2>

<p><strong>Product:</strong> {product_name}</p>
<p><strong>Situation:</strong> Critical low inventory requiring immediate replenishment</p>

<h3>Meeting Agenda</h3>
<ol>
    <li>Review current situation and root cause analysis (5 min)</li>
    <li>Discuss proposed replenishment plan (10 min)</li>
    <li>Assign responsibilities and timelines (10 min)</li>
    <li>Q&A and next steps (5 min)</li>
</ol>

<h3>Preparation</h3>
<p>Please review the following before the meeting:</p>
<ul>
    <li><a href="{project_url}">Asana Project: Emergency Replenishment</a></li>
    <li>Attached: Optimization Plan</li>
</ul>

<h3>Attendees Expected</h3>
<ul>
    <li>Procurement Team - Order placement</li>
    <li>Logistics Team - Shipping coordination</li>
    <li>Planning Team - Forecast updates</li>
</ul>

<p><em>This meeting was automatically scheduled by LOGI-BOT Agent</em></p>
"""
        return body
    
    def _get_next_business_day(self) -> datetime:
        """Get next business day (Monday-Friday)."""
        next_day = datetime.now() + timedelta(days=1)
        
        # If weekend, move to Monday
        while next_day.weekday() >= 5:  # 5=Saturday, 6=Sunday
            next_day += timedelta(days=1)
        
        return next_day

    # ===================== NEW ENHANCED COMPOSIO TOOLS =====================
    
    def _send_supplier_gmail_alert(self, data: Dict) -> Dict:
        """Send Gmail alert to suppliers about critical stock shortage."""
        try:
            product_name = data.get('product_name', 'Unknown Product')
            current_stock = data.get('current_stock', 0)
            required_qty = data.get('required_quantity', 100)
            priority = data.get('priority', 'high')
            company_name = data.get('company_name', 'ConstructCo Materials')
            
            # Get supplier emails based on product category
            supplier_emails = self._get_supplier_contacts(data)
            
            payload = {
                "tool": "gmail",
                "action": "send_email",
                "parameters": {
                    "to": supplier_emails,
                    "subject": f"🚨 URGENT: Critical Stock Shortage - {product_name}",
                    "body": f"""
Dear Supplier,

We are experiencing a critical stock shortage that requires immediate attention:

PRODUCT: {product_name}
CURRENT STOCK: {current_stock} units
REQUIRED QUANTITY: {required_qty} units
PRIORITY LEVEL: {priority.upper()}

IMMEDIATE ACTIONS NEEDED:
1. Confirm current availability of {product_name}
2. Provide earliest delivery date for {required_qty} units
3. Share updated pricing and terms
4. Confirm order processing timeline

This is a high-priority request affecting our operations. Please respond within 2 hours.

Best regards,
{company_name} Supply Chain Team
Automated by LOGI-BOT
""",
                    "priority": "high",
                    "request_read_receipt": True
                }
            }
            
            response = self._call_composio_api(payload)
            
            return {
                "success": True,
                "tool": "gmail",
                "action": "send_supplier_alert",
                "data": {
                    "recipients": supplier_emails,
                    "message_id": response.get("message_id"),
                    "sent_at": datetime.now().isoformat()
                }
            }
            
        except Exception as e:
            logger.error(f"Gmail supplier alert failed: {str(e)}")
            return {
                "success": False,
                "tool": "gmail",
                "error": str(e)
            }
    
    def _send_slack_notification(self, data: Dict) -> Dict:
        """Send Slack notification to supply chain team."""
        try:
            product_name = data.get('product_name', 'Unknown Product')
            current_stock = data.get('current_stock', 0)
            priority = data.get('priority', 'high')
            root_cause = data.get('root_cause', 'Unknown cause')
            
            # Determine urgency emoji and channel
            urgency_emoji = "🔥" if priority == "critical" else "⚠️"
            channel = "#supply-chain-alerts" if priority == "critical" else "#supply-chain-updates"
            
            payload = {
                "tool": "slack",
                "action": "send_message",
                "parameters": {
                    "channel": channel,
                    "message": f"""
{urgency_emoji} *STOCK ALERT - {priority.upper()}*

*Product:* {product_name}
*Current Stock:* {current_stock} units
*Root Cause:* {root_cause}

*Actions in Progress:*
• Suppliers contacted via Gmail
• Asana project created for tracking
• Meeting scheduled with procurement team
• Draft orders being prepared

*Timeline:* Emergency replenishment initiated
*LOGI-BOT Execution ID:* {data.get('execution_id', 'N/A')}

@channel Please review and take necessary actions.
""",
                    "blocks": [
                        {
                            "type": "section",
                            "text": {
                                "type": "mrkdwn",
                                "text": f"{urgency_emoji} *Stock Alert: {product_name}*"
                            }
                        },
                        {
                            "type": "fields",
                            "fields": [
                                {
                                    "type": "mrkdwn",
                                    "text": f"*Current Stock:*\n{current_stock} units"
                                },
                                {
                                    "type": "mrkdwn",
                                    "text": f"*Priority:*\n{priority.upper()}"
                                }
                            ]
                        },
                        {
                            "type": "actions",
                            "elements": [
                                {
                                    "type": "button",
                                    "text": {
                                        "type": "plain_text",
                                        "text": "View Asana Project"
                                    },
                                    "url": data.get('asana_project_url', '#')
                                },
                                {
                                    "type": "button",
                                    "text": {
                                        "type": "plain_text",
                                        "text": "View Dashboard"
                                    },
                                    "url": "http://localhost:3000/manufacturer/logibot-dashboard"
                                }
                            ]
                        }
                    ]
                }
            }
            
            response = self._call_composio_api(payload)
            
            return {
                "success": True,
                "tool": "slack",
                "action": "send_notification",
                "data": {
                    "channel": channel,
                    "timestamp": response.get("timestamp"),
                    "sent_at": datetime.now().isoformat()
                }
            }
            
        except Exception as e:
            logger.error(f"Slack notification failed: {str(e)}")
            return {
                "success": False,
                "tool": "slack",
                "error": str(e)
            }
    
    def _update_inventory_sheets(self, data: Dict) -> Dict:
        """Update Google Sheets inventory tracking."""
        try:
            product_name = data.get('product_name', 'Unknown Product')
            current_stock = data.get('current_stock', 0)
            required_qty = data.get('required_quantity', 100)
            execution_id = data.get('execution_id', 'N/A')
            
            payload = {
                "tool": "googlesheets",
                "action": "append_row",
                "parameters": {
                    "spreadsheet_id": "1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms",  # Demo sheet
                    "range": "Inventory_Alerts!A:G",
                    "values": [
                        [
                            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            product_name,
                            current_stock,
                            required_qty,
                            data.get('priority', 'high'),
                            execution_id,
                            "LOGI-BOT Auto-Alert"
                        ]
                    ],
                    "value_input_option": "USER_ENTERED"
                }
            }
            
            response = self._call_composio_api(payload)
            
            # Also update dashboard summary
            summary_payload = {
                "tool": "googlesheets",
                "action": "update_cell",
                "parameters": {
                    "spreadsheet_id": "1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms",
                    "range": "Dashboard!B2",
                    "values": [[f"Last Alert: {product_name} at {datetime.now().strftime('%H:%M')}"]]
                }
            }
            
            self._call_composio_api(summary_payload)
            
            return {
                "success": True,
                "tool": "googlesheets",
                "action": "update_inventory_tracking",
                "data": {
                    "sheet_url": f"https://docs.google.com/spreadsheets/d/1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms",
                    "updated_at": datetime.now().isoformat()
                }
            }
            
        except Exception as e:
            logger.error(f"Google Sheets update failed: {str(e)}")
            return {
                "success": False,
                "tool": "googlesheets",
                "error": str(e)
            }
    
    def _get_supplier_contacts(self, data: Dict) -> List[str]:
        """Get supplier email contacts based on product type."""
        product_name = data.get('product_name', '').upper()
        
        # Mock supplier database - in real world this would query actual supplier DB
        supplier_mapping = {
            'CEMENT': ['cement.supplier@buildsupply.com', 'orders@cementworld.com'],
            'STEEL': ['steel.orders@metalworks.com', 'supply@steelcorp.com'],
            'COAL': ['coal.supply@energysource.com', 'orders@coalmineral.com'],
            'CONCRETE': ['concrete@buildmart.com', 'orders@concretesupply.com'],
            'LIMESTONE': ['limestone@quarryco.com', 'supply@stoneworks.com'],
            'DEFAULT': ['general.supply@constructsupply.com', 'emergency@buildsupply.com']
        }
        
        # Find matching suppliers
        for key in supplier_mapping:
            if key in product_name:
                return supplier_mapping[key]
        
        return supplier_mapping['DEFAULT']
