"""
Budget Enforcer - Cost Control and Prevention

Enforces:
- Hard budget limits (daily, per-agent, per-operation)
- Rate limiting on API calls
- Cost prediction before execution
- Emergency shutdown triggers
- Multi-factor approval for high-cost operations

Prevents budget manipulation and runaway costs
"""

import logging
import threading
from typing import Dict, Optional, Tuple, List
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import time

logger = logging.getLogger(__name__)


class BudgetStatus(Enum):
    """Budget status states"""
    HEALTHY = "healthy"
    WARNING = "warning"
    CRITICAL = "critical"
    EXCEEDED = "exceeded"
    EMERGENCY_STOP = "emergency_stop"


@dataclass
class BudgetLimit:
    """Budget limit definition"""
    name: str
    limit: float  # Dollar amount
    period: str  # 'hourly', 'daily', 'weekly', 'monthly', 'operation'
    current_spend: float = 0.0
    period_start: datetime = field(default_factory=datetime.now)
    enforced: bool = True  # Hard limit vs soft limit

    def reset_if_needed(self):
        """Reset budget if period has elapsed"""
        now = datetime.now()
        should_reset = False

        if self.period == 'hourly' and (now - self.period_start) > timedelta(hours=1):
            should_reset = True
        elif self.period == 'daily' and (now - self.period_start) > timedelta(days=1):
            should_reset = True
        elif self.period == 'weekly' and (now - self.period_start) > timedelta(weeks=1):
            should_reset = True
        elif self.period == 'monthly' and (now - self.period_start) > timedelta(days=30):
            should_reset = True

        if should_reset:
            logger.info(f"Resetting budget '{self.name}' (spent: ${self.current_spend:.2f})")
            self.current_spend = 0.0
            self.period_start = now

    @property
    def remaining(self) -> float:
        """Get remaining budget"""
        return max(0, self.limit - self.current_spend)

    @property
    def percent_used(self) -> float:
        """Get percentage of budget used"""
        if self.limit == 0:
            return 100.0
        return (self.current_spend / self.limit) * 100

    @property
    def status(self) -> BudgetStatus:
        """Get budget status"""
        pct = self.percent_used
        if pct >= 100:
            return BudgetStatus.EXCEEDED
        elif pct >= 90:
            return BudgetStatus.CRITICAL
        elif pct >= 75:
            return BudgetStatus.WARNING
        else:
            return BudgetStatus.HEALTHY


@dataclass
class CostPrediction:
    """Cost prediction for an operation"""
    estimated_cost: float
    confidence: float  # 0.0 - 1.0
    token_estimate: int
    model_used: str
    factors: Dict[str, any]


class RateLimiter:
    """Token bucket rate limiter for API calls"""

    def __init__(self, calls_per_minute: int = 60, burst_size: int = 10):
        """
        Initialize rate limiter

        Args:
            calls_per_minute: Sustained rate limit
            burst_size: Maximum burst size
        """
        self.calls_per_minute = calls_per_minute
        self.burst_size = burst_size
        self.tokens = burst_size
        self.last_update = time.time()
        self.lock = threading.Lock()

        self.refill_rate = calls_per_minute / 60.0  # Tokens per second

    def acquire(self, timeout: float = 10.0) -> bool:
        """
        Acquire a token (blocking with timeout)

        Args:
            timeout: Maximum wait time in seconds

        Returns:
            True if token acquired, False if timeout
        """
        deadline = time.time() + timeout

        while time.time() < deadline:
            with self.lock:
                now = time.time()
                elapsed = now - self.last_update

                # Refill tokens based on elapsed time
                self.tokens = min(
                    self.burst_size,
                    self.tokens + (elapsed * self.refill_rate)
                )
                self.last_update = now

                # Check if we have tokens
                if self.tokens >= 1.0:
                    self.tokens -= 1.0
                    return True

            # Wait a bit before retry
            time.sleep(0.1)

        return False

    def try_acquire(self) -> bool:
        """Try to acquire without blocking"""
        return self.acquire(timeout=0.0)


class BudgetEnforcer:
    """
    Enforce budget limits and prevent runaway costs

    Features:
    - Multiple budget limits (daily, hourly, per-agent, etc.)
    - Rate limiting
    - Cost prediction
    - Emergency shutdown
    - Approval workflows for high-cost operations
    """

    def __init__(
        self,
        global_daily_limit: float = 100.0,
        global_hourly_limit: float = 20.0,
        per_agent_daily_limit: float = 10.0,
        per_operation_limit: float = 30.0,
        high_cost_threshold: float = 5.0,  # Requires approval
        emergency_stop_threshold: float = 150.0,  # Emergency stop
        api_calls_per_minute: int = 60
    ):
        """
        Initialize budget enforcer

        Args:
            global_daily_limit: Maximum daily spend across all agents
            global_hourly_limit: Maximum hourly spend
            per_agent_daily_limit: Maximum daily spend per agent
            per_operation_limit: Maximum cost per operation
            high_cost_threshold: Operations above this require approval
            emergency_stop_threshold: Trigger emergency stop
            api_calls_per_minute: Rate limit for API calls
        """
        self.global_limits = {
            'daily': BudgetLimit('global_daily', global_daily_limit, 'daily'),
            'hourly': BudgetLimit('global_hourly', global_hourly_limit, 'hourly')
        }

        self.agent_limits: Dict[str, Dict[str, BudgetLimit]] = {}
        self.per_agent_daily_limit = per_agent_daily_limit
        self.per_operation_limit = per_operation_limit
        self.high_cost_threshold = high_cost_threshold
        self.emergency_stop_threshold = emergency_stop_threshold

        # Rate limiter
        self.rate_limiter = RateLimiter(api_calls_per_minute)

        # Emergency stop flag
        self.emergency_stop_active = False
        self.emergency_stop_reason: Optional[str] = None

        # Approval queue
        self.pending_approvals: List[Dict] = []

        # Stats
        self.total_operations = 0
        self.total_cost = 0.0
        self.blocked_operations = 0
        self.blocked_cost_saved = 0.0

        self.lock = threading.Lock()

        logger.info(
            f"BudgetEnforcer initialized "
            f"(daily=${global_daily_limit}, hourly=${global_hourly_limit})"
        )

    def check_and_reserve(
        self,
        agent_id: str,
        estimated_cost: float,
        operation: str = "api_call"
    ) -> Tuple[bool, Optional[str]]:
        """
        Check if operation is allowed and reserve budget

        Args:
            agent_id: Agent making the request
            estimated_cost: Estimated cost of operation
            operation: Operation description

        Returns:
            Tuple of (allowed, reason_if_blocked)
        """
        with self.lock:
            # Check emergency stop
            if self.emergency_stop_active:
                self.blocked_operations += 1
                self.blocked_cost_saved += estimated_cost
                return False, f"EMERGENCY STOP ACTIVE: {self.emergency_stop_reason}"

            # Reset budgets if periods elapsed
            for limit in self.global_limits.values():
                limit.reset_if_needed()

            if agent_id in self.agent_limits:
                for limit in self.agent_limits[agent_id].values():
                    limit.reset_if_needed()

            # Check per-operation limit
            if estimated_cost > self.per_operation_limit:
                logger.warning(
                    f"Operation cost ${estimated_cost:.4f} exceeds per-op limit "
                    f"${self.per_operation_limit:.2f}"
                )
                self.blocked_operations += 1
                self.blocked_cost_saved += estimated_cost
                return False, f"Exceeds per-operation limit (${self.per_operation_limit:.2f})"

            # Check global limits
            for limit_name, limit in self.global_limits.items():
                if limit.enforced and (limit.current_spend + estimated_cost) > limit.limit:
                    logger.warning(
                        f"Operation would exceed {limit_name} limit "
                        f"(${limit.current_spend:.2f} + ${estimated_cost:.4f} > ${limit.limit:.2f})"
                    )
                    self.blocked_operations += 1
                    self.blocked_cost_saved += estimated_cost
                    return False, f"Exceeds {limit_name} budget limit"

            # Check per-agent limits
            if agent_id not in self.agent_limits:
                self.agent_limits[agent_id] = {
                    'daily': BudgetLimit(
                        f'{agent_id}_daily',
                        self.per_agent_daily_limit,
                        'daily'
                    )
                }

            agent_limit = self.agent_limits[agent_id]['daily']
            if agent_limit.enforced and (agent_limit.current_spend + estimated_cost) > agent_limit.limit:
                logger.warning(
                    f"Agent {agent_id} would exceed daily limit "
                    f"(${agent_limit.current_spend:.2f} + ${estimated_cost:.4f} > ${agent_limit.limit:.2f})"
                )
                self.blocked_operations += 1
                self.blocked_cost_saved += estimated_cost
                return False, f"Agent exceeds daily budget limit"

            # Check if approaching emergency stop threshold
            new_daily_total = self.global_limits['daily'].current_spend + estimated_cost
            if new_daily_total >= self.emergency_stop_threshold:
                logger.critical(
                    f"EMERGENCY STOP TRIGGERED: Daily spend ${new_daily_total:.2f} "
                    f">= ${self.emergency_stop_threshold:.2f}"
                )
                self.trigger_emergency_stop(
                    f"Daily spend ${new_daily_total:.2f} exceeded emergency threshold "
                    f"${self.emergency_stop_threshold:.2f}"
                )
                self.blocked_operations += 1
                self.blocked_cost_saved += estimated_cost
                return False, "EMERGENCY STOP: Budget threshold exceeded"

            # Reserve the budget
            for limit in self.global_limits.values():
                limit.current_spend += estimated_cost

            agent_limit.current_spend += estimated_cost

            self.total_operations += 1
            self.total_cost += estimated_cost

            # Log warnings if approaching limits
            for limit_name, limit in self.global_limits.items():
                if limit.status in [BudgetStatus.WARNING, BudgetStatus.CRITICAL]:
                    logger.warning(
                        f"{limit_name} budget at {limit.percent_used:.1f}% "
                        f"(${limit.current_spend:.2f} / ${limit.limit:.2f})"
                    )

            return True, None

    def release_unused(self, agent_id: str, reserved_cost: float, actual_cost: float):
        """
        Release unused reserved budget

        Args:
            agent_id: Agent that made the request
            reserved_cost: Amount that was reserved
            actual_cost: Actual amount used
        """
        if actual_cost >= reserved_cost:
            return  # Used more than or equal to reserved

        refund = reserved_cost - actual_cost

        with self.lock:
            # Refund to global limits
            for limit in self.global_limits.values():
                limit.current_spend -= refund

            # Refund to agent limit
            if agent_id in self.agent_limits:
                agent_limit = self.agent_limits[agent_id]['daily']
                agent_limit.current_spend -= refund

            self.total_cost -= refund

            logger.debug(f"Released ${refund:.4f} unused budget for {agent_id}")

    def predict_cost(
        self,
        input_tokens: int,
        output_tokens: int,
        model: str
    ) -> CostPrediction:
        """
        Predict cost of an operation

        Args:
            input_tokens: Estimated input tokens
            output_tokens: Estimated output tokens
            model: Model to use

        Returns:
            Cost prediction
        """
        # Model costs (per million tokens)
        MODEL_COSTS = {
            "claude-opus-4-5-20251101": {"input": 15.00, "output": 75.00},
            "claude-sonnet-4-5-20250929": {"input": 3.00, "output": 15.00},
            "claude-3-5-haiku-20241022": {"input": 0.80, "output": 4.00},
        }

        if model not in MODEL_COSTS:
            model = "claude-sonnet-4-5-20250929"  # Default

        costs = MODEL_COSTS[model]

        input_cost = (input_tokens / 1_000_000) * costs['input']
        output_cost = (output_tokens / 1_000_000) * costs['output']
        total_cost = input_cost + output_cost

        # Add 10% buffer for uncertainty
        estimated_cost = total_cost * 1.1

        return CostPrediction(
            estimated_cost=estimated_cost,
            confidence=0.9,  # 90% confidence with buffer
            token_estimate=input_tokens + output_tokens,
            model_used=model,
            factors={
                'input_tokens': input_tokens,
                'output_tokens': output_tokens,
                'input_cost': input_cost,
                'output_cost': output_cost
            }
        )

    def rate_limit_check(self, timeout: float = 10.0) -> bool:
        """
        Check rate limit (blocks until token available)

        Args:
            timeout: Maximum wait time

        Returns:
            True if allowed, False if rate limit exceeded
        """
        return self.rate_limiter.acquire(timeout)

    def trigger_emergency_stop(self, reason: str):
        """
        Trigger emergency stop - blocks ALL operations

        Args:
            reason: Reason for emergency stop
        """
        with self.lock:
            self.emergency_stop_active = True
            self.emergency_stop_reason = reason
            logger.critical(f"EMERGENCY STOP ACTIVATED: {reason}")

    def clear_emergency_stop(self, authorized_by: str):
        """
        Clear emergency stop (requires authorization)

        Args:
            authorized_by: Who authorized the clear
        """
        with self.lock:
            if self.emergency_stop_active:
                logger.info(f"Emergency stop cleared by {authorized_by}")
                self.emergency_stop_active = False
                self.emergency_stop_reason = None

    def requires_approval(self, estimated_cost: float) -> bool:
        """Check if operation requires manual approval"""
        return estimated_cost > self.high_cost_threshold

    def request_approval(
        self,
        agent_id: str,
        operation: str,
        estimated_cost: float,
        details: Dict
    ) -> str:
        """
        Request approval for high-cost operation

        Args:
            agent_id: Agent requesting approval
            operation: Operation description
            estimated_cost: Estimated cost
            details: Additional details

        Returns:
            Approval request ID
        """
        approval_id = f"approval_{int(time.time())}_{agent_id}"

        request = {
            'id': approval_id,
            'agent_id': agent_id,
            'operation': operation,
            'estimated_cost': estimated_cost,
            'details': details,
            'requested_at': datetime.now(),
            'status': 'pending'
        }

        with self.lock:
            self.pending_approvals.append(request)

        logger.info(
            f"Approval requested for {agent_id}: {operation} "
            f"(cost: ${estimated_cost:.2f})"
        )

        return approval_id

    def get_status(self) -> Dict:
        """Get budget status"""
        with self.lock:
            return {
                'emergency_stop': {
                    'active': self.emergency_stop_active,
                    'reason': self.emergency_stop_reason
                },
                'global_budgets': {
                    name: {
                        'limit': limit.limit,
                        'spent': limit.current_spend,
                        'remaining': limit.remaining,
                        'percent_used': limit.percent_used,
                        'status': limit.status.value
                    }
                    for name, limit in self.global_limits.items()
                },
                'stats': {
                    'total_operations': self.total_operations,
                    'total_cost': self.total_cost,
                    'blocked_operations': self.blocked_operations,
                    'blocked_cost_saved': self.blocked_cost_saved
                },
                'rate_limit': {
                    'calls_per_minute': self.rate_limiter.calls_per_minute,
                    'tokens_available': self.rate_limiter.tokens
                },
                'pending_approvals': len(self.pending_approvals)
            }


# Singleton instance
_budget_enforcer_instance = None


def get_budget_enforcer() -> BudgetEnforcer:
    """Get or create budget enforcer singleton"""
    global _budget_enforcer_instance
    if _budget_enforcer_instance is None:
        _budget_enforcer_instance = BudgetEnforcer()
    return _budget_enforcer_instance
