"""
AI Optimization Engine for LOGI-BOT

Generates optimized solutions for supply chain disruptions.
"""

from typing import Dict, List, Optional
from datetime import datetime, timedelta
import json


class OptimizationEngine:
    """AI-powered optimization engine for supply chain decisions."""
    
    def __init__(self, config):
        """
        Initialize the optimization engine.
        
        Args:
            config: OptimizationConfig instance
        """
        self.config = config
        self.learning_enabled = config.enable_learning
        self.decision_history = []
    
    def run(self, task_data: Dict) -> Dict:
        """
        Execute optimization task.
        
        Args:
            task_data: Dictionary containing task parameters
                - task: Task type (e.g., 'emergency_replenishment')
                - product_id: Product identifier
                - product_name: Product name
                - current_stock: Current stock level
                - company_id: Company identifier
                - priority: Priority level ('low', 'medium', 'high', 'critical')
                - root_cause: Identified root cause
                - evidence: Supporting evidence from analysis
                
        Returns:
            Dict containing optimized solution
        """
        task_type = task_data.get('task', 'unknown')
        
        if task_type == 'emergency_replenishment':
            return self._optimize_emergency_replenishment(task_data)
        elif task_type == 'demand_forecast_update':
            return self._optimize_demand_forecast(task_data)
        elif task_type == 'supplier_selection':
            return self._optimize_supplier_selection(task_data)
        else:
            return self._default_optimization(task_data)
    
    def _optimize_emergency_replenishment(self, task_data: Dict) -> Dict:
        """Optimize emergency replenishment strategy."""
        
        product_id = task_data.get('product_id')
        product_name = task_data.get('product_name', 'Unknown Product')
        current_stock = task_data.get('current_stock', 0)
        priority = task_data.get('priority', 'high')
        root_cause = task_data.get('root_cause', 'unknown')
        evidence = task_data.get('evidence', {})
        
        # Calculate optimal replenishment quantity
        consumption_data = evidence.get('consumption', {})
        forecast_data = evidence.get('forecast', {})
        
        # Base calculation on recent consumption rate
        daily_rate = consumption_data.get('recent_daily_rate', 10)
        
        # Determine replenishment horizon based on priority
        horizon_days = {
            'critical': 14,  # 2 weeks
            'high': 21,      # 3 weeks
            'medium': 30,    # 1 month
            'low': 45        # 1.5 months
        }.get(priority, 30)
        
        # Calculate base replenishment quantity
        base_quantity = daily_rate * horizon_days
        
        # Apply safety factor based on root cause
        safety_factors = {
            'demand_surge': 1.5,  # 50% buffer
            'supplier_delay': 1.3,  # 30% buffer
            'forecast_error': 1.4,  # 40% buffer
            'unknown': 1.2  # 20% buffer
        }
        safety_factor = safety_factors.get(root_cause, 1.2)
        
        # Calculate final replenishment quantity
        replenishment_qty = int(base_quantity * safety_factor)
        
        # Account for current stock
        net_requirement = max(0, replenishment_qty - current_stock)
        
        # Determine sourcing strategy
        sourcing_strategy = self._determine_sourcing_strategy(
            net_requirement,
            priority,
            root_cause
        )
        
        # Calculate timeline
        timeline = self._calculate_replenishment_timeline(
            priority,
            sourcing_strategy
        )
        
        # Generate action items
        action_items = self._generate_replenishment_actions(
            product_name,
            net_requirement,
            sourcing_strategy,
            timeline
        )
        
        solution = {
            "task": "emergency_replenishment",
            "product_id": product_id,
            "product_name": product_name,
            "analysis": {
                "current_stock": current_stock,
                "daily_consumption_rate": round(daily_rate, 2),
                "replenishment_horizon_days": horizon_days,
                "safety_factor": safety_factor,
                "root_cause": root_cause
            },
            "recommendation": {
                "total_replenishment_qty": replenishment_qty,
                "net_requirement": net_requirement,
                "sourcing_strategy": sourcing_strategy,
                "timeline": timeline,
                "estimated_stock_out_date": self._estimate_stockout_date(
                    current_stock, daily_rate
                ),
                "priority_level": priority
            },
            "action_items": action_items,
            "generated_at": datetime.now().isoformat(),
            "confidence_score": self._calculate_confidence_score(evidence)
        }
        
        # Log decision for learning
        if self.learning_enabled:
            self._log_decision(solution)
        
        return solution
    
    def _determine_sourcing_strategy(
        self,
        quantity: int,
        priority: str,
        root_cause: str
    ) -> Dict:
        """Determine optimal sourcing strategy."""
        
        strategy = {
            "primary_source": "existing_supplier",
            "backup_sources": [],
            "shipping_method": "standard",
            "split_order": False
        }
        
        # High priority or large quantity = split order
        if priority in ['critical', 'high'] or quantity > 1000:
            strategy["split_order"] = True
            strategy["backup_sources"].append("alternative_supplier")
        
        # Supplier issues = use alternative
        if root_cause == 'supplier_delay':
            strategy["primary_source"] = "alternative_supplier"
            strategy["shipping_method"] = "expedited"
        
        # Critical priority = expedited everything
        if priority == 'critical':
            strategy["shipping_method"] = "express"
            strategy["backup_sources"].extend([
                "spot_market",
                "internal_transfer"
            ])
        
        return strategy
    
    def _calculate_replenishment_timeline(
        self,
        priority: str,
        sourcing_strategy: Dict
    ) -> Dict:
        """Calculate replenishment timeline."""
        
        # Base lead times (in days)
        base_lead_times = {
            "existing_supplier": 7,
            "alternative_supplier": 10,
            "spot_market": 3,
            "internal_transfer": 2
        }
        
        # Shipping adjustments
        shipping_adjustments = {
            "standard": 0,
            "expedited": -2,
            "express": -4
        }
        
        source = sourcing_strategy.get("primary_source", "existing_supplier")
        shipping = sourcing_strategy.get("shipping_method", "standard")
        
        lead_time = base_lead_times.get(source, 7)
        lead_time += shipping_adjustments.get(shipping, 0)
        lead_time = max(1, lead_time)  # Minimum 1 day
        
        order_date = datetime.now()
        expected_delivery = order_date + timedelta(days=lead_time)
        
        return {
            "order_placement": order_date.isoformat(),
            "expected_delivery": expected_delivery.isoformat(),
            "lead_time_days": lead_time,
            "source": source,
            "shipping_method": shipping
        }
    
    def _generate_replenishment_actions(
        self,
        product_name: str,
        quantity: int,
        sourcing_strategy: Dict,
        timeline: Dict
    ) -> List[Dict]:
        """Generate specific action items for replenishment."""
        
        actions = []
        
        # Action 1: Place primary order
        actions.append({
            "id": 1,
            "action": "place_replenishment_order",
            "description": f"Place order for {quantity} units of {product_name}",
            "source": sourcing_strategy["primary_source"],
            "quantity": quantity,
            "priority": "high",
            "deadline": timeline["order_placement"],
            "status": "pending",
            "assigned_to": "procurement_team"
        })
        
        # Action 2: Coordinate logistics
        actions.append({
            "id": 2,
            "action": "coordinate_logistics",
            "description": f"Arrange {sourcing_strategy['shipping_method']} shipping",
            "shipping_method": sourcing_strategy["shipping_method"],
            "expected_delivery": timeline["expected_delivery"],
            "priority": "high",
            "deadline": timeline["order_placement"],
            "status": "pending",
            "assigned_to": "logistics_team"
        })
        
        # Action 3: Update inventory forecast
        actions.append({
            "id": 3,
            "action": "update_forecast",
            "description": f"Update inventory forecast for {product_name}",
            "priority": "medium",
            "deadline": (datetime.now() + timedelta(days=1)).isoformat(),
            "status": "pending",
            "assigned_to": "planning_team"
        })
        
        # Action 4: Monitor stock levels (ongoing)
        actions.append({
            "id": 4,
            "action": "monitor_stock",
            "description": f"Daily monitoring of {product_name} stock levels",
            "priority": "high",
            "ongoing": True,
            "status": "active",
            "assigned_to": "inventory_team"
        })
        
        # If split order strategy
        if sourcing_strategy.get("split_order"):
            actions.append({
                "id": 5,
                "action": "place_backup_order",
                "description": f"Place backup order for {quantity // 2} units",
                "source": "alternative_supplier",
                "quantity": quantity // 2,
                "priority": "medium",
                "deadline": (datetime.now() + timedelta(days=1)).isoformat(),
                "status": "pending",
                "assigned_to": "procurement_team"
            })
        
        return actions
    
    def _estimate_stockout_date(self, current_stock: int, daily_rate: float) -> str:
        """Estimate when stock will run out."""
        if daily_rate <= 0:
            return "N/A"
        
        days_until_stockout = current_stock / daily_rate
        stockout_date = datetime.now() + timedelta(days=days_until_stockout)
        
        return stockout_date.strftime("%Y-%m-%d")
    
    def _calculate_confidence_score(self, evidence: Dict) -> float:
        """Calculate confidence score for the solution."""
        score = 0.5  # Base confidence
        
        consumption = evidence.get('consumption', {})
        forecast = evidence.get('forecast', {})
        
        # Increase confidence based on data quality
        if consumption.get('recent_order_count', 0) > 5:
            score += 0.1
        
        if forecast.get('forecast_accuracy', 0) > 70:
            score += 0.2
        
        if consumption.get('historical_order_count', 0) > 20:
            score += 0.1
        
        return min(score, 1.0)
    
    def _optimize_demand_forecast(self, task_data: Dict) -> Dict:
        """Optimize demand forecasting parameters."""
        return {
            "task": "demand_forecast_update",
            "status": "completed",
            "message": "Forecast optimization not yet implemented"
        }
    
    def _optimize_supplier_selection(self, task_data: Dict) -> Dict:
        """Optimize supplier selection."""
        return {
            "task": "supplier_selection",
            "status": "completed",
            "message": "Supplier optimization not yet implemented"
        }
    
    def _default_optimization(self, task_data: Dict) -> Dict:
        """Default optimization handler."""
        return {
            "task": task_data.get('task', 'unknown'),
            "status": "pending",
            "message": "Optimization handler not implemented for this task type"
        }
    
    def _log_decision(self, decision: Dict):
        """Log decision for machine learning."""
        self.decision_history.append({
            "timestamp": datetime.now().isoformat(),
            "decision": decision
        })
        
        # Keep only last 1000 decisions
        if len(self.decision_history) > 1000:
            self.decision_history = self.decision_history[-1000:]
