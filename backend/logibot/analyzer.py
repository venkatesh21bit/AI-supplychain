"""
Root Cause Analysis Engine for LOGI-BOT
Analyzes low inventory alerts to determine underlying causes
"""
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from django.db import connection
from .config import AgentConfig

logger = logging.getLogger(__name__)

class RootCauseAnalyzer:
    """
    Analyzes supply chain disruptions to determine root causes
    """
    
    def __init__(self, config: AgentConfig):
        self.config = config
        
    def analyze_low_inventory(self, product_id: int, company_id: int) -> Dict:
        """
        Main analysis method for low inventory alerts
        """
        logger.info(f"Starting root cause analysis for product {product_id}, company {company_id}")
        
        try:
            # Get basic product information
            product_info = self._get_product_info(product_id, company_id)
            if not product_info:
                return {
                    "error": "Product not found",
                    "confidence": 0.0,
                    "root_cause": "unknown"
                }
            
            # Perform analysis steps
            consumption_analysis = self._analyze_consumption_rate(product_id, company_id)
            forecast_analysis = self._compare_against_forecast(product_id, company_id)
            supplier_analysis = self._analyze_supplier_performance(product_id, company_id)
            pending_orders = self._check_pending_orders(product_id, company_id)
            
            # Determine root cause
            root_cause, confidence = self._determine_root_cause(
                consumption_analysis, forecast_analysis, supplier_analysis, pending_orders
            )
            
            # Generate recommendations
            recommendations = self._generate_recommendations(root_cause, product_info)
            
            result = {
                "product_id": product_id,
                "product_name": product_info.get("name", "Unknown"),
                "current_inventory": product_info.get("current_inventory", 0),
                "root_cause": root_cause,
                "confidence": confidence,
                "analysis": {
                    "consumption_rate": consumption_analysis,
                    "forecast_comparison": forecast_analysis,
                    "supplier_performance": supplier_analysis,
                    "pending_orders": pending_orders
                },
                "recommendations": recommendations,
                "timestamp": datetime.now().isoformat()
            }
            
            logger.info(f"Analysis complete: {root_cause} with {confidence:.2f} confidence")
            return result
            
        except Exception as e:
            logger.error(f"Analysis failed: {str(e)}")
            return {
                "error": str(e),
                "confidence": 0.0,
                "root_cause": "analysis_failed",
                "timestamp": datetime.now().isoformat()
            }
    
    def _get_product_info(self, product_id: int, company_id: int) -> Optional[Dict]:
        """Get basic product information"""
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT p.product_id, p.name, p.available_quantity, c.name as company_name
                FROM app_product p
                JOIN app_company c ON p.company_id = c.id
                WHERE p.product_id = %s AND c.id = %s
            """, [product_id, company_id])
            
            row = cursor.fetchone()
            if row:
                return {
                    "id": row[0],
                    "name": row[1],
                    "current_inventory": row[2],
                    "company_name": row[3]
                }
            return None
    
    def _analyze_consumption_rate(self, product_id: int, company_id: int) -> Dict:
        """Analyze recent consumption patterns"""
        seven_days_ago = datetime.now() - timedelta(days=7)
        thirty_days_ago = datetime.now() - timedelta(days=30)
        
        with connection.cursor() as cursor:
            # Get recent consumption (last 7 days)
            recent_query = """
                SELECT SUM(oi.quantity) as total_consumed
                FROM app_orderitem oi
                JOIN app_order o ON oi.order_id = o.order_id
                WHERE oi.product_id = %s 
                AND o.order_date >= %s
                AND o.status IN ('completed', 'shipped', 'delivered')
            """
            cursor.execute(recent_query, [product_id, seven_days_ago])
            recent_row = cursor.fetchone()
            recent_consumption = recent_row[0] if recent_row and recent_row[0] else 0
            
            # Get historical average (last 30 days, excluding recent 7)
            historical_query = """
                SELECT SUM(oi.quantity) as total_consumed
                FROM app_orderitem oi
                JOIN app_order o ON oi.order_id = o.order_id
                WHERE oi.product_id = %s 
                AND o.order_date BETWEEN %s AND %s
                AND o.status IN ('completed', 'shipped', 'delivered')
            """
            cursor.execute(historical_query, [product_id, thirty_days_ago, seven_days_ago])
            historical_row = cursor.fetchone()
            historical_consumption = historical_row[0] if historical_row and historical_row[0] else 0
            
            # Calculate daily averages
            recent_daily = recent_consumption / 7 if recent_consumption else 0
            historical_daily = historical_consumption / 23 if historical_consumption else 0  # 30-7 = 23 days
            
            # Calculate percentage change
            if historical_daily > 0:
                change_percentage = ((recent_daily - historical_daily) / historical_daily) * 100
            else:
                change_percentage = 100 if recent_daily > 0 else 0
            
            return {
                "recent_consumption_7d": recent_consumption,
                "historical_consumption_23d": historical_consumption,
                "recent_daily_average": recent_daily,
                "historical_daily_average": historical_daily,
                "change_percentage": change_percentage,
                "indicates_surge": change_percentage > 50,  # More than 50% increase
                "data_available": historical_consumption > 0 or recent_consumption > 0
            }
    
    def _compare_against_forecast(self, product_id: int, company_id: int) -> Dict:
        """Compare actual consumption against forecasts"""
        # Note: This is a simplified version. In production, you'd have proper forecasting tables
        with connection.cursor() as cursor:
            # For now, we'll simulate forecast data based on historical patterns
            thirty_days_ago = datetime.now() - timedelta(days=30)
            
            cursor.execute("""
                SELECT AVG(oi.quantity) as avg_order_size, COUNT(*) as order_count
                FROM app_orderitem oi
                JOIN app_order o ON oi.order_id = o.order_id
                WHERE oi.product_id = %s 
                AND o.order_date >= %s
                AND o.status IN ('completed', 'shipped', 'delivered')
            """, [product_id, thirty_days_ago])
            
            row = cursor.fetchone()
            if row and row[0]:
                avg_order_size = float(row[0])
                order_count = row[1]
                
                # Simple forecast: historical average * expected orders
                expected_weekly_orders = order_count / 4  # 30 days ~ 4 weeks
                forecasted_weekly_consumption = avg_order_size * expected_weekly_orders
                
                return {
                    "forecasted_weekly_consumption": forecasted_weekly_consumption,
                    "avg_order_size": avg_order_size,
                    "historical_order_count": order_count,
                    "forecast_available": True,
                    "significant_deviation": False  # Would need actual vs forecast comparison
                }
            else:
                return {
                    "forecasted_weekly_consumption": 0,
                    "forecast_available": False,
                    "significant_deviation": False
                }
    
    def _analyze_supplier_performance(self, product_id: int, company_id: int) -> Dict:
        """Analyze supplier delivery performance"""
        thirty_days_ago = datetime.now() - timedelta(days=30)
        
        with connection.cursor() as cursor:
            # Check for delayed or pending orders
            cursor.execute("""
                SELECT COUNT(*) as delayed_orders, 
                       AVG(JULIANDAY('now') - JULIANDAY(o.order_date)) as avg_processing_days
                FROM app_order o
                JOIN app_orderitem oi ON o.order_id = oi.order_id
                WHERE oi.product_id = %s 
                AND o.order_date >= %s
                AND o.status IN ('pending', 'processing')
                AND JULIANDAY('now') - JULIANDAY(o.order_date) > 7
            """, [product_id, thirty_days_ago])
            
            row = cursor.fetchone()
            delayed_orders = row[0] if row else 0
            avg_processing_days = row[1] if row and row[1] else 0
            
            return {
                "delayed_orders_count": delayed_orders,
                "avg_processing_days": avg_processing_days,
                "supplier_issues_detected": delayed_orders > 0 or avg_processing_days > 7,
                "performance_rating": "poor" if delayed_orders > 2 else "acceptable"
            }
    
    def _check_pending_orders(self, product_id: int, company_id: int) -> Dict:
        """Check for pending replenishment orders"""
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT COUNT(*) as pending_count, 
                       SUM(oi.quantity) as total_pending_quantity,
                       MIN(o.order_date) as oldest_order_date
                FROM app_order o
                JOIN app_orderitem oi ON o.order_id = oi.order_id
                WHERE oi.product_id = %s 
                AND o.status IN ('pending', 'processing', 'confirmed')
            """, [product_id])
            
            row = cursor.fetchone()
            if row:
                pending_count = row[0] if row[0] else 0
                total_pending = row[1] if row[1] else 0
                oldest_date = row[2]
                
                return {
                    "pending_orders_count": pending_count,
                    "total_pending_quantity": total_pending,
                    "oldest_pending_order": oldest_date,
                    "replenishment_in_progress": pending_count > 0
                }
            else:
                return {
                    "pending_orders_count": 0,
                    "total_pending_quantity": 0,
                    "replenishment_in_progress": False
                }
    
    def _determine_root_cause(self, consumption_analysis: Dict, forecast_analysis: Dict, 
                            supplier_analysis: Dict, pending_orders: Dict) -> Tuple[str, float]:
        """Determine the most likely root cause with confidence score"""
        
        evidence_scores = {}
        
        # Evidence for demand surge
        if consumption_analysis.get("indicates_surge", False):
            evidence_scores["demand_surge"] = 0.8
        elif consumption_analysis.get("change_percentage", 0) > 20:
            evidence_scores["demand_surge"] = 0.5
        
        # Evidence for supplier delays
        if supplier_analysis.get("supplier_issues_detected", False):
            evidence_scores["supplier_delay"] = 0.7
        
        # Evidence for forecast inaccuracy
        if forecast_analysis.get("significant_deviation", False):
            evidence_scores["forecast_error"] = 0.6
        
        # Evidence for lack of replenishment
        if not pending_orders.get("replenishment_in_progress", False):
            evidence_scores["no_replenishment"] = 0.5
        
        # If no clear evidence, default to general inventory management issue
        if not evidence_scores:
            evidence_scores["inventory_management"] = 0.4
        
        # Select highest scoring root cause
        root_cause = max(evidence_scores.keys(), key=lambda k: evidence_scores[k])
        confidence = evidence_scores[root_cause]
        
        return root_cause, confidence
    
    def _generate_recommendations(self, root_cause: str, product_info: Dict) -> List[str]:
        """Generate actionable recommendations based on root cause"""
        recommendations = []
        
        if root_cause == "demand_surge":
            recommendations.extend([
                "Increase safety stock levels for this product",
                "Review demand forecasting models",
                "Consider expedited ordering from suppliers",
                "Analyze market trends causing demand increase"
            ])
        
        elif root_cause == "supplier_delay":
            recommendations.extend([
                "Contact suppliers to expedite pending orders",
                "Evaluate alternative suppliers",
                "Implement supplier performance monitoring",
                "Consider emergency procurement options"
            ])
        
        elif root_cause == "forecast_error":
            recommendations.extend([
                "Update demand forecasting models",
                "Review historical consumption patterns",
                "Implement more frequent inventory reviews",
                "Consider seasonal demand adjustments"
            ])
        
        elif root_cause == "no_replenishment":
            recommendations.extend([
                "Immediately place replenishment orders",
                "Review reorder point settings",
                "Implement automated reordering system",
                "Set up low inventory alerts"
            ])
        
        else:  # inventory_management or other
            recommendations.extend([
                "Conduct full inventory audit",
                "Review inventory management processes",
                "Implement better tracking systems",
                "Train staff on inventory procedures"
            ])
        
        return recommendations