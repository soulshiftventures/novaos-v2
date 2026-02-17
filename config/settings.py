"""
NovaOS V2 Configuration Settings
"""

import os
from pathlib import Path

# === PATHS ===
BASE_DIR = Path("/Users/krissanders/novaos-v2")
DATA_DIR = BASE_DIR / "data"
DB_PATH = DATA_DIR / "novaos.db"
AGENTS_DIR = BASE_DIR / "agents"
LOGS_DIR = BASE_DIR / "logs"

# Existing DDS system path
DDS_PATH = Path("/Users/krissanders/prospecting_agent")

# === API CONFIGURATION ===

# Anthropic API (Claude)
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY")

# Model selection and costs (per million tokens)
MODELS = {
    "opus": {
        "id": "claude-opus-4-5-20251101",
        "input_cost": 15.00,  # $15 per 1M input tokens
        "output_cost": 75.00,  # $75 per 1M output tokens
        "max_tokens": 200000,
        "use_case": "critical_decisions"
    },
    "sonnet": {
        "id": "claude-sonnet-4-5-20250929",
        "input_cost": 3.00,  # $3 per 1M input tokens
        "output_cost": 15.00,  # $15 per 1M output tokens
        "max_tokens": 200000,
        "use_case": "general_purpose"
    },
    "haiku": {
        "id": "claude-3-5-haiku-20241022",
        "input_cost": 0.80,  # $0.80 per 1M input tokens
        "output_cost": 4.00,  # $4 per 1M output tokens
        "max_tokens": 200000,
        "use_case": "filtering_and_simple_tasks"
    }
}

# Default model for different operations
DEFAULT_MODELS = {
    "board_agents": "sonnet",  # Board decisions
    "departments": "sonnet",  # Department management
    "execution_agents": "haiku",  # Task execution
    "council": "sonnet",  # R&D Expert Council
    "critical": "opus"  # Critical decisions only
}

# === TOKEN BUDGETS ===

# Board agent token budgets (per operation)
BOARD_AGENT_BUDGETS = {
    "ceo": 2000,  # GO/NO-GO decisions
    "cfo": 1000,  # Financial analysis
    "cmo": 1500,  # Market scanning
    "cto": 1000,  # Tech evaluation
    "coo": 500   # Status checks
}

# Department agent budgets (per operation)
DEPARTMENT_BUDGETS = {
    "sales": 1500,
    "marketing": 1500,
    "product": 2000,
    "operations": 1000,
    "research": 2000
}

# R&D Council avatar budgets (per analysis)
COUNCIL_AVATAR_BUDGET = 500  # Each avatar gets 500 tokens max

# Execution agent budgets
EXECUTION_AGENT_BUDGET = 1000  # Default for task agents

# === COST OPTIMIZATION ===

# Maximum AI costs as % of revenue
MAX_AI_COST_PERCENT = 5.0  # Target: <5%

# Alert threshold (higher than target)
ALERT_AI_COST_PERCENT = 10.0  # Alert if >10%

# Auto-optimization triggers
AUTO_OPTIMIZE_TRIGGERS = {
    "cost_percent_exceeded": ALERT_AI_COST_PERCENT,
    "negative_roi_days": 3,  # Pause agent if negative ROI for 3 days
    "monthly_budget_percent": 80  # Alert at 80% of monthly budget
}

# === CACHING ===

# Cache settings for repeated queries
CACHE_SETTINGS = {
    "enabled": True,
    "ttl_seconds": {
        "market_data": 3600,  # 1 hour
        "trend_data": 1800,   # 30 minutes
        "competitor_data": 7200,  # 2 hours
        "financial_data": 300  # 5 minutes
    }
}

# === MONITORING ===

# System health check intervals (seconds)
MONITORING_INTERVALS = {
    "system_health": 60,  # Every minute
    "cost_tracking": 300,  # Every 5 minutes
    "roi_calculation": 900,  # Every 15 minutes
    "agent_health": 300  # Every 5 minutes
}

# Alert channels
ALERT_CHANNELS = {
    "console": True,
    "file": True,
    "email": False,  # Configure SMTP if needed
    "slack": False   # Configure webhook if needed
}

# === DEPARTMENT CONFIGURATIONS ===

DEPARTMENT_CONFIGS = {
    "sales": {
        "owns": ["DDS prospecting system"],
        "metrics": ["leads_generated", "cost_per_lead", "conversion_rate"],
        "auto_deploy": True
    },
    "marketing": {
        "owns": ["content creation", "SEO", "social media"],
        "metrics": ["reach", "engagement", "cost_per_impression"],
        "auto_deploy": True
    },
    "product": {
        "owns": ["digital products", "SaaS building"],
        "metrics": ["products_launched", "revenue_per_product"],
        "auto_deploy": False
    },
    "operations": {
        "owns": ["infrastructure", "monitoring", "optimization"],
        "metrics": ["uptime", "cost_efficiency", "system_health"],
        "auto_deploy": True
    },
    "research": {
        "owns": ["R&D Expert Council", "opportunity analysis"],
        "metrics": ["opportunities_identified", "prediction_accuracy"],
        "auto_deploy": True
    }
}

# === R&D EXPERT COUNCIL ===

COUNCIL_AVATARS = {
    "thiel": {
        "name": "Thiel",
        "perspective": "Contrarian, monopoly thinking, 0-to-1",
        "key_question": "What's the contrarian truth nobody sees?",
        "focus": "Unique advantages, avoiding competition"
    },
    "musk": {
        "name": "Musk",
        "perspective": "First principles, aggressive speed",
        "key_question": "What's the physics-level truth here?",
        "focus": "Rapid execution, vertical integration"
    },
    "graham": {
        "name": "Graham",
        "perspective": "Startup fundamentals, simplicity",
        "key_question": "Do people actually want this?",
        "focus": "Product-market fit, user needs"
    },
    "taleb": {
        "name": "Taleb",
        "perspective": "Risk management, antifragility",
        "key_question": "What could destroy us? How do we benefit from volatility?",
        "focus": "Downside protection, asymmetric bets"
    }
}

# === LOGGING ===

LOG_SETTINGS = {
    "level": "INFO",
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    "file": str(LOGS_DIR / "novaos.log"),
    "max_bytes": 10485760,  # 10MB
    "backup_count": 5
}

# === MCP INTEGRATION ===

MCP_CONFIG = {
    "enabled": True,
    "server_path": Path("/Users/krissanders/novaos-memory-mcp"),
    "auto_save_decisions": True,
    "auto_save_opportunities": True,
    "auto_save_council_sessions": True
}

# === SYSTEM DEFAULTS ===

DEFAULT_AGENT_CONFIG = {
    "auto_shutdown_on_negative_roi": True,
    "report_interval_seconds": 300,  # Report every 5 minutes
    "max_retries": 3,
    "retry_delay_seconds": 5
}

# === FEATURE FLAGS ===

FEATURES = {
    "auto_optimization": True,
    "council_enabled": True,
    "dds_integration": True,
    "cost_alerts": True,
    "roi_tracking": True,
    "aggressive_caching": True,
    "batch_processing": True
}
