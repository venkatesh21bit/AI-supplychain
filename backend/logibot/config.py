"""
Configuration management for LOGI-BOT agent.
"""

import os
from dataclasses import dataclass, field
from typing import Dict, List, Optional
from enum import Enum


class AlertType(Enum):
    """Types of alerts the agent can handle."""
    LOW_INVENTORY = "low_inventory"
    DELAYED_SHIPMENT = "delayed_shipment"
    DEMAND_SURGE = "demand_surge"
    SUPPLIER_ISSUE = "supplier_issue"


class Priority(Enum):
    """Priority levels for agent actions."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class InventoryThresholds:
    """Inventory monitoring thresholds."""
    critical_level: int = 10  # Critical inventory level
    warning_level: int = 20   # Warning inventory level
    reorder_point: int = 15   # When to trigger reorder
    safety_stock: int = 5     # Minimum safety stock


@dataclass
class ComposioConfig:
    """Composio integration configuration."""
    api_key: str = field(default_factory=lambda: os.getenv("COMPOSIO_API_KEY", ""))
    base_url: str = "https://backend.composio.dev/api/v1"
    
    # Tool configurations
    asana_workspace_id: str = field(default_factory=lambda: os.getenv("ASANA_WORKSPACE_ID", ""))
    outlook_account: str = field(default_factory=lambda: os.getenv("OUTLOOK_ACCOUNT", ""))
    
    # Timeout settings
    connection_timeout: int = 30
    read_timeout: int = 60


@dataclass
class OptimizationConfig:
    """AI Optimization Engine configuration."""
    model: str = "gpt-4"
    temperature: float = 0.7
    max_tokens: int = 1000
    enable_learning: bool = True


@dataclass
class AgentConfig:
    """Main configuration for LOGI-BOT agent."""
    
    # Agent identification
    agent_name: str = "LOGI-BOT"
    agent_version: str = "1.0.0"
    
    # Database configuration
    database_url: str = field(default_factory=lambda: os.getenv("DATABASE_URL", ""))
    
    # Monitoring configuration
    inventory_thresholds: InventoryThresholds = field(default_factory=InventoryThresholds)
    check_interval_seconds: int = 300  # Check every 5 minutes
    
    # Integration configurations
    composio: ComposioConfig = field(default_factory=ComposioConfig)
    optimization: OptimizationConfig = field(default_factory=OptimizationConfig)
    
    # Workflow settings
    max_retries: int = 3
    retry_delay_seconds: int = 5
    enable_auto_resolution: bool = True
    require_human_approval: bool = True  # For critical actions
    
    # Notification settings
    notification_emails: List[str] = field(default_factory=list)
    slack_webhook_url: Optional[str] = field(default_factory=lambda: os.getenv("SLACK_WEBHOOK_URL"))
    
    # Logging
    log_level: str = "INFO"
    log_file: str = "logibot.log"
    
    @classmethod
    def from_env(cls) -> 'AgentConfig':
        """Create configuration from environment variables."""
        return cls(
            database_url=os.getenv("DATABASE_URL", ""),
            composio=ComposioConfig(
                api_key=os.getenv("COMPOSIO_API_KEY", ""),
                asana_workspace_id=os.getenv("ASANA_WORKSPACE_ID", ""),
                outlook_account=os.getenv("OUTLOOK_ACCOUNT", "")
            )
        )
    
    def validate(self) -> bool:
        """Validate configuration."""
        errors = []
        
        if not self.database_url:
            errors.append("DATABASE_URL is required")
        
        if not self.composio.api_key:
            errors.append("COMPOSIO_API_KEY is required")
        
        if errors:
            raise ValueError(f"Configuration errors: {', '.join(errors)}")
        
        return True
