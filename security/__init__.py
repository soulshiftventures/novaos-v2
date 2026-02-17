"""
NovaOS V2 Security Layer

Comprehensive security protections for autonomous AI agents:
- Prompt injection defense
- Budget enforcement
- Access control
- Sandboxed execution
- Data protection
- Monitoring & alerting
- Behavioral guardrails
"""

from .security_manager import SecurityManager, get_security_manager
from .input_validator import InputValidator
from .budget_enforcer import BudgetEnforcer
from .access_control import AccessController
from .sandbox import SecureSandbox
from .monitor import SecurityMonitor
from .audit import AuditLogger

__all__ = [
    'SecurityManager',
    'get_security_manager',
    'InputValidator',
    'BudgetEnforcer',
    'AccessController',
    'SecureSandbox',
    'SecurityMonitor',
    'AuditLogger'
]

__version__ = '2.0.0'
