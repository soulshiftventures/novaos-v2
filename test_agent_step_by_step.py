#!/usr/bin/env python3
"""Test agent initialization step by step to find the timestamp overflow"""

import sys
import traceback

print("="*60)
print("STEP-BY-STEP AGENT INITIALIZATION TEST")
print("="*60)

try:
    print("\n[1] Importing datetime...")
    from datetime import datetime
    print(f"    ✓ datetime.now() = {datetime.now()}")

    print("\n[2] Importing ContentArbitrage...")
    from revenue_agents import ContentArbitrage
    print("    ✓ Import successful")

    print("\n[3] Creating ContentArbitrage instance...")
    agent = ContentArbitrage(worker_id="test", platform="upwork", run_interval=300)
    print("    ✓ Instance created")

    print("\n[4] Calling agent.start()...")
    agent.start()
    print("    ✓ Agent started")

    print("\n[5] Sleeping for 5 seconds...")
    import time
    time.sleep(5)
    print("    ✓ Still running!")

    print("\n" + "="*60)
    print("SUCCESS! Agent is running without errors")
    print("="*60)

    # Keep running
    time.sleep(float('inf'))

except Exception as e:
    print(f"\n✗ ERROR at current step:")
    print(f"  {type(e).__name__}: {e}")
    traceback.print_exc()
    sys.exit(1)
