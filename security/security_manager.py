"""
Security Manager - Main Security Orchestration

Coordinates all security components:
- Input validation (prompt injection defense)
- Budget enforcement
- Access control
- Sandboxed execution
- Security monitoring
- Audit logging

Provides unified security interface for NovaOS
"""

import logging
from typing import Dict, Optional, Tuple, Any, List
from dataclasses import dataclass
from enum import Enum

from .input_validator import InputValidator, get_input_validator, ValidationResult, ThreatLevel
from .budget_enforcer import BudgetEnforcer, get_budget_enforcer, CostPrediction
from .access_control import AccessController, get_access_controller, Permission, Role
from .sandbox import SecureSandbox, get_sandbox, SandboxConfig, ExecutionResult
from .monitor import SecurityMonitor, get_security_monitor, AlertLevel, AnomalyType, SecurityEvent
from .audit import AuditLogger, get_audit_logger, AuditEventType, log_security_event

logger = logging.getLogger(__name__)


class SecurityLevel(Enum):
    """Overall security posture"""
    PERMISSIVE = "permissive"  # Minimal security (development)
    BALANCED = "balanced"  # Balanced security and usability
    STRICT = "strict"  # High security (production)
    PARANOID = "paranoid"  # Maximum security (sensitive data)


@dataclass
class SecurityCheckResult:
    """Result of comprehensive security check"""
    allowed: bool
    reason: Optional[str]
    checks_passed: List[str]
    checks_failed: List[str]
    threat_level: ThreatLevel
    cost_reserved: float = 0.0


class SecurityManager:
    """
    Main security orchestration layer

    This class coordinates all security components and provides
    a unified interface for security checks and enforcement.
    """

    def __init__(
        self,
        security_level: SecurityLevel = SecurityLevel.STRICT,
        enable_input_validation: bool = True,
        enable_budget_enforcement: bool = True,
        enable_access_control: bool = True,
        enable_sandbox: bool = True,
        enable_monitoring: bool = True,
        enable_audit: bool = True
    ):
        """
        Initialize security manager

        Args:
            security_level: Overall security level
            enable_input_validation: Enable input validation
            enable_budget_enforcement: Enable budget enforcement
            enable_access_control: Enable access control
            enable_sandbox: Enable sandboxed execution
            enable_monitoring: Enable security monitoring
            enable_audit: Enable audit logging
        """
        self.security_level = security_level
        self.enable_input_validation = enable_input_validation
        self.enable_budget_enforcement = enable_budget_enforcement
        self.enable_access_control = enable_access_control
        self.enable_sandbox = enable_sandbox
        self.enable_monitoring = enable_monitoring
        self.enable_audit = enable_audit

        # Initialize components
        self.input_validator = get_input_validator(
            strict_mode=(security_level in [SecurityLevel.STRICT, SecurityLevel.PARANOID])
        ) if enable_input_validation else None

        self.budget_enforcer = get_budget_enforcer() if enable_budget_enforcement else None
        self.access_controller = get_access_controller() if enable_access_control else None

        sandbox_config = SandboxConfig(
            allow_network=(security_level != SecurityLevel.PARANOID),
            allow_file_write=(security_level in [SecurityLevel.PERMISSIVE, SecurityLevel.BALANCED])
        )
        self.sandbox = get_sandbox(sandbox_config) if enable_sandbox else None

        self.monitor = get_security_monitor() if enable_monitoring else None
        self.audit_logger = get_audit_logger() if enable_audit else None

        # Set up monitoring callbacks
        if self.monitor:
            self.monitor.add_alert_callback(self._handle_security_alert)

        logger.info(
            f"SecurityManager initialized (level={security_level.value}, "
            f"components: validator={enable_input_validation}, "
            f"budget={enable_budget_enforcement}, "
            f"access={enable_access_control}, "
            f"sandbox={enable_sandbox}, "
            f"monitor={enable_monitoring}, "
            f"audit={enable_audit})"
        )

    def check_agent_operation(
        self,
        agent_id: str,
        operation: str,
        input_data: Optional[str] = None,
        config: Optional[Dict] = None,
        estimated_tokens: Optional[Tuple[int, int]] = None,
        session_id: Optional[str] = None
    ) -> SecurityCheckResult:
        """
        Comprehensive security check before agent operation

        Args:
            agent_id: Agent performing operation
            operation: Operation type
            input_data: Input data to validate
            config: Configuration to validate
            estimated_tokens: (input_tokens, output_tokens) for cost estimation
            session_id: Session ID for access control

        Returns:
            Security check result
        """
        checks_passed = []
        checks_failed = []
        threat_level = ThreatLevel.SAFE
        cost_reserved = 0.0

        # 1. Access Control Check
        if self.enable_access_control and session_id:
            required_permission = self._get_required_permission(operation)
            authorized, error = self.access_controller.check_permission(session_id, required_permission)

            if not authorized:
                checks_failed.append(f"access_control: {error}")
                threat_level = ThreatLevel.CRITICAL

                if self.audit_logger:
                    self.audit_logger.log(
                        AuditEventType.AUTHZ_DENIED,
                        actor=agent_id,
                        action=operation,
                        result="denied",
                        details={'reason': error},
                        session_id=session_id
                    )

                return SecurityCheckResult(
                    allowed=False,
                    reason=f"Access denied: {error}",
                    checks_passed=checks_passed,
                    checks_failed=checks_failed,
                    threat_level=threat_level
                )

            checks_passed.append("access_control")

            if self.audit_logger:
                self.audit_logger.log(
                    AuditEventType.AUTHZ_GRANTED,
                    actor=agent_id,
                    action=operation,
                    session_id=session_id
                )

        # 2. Input Validation
        if self.enable_input_validation and input_data:
            result = self.input_validator.validate(input_data, context=f"{agent_id}:{operation}")

            if not result.is_valid:
                checks_failed.append(f"input_validation: {', '.join(result.threats_detected)}")
                threat_level = max(threat_level, result.threat_level, key=lambda t: list(ThreatLevel).index(t))

                if self.monitor:
                    self.monitor.record_event(SecurityEvent(
                        timestamp=safe_datetime_now(),
                        event_type=AnomalyType.SUSPICIOUS_INPUT,
                        level=AlertLevel.WARNING if result.threat_level == ThreatLevel.SUSPICIOUS else AlertLevel.CRITICAL,
                        description=f"Input validation failed: {result.threats_detected}",
                        source=agent_id,
                        metadata={'threats': result.threats_detected}
                    ))

                if self.audit_logger:
                    log_security_event(
                        AuditEventType.INPUT_BLOCKED,
                        actor=agent_id,
                        details={'threats': result.threats_detected, 'input_snippet': input_data[:100]}
                    )

                return SecurityCheckResult(
                    allowed=False,
                    reason=f"Input validation failed: {', '.join(result.threats_detected)}",
                    checks_passed=checks_passed,
                    checks_failed=checks_failed,
                    threat_level=threat_level
                )

            checks_passed.append("input_validation")

            if result.threat_level != ThreatLevel.SAFE:
                threat_level = result.threat_level

        # 3. Config Validation
        if self.enable_input_validation and config:
            config_valid, config_issues = self.input_validator.validate_config(config)

            if not config_valid:
                checks_failed.append(f"config_validation: {', '.join(config_issues)}")
                threat_level = ThreatLevel.DANGEROUS

                return SecurityCheckResult(
                    allowed=False,
                    reason=f"Config validation failed: {', '.join(config_issues)}",
                    checks_passed=checks_passed,
                    checks_failed=checks_failed,
                    threat_level=threat_level
                )

            checks_passed.append("config_validation")

        # 4. Budget Check and Reservation
        if self.enable_budget_enforcement and estimated_tokens:
            input_tokens, output_tokens = estimated_tokens

            # Predict cost
            cost_pred = self.budget_enforcer.predict_cost(
                input_tokens,
                output_tokens,
                model="claude-sonnet-4-5-20250929"  # Default model
            )

            # Check rate limit
            if not self.budget_enforcer.rate_limit_check(timeout=5.0):
                checks_failed.append("rate_limit_exceeded")

                if self.monitor:
                    self.monitor.record_event(SecurityEvent(
                        timestamp=safe_datetime_now(),
                        event_type=AnomalyType.RATE_LIMIT_EXCEEDED,
                        level=AlertLevel.WARNING,
                        description="Rate limit exceeded",
                        source=agent_id
                    ))

                return SecurityCheckResult(
                    allowed=False,
                    reason="Rate limit exceeded",
                    checks_passed=checks_passed,
                    checks_failed=checks_failed,
                    threat_level=threat_level
                )

            # Check and reserve budget
            allowed, budget_reason = self.budget_enforcer.check_and_reserve(
                agent_id,
                cost_pred.estimated_cost,
                operation
            )

            if not allowed:
                checks_failed.append(f"budget: {budget_reason}")

                if self.monitor:
                    self.monitor.record_event(SecurityEvent(
                        timestamp=safe_datetime_now(),
                        event_type=AnomalyType.BUDGET_VIOLATION,
                        level=AlertLevel.CRITICAL if "EMERGENCY" in budget_reason else AlertLevel.WARNING,
                        description=budget_reason,
                        source=agent_id,
                        metadata={'estimated_cost': cost_pred.estimated_cost}
                    ))

                if self.audit_logger:
                    self.audit_logger.log(
                        AuditEventType.BUDGET_EXCEEDED,
                        actor=agent_id,
                        action=operation,
                        result="blocked",
                        details={'reason': budget_reason, 'cost': cost_pred.estimated_cost}
                    )

                return SecurityCheckResult(
                    allowed=False,
                    reason=f"Budget check failed: {budget_reason}",
                    checks_passed=checks_passed,
                    checks_failed=checks_failed,
                    threat_level=threat_level
                )

            checks_passed.append("budget_check")
            cost_reserved = cost_pred.estimated_cost

            # Record cost for monitoring
            if self.monitor:
                self.monitor.record_cost(agent_id, cost_pred.estimated_cost)

        # All checks passed
        if self.audit_logger:
            self.audit_logger.log(
                AuditEventType.AUTHZ_GRANTED,
                actor=agent_id,
                action=operation,
                result="allowed",
                details={'checks_passed': checks_passed, 'threat_level': threat_level.value}
            )

        return SecurityCheckResult(
            allowed=True,
            reason=None,
            checks_passed=checks_passed,
            checks_failed=[],
            threat_level=threat_level,
            cost_reserved=cost_reserved
        )

    def execute_sandboxed(
        self,
        agent_id: str,
        command: List[str],
        session_id: Optional[str] = None
    ) -> Tuple[bool, ExecutionResult]:
        """
        Execute command in sandbox with security checks

        Args:
            agent_id: Agent executing command
            command: Command to execute
            session_id: Session ID for access control

        Returns:
            Tuple of (allowed, execution_result)
        """
        if not self.enable_sandbox:
            return False, None

        # Check permissions
        if self.enable_access_control and session_id:
            authorized, error = self.access_controller.check_permission(
                session_id,
                Permission.API_CALL
            )

            if not authorized:
                if self.audit_logger:
                    self.audit_logger.log(
                        AuditEventType.AUTHZ_DENIED,
                        actor=agent_id,
                        action="sandbox_execute",
                        result="denied",
                        details={'command': ' '.join(command), 'reason': error}
                    )
                return False, None

        # Execute in sandbox
        result = self.sandbox.execute_command(command)

        # Log violations
        if result.violations and self.monitor:
            for violation in result.violations:
                self.monitor.record_sandbox_violation(agent_id, violation, ' '.join(command))

        # Audit log
        if self.audit_logger:
            self.audit_logger.log(
                AuditEventType.SANDBOX_VIOLATION if result.violations else AuditEventType.AGENT_DEPLOYED,
                actor=agent_id,
                action="sandbox_execute",
                result="success" if result.success else "failure",
                details={
                    'command': ' '.join(command),
                    'violations': result.violations,
                    'exit_code': result.exit_code
                }
            )

        return True, result

    def _get_required_permission(self, operation: str) -> Permission:
        """Map operation to required permission"""
        permission_map = {
            'deploy': Permission.AGENT_DEPLOY,
            'kill': Permission.AGENT_KILL,
            'pause': Permission.AGENT_PAUSE,
            'resume': Permission.AGENT_RESUME,
            'view': Permission.AGENT_VIEW,
            'api_call': Permission.API_CALL,
            'data_read': Permission.DATA_READ,
            'data_write': Permission.DATA_WRITE,
            'budget_modify': Permission.BUDGET_MODIFY,
        }
        return permission_map.get(operation, Permission.API_CALL)

    def _handle_security_alert(self, alert):
        """Handle security alerts"""
        logger.warning(
            f"SECURITY ALERT: {alert.title} (level={alert.level.value}) - "
            f"{alert.description}"
        )

        # For EMERGENCY alerts, trigger emergency stop
        if alert.level == AlertLevel.EMERGENCY and self.budget_enforcer:
            self.budget_enforcer.trigger_emergency_stop(alert.description)

    def get_security_status(self) -> Dict:
        """Get overall security status"""
        status = {
            'security_level': self.security_level.value,
            'timestamp': safe_datetime_now().isoformat()
        }

        if self.input_validator:
            status['input_validation'] = self.input_validator.get_stats()

        if self.budget_enforcer:
            status['budget'] = self.budget_enforcer.get_status()

        if self.access_controller:
            status['access_control'] = self.access_controller.get_status()

        if self.sandbox:
            status['sandbox'] = self.sandbox.get_stats()

        if self.monitor:
            status['monitoring'] = self.monitor.get_stats()
            status['health'] = self.monitor.get_health_summary()

        if self.audit_logger:
            status['audit'] = self.audit_logger.get_stats()

        return status

    def create_api_key(
        self,
        name: str,
        role: Role,
        authorized_by: str,
        expires_days: Optional[int] = 90
    ) -> Tuple[str, str]:
        """
        Create API key with security checks

        Args:
            name: Key name
            role: Role for key
            authorized_by: Who is creating the key
            expires_days: Days until expiration

        Returns:
            Tuple of (key_id, plaintext_key)
        """
        if not self.access_controller:
            raise RuntimeError("Access control not enabled")

        key_id, plaintext_key = self.access_controller.create_api_key(
            name, role, expires_days
        )

        if self.audit_logger:
            self.audit_logger.log(
                AuditEventType.AUTH_KEY_CREATED,
                actor=authorized_by,
                action="create_api_key",
                resource=key_id,
                details={'name': name, 'role': role.value, 'expires_days': expires_days}
            )

        return key_id, plaintext_key

    def authenticate(
        self,
        api_key: str,
        ip_address: Optional[str] = None
    ) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Authenticate with API key

        Args:
            api_key: API key
            ip_address: Source IP

        Returns:
            Tuple of (success, session_id, error_message)
        """
        if not self.access_controller:
            return False, None, "Access control not enabled"

        success, session_id, error = self.access_controller.authenticate(
            api_key, ip_address
        )

        if success and self.audit_logger:
            session = self.access_controller.get_session(session_id)
            self.audit_logger.log(
                AuditEventType.AUTH_SUCCESS,
                actor=session.key_id if session else "unknown",
                action="authenticate",
                result="success",
                ip_address=ip_address,
                session_id=session_id
            )
        elif not success and self.audit_logger:
            self.audit_logger.log(
                AuditEventType.AUTH_FAILURE,
                actor="unknown",
                action="authenticate",
                result="failure",
                details={'reason': error},
                ip_address=ip_address
            )

            if self.monitor:
                self.monitor.record_auth_failure(ip_address, error)

        return success, session_id, error


# Singleton instance
_security_manager_instance = None


def get_security_manager(
    security_level: SecurityLevel = SecurityLevel.STRICT
) -> SecurityManager:
    """Get or create security manager singleton"""
    global _security_manager_instance
    if _security_manager_instance is None:
        _security_manager_instance = SecurityManager(security_level=security_level)
    return _security_manager_instance


from datetime import datetime


def safe_datetime_now():
    """Get current datetime with fallback for timestamp overflow"""
    try:
        return datetime.now()
    except (OSError, OverflowError, ValueError):
        from datetime import datetime as dt
        return dt(2025, 1, 1, 0, 0, 0)

