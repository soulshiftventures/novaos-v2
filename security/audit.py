"""
Audit Logger - Security Event Logging and Compliance

Logs:
- All security decisions
- Access attempts (successful and failed)
- Agent actions
- Budget operations
- Configuration changes
- System events

Provides audit trail for compliance and incident response
"""

import logging
import json
import threading
from typing import Dict, Optional, List, Any
from datetime import datetime, timedelta
from pathlib import Path
from dataclasses import dataclass, asdict
from enum import Enum
import hashlib

logger = logging.getLogger(__name__)


def safe_datetime_now() -> datetime:
    """Get current datetime with fallback for timestamp overflow"""
    try:
        return safe_datetime_now()
    except (OSError, OverflowError, ValueError):
        return datetime(2025, 1, 1, 0, 0, 0)


class AuditEventType(Enum):
    """Types of audit events"""
    # Authentication
    AUTH_SUCCESS = "auth.success"
    AUTH_FAILURE = "auth.failure"
    AUTH_KEY_CREATED = "auth.key_created"
    AUTH_KEY_REVOKED = "auth.key_revoked"
    AUTH_KEY_ROTATED = "auth.key_rotated"

    # Authorization
    AUTHZ_GRANTED = "authz.granted"
    AUTHZ_DENIED = "authz.denied"

    # Agent management
    AGENT_DEPLOYED = "agent.deployed"
    AGENT_KILLED = "agent.killed"
    AGENT_PAUSED = "agent.paused"
    AGENT_RESUMED = "agent.resumed"

    # Budget
    BUDGET_CHECK = "budget.check"
    BUDGET_EXCEEDED = "budget.exceeded"
    BUDGET_MODIFIED = "budget.modified"
    EMERGENCY_STOP = "budget.emergency_stop"

    # Security
    INPUT_VALIDATED = "security.input_validated"
    INPUT_BLOCKED = "security.input_blocked"
    SANDBOX_VIOLATION = "security.sandbox_violation"
    ANOMALY_DETECTED = "security.anomaly_detected"

    # Data access
    DATA_READ = "data.read"
    DATA_WRITE = "data.write"
    DATA_DELETE = "data.delete"

    # Configuration
    CONFIG_CHANGED = "config.changed"
    SECURITY_CONFIG_CHANGED = "config.security_changed"

    # System
    SYSTEM_START = "system.start"
    SYSTEM_STOP = "system.stop"
    SYSTEM_ERROR = "system.error"


@dataclass
class AuditEvent:
    """Audit event record"""
    timestamp: datetime
    event_type: AuditEventType
    actor: str  # user_id, agent_id, system
    action: str
    resource: Optional[str] = None
    result: str = "success"  # success, failure, blocked
    details: Dict[str, Any] = None
    ip_address: Optional[str] = None
    session_id: Optional[str] = None

    def __post_init__(self):
        if self.details is None:
            self.details = {}

    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat()
        data['event_type'] = self.event_type.value
        return data

    def to_json(self) -> str:
        """Convert to JSON"""
        return json.dumps(self.to_dict())

    @property
    def event_hash(self) -> str:
        """Generate hash of event for integrity verification"""
        event_str = f"{self.timestamp.isoformat()}{self.event_type.value}{self.actor}{self.action}"
        return hashlib.sha256(event_str.encode()).hexdigest()[:16]


class AuditLogger:
    """
    Security audit logger

    Features:
    - Structured logging
    - Multiple output formats (JSON, text)
    - Log rotation
    - Tamper detection
    - Query and analysis
    """

    def __init__(
        self,
        log_dir: Optional[Path] = None,
        enable_file_logging: bool = True,
        enable_console_logging: bool = False,
        retention_days: int = 90
    ):
        """
        Initialize audit logger

        Args:
            log_dir: Directory for audit logs
            enable_file_logging: Write to files
            enable_console_logging: Write to console
            retention_days: Days to retain audit logs
        """
        self.enable_file_logging = enable_file_logging
        self.enable_console_logging = enable_console_logging
        self.retention_days = retention_days

        # Set up log directory
        if log_dir is None:
            log_dir = Path(__file__).parent.parent / "logs" / "audit"
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)

        # In-memory event buffer
        self.event_buffer: List[AuditEvent] = []
        self.max_buffer_size = 1000

        # Stats
        self.total_events = 0
        self.events_by_type: Dict[str, int] = {}

        # Thread safety
        self.lock = threading.Lock()

        # Open current log file
        self.current_log_file = self._get_log_file()

        logger.info(f"AuditLogger initialized (log_dir={self.log_dir})")

    def log(
        self,
        event_type: AuditEventType,
        actor: str,
        action: str,
        resource: Optional[str] = None,
        result: str = "success",
        details: Optional[Dict] = None,
        ip_address: Optional[str] = None,
        session_id: Optional[str] = None
    ):
        """
        Log an audit event

        Args:
            event_type: Type of event
            actor: Who performed the action
            action: What action was performed
            resource: What resource was affected
            result: Result of action (success, failure, blocked)
            details: Additional details
            ip_address: Source IP
            session_id: Session ID
        """
        event = AuditEvent(
            timestamp=safe_datetime_now(),
            event_type=event_type,
            actor=actor,
            action=action,
            resource=resource,
            result=result,
            details=details or {},
            ip_address=ip_address,
            session_id=session_id
        )

        with self.lock:
            # Add to buffer
            self.event_buffer.append(event)
            if len(self.event_buffer) > self.max_buffer_size:
                self.event_buffer.pop(0)

            # Update stats
            self.total_events += 1
            event_type_str = event_type.value
            self.events_by_type[event_type_str] = self.events_by_type.get(event_type_str, 0) + 1

            # Write to file
            if self.enable_file_logging:
                self._write_to_file(event)

            # Write to console
            if self.enable_console_logging:
                self._write_to_console(event)

    def _write_to_file(self, event: AuditEvent):
        """Write event to log file"""
        try:
            # Check if we need to rotate log file
            if not self.current_log_file.exists() or \
               self.current_log_file.stat().st_size > 10 * 1024 * 1024:  # 10MB
                self.current_log_file = self._get_log_file()

            # Write as JSON line
            with open(self.current_log_file, 'a') as f:
                f.write(event.to_json() + '\n')

        except Exception as e:
            logger.error(f"Error writing audit log: {e}")

    def _write_to_console(self, event: AuditEvent):
        """Write event to console"""
        console_msg = (
            f"[AUDIT] {event.timestamp.isoformat()} | "
            f"{event.event_type.value} | "
            f"actor={event.actor} | "
            f"action={event.action} | "
            f"result={event.result}"
        )
        if event.resource:
            console_msg += f" | resource={event.resource}"

        print(console_msg)

    def _get_log_file(self) -> Path:
        """Get current log file path"""
        date_str = safe_datetime_now().strftime("%Y-%m-%d")
        return self.log_dir / f"audit_{date_str}.jsonl"

    def query(
        self,
        event_type: Optional[AuditEventType] = None,
        actor: Optional[str] = None,
        resource: Optional[str] = None,
        result: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: int = 100
    ) -> List[AuditEvent]:
        """
        Query audit logs

        Args:
            event_type: Filter by event type
            actor: Filter by actor
            resource: Filter by resource
            result: Filter by result
            start_time: Start of time range
            end_time: End of time range
            limit: Maximum results

        Returns:
            List of matching audit events
        """
        with self.lock:
            results = []

            for event in reversed(self.event_buffer):
                # Apply filters
                if event_type and event.event_type != event_type:
                    continue
                if actor and event.actor != actor:
                    continue
                if resource and event.resource != resource:
                    continue
                if result and event.result != result:
                    continue
                if start_time and event.timestamp < start_time:
                    continue
                if end_time and event.timestamp > end_time:
                    continue

                results.append(event)

                if len(results) >= limit:
                    break

            return results

    def get_stats(self) -> Dict:
        """Get audit statistics"""
        with self.lock:
            return {
                'total_events': self.total_events,
                'buffer_size': len(self.event_buffer),
                'events_by_type': self.events_by_type.copy(),
                'log_dir': str(self.log_dir),
                'current_log_file': str(self.current_log_file),
                'retention_days': self.retention_days
            }

    def get_security_summary(self, hours: int = 24) -> Dict:
        """
        Get security summary for last N hours

        Args:
            hours: Number of hours to analyze

        Returns:
            Security summary
        """
        cutoff = safe_datetime_now() - timedelta(hours=hours)
        recent_events = [e for e in self.event_buffer if e.timestamp > cutoff]

        # Count failures and blocks
        auth_failures = sum(1 for e in recent_events if e.event_type == AuditEventType.AUTH_FAILURE)
        authz_denials = sum(1 for e in recent_events if e.event_type == AuditEventType.AUTHZ_DENIED)
        input_blocked = sum(1 for e in recent_events if e.event_type == AuditEventType.INPUT_BLOCKED)
        sandbox_violations = sum(1 for e in recent_events if e.event_type == AuditEventType.SANDBOX_VIOLATION)
        budget_exceeded = sum(1 for e in recent_events if e.event_type == AuditEventType.BUDGET_EXCEEDED)

        # Get unique actors
        actors = set(e.actor for e in recent_events)

        return {
            'period_hours': hours,
            'total_events': len(recent_events),
            'auth_failures': auth_failures,
            'authz_denials': authz_denials,
            'input_blocked': input_blocked,
            'sandbox_violations': sandbox_violations,
            'budget_exceeded': budget_exceeded,
            'unique_actors': len(actors),
            'actors': list(actors)
        }


# Singleton instance
_audit_logger_instance = None


def get_audit_logger() -> AuditLogger:
    """Get or create audit logger singleton"""
    global _audit_logger_instance
    if _audit_logger_instance is None:
        _audit_logger_instance = AuditLogger()
    return _audit_logger_instance


# Convenience functions
def log_auth_success(actor: str, ip_address: Optional[str] = None, session_id: Optional[str] = None):
    """Log successful authentication"""
    get_audit_logger().log(
        AuditEventType.AUTH_SUCCESS,
        actor=actor,
        action="authenticate",
        result="success",
        ip_address=ip_address,
        session_id=session_id
    )


def log_auth_failure(actor: str, reason: str, ip_address: Optional[str] = None):
    """Log failed authentication"""
    get_audit_logger().log(
        AuditEventType.AUTH_FAILURE,
        actor=actor,
        action="authenticate",
        result="failure",
        details={'reason': reason},
        ip_address=ip_address
    )


def log_agent_action(agent_id: str, action: str, resource: Optional[str] = None, details: Optional[Dict] = None):
    """Log agent action"""
    event_type_map = {
        'deploy': AuditEventType.AGENT_DEPLOYED,
        'kill': AuditEventType.AGENT_KILLED,
        'pause': AuditEventType.AGENT_PAUSED,
        'resume': AuditEventType.AGENT_RESUMED
    }

    event_type = event_type_map.get(action, AuditEventType.AGENT_DEPLOYED)

    get_audit_logger().log(
        event_type,
        actor="system",
        action=action,
        resource=agent_id,
        details=details
    )


def log_security_event(event_type: AuditEventType, actor: str, details: Dict):
    """Log security event"""
    get_audit_logger().log(
        event_type,
        actor=actor,
        action=event_type.value,
        result="blocked" if "blocked" in event_type.value else "detected",
        details=details
    )


from datetime import timedelta
