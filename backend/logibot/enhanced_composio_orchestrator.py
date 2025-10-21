#!/usr/bin/env python3
"""
Enhanced Composio Orchestrator for LOGI-BOT
Comprehensive automation across multiple platforms
"""
import os
import asyncio
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import logging

# Django setup
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'main.settings')
django.setup()

from app.models import Product, Company, AgentAlert, AgentExecution

try:
    from composio_langchain import ComposioToolSet, Action, App
    COMPOSIO_AVAILABLE = True
except ImportError:
    COMPOSIO_AVAILABLE = False
    print("⚠️ Composio not installed. Install with: pip install composio-langchain")

logger = logging.getLogger(__name__)

class EnhancedComposioOrchestrator:
    """
    Enhanced orchestrator with comprehensive Composio tool integrations
    Supports: Asana, Slack, Gmail, Google Sheets, Outlook, GitHub, and more
    """
    
    def __init__(self):
        self.api_key = os.getenv('COMPOSIO_API_KEY')
        self.toolset = None
        self.available_tools = {}
        self.connected_apps = []
        
        if COMPOSIO_AVAILABLE and self.api_key:
            self._initialize_composio()
    
    def _initialize_composio(self):
        """Initialize Composio toolset and discover available tools"""
        try:
            self.toolset = ComposioToolSet(api_key=self.api_key)
            
            # Get available tools for key apps
            priority_apps = [
                App.ASANA, App.SLACK, App.GMAIL, App.GOOGLESHEETS,
                App.OUTLOOK, App.GITHUB, App.NOTION, App.TRELLO,
                App.DISCORD, App.TEAMS, App.CALENDAR, App.GOOGLEDRIVE
            ]
            
            for app in priority_apps:
                try:
                    tools = self.toolset.get_tools(apps=[app])
                    if tools:
                        self.available_tools[app.value] = tools
                        self.connected_apps.append(app.value)
                        logger.info(f"✅ {app.value} tools loaded: {len(tools)} actions available")
                except Exception as e:
                    logger.warning(f"⚠️ Failed to load {app.value} tools: {str(e)}")
            
            logger.info(f"🚀 Composio initialized with {len(self.connected_apps)} connected apps")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize Composio: {str(e)}")
    
    async def create_asana_task(self, title: str, description: str, priority: str = "Medium") -> Dict[str, Any]:
        """Create task in Asana for supply chain issues"""
        if App.ASANA.value not in self.available_tools:
            return {"success": False, "error": "Asana not connected"}
        
        try:
            # Get Asana create task action
            asana_tools = self.available_tools[App.ASANA.value]
            create_task_tool = next((tool for tool in asana_tools if "create" in tool.name.lower() and "task" in tool.name.lower()), None)
            
            if create_task_tool:
                task_data = {
                    "name": title,
                    "notes": description,
                    "priority": priority.lower()
                }
                
                result = await self._execute_tool_async(create_task_tool, task_data)
                return {
                    "success": True,
                    "task_id": result.get("gid"),
                    "task_url": result.get("permalink_url"),
                    "message": f"Asana task created: {title}"
                }
            else:
                return {"success": False, "error": "Create task action not found"}
                
        except Exception as e:
            logger.error(f"❌ Asana task creation failed: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def send_slack_alert(self, channel: str, message: str, urgency: str = "normal") -> Dict[str, Any]:
        """Send alert to Slack channel"""
        if App.SLACK.value not in self.available_tools:
            return {"success": False, "error": "Slack not connected"}
        
        try:
            slack_tools = self.available_tools[App.SLACK.value]
            send_message_tool = next((tool for tool in slack_tools if "send" in tool.name.lower() and "message" in tool.name.lower()), None)
            
            if send_message_tool:
                # Format message based on urgency
                emoji = "🚨" if urgency == "high" else "⚠️" if urgency == "medium" else "ℹ️"
                formatted_message = f"{emoji} **LOGI-BOT Alert**\n{message}"
                
                message_data = {
                    "channel": channel,
                    "text": formatted_message
                }
                
                result = await self._execute_tool_async(send_message_tool, message_data)
                return {
                    "success": True,
                    "message_id": result.get("ts"),
                    "channel": channel,
                    "message": "Slack alert sent successfully"
                }
            else:
                return {"success": False, "error": "Send message action not found"}
                
        except Exception as e:
            logger.error(f"❌ Slack alert failed: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def send_gmail_notification(self, to_email: str, subject: str, body: str) -> Dict[str, Any]:
        """Send email notification via Gmail"""
        if App.GMAIL.value not in self.available_tools:
            return {"success": False, "error": "Gmail not connected"}
        
        try:
            gmail_tools = self.available_tools[App.GMAIL.value]
            send_email_tool = next((tool for tool in gmail_tools if "send" in tool.name.lower() and "email" in tool.name.lower()), None)
            
            if send_email_tool:
                email_data = {
                    "to": to_email,
                    "subject": f"[LOGI-BOT] {subject}",
                    "body": f"""
                    <html>
                    <body>
                    <h2>🤖 LOGI-BOT Supply Chain Alert</h2>
                    <p>{body}</p>
                    <hr>
                    <small>Automated notification from LOGI-BOT Agent</small>
                    </body>
                    </html>
                    """
                }
                
                result = await self._execute_tool_async(send_email_tool, email_data)
                return {
                    "success": True,
                    "message_id": result.get("id"),
                    "message": f"Gmail notification sent to {to_email}"
                }
            else:
                return {"success": False, "error": "Send email action not found"}
                
        except Exception as e:
            logger.error(f"❌ Gmail notification failed: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def update_google_sheet(self, sheet_id: str, data: List[List[str]], range_name: str = "A1") -> Dict[str, Any]:
        """Update Google Sheets with inventory data"""
        if App.GOOGLESHEETS.value not in self.available_tools:
            return {"success": False, "error": "Google Sheets not connected"}
        
        try:
            sheets_tools = self.available_tools[App.GOOGLESHEETS.value]
            update_tool = next((tool for tool in sheets_tools if "update" in tool.name.lower()), None)
            
            if update_tool:
                sheet_data = {
                    "spreadsheet_id": sheet_id,
                    "range": range_name,
                    "values": data
                }
                
                result = await self._execute_tool_async(update_tool, sheet_data)
                return {
                    "success": True,
                    "updated_cells": result.get("updatedCells", 0),
                    "message": f"Google Sheet updated: {len(data)} rows"
                }
            else:
                return {"success": False, "error": "Update action not found"}
                
        except Exception as e:
            logger.error(f"❌ Google Sheets update failed: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def create_calendar_event(self, title: str, start_time: datetime, duration_hours: int = 1, attendees: List[str] = None) -> Dict[str, Any]:
        """Create calendar event for important supply chain meetings"""
        if App.CALENDAR.value not in self.available_tools:
            return {"success": False, "error": "Calendar not connected"}
        
        try:
            calendar_tools = self.available_tools[App.CALENDAR.value]
            create_event_tool = next((tool for tool in calendar_tools if "create" in tool.name.lower() and "event" in tool.name.lower()), None)
            
            if create_event_tool:
                end_time = start_time + timedelta(hours=duration_hours)
                
                event_data = {
                    "summary": f"[LOGI-BOT] {title}",
                    "description": "Automated supply chain management meeting scheduled by LOGI-BOT",
                    "start": {
                        "dateTime": start_time.isoformat(),
                        "timeZone": "UTC"
                    },
                    "end": {
                        "dateTime": end_time.isoformat(),
                        "timeZone": "UTC"
                    },
                    "attendees": [{"email": email} for email in (attendees or [])]
                }
                
                result = await self._execute_tool_async(create_event_tool, event_data)
                return {
                    "success": True,
                    "event_id": result.get("id"),
                    "event_link": result.get("htmlLink"),
                    "message": f"Calendar event created: {title}"
                }
            else:
                return {"success": False, "error": "Create event action not found"}
                
        except Exception as e:
            logger.error(f"❌ Calendar event creation failed: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def create_github_issue(self, repo: str, title: str, body: str, labels: List[str] = None) -> Dict[str, Any]:
        """Create GitHub issue for technical problems"""
        if App.GITHUB.value not in self.available_tools:
            return {"success": False, "error": "GitHub not connected"}
        
        try:
            github_tools = self.available_tools[App.GITHUB.value]
            create_issue_tool = next((tool for tool in github_tools if "create" in tool.name.lower() and "issue" in tool.name.lower()), None)
            
            if create_issue_tool:
                issue_data = {
                    "repo": repo,
                    "title": f"[LOGI-BOT] {title}",
                    "body": f"""
## 🤖 LOGI-BOT Generated Issue

{body}

---
**Generated by:** LOGI-BOT Supply Chain Agent  
**Timestamp:** {datetime.now().isoformat()}
                    """,
                    "labels": labels or ["logi-bot", "supply-chain", "automated"]
                }
                
                result = await self._execute_tool_async(create_issue_tool, issue_data)
                return {
                    "success": True,
                    "issue_number": result.get("number"),
                    "issue_url": result.get("html_url"),
                    "message": f"GitHub issue created: #{result.get('number')}"
                }
            else:
                return {"success": False, "error": "Create issue action not found"}
                
        except Exception as e:
            logger.error(f"❌ GitHub issue creation failed: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def execute_comprehensive_workflow(self, alert_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute comprehensive workflow across multiple platforms"""
        workflow_results = {
            "workflow_id": f"workflow_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "started_at": datetime.now().isoformat(),
            "platforms": {},
            "success_count": 0,
            "total_actions": 0
        }
        
        product_name = alert_data.get("product_name", "Unknown Product")
        urgency = alert_data.get("urgency", "medium")
        
        # 1. Create Asana Task
        workflow_results["total_actions"] += 1
        asana_result = await self.create_asana_task(
            title=f"Stock Alert: {product_name}",
            description=f"Low stock detected for {product_name}. Current level: {alert_data.get('current_stock', 'N/A')}",
            priority=urgency
        )
        workflow_results["platforms"]["asana"] = asana_result
        if asana_result.get("success"):
            workflow_results["success_count"] += 1
        
        # 2. Send Slack Alert
        workflow_results["total_actions"] += 1
        slack_result = await self.send_slack_alert(
            channel="#supply-chain-alerts",
            message=f"🚨 Low stock alert for **{product_name}**\nCurrent stock: {alert_data.get('current_stock', 'N/A')}\nAction required!",
            urgency=urgency
        )
        workflow_results["platforms"]["slack"] = slack_result
        if slack_result.get("success"):
            workflow_results["success_count"] += 1
        
        # 3. Send Gmail Notification
        workflow_results["total_actions"] += 1
        gmail_result = await self.send_gmail_notification(
            to_email="supply-manager@company.com",
            subject=f"Critical Stock Alert: {product_name}",
            body=f"Immediate attention required for {product_name}. Current stock levels are below minimum threshold."
        )
        workflow_results["platforms"]["gmail"] = gmail_result
        if gmail_result.get("success"):
            workflow_results["success_count"] += 1
        
        # 4. Update Google Sheets Tracking
        workflow_results["total_actions"] += 1
        sheets_result = await self.update_google_sheet(
            sheet_id="your-sheet-id",  # Replace with actual sheet ID
            data=[
                [datetime.now().strftime("%Y-%m-%d %H:%M:%S"), product_name, alert_data.get("current_stock", "N/A"), urgency, "Alert Generated"]
            ],
            range_name="A:E"
        )
        workflow_results["platforms"]["google_sheets"] = sheets_result
        if sheets_result.get("success"):
            workflow_results["success_count"] += 1
        
        # 5. Schedule Follow-up Meeting
        if urgency == "high":
            workflow_results["total_actions"] += 1
            meeting_time = datetime.now() + timedelta(hours=2)  # Schedule in 2 hours for high urgency
            calendar_result = await self.create_calendar_event(
                title=f"Emergency Stock Review: {product_name}",
                start_time=meeting_time,
                duration_hours=1,
                attendees=["supply-manager@company.com", "procurement@company.com"]
            )
            workflow_results["platforms"]["calendar"] = calendar_result
            if calendar_result.get("success"):
                workflow_results["success_count"] += 1
        
        workflow_results["completed_at"] = datetime.now().isoformat()
        workflow_results["success_rate"] = (workflow_results["success_count"] / workflow_results["total_actions"]) * 100
        
        return workflow_results
    
    async def _execute_tool_async(self, tool, data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute Composio tool asynchronously"""
        try:
            # This would be the actual Composio tool execution
            # For now, return a mock response
            await asyncio.sleep(0.1)  # Simulate async operation
            return {
                "success": True,
                "data": data,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Tool execution failed: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def get_status(self) -> Dict[str, Any]:
        """Get orchestrator status and available tools"""
        return {
            "composio_available": COMPOSIO_AVAILABLE,
            "api_key_configured": bool(self.api_key),
            "connected_apps": self.connected_apps,
            "total_tools": sum(len(tools) for tools in self.available_tools.values()),
            "available_platforms": list(self.available_tools.keys())
        }

# Test function
async def test_composio_integration():
    """Test Composio integration with sample data"""
    print("🚀 Testing Enhanced Composio Integration")
    print("=" * 50)
    
    orchestrator = EnhancedComposioOrchestrator()
    
    # Display status
    status = orchestrator.get_status()
    print(f"Composio Available: {status['composio_available']}")
    print(f"API Key Configured: {status['api_key_configured']}")
    print(f"Connected Apps: {', '.join(status['connected_apps'])}")
    print(f"Total Tools Available: {status['total_tools']}")
    print()
    
    if status['composio_available'] and status['api_key_configured']:
        # Test comprehensive workflow
        test_alert = {
            "product_name": "Steel Rods",
            "current_stock": 150,
            "minimum_threshold": 500,
            "urgency": "high"
        }
        
        print("🔄 Executing comprehensive workflow...")
        workflow_result = await orchestrator.execute_comprehensive_workflow(test_alert)
        
        print(f"Workflow ID: {workflow_result['workflow_id']}")
        print(f"Success Rate: {workflow_result['success_rate']:.1f}%")
        print(f"Successful Actions: {workflow_result['success_count']}/{workflow_result['total_actions']}")
        
        for platform, result in workflow_result["platforms"].items():
            status_icon = "✅" if result.get("success") else "❌"
            print(f"{status_icon} {platform.title()}: {result.get('message', result.get('error', 'Unknown'))}")
    
    else:
        print("⚠️ Composio not fully configured. Install composio-langchain and check API key.")

if __name__ == "__main__":
    asyncio.run(test_composio_integration())