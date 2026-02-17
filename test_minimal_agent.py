#!/usr/bin/env python3
"""
Minimal test agent - ZERO datetime usage
Just proves the platform can run Python code
"""

import time
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MinimalAgent:
    def __init__(self, agent_id):
        self.agent_id = agent_id
        self.running = False
        logger.info(f"MinimalAgent {agent_id} initialized")

    def start(self):
        self.running = True
        logger.info(f"MinimalAgent {self.agent_id} started")

        cycle = 0
        while self.running:
            cycle += 1
            logger.info(f"MinimalAgent {self.agent_id} - Cycle {cycle} - I'm alive!")
            time.sleep(10)

if __name__ == "__main__":
    agent = MinimalAgent("test_agent")
    logger.info("Creating agent...")
    agent.start()
