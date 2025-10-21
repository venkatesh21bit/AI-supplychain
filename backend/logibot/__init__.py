"""
LOGI-BOT: Autonomous Supply Chain Resilience Agent

A production-ready intelligent agent that proactively detects, diagnoses,
and resolves supply chain disruptions through autonomous orchestration.
"""

__version__ = "1.0.0"
__author__ = "Vendor Innovation Team"

from .agent import LogiBot
from .config import AgentConfig

__all__ = ['LogiBot', 'AgentConfig']
