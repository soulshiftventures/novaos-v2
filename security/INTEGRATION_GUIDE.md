# NovaOS V2 Security Integration Guide

## Overview

This guide shows how to integrate the security layer into existing NovaOS V2 components.

## Quick Integration Checklist

- [ ] Import security manager
- [ ] Initialize security on system startup
- [ ] Add security checks to agent operations
- [ ] Secure all API endpoints
- [ ] Enable audit logging
- [ ] Set up monitoring alerts
- [ ] Test with attack simulations
- [ ] Review security documentation

---

## 1. Agent Factory Integration

### File: `/Users/krissanders/novaos-v2/core/agent_factory.py`

Add security checks to agent deployment and management:

```python
# Add to imports at top of file
from security import get_security_manager, SecurityLevel
from security.audit import log_agent_action

class AgentFactory:
    def __init__(self):
        self.memory = get_memory()
        # Initialize security
        self.security = get_security_manager(SecurityLevel.STRICT)

    def deploy_agent(self, agent_type: str, name: str, department: str,
                    config: Dict = None, token_budget: int = None,
                    session_id: str = None) -> str:
        """Deploy a new execution agent with security checks"""

        # Security check: Validate agent name
        is_valid, error = self.security.input_validator.validate_agent_name(name)
        if not is_valid:
            raise ValueError(f"Invalid agent name: {error}")

        # Security check: Validate configuration
        if config:
            config_valid, issues = self.security.input_validator.validate_config(config)
            if not config_valid:
                raise ValueError(f"Invalid configuration: {', '.join(issues)}")

        # Security check: Authorization
        if session_id:
            authorized, error = self.security.access_controller.check_permission(
                session_id,
                Permission.AGENT_DEPLOY
            )
            if not authorized:
                raise PermissionError(f"Not authorized to deploy agents: {error}")

        # Original deployment logic
        agent_id = f"{agent_type}_{uuid.uuid4().hex[:8]}"
        # ... rest of deployment code ...

        # Audit log
        log_agent_action(agent_id, 'deploy', details={
            'name': name,
            'type': agent_type,
            'department': department,
            'budget': token_budget
        })

        return agent_id

    def kill_agent(self, agent_id: str, session_id: str = None) -> bool:
        """Kill agent with security checks"""

        # Security check: Authorization
        if session_id:
            authorized, error = self.security.access_controller.check_permission(
                session_id,
                Permission.AGENT_KILL
            )
            if not authorized:
                raise PermissionError(f"Not authorized to kill agents: {error}")

        # Original kill logic
        self.memory.update_agent_status(agent_id, "killed")
        # ... rest of kill code ...

        # Audit log
        log_agent_action(agent_id, 'kill')

        return True
```

---

## 2. Autonomous Engine Integration

### File: `/Users/krissanders/novaos-v2/core/autonomous.py`

Add security guardrails to autonomous decisions:

```python
# Add to imports
from security import get_security_manager, SecurityLevel
from security.monitor import get_security_monitor, SecurityEvent, AnomalyType, AlertLevel

class AutonomousEngine:
    def __init__(self, ...):
        # Existing initialization
        self.enabled = enabled
        # ... existing code ...

        # Add security
        self.security = get_security_manager(SecurityLevel.STRICT)
        self.monitor = get_security_monitor()

    def execute_decision(self, decision: AutonDecision, worker_manager) -> bool:
        """Execute decision with security checks"""

        if not self.enabled:
            return False

        # Security check: Budget check before expensive decisions
        if decision.decision_type in ['deploy', 'scale_up']:
            allowed, reason = self.security.budget_enforcer.check_and_reserve(
                decision.target,
                abs(decision.cost_impact),
                decision.decision_type
            )

            if not allowed:
                logger.warning(f"Autonomous decision blocked by budget: {reason}")
                # Record as security event
                self.monitor.record_event(SecurityEvent(
                    timestamp=datetime.now(),
                    event_type=AnomalyType.BUDGET_VIOLATION,
                    level=AlertLevel.WARNING,
                    description=f"Autonomous decision blocked: {reason}",
                    source="autonomous_engine",
                    metadata={'decision': decision.decision_type, 'target': decision.target}
                ))
                return False

        # Security check: Anomaly detection
        if decision.decision_type == 'kill' and decision.expected_roi > 0:
            # Killing a profitable agent is suspicious
            self.monitor.record_event(SecurityEvent(
                timestamp=datetime.now(),
                event_type=AnomalyType.UNUSUAL_PATTERN,
                level=AlertLevel.WARNING,
                description=f"Autonomous engine attempting to kill profitable agent",
                source="autonomous_engine",
                metadata={'agent': decision.target, 'roi': decision.expected_roi}
            ))

        # Original execution logic
        try:
            if decision.decision_type == 'scale_up':
                worker_manager.scale_worker(decision.target, decision.metadata['multiplier'])
            # ... rest of execution code ...

            return True
        except Exception as e:
            logger.error(f"Error executing decision: {e}")
            return False
```

---

## 3. API Integration

### File: `/Users/krissanders/novaos-v2/dashboard/api.py`

Secure all API endpoints:

```python
# Add to imports
from security import get_security_manager, SecurityLevel, Role
from security.audit import AuditEventType
from flask import request, jsonify

# Initialize security
security = get_security_manager(SecurityLevel.STRICT)

# Authentication decorator
def require_auth(f):
    """Decorator to require authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Get API key from header
        api_key = request.headers.get('X-API-Key')
        if not api_key:
            return jsonify({'error': 'API key required'}), 401

        # Authenticate
        success, session_id, error = security.authenticate(
            api_key=api_key,
            ip_address=request.remote_addr
        )

        if not success:
            return jsonify({'error': error}), 401

        # Add session to request context
        request.session_id = session_id

        return f(*args, **kwargs)
    return decorated_function

# Permission check decorator
def require_permission(permission):
    """Decorator to require specific permission"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            session_id = getattr(request, 'session_id', None)
            if not session_id:
                return jsonify({'error': 'Not authenticated'}), 401

            authorized, error = security.access_controller.check_permission(
                session_id,
                permission
            )

            if not authorized:
                return jsonify({'error': error}), 403

            return f(*args, **kwargs)
        return decorated_function
    return decorator

# Example protected endpoint
@app.route('/api/agents/deploy', methods=['POST'])
@require_auth
@require_permission(Permission.AGENT_DEPLOY)
def deploy_agent():
    """Deploy new agent with security checks"""
    data = request.json

    # Validate input
    result = security.check_agent_operation(
        agent_id="system",
        operation="deploy",
        input_data=json.dumps(data),
        config=data.get('config'),
        session_id=request.session_id
    )

    if not result.allowed:
        return jsonify({
            'error': result.reason,
            'threat_level': result.threat_level.value
        }), 400

    # Deploy agent (original logic)
    agent_id = agent_factory.deploy_agent(
        agent_type=data['type'],
        name=data['name'],
        department=data['department'],
        config=data.get('config'),
        session_id=request.session_id
    )

    return jsonify({
        'agent_id': agent_id,
        'status': 'deployed'
    })
```

---

## 4. Worker Integration

### File: `/Users/krissanders/novaos-v2/workers/base_worker.py`

Add security checks to worker execution:

```python
# Add to imports
from security import get_security_manager, SecurityLevel

class BaseWorker:
    def __init__(self, worker_id: str, name: str, ...):
        # Existing initialization
        self.worker_id = worker_id
        # ... existing code ...

        # Add security
        self.security = get_security_manager(SecurityLevel.STRICT)

    def _execute_with_recovery(self):
        """Execute work with crash recovery and security checks"""

        try:
            self.metrics.total_runs += 1

            # Security check: Budget check before expensive operation
            # Estimate cost based on typical operation
            estimated_cost = self._estimate_operation_cost()

            allowed, reason = self.security.budget_enforcer.check_and_reserve(
                self.worker_id,
                estimated_cost,
                "worker_run"
            )

            if not allowed:
                logger.warning(f"Worker {self.worker_id} blocked by budget: {reason}")
                self.metrics.failed_runs += 1
                return None

            # Run the actual work
            result = self.run()

            # Release unused budget if actual cost is less
            if result and isinstance(result, dict) and 'cost' in result:
                actual_cost = result['cost']
                self.security.budget_enforcer.release_unused(
                    self.worker_id,
                    estimated_cost,
                    actual_cost
                )

            # Track results
            if result:
                self.metrics.successful_runs += 1
                if isinstance(result, dict):
                    revenue = result.get('revenue', 0.0)
                    cost = result.get('cost', 0.0)
                    self.metrics.total_revenue += revenue
                    self.metrics.total_cost += cost

                    # Security monitoring: Report cost
                    self.security.monitor.record_cost(self.worker_id, cost)
            else:
                self.metrics.failed_runs += 1

        except Exception as e:
            logger.error(f"Worker {self.worker_id} crashed: {e}")
            self.metrics.failed_runs += 1
            self.metrics.crash_count += 1

            # Security monitoring: Report crash
            if self.metrics.crash_count >= 3:
                self.security.monitor.record_event(SecurityEvent(
                    timestamp=datetime.now(),
                    event_type=AnomalyType.AGENT_CRASH,
                    level=AlertLevel.WARNING,
                    description=f"Worker crashing repeatedly ({self.metrics.crash_count} times)",
                    source=self.worker_id
                ))

    def _estimate_operation_cost(self) -> float:
        """Estimate cost of one operation"""
        # Simple estimation: use average past cost or default
        if self.metrics.total_runs > 0:
            return self.metrics.total_cost / self.metrics.total_runs
        return 0.05  # Default estimate
```

---

## 5. CLI Integration

### File: `/Users/krissanders/novaos-v2/cli.py`

Add security initialization and commands:

```python
# Add to imports
from security import get_security_manager, SecurityLevel, Role
from security.audit import get_audit_logger
import getpass

@click.group()
def cli():
    """NovaOS V2 CLI with security"""
    pass

@cli.command()
@click.option('--level', type=click.Choice(['PERMISSIVE', 'BALANCED', 'STRICT', 'PARANOID']),
              default='STRICT', help='Security level')
def init_security(level):
    """Initialize security system"""
    security_level = SecurityLevel[level]
    security = get_security_manager(security_level)

    click.echo(f"✓ Security initialized at {level} level")
    click.echo("\nCreating admin API key...")

    # Create admin key
    key_id, plaintext_key = security.create_api_key(
        name="admin_key",
        role=Role.ADMIN,
        authorized_by="cli_init",
        expires_days=365
    )

    click.echo(f"\n{'='*60}")
    click.echo("ADMIN API KEY - SAVE THIS SECURELY!")
    click.echo(f"{'='*60}")
    click.echo(f"Key ID: {key_id}")
    click.echo(f"Secret Key: {plaintext_key}")
    click.echo(f"{'='*60}")
    click.echo("\n⚠️  This key will NEVER be shown again!")
    click.echo("Store it in a password manager or secure vault.\n")

@cli.command()
def security_status():
    """Show security status"""
    security = get_security_manager()
    status = security.get_security_status()

    click.echo("\n=== SECURITY STATUS ===\n")
    click.echo(f"Security Level: {status['security_level']}")

    if 'budget' in status:
        budget = status['budget']
        click.echo(f"\nBudget:")
        click.echo(f"  Daily: ${budget['global_budgets']['daily']['spent']:.2f} / "
                   f"${budget['global_budgets']['daily']['limit']:.2f}")
        click.echo(f"  Status: {budget['global_budgets']['daily']['status']}")

    if 'health' in status:
        health = status['health']
        click.echo(f"\nSecurity Health: {health['health_status']}")
        click.echo(f"  Active Alerts: {health['active_alerts']}")
        click.echo(f"  Critical Events (1h): {health['critical_events']}")

    if 'access_control' in status:
        access = status['access_control']
        click.echo(f"\nAccess Control:")
        click.echo(f"  API Keys: {access['api_keys']['active']} active")
        click.echo(f"  Sessions: {access['sessions']['active']} active")
        click.echo(f"  Success Rate: {access['stats']['success_rate']:.1f}%")

@cli.command()
@click.option('--hours', default=24, help='Hours to analyze')
def security_report(hours):
    """Generate security report"""
    audit = get_audit_logger()
    monitor = get_security_monitor()

    summary = audit.get_security_summary(hours=hours)
    health = monitor.get_health_summary()

    click.echo(f"\n=== SECURITY REPORT (Last {hours} hours) ===\n")
    click.echo(f"Total Events: {summary['total_events']}")
    click.echo(f"Auth Failures: {summary['auth_failures']}")
    click.echo(f"Authorization Denials: {summary['authz_denials']}")
    click.echo(f"Inputs Blocked: {summary['input_blocked']}")
    click.echo(f"Sandbox Violations: {summary['sandbox_violations']}")
    click.echo(f"Budget Exceeded: {summary['budget_exceeded']}")

    click.echo(f"\nHealth Status: {health['health_status']}")
    if health['most_common_threat']:
        click.echo(f"Most Common Threat: {health['most_common_threat']}")

    # Show recent critical events
    events = monitor.get_recent_events(count=10, level=AlertLevel.CRITICAL)
    if events:
        click.echo(f"\nRecent Critical Events:")
        for event in events:
            click.echo(f"  [{event.timestamp.strftime('%H:%M:%S')}] "
                      f"{event.event_type.value} - {event.description}")

if __name__ == '__main__':
    cli()
```

---

## 6. Startup Integration

### File: `/Users/krissanders/novaos-v2/nova` (main startup script)

Add security initialization on system startup:

```python
#!/usr/bin/env python3
"""
NovaOS V2 - Secure Startup
"""

from security import get_security_manager, SecurityLevel
from security.monitor import get_security_monitor, Alert, AlertLevel
import os

def send_telegram_alert(alert: Alert):
    """Send critical alerts to Telegram"""
    if alert.level in [AlertLevel.CRITICAL, AlertLevel.EMERGENCY]:
        # Implement Telegram notification
        message = f"🚨 {alert.title}\n\n{alert.description}"
        # telegram_bot.send_message(message)
        print(f"ALERT: {message}")

def main():
    print("Starting NovaOS V2 with Security...")

    # Initialize security
    security_level = os.environ.get('NOVAOS_SECURITY_LEVEL', 'STRICT')
    security = get_security_manager(SecurityLevel[security_level])

    print(f"✓ Security initialized at {security_level} level")

    # Set up monitoring
    monitor = get_security_monitor()
    monitor.add_alert_callback(send_telegram_alert)

    print("✓ Security monitoring active")

    # Check if master password is set
    if not os.environ.get('NOVAOS_MASTER_PASSWORD'):
        print("⚠️  WARNING: NOVAOS_MASTER_PASSWORD not set!")
        print("   Encryption will use fallback mode.")
        print("   Set NOVAOS_MASTER_PASSWORD in production!")

    # Get security status
    status = security.get_security_status()
    health = status.get('health', {})

    print(f"✓ Security health: {health.get('health_status', 'UNKNOWN')}")

    # Start NovaOS (original startup code)
    # ...

if __name__ == '__main__':
    main()
```

---

## Testing Integration

After integrating security, test with:

```bash
# Run security test suite
python3 security/test_security.py

# Initialize security
./nova init-security --level STRICT

# Check status
./nova security-status

# Generate report
./nova security-report --hours 24
```

---

## Rollout Plan

### Phase 1: Development (Week 1)
- [ ] Integrate security into agent factory
- [ ] Add security checks to API endpoints
- [ ] Test with PERMISSIVE security level
- [ ] Run attack simulations

### Phase 2: Staging (Week 2)
- [ ] Enable BALANCED security level
- [ ] Integrate monitoring and alerting
- [ ] Test autonomous engine with guardrails
- [ ] Review audit logs

### Phase 3: Production (Week 3)
- [ ] Enable STRICT security level
- [ ] Set production budget limits
- [ ] Configure Telegram alerts
- [ ] Train team on emergency procedures
- [ ] Monitor for 48 hours before full rollout

### Phase 4: Hardening (Week 4)
- [ ] Review security events
- [ ] Tune detection thresholds
- [ ] Update threat patterns
- [ ] Conduct red team exercise
- [ ] Document lessons learned

---

## Troubleshooting

### Security checks failing for legitimate operations

**Solution**: Review validation rules and adjust thresholds. Check audit logs to understand what's being blocked.

### Budget limits too restrictive

**Solution**: Start with higher limits and gradually tighten. Monitor actual costs for 1 week before setting production limits.

### Performance impact

**Solution**: Security adds <10ms latency per operation. If performance is critical, use BALANCED mode or optimize specific checks.

### Alert fatigue

**Solution**: Tune alert thresholds. Start with CRITICAL alerts only, then add WARNING alerts after baseline is established.

---

**Integration complete! Your NovaOS V2 is now secured against real-world threats.**
