#!/usr/bin/env python3
"""
Debug script to identify where timestamp overflow occurs during import
"""

import sys
import traceback

print("=" * 60)
print("IMPORT DEBUG - Testing each module step by step")
print("=" * 60)

modules_to_test = [
    ("datetime", "from datetime import datetime"),
    ("workers.base_worker", "from workers.base_worker import BaseWorker"),
    ("security.budget_enforcer", "from security.budget_enforcer import BudgetEnforcer"),
    ("security.access_control", "from security.access_control import AccessController"),
    ("security.monitor", "from security.monitor import SecurityMonitor"),
    ("security.audit", "from security.audit import AuditLogger"),
    ("security", "from security import get_security_manager"),
    ("revenue_agents.content_arbitrage", "from revenue_agents.content_arbitrage import ContentArbitrage"),
]

for name, import_stmt in modules_to_test:
    try:
        print(f"\n[TESTING] {name}")
        print(f"  Import: {import_stmt}")
        exec(import_stmt)
        print(f"  ✓ SUCCESS")
    except Exception as e:
        print(f"  ✗ FAILED: {type(e).__name__}: {e}")
        traceback.print_exc()
        print("\n" + "=" * 60)
        print(f"ERROR FOUND IN: {name}")
        print("=" * 60)
        sys.exit(1)

print("\n" + "=" * 60)
print("ALL IMPORTS SUCCESSFUL!")
print("=" * 60)
