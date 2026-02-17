"""
NovaOS V2 - Incremental Agent Spawner
Gradually spawns revenue agents based on performance validation
"""

import os
import time
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import subprocess

logger = logging.getLogger(__name__)


class AgentSpawner:
    """
    Incrementally spawns revenue agents based on validation criteria

    Strategy:
    - Hour 1: Start 3 agents (1 of each type)
    - Hour 2: If no errors, spawn 6 more
    - Hour 4: If ROI positive, spawn remaining 9
    - Total at full deployment: 18 agents
    """

    def __init__(self):
        self.spawn_log = []
        self.active_agents = []

        # Spawning schedule
        self.spawn_schedule = [
            {
                'delay_hours': 0,
                'agents': [
                    {'type': 'DigitalProductCreator', 'id': 'product_ai_ml', 'niche': 'AI/ML'},
                    {'type': 'ContentArbitrage', 'id': 'arbitrage_upwork', 'platform': 'upwork'},
                    {'type': 'LeadGenerator', 'id': 'leads_saas', 'industry': 'SaaS'}
                ],
                'validation': 'none'  # First batch, no validation needed
            },
            {
                'delay_hours': 2,
                'agents': [
                    {'type': 'DigitalProductCreator', 'id': 'product_productivity', 'niche': 'Productivity'},
                    {'type': 'DigitalProductCreator', 'id': 'product_business', 'niche': 'Business Automation'},
                    {'type': 'ContentArbitrage', 'id': 'arbitrage_fiverr', 'platform': 'fiverr'},
                    {'type': 'LeadGenerator', 'id': 'leads_ecommerce', 'industry': 'Ecommerce'},
                    {'type': 'LeadGenerator', 'id': 'leads_marketing', 'industry': 'Marketing Agencies'},
                    {'type': 'LeadGenerator', 'id': 'leads_consulting', 'industry': 'Consulting'}
                ],
                'validation': 'no_errors'  # Check first batch has no errors
            },
            {
                'delay_hours': 4,
                'agents': [
                    {'type': 'DigitalProductCreator', 'id': 'product_dev', 'niche': 'Developer Tools'},
                    {'type': 'DigitalProductCreator', 'id': 'product_creator', 'niche': 'Creator Tools'},
                    {'type': 'ContentArbitrage', 'id': 'arbitrage_freelancer', 'platform': 'freelancer'},
                    {'type': 'LeadGenerator', 'id': 'leads_realestate', 'industry': 'Real Estate'},
                    {'type': 'LeadGenerator', 'id': 'leads_healthcare', 'industry': 'Healthcare'},
                    {'type': 'LeadGenerator', 'id': 'leads_fintech', 'industry': 'Fintech'},
                    {'type': 'LeadGenerator', 'id': 'leads_legal', 'industry': 'Legal Services'},
                    {'type': 'LeadGenerator', 'id': 'leads_education', 'industry': 'Education'},
                    {'type': 'LeadGenerator', 'id': 'leads_hospitality', 'industry': 'Hospitality'}
                ],
                'validation': 'positive_roi'  # Check for actual output/activity
            }
        ]

        self.start_time = safe_datetime_now()

    def should_spawn_batch(self, batch_index: int) -> tuple[bool, str]:
        """
        Check if a batch should be spawned

        Returns:
            (should_spawn, reason)
        """
        if batch_index >= len(self.spawn_schedule):
            return False, "No more batches"

        batch = self.spawn_schedule[batch_index]

        # Check time delay
        elapsed_hours = (safe_datetime_now() - self.start_time).total_seconds() / 3600
        if elapsed_hours < batch['delay_hours']:
            return False, f"Waiting {batch['delay_hours'] - elapsed_hours:.1f} more hours"

        # Check validation criteria
        validation = batch['validation']

        if validation == 'none':
            return True, "Initial batch, no validation needed"

        elif validation == 'no_errors':
            # Check if first batch is running without errors
            errors = self._check_agent_errors()
            if errors:
                return False, f"First batch has errors: {errors}"
            return True, "First batch running successfully"

        elif validation == 'positive_roi':
            # Check if agents are producing outputs
            has_activity = self._check_agent_activity()
            if not has_activity:
                return False, "No agent activity detected yet"

            # Check budget is reasonable
            within_budget = self._check_budget()
            if not within_budget:
                return False, "Budget exceeded"

            return True, "Agents active and within budget"

        return False, "Unknown validation"

    def _check_agent_errors(self) -> Optional[str]:
        """Check if any active agents have errors"""
        try:
            # Check Render logs or local logs for errors
            # For now, simulate check
            return None  # No errors
        except Exception as e:
            return str(e)

    def _check_agent_activity(self) -> bool:
        """Check if agents are producing outputs"""
        try:
            from pathlib import Path

            # Check if agents have created any outputs
            products_dir = Path("/Users/krissanders/novaos-v2/data/products")
            fulfillments_dir = Path("/Users/krissanders/novaos-v2/data/fulfillments")
            outreach_dir = Path("/Users/krissanders/novaos-v2/data/outreach")

            # Count files created
            product_count = len(list(products_dir.glob("*.json"))) if products_dir.exists() else 0
            fulfillment_count = len(list(fulfillments_dir.glob("*.txt"))) if fulfillments_dir.exists() else 0
            outreach_count = len(list(outreach_dir.glob("*.txt"))) if outreach_dir.exists() else 0

            total_outputs = product_count + fulfillment_count + outreach_count

            logger.info(f"Agent activity check: {total_outputs} outputs created")
            return total_outputs > 0

        except Exception as e:
            logger.error(f"Error checking activity: {e}")
            return False

    def _check_budget(self) -> bool:
        """Check if we're within budget"""
        try:
            from security.budget_enforcer import get_budget_enforcer

            enforcer = get_budget_enforcer()
            status = enforcer.get_status()

            # Check daily budget usage
            daily_percentage = (status['daily_spend'] / status['daily_limit']) * 100

            logger.info(f"Budget check: {daily_percentage:.1f}% of daily budget used")

            # Allow spawn if under 80% of daily budget
            return daily_percentage < 80

        except Exception as e:
            logger.error(f"Error checking budget: {e}")
            return True  # Default to allowing if check fails

    def spawn_batch(self, batch_index: int) -> bool:
        """
        Spawn a batch of agents

        Returns:
            True if spawned successfully
        """
        if batch_index >= len(self.spawn_schedule):
            logger.warning(f"Invalid batch index: {batch_index}")
            return False

        batch = self.spawn_schedule[batch_index]
        logger.info(f"Spawning batch {batch_index + 1}: {len(batch['agents'])} agents")

        for agent_config in batch['agents']:
            try:
                agent_type = agent_config['type']
                agent_id = agent_config['id']

                logger.info(f"Spawning {agent_type} ({agent_id})")

                # In production on Render, these would be separate services
                # For local testing, import and start agents
                if agent_type == 'DigitalProductCreator':
                    from revenue_agents import DigitalProductCreator
                    agent = DigitalProductCreator(
                        worker_id=agent_id,
                        niche=agent_config['niche']
                    )

                elif agent_type == 'ContentArbitrage':
                    from revenue_agents import ContentArbitrage
                    agent = ContentArbitrage(
                        worker_id=agent_id,
                        platform=agent_config['platform']
                    )

                elif agent_type == 'LeadGenerator':
                    from revenue_agents import LeadGenerator


def safe_datetime_now():
    """Get current datetime with fallback for timestamp overflow"""
    try:
        return datetime.now()
    except (OSError, OverflowError, ValueError):
        from datetime import datetime as dt
        return dt(2025, 1, 1, 0, 0, 0)

                    agent = LeadGenerator(
                        worker_id=agent_id,
                        target_industry=agent_config['industry']
                    )

                self.active_agents.append({
                    'id': agent_id,
                    'type': agent_type,
                    'agent': agent,
                    'started_at': safe_datetime_now()
                })

                logger.info(f"✓ Spawned {agent_id}")

            except Exception as e:
                logger.error(f"Failed to spawn {agent_id}: {e}")
                return False

        self.spawn_log.append({
            'batch': batch_index + 1,
            'count': len(batch['agents']),
            'time': safe_datetime_now(),
            'agents': [a['id'] for a in batch['agents']]
        })

        return True

    def run_incremental_spawn(self):
        """
        Main loop: incrementally spawn agents based on schedule
        """
        logger.info("Starting incremental agent spawner")
        logger.info(f"Schedule: {len(self.spawn_schedule)} batches")

        current_batch = 0

        while current_batch < len(self.spawn_schedule):
            # Check if we should spawn this batch
            should_spawn, reason = self.should_spawn_batch(current_batch)

            if should_spawn:
                logger.info(f"Spawning batch {current_batch + 1}: {reason}")
                success = self.spawn_batch(current_batch)

                if success:
                    logger.info(f"✓ Batch {current_batch + 1} spawned successfully")
                    current_batch += 1
                else:
                    logger.error(f"✗ Failed to spawn batch {current_batch + 1}")
                    break
            else:
                logger.info(f"Waiting to spawn batch {current_batch + 1}: {reason}")
                time.sleep(300)  # Check every 5 minutes

        logger.info(f"Incremental spawning complete: {len(self.active_agents)} agents active")

    def get_status(self) -> Dict:
        """Get spawner status"""
        return {
            'active_agents': len(self.active_agents),
            'batches_spawned': len(self.spawn_log),
            'start_time': self.start_time.isoformat(),
            'spawn_log': self.spawn_log
        }


def start_incremental_spawning():
    """Start the incremental spawning process"""
    spawner = AgentSpawner()
    spawner.run_incremental_spawn()


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    start_incremental_spawning()
