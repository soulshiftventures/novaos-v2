"""
Security Monitor - Anomaly Detection and Alerting

Monitors for:
- Unusual spending patterns
- Suspicious activity (failed auth, violations)
- Agent behavior anomalies
- Data exfiltration attempts
- System health issues
- Security events

Provides real-time alerts and threat detection
"""

import logging
import threading
from typing import Dict, List, Optional, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
from collections import deque
import statistics

logger = logging.getLogger(__name__)


def safe_datetime_now() -> datetime:
    """Get current datetime with fallback for timestamp overflow"""
    try:
        return safe_datetime_now()
    except (OSError, OverflowError, ValueError):
        return datetime(2025, 1, 1, 0, 0, 0)


class AlertLevel(Enum):
    """Alert severity levels"""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"
    EMERGENCY = "emergency"


class AnomalyType(Enum):
    """Types of anomalies"""
    COST_SPIKE = "cost_spike"
    AUTH_FAILURES = "auth_failures"
    BUDGET_VIOLATION = "budget_violation"
    SUSPICIOUS_INPUT = "suspicious_input"
    SANDBOX_VIOLATION = "sandbox_violation"
    RATE_LIMIT_EXCEEDED = "rate_limit_exceeded"
    UNUSUAL_PATTERN = "unusual_pattern"
    DATA_EXFILTRATION = "data_exfiltration"
    AGENT_CRASH = "agent_crash"
    SYSTEM_OVERLOAD = "system_overload"


@dataclass
class SecurityEvent:
    """Security event record"""
    timestamp: datetime
    event_type: AnomalyType
    level: AlertLevel
    description: str
    source: str  # agent_id, system component, etc.
    metadata: Dict = field(default_factory=dict)
    acknowledged: bool = False


@dataclass
class Alert:
    """Security alert"""
    alert_id: str
    timestamp: datetime
    level: AlertLevel
    title: str
    description: str
    events: List[SecurityEvent]
    actionable: bool = True
    action_required: Optional[str] = None


class SecurityMonitor:
    """
    Monitor system for security anomalies

    Features:
    - Statistical anomaly detection
    - Pattern recognition
    - Real-time alerting
    - Event correlation
    - Threat scoring
    """

    def __init__(
        self,
        cost_spike_threshold: float = 2.0,  # 2x average
        auth_failure_threshold: int = 5,  # failures per minute
        window_minutes: int = 15,  # rolling window size
        enable_alerts: bool = True
    ):
        """
        Initialize security monitor

        Args:
            cost_spike_threshold: Threshold for cost spike detection (multiplier)
            auth_failure_threshold: Max auth failures per minute
            window_minutes: Size of rolling window for statistics
            enable_alerts: Enable real-time alerting
        """
        self.cost_spike_threshold = cost_spike_threshold
        self.auth_failure_threshold = auth_failure_threshold
        self.window_minutes = window_minutes
        self.enable_alerts = enable_alerts

        # Event storage (rolling window)
        self.events: deque[SecurityEvent] = deque(maxlen=1000)
        self.alerts: List[Alert] = []

        # Statistics (rolling windows)
        self.cost_history: deque[Tuple[datetime, float]] = deque(maxlen=100)
        self.auth_failures: deque[datetime] = deque(maxlen=100)
        self.sandbox_violations: deque[datetime] = deque(maxlen=100)

        # Alert callbacks
        self.alert_callbacks: List[Callable[[Alert], None]] = []

        # Thread safety
        self.lock = threading.Lock()

        # Stats
        self.total_events = 0
        self.total_alerts = 0

        logger.info("SecurityMonitor initialized")

    def record_event(self, event: SecurityEvent):
        """
        Record a security event

        Args:
            event: Security event to record
        """
        with self.lock:
            self.events.append(event)
            self.total_events += 1

            # Update specific trackers
            if event.event_type == AnomalyType.AUTH_FAILURES:
                self.auth_failures.append(event.timestamp)
            elif event.event_type == AnomalyType.SANDBOX_VIOLATION:
                self.sandbox_violations.append(event.timestamp)
            elif event.event_type == AnomalyType.COST_SPIKE:
                cost = event.metadata.get('cost', 0.0)
                self.cost_history.append((event.timestamp, cost))

            # Check if event should trigger alert
            if event.level in [AlertLevel.CRITICAL, AlertLevel.EMERGENCY]:
                self._create_alert_from_event(event)

            logger.info(
                f"Security event: {event.event_type.value} "
                f"(level={event.level.value}, source={event.source})"
            )

    def record_cost(self, agent_id: str, cost: float):
        """
        Record cost and check for anomalies

        Args:
            agent_id: Agent that incurred cost
            cost: Cost amount
        """
        now = safe_datetime_now()

        with self.lock:
            self.cost_history.append((now, cost))

            # Check for cost spike
            if len(self.cost_history) >= 10:
                recent_costs = [c for _, c in list(self.cost_history)[-10:]]
                avg_cost = statistics.mean(recent_costs)

                if cost > avg_cost * self.cost_spike_threshold:
                    event = SecurityEvent(
                        timestamp=now,
                        event_type=AnomalyType.COST_SPIKE,
                        level=AlertLevel.WARNING,
                        description=f"Cost spike detected: ${cost:.2f} (avg: ${avg_cost:.2f})",
                        source=agent_id,
                        metadata={'cost': cost, 'average': avg_cost}
                    )
                    self.record_event(event)

    def record_auth_failure(self, ip_address: Optional[str] = None, reason: str = ""):
        """
        Record authentication failure

        Args:
            ip_address: Source IP
            reason: Failure reason
        """
        now = safe_datetime_now()

        with self.lock:
            self.auth_failures.append(now)

            # Clean old entries (older than window)
            cutoff = now - timedelta(minutes=self.window_minutes)
            while self.auth_failures and self.auth_failures[0] < cutoff:
                self.auth_failures.popleft()

            # Check if threshold exceeded
            if len(self.auth_failures) >= self.auth_failure_threshold:
                event = SecurityEvent(
                    timestamp=now,
                    event_type=AnomalyType.AUTH_FAILURES,
                    level=AlertLevel.CRITICAL,
                    description=f"High auth failure rate: {len(self.auth_failures)} failures in {self.window_minutes} minutes",
                    source=ip_address or "unknown",
                    metadata={'count': len(self.auth_failures), 'reason': reason}
                )
                self.record_event(event)

    def record_sandbox_violation(self, agent_id: str, violation: str, command: str = ""):
        """
        Record sandbox violation

        Args:
            agent_id: Agent that caused violation
            violation: Violation type
            command: Command that was blocked
        """
        now = safe_datetime_now()

        event = SecurityEvent(
            timestamp=now,
            event_type=AnomalyType.SANDBOX_VIOLATION,
            level=AlertLevel.WARNING,
            description=f"Sandbox violation: {violation}",
            source=agent_id,
            metadata={'violation': violation, 'command': command}
        )

        self.record_event(event)

        # Check for repeated violations
        with self.lock:
            cutoff = now - timedelta(minutes=self.window_minutes)
            recent_violations = [
                e for e in self.events
                if e.event_type == AnomalyType.SANDBOX_VIOLATION
                and e.source == agent_id
                and e.timestamp > cutoff
            ]

            if len(recent_violations) >= 5:
                alert_event = SecurityEvent(
                    timestamp=now,
                    event_type=AnomalyType.UNUSUAL_PATTERN,
                    level=AlertLevel.CRITICAL,
                    description=f"Repeated sandbox violations from {agent_id}",
                    source=agent_id,
                    metadata={'violation_count': len(recent_violations)}
                )
                self.record_event(alert_event)

    def detect_data_exfiltration(
        self,
        agent_id: str,
        destination: str,
        data_size: int
    ):
        """
        Detect potential data exfiltration

        Args:
            agent_id: Agent attempting exfiltration
            destination: Destination URL/IP
            data_size: Size of data being sent
        """
        event = SecurityEvent(
            timestamp=safe_datetime_now(),
            event_type=AnomalyType.DATA_EXFILTRATION,
            level=AlertLevel.CRITICAL,
            description=f"Potential data exfiltration to {destination}",
            source=agent_id,
            metadata={
                'destination': destination,
                'data_size': data_size
            }
        )
        self.record_event(event)

    def _create_alert_from_event(self, event: SecurityEvent):
        """Create alert from critical event"""
        # Safe timestamp generation
        try:
            ts = int(safe_datetime_now().timestamp())
        except (OSError, OverflowError, ValueError):
            ts = int(datetime(2025, 1, 1).timestamp())

        alert = Alert(
            alert_id=f"alert_{ts}",
            timestamp=event.timestamp,
            level=event.level,
            title=f"{event.event_type.value.replace('_', ' ').title()}",
            description=event.description,
            events=[event],
            actionable=True,
            action_required=self._get_recommended_action(event)
        )

        with self.lock:
            self.alerts.append(alert)
            self.total_alerts += 1

        # Trigger callbacks
        if self.enable_alerts:
            for callback in self.alert_callbacks:
                try:
                    callback(alert)
                except Exception as e:
                    logger.error(f"Error in alert callback: {e}")

        logger.warning(
            f"ALERT CREATED: {alert.title} (level={alert.level.value}) - "
            f"{alert.description}"
        )

    def _get_recommended_action(self, event: SecurityEvent) -> str:
        """Get recommended action for event"""
        actions = {
            AnomalyType.COST_SPIKE: "Review agent activity and consider pausing",
            AnomalyType.AUTH_FAILURES: "Check for brute force attack, consider IP blocking",
            AnomalyType.BUDGET_VIOLATION: "Review budget limits and agent spending",
            AnomalyType.SUSPICIOUS_INPUT: "Review input validation rules",
            AnomalyType.SANDBOX_VIOLATION: "Review agent behavior and sandbox config",
            AnomalyType.DATA_EXFILTRATION: "IMMEDIATE ACTION: Kill agent and review logs",
            AnomalyType.UNUSUAL_PATTERN: "Investigate agent behavior",
        }
        return actions.get(event.event_type, "Investigate and take appropriate action")

    def add_alert_callback(self, callback: Callable[[Alert], None]):
        """
        Add callback for alerts

        Args:
            callback: Function to call when alert is created
        """
        with self.lock:
            self.alert_callbacks.append(callback)

    def get_recent_events(
        self,
        count: int = 50,
        level: Optional[AlertLevel] = None,
        event_type: Optional[AnomalyType] = None
    ) -> List[SecurityEvent]:
        """
        Get recent security events

        Args:
            count: Number of events to return
            level: Filter by alert level
            event_type: Filter by event type

        Returns:
            List of security events
        """
        with self.lock:
            events = list(self.events)

            # Filter
            if level:
                events = [e for e in events if e.level == level]
            if event_type:
                events = [e for e in events if e.event_type == event_type]

            # Sort by timestamp (newest first)
            events.sort(key=lambda e: e.timestamp, reverse=True)

            return events[:count]

    def get_active_alerts(self) -> List[Alert]:
        """Get unacknowledged alerts"""
        with self.lock:
            return [a for a in self.alerts if not any(e.acknowledged for e in a.events)]

    def acknowledge_alert(self, alert_id: str):
        """Acknowledge an alert"""
        with self.lock:
            for alert in self.alerts:
                if alert.alert_id == alert_id:
                    for event in alert.events:
                        event.acknowledged = True
                    logger.info(f"Alert acknowledged: {alert_id}")
                    return True
        return False

    def get_stats(self) -> Dict:
        """Get monitor statistics"""
        with self.lock:
            now = safe_datetime_now()
            cutoff = now - timedelta(minutes=self.window_minutes)

            recent_events = [e for e in self.events if e.timestamp > cutoff]

            return {
                'total_events': self.total_events,
                'total_alerts': self.total_alerts,
                'recent_events': len(recent_events),
                'active_alerts': len(self.get_active_alerts()),
                'events_by_type': {
                    event_type.value: sum(1 for e in recent_events if e.event_type == event_type)
                    for event_type in AnomalyType
                },
                'events_by_level': {
                    level.value: sum(1 for e in recent_events if e.level == level)
                    for level in AlertLevel
                },
                'window_minutes': self.window_minutes
            }

    def get_health_summary(self) -> Dict:
        """Get system security health summary"""
        with self.lock:
            now = safe_datetime_now()
            hour_ago = now - timedelta(hours=1)

            recent_events = [e for e in self.events if e.timestamp > hour_ago]
            critical_events = [e for e in recent_events if e.level in [AlertLevel.CRITICAL, AlertLevel.EMERGENCY]]

            # Determine health status
            if any(e.level == AlertLevel.EMERGENCY for e in critical_events):
                health = "CRITICAL"
            elif len(critical_events) > 5:
                health = "WARNING"
            elif len(critical_events) > 0:
                health = "NEEDS_ATTENTION"
            else:
                health = "HEALTHY"

            return {
                'health_status': health,
                'last_hour_events': len(recent_events),
                'critical_events': len(critical_events),
                'active_alerts': len(self.get_active_alerts()),
                'most_common_threat': self._get_most_common_threat(recent_events),
                'timestamp': now.isoformat()
            }

    def _get_most_common_threat(self, events: List[SecurityEvent]) -> Optional[str]:
        """Get most common threat type from events"""
        if not events:
            return None

        threat_counts = {}
        for event in events:
            threat_type = event.event_type.value
            threat_counts[threat_type] = threat_counts.get(threat_type, 0) + 1

        if threat_counts:
            return max(threat_counts, key=threat_counts.get)
        return None


# Singleton instance
_monitor_instance = None


def get_security_monitor() -> SecurityMonitor:
    """Get or create security monitor singleton"""
    global _monitor_instance
    if _monitor_instance is None:
        _monitor_instance = SecurityMonitor()
    return _monitor_instance
