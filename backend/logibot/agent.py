"""
LOGI-BOT: Main Agent Module

Autonomous Supply Chain Resilience Agent that detects, diagnoses,
and resolves supply chain disruptions.
"""

from typing import Dict, List, Optional
from datetime import datetime
import logging
import traceback
from django.db import connection

from .config import AgentConfig, AlertType, Priority
from .analyzer import RootCauseAnalyzer
from .optimization_engine import OptimizationEngine
from .composio_orchestrator import ComposioOrchestrator
from .advanced_features import AdvancedLogiBotFeatures, GoogleCloudConfig

logger = logging.getLogger(__name__)


class LogiBot:
    """
    Autonomous Supply Chain Resilience Agent.
    
    Capabilities:
    - Proactive monitoring of inventory levels
    - Root cause analysis of disruptions
    - AI-powered solution optimization
    - Autonomous workflow orchestration
    """
    
    def __init__(self, config: Optional[AgentConfig] = None):
        """
        Initialize LOGI-BOT agent.
        
        Args:
            config: Agent configuration (defaults to environment config)
        """
        self.config = config or AgentConfig.from_env()
        self.config.validate()
        
        # Initialize core components
        self.analyzer = RootCauseAnalyzer(connection)
        self.optimizer = OptimizationEngine(self.config.optimization)
        self.orchestrator = ComposioOrchestrator(self.config.composio)
        
        # Initialize advanced AI features with Google Cloud
        google_cloud_config = GoogleCloudConfig(
            api_key=self._get_google_cloud_api_key(),
            project_id=self._get_google_cloud_project_id()
        )
        self.advanced_features = AdvancedLogiBotFeatures(google_cloud_config, self.orchestrator)
        
        # Agent state
        self.active = False
        self.current_workflows = {}
        self.execution_history = []
        
        logger.info(f"LOGI-BOT v{self.config.agent_version} initialized with Advanced AI Features")
        logger.info("Available advanced features: Multilingual Communication, Document Intelligence, Voice Commands, Sentiment Analysis, Predictive Analytics")
    
    def handle_alert(self, alert_type: str, alert_data: Dict) -> Dict:
        """
        Main entry point for handling alerts.
        
        Args:
            alert_type: Type of alert (e.g., 'low_inventory')
            alert_data: Alert data including product info
            
        Returns:
            Dict containing execution results
        """
        execution_id = f"exec_{datetime.now().timestamp()}"
        
        logger.info(f"[{execution_id}] Handling alert: {alert_type}")
        logger.info(f"[{execution_id}] Alert data: {alert_data}")
        
        result = {
            "execution_id": execution_id,
            "alert_type": alert_type,
            "started_at": datetime.now().isoformat(),
            "status": "started",
            "steps": []
        }
        
        try:
            if alert_type == AlertType.LOW_INVENTORY.value:
                result = self._handle_low_inventory_alert(alert_data, execution_id)
            else:
                result["status"] = "unsupported"
                result["message"] = f"Alert type '{alert_type}' is not yet supported"
            
        except Exception as e:
            logger.error(f"[{execution_id}] Alert handling failed: {str(e)}")
            logger.error(traceback.format_exc())
            result["status"] = "failed"
            result["error"] = str(e)
            result["traceback"] = traceback.format_exc()
        
        finally:
            result["completed_at"] = datetime.now().isoformat()
            self._log_execution(result)
        
        return result
    
    def _handle_low_inventory_alert(self, alert_data: Dict, execution_id: str) -> Dict:
        """
        Handle low inventory alert with full autonomous workflow.
        
        Workflow:
        1. Investigate root cause
        2. Formulate optimal solution
        3. Orchestrate response (Asana, Outlook, ERP)
        
        Args:
            alert_data: Alert data
            execution_id: Unique execution identifier
            
        Returns:
            Dict containing workflow results
        """
        product_id = alert_data['product_id']
        product_name = alert_data['product_name']
        current_stock = alert_data['current_stock']
        company_id = alert_data['company_id']
        
        result = {
            "execution_id": execution_id,
            "alert_type": "low_inventory",
            "product_id": product_id,
            "product_name": product_name,
            "started_at": datetime.now().isoformat(),
            "steps": []
        }
        
        # STEP 1: Root Cause Analysis
        logger.info(f"[{execution_id}] Step 1: Analyzing root cause...")
        try:
            analysis = self.analyzer.analyze_low_inventory(
                product_id=product_id,
                company_id=company_id
            )
            
            result["steps"].append({
                "step": 1,
                "name": "root_cause_analysis",
                "status": "completed",
                "data": analysis,
                "completed_at": datetime.now().isoformat()
            })
            
            root_cause = analysis['root_cause']
            confidence = analysis['confidence']
            
            logger.info(f"[{execution_id}] Root cause identified: {root_cause} (confidence: {confidence:.2%})")
            
        except Exception as e:
            logger.error(f"[{execution_id}] Root cause analysis failed: {str(e)}")
            result["steps"].append({
                "step": 1,
                "name": "root_cause_analysis",
                "status": "failed",
                "error": str(e)
            })
            raise
        
        # STEP 2: Solution Formulation
        logger.info(f"[{execution_id}] Step 2: Formulating optimal solution...")
        try:
            optimization_task = {
                'task': 'emergency_replenishment',
                'product_id': product_id,
                'product_name': product_name,
                'current_stock': current_stock,
                'company_id': company_id,
                'priority': self._determine_priority(current_stock, analysis),
                'root_cause': root_cause,
                'evidence': analysis.get('analysis', {})
            }
            
            solution = self.optimizer.run(optimization_task)
            
            result["steps"].append({
                "step": 2,
                "name": "solution_formulation",
                "status": "completed",
                "data": solution,
                "completed_at": datetime.now().isoformat()
            })
            
            logger.info(f"[{execution_id}] Solution generated: {solution['recommendation']}")
            
        except Exception as e:
            logger.error(f"[{execution_id}] Solution formulation failed: {str(e)}")
            result["steps"].append({
                "step": 2,
                "name": "solution_formulation",
                "status": "failed",
                "error": str(e)
            })
            raise
        
        # STEP 3: Orchestrate Response
        logger.info(f"[{execution_id}] Step 3: Orchestrating response workflow...")
        try:
            workflow_data = {
                'product_id': product_id,
                'product_name': product_name,
                'current_stock': current_stock,
                'company_id': company_id,
                'root_cause': root_cause,
                'solution': solution,
                'analysis': analysis
            }
            
            # Execute the full orchestration workflow
            orchestration_result = self.orchestrator.execute_workflow(
                workflow_type='emergency_replenishment',
                workflow_data=workflow_data
            )
            
            result["steps"].append({
                "step": 3,
                "name": "workflow_orchestration",
                "status": "completed",
                "data": orchestration_result,
                "completed_at": datetime.now().isoformat()
            })
            
            logger.info(f"[{execution_id}] Orchestration completed successfully")
            
        except Exception as e:
            logger.error(f"[{execution_id}] Workflow orchestration failed: {str(e)}")
            result["steps"].append({
                "step": 3,
                "name": "workflow_orchestration",
                "status": "failed",
                "error": str(e)
            })
            # Don't raise - workflow failures shouldn't stop the agent
        
        # Final status
        all_steps_completed = all(
            step.get("status") == "completed" 
            for step in result["steps"]
        )
        
        result["status"] = "completed" if all_steps_completed else "partial_success"
        result["completed_at"] = datetime.now().isoformat()
        
        # Generate summary
        result["summary"] = self._generate_execution_summary(result)
        
        logger.info(f"[{execution_id}] Alert handling completed with status: {result['status']}")
        
        return result
    
    def _determine_priority(self, current_stock: int, analysis: Dict) -> str:
        """Determine priority level based on stock and analysis."""
        
        # Critical: Stock below 10 units
        if current_stock < 10:
            return Priority.CRITICAL.value
        
        # High: Stock below 20 units OR demand surge detected
        if current_stock < 20:
            return Priority.HIGH.value
        
        consumption = analysis.get('evidence', {}).get('consumption', {})
        if consumption.get('is_demand_surge', False):
            return Priority.HIGH.value
        
        # Medium: Stock below 30 units
        if current_stock < 30:
            return Priority.MEDIUM.value
        
        return Priority.LOW.value
    
    def _generate_execution_summary(self, result: Dict) -> Dict:
        """Generate human-readable execution summary."""
        
        steps_completed = sum(
            1 for step in result["steps"] 
            if step.get("status") == "completed"
        )
        total_steps = len(result["steps"])
        
        summary = {
            "product": result.get("product_name", "Unknown"),
            "execution_status": result["status"],
            "steps_completed": f"{steps_completed}/{total_steps}",
            "actions_taken": []
        }
        
        # Extract key actions
        for step in result["steps"]:
            if step.get("status") == "completed":
                step_name = step.get("name")
                
                if step_name == "root_cause_analysis":
                    data = step.get("data", {})
                    summary["root_cause"] = data.get("root_cause")
                    summary["confidence"] = f"{data.get('confidence', 0):.0%}"
                    summary["actions_taken"].append(
                        f"Identified root cause: {data.get('root_cause')}"
                    )
                
                elif step_name == "solution_formulation":
                    data = step.get("data", {})
                    rec = data.get("recommendation", {})
                    summary["replenishment_qty"] = rec.get("net_requirement")
                    summary["actions_taken"].append(
                        f"Generated replenishment plan for {rec.get('net_requirement')} units"
                    )
                
                elif step_name == "workflow_orchestration":
                    data = step.get("data", {})
                    workflow_steps = data.get("steps", [])
                    for ws in workflow_steps:
                        if ws.get("status") == "success":
                            summary["actions_taken"].append(
                                f"Completed: {ws.get('step')}"
                            )
        
        return summary
    
    def _log_execution(self, result: Dict):
        """Log execution for monitoring and learning."""
        self.execution_history.append({
            "timestamp": datetime.now().isoformat(),
            "execution": result
        })
        
        # Keep only last 100 executions in memory
        if len(self.execution_history) > 100:
            self.execution_history = self.execution_history[-100:]
    
    def get_status(self) -> Dict:
        """Get current agent status."""
        return {
            "agent": self.config.agent_name,
            "version": self.config.agent_version,
            "active": self.active,
            "total_executions": len(self.execution_history),
            "active_workflows": len(self.current_workflows),
            "last_execution": self.execution_history[-1] if self.execution_history else None
        }
    
    def start(self):
        """Start the agent."""
        self.active = True
        logger.info(f"{self.config.agent_name} started")
    
    def stop(self):
        """Stop the agent."""
        self.active = False
        logger.info(f"{self.config.agent_name} stopped")

    def _get_google_cloud_api_key(self) -> str:
        """Get Google Cloud API key from environment or config."""
        import os
        return os.getenv("GOOGLE_CLOUD_API_KEY", "")
    
    def _get_google_cloud_project_id(self) -> str:
        """Get Google Cloud project ID from environment or config."""
        import os
        return os.getenv("GOOGLE_CLOUD_PROJECT_ID", "logi-bot-project")

    # ===================== ENHANCED ALERT HANDLING WITH AI FEATURES =====================

    async def handle_enhanced_alert(self, alert_type: str, alert_data: Dict, features_enabled: List[str] = None) -> Dict:
        """
        Enhanced alert handling with AI-powered features.
        
        Args:
            alert_type: Type of alert
            alert_data: Alert data
            features_enabled: List of advanced features to enable
            
        Returns:
            Enhanced execution results with AI insights
        """
        execution_id = f"exec_enhanced_{datetime.now().timestamp()}"
        features_enabled = features_enabled or []
        
        logger.info(f"[{execution_id}] Enhanced alert handling with features: {features_enabled}")
        
        # Standard alert handling
        result = await self._handle_standard_alert(alert_type, alert_data, execution_id)
        
        # Add AI-powered enhancements
        if "multilingual_communication" in features_enabled:
            multilingual_result = await self.advanced_features.send_multilingual_supplier_alerts(
                alert_data, 
                target_languages=['es', 'fr', 'de', 'zh']
            )
            result["ai_features"]["multilingual_communication"] = multilingual_result
        
        if "predictive_analytics" in features_enabled:
            analytics_result = await self.advanced_features.generate_predictive_analytics_report(
                alert_data.get('company_id'),
                timeframe_days=30
            )
            result["ai_features"]["predictive_analytics"] = analytics_result
        
        if "sentiment_monitoring" in features_enabled:
            # Monitor supplier communication sentiment
            result["ai_features"]["sentiment_monitoring"] = {
                "enabled": True,
                "monitoring_channels": ["email", "slack", "asana_comments"]
            }
        
        return result

    async def _handle_standard_alert(self, alert_type: str, alert_data: Dict, execution_id: str) -> Dict:
        """Handle standard alert with AI features integration."""
        result = {
            "execution_id": execution_id,
            "alert_type": alert_type,
            "started_at": datetime.now().isoformat(),
            "status": "started",
            "steps": [],
            "ai_features": {}  # New section for AI enhancements
        }
        
        try:
            if alert_type == AlertType.LOW_INVENTORY.value:
                result = await self._handle_enhanced_low_inventory_alert(alert_data, execution_id)
            else:
                result["status"] = "unsupported"
                result["message"] = f"Alert type '{alert_type}' is not yet supported"
            
        except Exception as e:
            logger.error(f"[{execution_id}] Enhanced alert handling failed: {str(e)}")
            result["status"] = "failed"
            result["error"] = str(e)
        
        finally:
            result["completed_at"] = datetime.now().isoformat()
            self._log_execution(result)
        
        return result

    async def _handle_enhanced_low_inventory_alert(self, alert_data: Dict, execution_id: str) -> Dict:
        """Enhanced low inventory handling with AI features."""
        result = self._handle_low_inventory_alert(alert_data, execution_id)
        
        # Add AI enhancements
        result["ai_features"] = {}
        
        try:
            # Auto-enable predictive analytics for critical alerts
            if alert_data.get('priority') == 'critical':
                logger.info(f"[{execution_id}] Enabling predictive analytics for critical alert...")
                
                analytics_result = await self.advanced_features.generate_predictive_analytics_report(
                    alert_data.get('company_id', 0),
                    timeframe_days=14
                )
                result["ai_features"]["predictive_analytics"] = analytics_result
                
                # Create intelligent follow-up workflows based on predictions
                if analytics_result.get("ai_insights", {}).get("high_priority_actions"):
                    workflow_result = await self.advanced_features.create_intelligent_workflow(
                        workflow_trigger={
                            "type": "predictive_alert_follow_up",
                            "source_execution": execution_id,
                            "predictions": analytics_result["predictions"]
                        },
                        workflow_config={
                            "auto_adapt": True,
                            "intelligence_level": "high",
                            "cross_platform": True
                        }
                    )
                    result["ai_features"]["intelligent_workflow"] = workflow_result
            
            # Auto-enable multilingual communication for international suppliers
            if self._has_international_suppliers(alert_data):
                logger.info(f"[{execution_id}] Enabling multilingual supplier communication...")
                
                multilingual_result = await self.advanced_features.send_multilingual_supplier_alerts(
                    alert_data,
                    target_languages=['es', 'fr', 'de', 'zh', 'ja']
                )
                result["ai_features"]["multilingual_communication"] = multilingual_result
                
        except Exception as e:
            logger.error(f"[{execution_id}] AI features enhancement failed: {str(e)}")
            result["ai_features"]["error"] = str(e)
        
        return result

    def _has_international_suppliers(self, alert_data: Dict) -> bool:
        """Check if product has international suppliers."""
        # This would check your supplier database
        # For now, return True for demonstration
        return True

    # ===================== NEW AI-POWERED METHODS =====================

    async def process_voice_command(self, audio_data: bytes, user_context: Dict) -> Dict:
        """
        Process voice commands for hands-free operations.
        
        Args:
            audio_data: Raw audio bytes from microphone
            user_context: User context and permissions
            
        Returns:
            Voice command execution results
        """
        return await self.advanced_features.process_voice_command(audio_data, user_context)

    async def analyze_supplier_document(self, image_data: str, document_type: str, metadata: Dict) -> Dict:
        """
        Analyze supplier documents using OCR and AI.
        
        Args:
            image_data: Base64 encoded image data
            document_type: Type of document (invoice, contract, etc.)
            metadata: Additional document metadata
            
        Returns:
            Document analysis results
        """
        document_data = {
            "image_base64": image_data,
            "document_type": document_type,
            **metadata
        }
        return await self.advanced_features.process_supplier_documents(document_data)

    async def generate_executive_report(self, company_id: int, report_type: str = "executive_summary") -> Dict:
        """
        Generate AI-powered executive reports.
        
        Args:
            company_id: Company ID for report
            report_type: Type of report to generate
            
        Returns:
            Generated report with insights
        """
        if report_type == "predictive_analytics":
            return await self.advanced_features.generate_predictive_analytics_report(company_id)
        else:
            return await self.advanced_features.generate_smart_documents(report_type, {"company_id": company_id})

    async def create_smart_workflow(self, trigger_conditions: Dict, workflow_rules: Dict) -> Dict:
        """
        Create intelligent, self-adapting workflows.
        
        Args:
            trigger_conditions: Conditions that trigger the workflow
            workflow_rules: Rules and configuration for the workflow
            
        Returns:
            Created workflow with intelligent routing
        """
        return await self.advanced_features.create_intelligent_workflow(trigger_conditions, workflow_rules)

    def get_enhanced_status(self) -> Dict:
        """Get enhanced agent status with AI features."""
        base_status = self.get_status()
        
        ai_status = {
            "google_cloud_integration": bool(self._get_google_cloud_api_key()),
            "advanced_features_enabled": [
                "multilingual_communication",
                "document_intelligence", 
                "voice_command_processing",
                "sentiment_analysis",
                "predictive_analytics",
                "smart_document_generation",
                "intelligent_workflows"
            ],
            "ai_capabilities": {
                "languages_supported": ["en", "es", "fr", "de", "zh", "ja", "it", "pt"],
                "document_types": ["invoice", "contract", "purchase_order", "shipping_document"],
                "voice_commands": ["check stock", "create alert", "schedule meeting", "check orders"],
                "predictive_models": ["demand_forecasting", "risk_analysis", "inventory_optimization"]
            }
        }
        
        base_status["ai_features"] = ai_status
        return base_status
