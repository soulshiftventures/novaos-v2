"""
NovaOS V2 Financial Targets
10X Aggressive Revenue Goals
"""

from datetime import datetime, timedelta


def safe_datetime_now():
    """Get current datetime with fallback for timestamp overflow"""
    try:
        return safe_datetime_now()
    except (OSError, OverflowError, ValueError):
        from datetime import datetime as dt
        return dt(2025, 1, 1, 0, 0, 0)


# === REVENUE TARGETS (10X AGGRESSIVE) ===

MONTHLY_TARGETS = {
    1: 5000,      # Month 1: $5,000
    2: 8000,      # Month 2: $8,000
    3: 15000,     # Month 3: $15,000
    4: 25000,     # Month 4: $25,000
    5: 35000,     # Month 5: $35,000
    6: 50000,     # Month 6: $50,000
    7: 70000,     # Month 7: $70,000
    8: 90000,     # Month 8: $90,000
    9: 120000,    # Month 9: $120,000
    10: 150000,   # Month 10: $150,000
    11: 175000,   # Month 11: $175,000
    12: 200000    # Month 12: $200,000
}

# Weekly targets (for more granular tracking)
WEEKLY_TARGETS = {
    1: 1250,   # Week 1 of Month 1
    2: 1250,
    3: 1250,
    4: 1250,   # ~$5k Month 1
}

# Daily targets (aggressive daily goals)
def get_daily_target(month: int) -> float:
    """Calculate daily target for given month"""
    monthly_target = MONTHLY_TARGETS.get(month, 200000)
    return monthly_target / 30  # Rough daily average


# === AI COST BUDGETS ===

# Maximum AI spend per month (as absolute $ and % of revenue)
MONTHLY_AI_BUDGET = {
    1: 250,     # Max $250 in AI costs (5% of $5k target)
    2: 400,     # Max $400 (5% of $8k target)
    3: 750,     # Max $750 (5% of $15k target)
    4: 1250,    # Max $1,250 (5% of $25k target)
    5: 1750,    # Max $1,750 (5% of $35k target)
    6: 2500,    # Max $2,500 (5% of $50k target)
    7: 3500,    # Max $3,500 (5% of $70k target)
    8: 4500,    # Max $4,500 (5% of $90k target)
    9: 6000,    # Max $6,000 (5% of $120k target)
    10: 7500,   # Max $7,500 (5% of $150k target)
    11: 8750,   # Max $8,750 (5% of $175k target)
    12: 10000   # Max $10,000 (5% of $200k target)
}

# Daily AI budget
def get_daily_ai_budget(month: int) -> float:
    """Calculate daily AI budget for given month"""
    monthly_budget = MONTHLY_AI_BUDGET.get(month, 10000)
    return monthly_budget / 30


# === TARGET METRICS ===

TARGET_METRICS = {
    # Cost efficiency
    "ai_cost_percent": 5.0,  # Target: AI costs <5% of revenue
    "cost_per_lead": 10.0,   # Target: $10 per lead
    "cost_per_conversion": 100.0,  # Target: $100 per sale

    # Revenue efficiency
    "revenue_per_agent": 1000.0,  # Target: $1k revenue per agent per month
    "roi_minimum": 300,  # Target: 300% ROI (3x return)

    # Operational
    "opportunities_per_week": 5,  # Target: 5 new opportunities per week
    "conversion_rate": 0.10,  # Target: 10% conversion rate
    "customer_lifetime_value": 5000,  # Target: $5k LTV

    # Agent performance
    "agent_uptime": 0.95,  # Target: 95% uptime
    "avg_response_time": 30,  # Target: <30s response time
    "success_rate": 0.80  # Target: 80% task success rate
}


# === MILESTONE TRACKING ===

MILESTONES = {
    "first_dollar": {
        "target": 1,
        "description": "First dollar earned",
        "priority": "high"
    },
    "first_1k": {
        "target": 1000,
        "description": "First $1,000 earned",
        "priority": "high"
    },
    "first_10k": {
        "target": 10000,
        "description": "First $10,000 earned",
        "priority": "high"
    },
    "cost_positive": {
        "target": "revenue > costs",
        "description": "Revenue exceeds all costs",
        "priority": "critical"
    },
    "ai_sustainable": {
        "target": "ai_costs < 5% revenue",
        "description": "AI costs sustainable at <5%",
        "priority": "critical"
    },
    "first_50k_month": {
        "target": 50000,
        "description": "First $50k month (Month 6 target)",
        "priority": "high"
    },
    "first_100k_month": {
        "target": 100000,
        "description": "First $100k month",
        "priority": "high"
    },
    "first_200k_month": {
        "target": 200000,
        "description": "First $200k month (Year 1 target)",
        "priority": "critical"
    }
}


# === DEPARTMENT REVENUE TARGETS ===

# Expected revenue contribution by department (%)
DEPARTMENT_REVENUE_MIX = {
    "sales": 0.50,      # 50% - DDS prospecting
    "marketing": 0.20,  # 20% - Content/SEO
    "product": 0.25,    # 25% - Digital products
    "operations": 0.00, # 0% - Cost center
    "research": 0.05    # 5% - Consulting/analysis
}


def get_department_target(month: int, department: str) -> float:
    """Calculate department revenue target for given month"""
    monthly_target = MONTHLY_TARGETS.get(month, 200000)
    dept_mix = DEPARTMENT_REVENUE_MIX.get(department, 0.0)
    return monthly_target * dept_mix


# === ALERT THRESHOLDS ===

ALERT_THRESHOLDS = {
    "behind_target": 0.80,  # Alert if <80% of target
    "ahead_target": 1.20,   # Celebrate if >120% of target
    "cost_spike": 2.0,      # Alert if costs 2x expected
    "negative_roi": -0.10,  # Alert if ROI < -10%
    "burn_rate_high": 0.15  # Alert if burning >15% revenue on AI
}


# === FINANCIAL HELPERS ===

def get_current_month() -> int:
    """Get current month number (1-12) since NovaOS start"""
    # TODO: Set actual start date
    # For now, return current calendar month
    return safe_datetime_now().month


def get_current_target() -> dict:
    """Get current revenue and cost targets"""
    month = get_current_month()
    return {
        "month": month,
        "revenue_target": MONTHLY_TARGETS.get(month, 200000),
        "ai_budget": MONTHLY_AI_BUDGET.get(month, 10000),
        "daily_revenue_target": get_daily_target(month),
        "daily_ai_budget": get_daily_ai_budget(month)
    }


def calculate_required_daily_revenue(days_remaining: int, revenue_so_far: float, month: int) -> float:
    """Calculate required daily revenue to hit monthly target"""
    monthly_target = MONTHLY_TARGETS.get(month, 200000)
    remaining_revenue = monthly_target - revenue_so_far

    if days_remaining <= 0:
        return 0.0

    return remaining_revenue / days_remaining


def is_on_track(current_revenue: float, month: int, day_of_month: int) -> dict:
    """Check if revenue is on track for monthly target"""
    monthly_target = MONTHLY_TARGETS.get(month, 200000)
    expected_revenue = (monthly_target / 30) * day_of_month

    percent_of_expected = (current_revenue / expected_revenue * 100) if expected_revenue > 0 else 0

    return {
        "current_revenue": current_revenue,
        "expected_revenue": expected_revenue,
        "monthly_target": monthly_target,
        "percent_of_expected": percent_of_expected,
        "on_track": percent_of_expected >= 100,
        "status": "ahead" if percent_of_expected >= 120 else "on_track" if percent_of_expected >= 80 else "behind"
    }


def calculate_roi(revenue: float, costs: float) -> float:
    """Calculate ROI percentage"""
    if costs == 0:
        return 0.0 if revenue == 0 else float('inf')

    return ((revenue - costs) / costs) * 100
