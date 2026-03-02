"""
NovaOS Market Discovery Worker
Discovers opportunities → Scores them → Publishes to Redis → Autonomous building

Goal: $2-10M profit by March 1, 2027
"""

import os
import json
import redis
import anthropic
from datetime import datetime
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

# Configuration
ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY')
REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379')

client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

# Skill inventory
SKILLS_DIR = Path.home() / ".claude" / "skills"
TOTAL_SKILLS = 1174  # From analysis

class OpportunityScorer:
    """Scores market opportunities based on demand, capability, profit, speed."""

    def score_opportunity(self, opportunity):
        """
        Score = demand (40%) + capability (30%) + profit (20%) + speed (10%)
        """
        demand = self._score_demand(opportunity)
        capability = self._score_capability(opportunity)
        profit = self._score_profit(opportunity)
        speed = self._score_speed(opportunity)

        total = (
            demand * 0.4 +
            capability * 0.3 +
            profit * 0.2 +
            speed * 0.1
        )

        return {
            "total_score": total,
            "demand_score": demand,
            "capability_score": capability,
            "profit_score": profit,
            "speed_score": speed,
            "decision": "BUILD" if total > 75 else "RESEARCH" if total > 60 else "SKIP"
        }

    def _score_demand(self, opp):
        """Score based on market signals."""
        return opp.get("demand_score", 50)

    def _score_capability(self, opp):
        """Can we build this with our 1,174+ skills?"""
        required_skills = opp.get("required_skills", [])

        # Check if we have the skills
        if SKILLS_DIR.exists():
            available_skills = [d.name for d in SKILLS_DIR.iterdir() if d.is_dir()]
        else:
            available_skills = []

        if not required_skills:
            return 80  # Default if no specific skills required

        matched = sum(1 for skill in required_skills if skill in available_skills)
        total = len(required_skills)

        return (matched / total) * 100

    def _score_profit(self, opp):
        """Annual profit potential."""
        price = opp.get("price", 0)
        volume = opp.get("estimated_customers", 0)
        annual_revenue = price * volume * 12  # Monthly recurring

        if annual_revenue > 1_000_000:
            return 100
        elif annual_revenue > 100_000:
            return 80
        elif annual_revenue > 10_000:
            return 60
        elif annual_revenue > 1_000:
            return 40
        else:
            return 20

    def _score_speed(self, opp):
        """Time to first revenue."""
        days = opp.get("build_time_days", 30)

        if days <= 7:
            return 100
        elif days <= 14:
            return 80
        elif days <= 30:
            return 60
        elif days <= 60:
            return 40
        else:
            return 20


class MarketDiscoveryWorker:
    """Worker that discovers market opportunities and publishes them to Redis."""

    def __init__(self):
        self.scorer = OpportunityScorer()
        try:
            self.redis_client = redis.from_url(REDIS_URL)
            logger.info(f"Connected to Redis at {REDIS_URL}")
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            self.redis_client = None

    def discover_reddit_opportunities(self):
        """Scan Reddit for pain points."""
        subreddits = [
            "Entrepreneur",
            "smallbusiness",
            "SaaS",
            "freelance",
            "marketing",
            "legal",
            "automation",
            "startups",
            "digitalnomad"
        ]

        keywords = [
            "I need",
            "Looking for",
            "Does anyone know",
            "Frustrated with",
            "I wish there was",
            "Need a tool",
            "How do I automate",
            "Best tool for"
        ]

        prompt = f"""
Analyze Reddit for business opportunities.

SUBREDDITS: {', '.join(subreddits)}
KEYWORDS: {', '.join(keywords)}

Find the TOP 5 most mentioned pain points in the last 7 days.

For each, provide:
1. Problem description
2. Number of mentions (estimate)
3. Subreddits where mentioned
4. Potential solution type
5. Estimated willingness to pay ($)
6. Demand score (0-100)
7. Required skills to build (list)
8. Build time estimate (days)
9. Estimated customers per month

Return as JSON array with these exact fields:
[{{
  "source": "reddit",
  "problem": "...",
  "mentions": 100,
  "subreddits": ["...", "..."],
  "solution_type": "...",
  "price": 100,
  "demand_score": 80,
  "required_skills": ["skill1", "skill2"],
  "build_time_days": 7,
  "estimated_customers": 50
}}]
"""

        try:
            logger.info("Discovering Reddit opportunities...")
            response = client.messages.create(
                model="claude-sonnet-4-5-20250929",
                max_tokens=4096,
                messages=[{"role": "user", "content": prompt}]
            )

            result = response.content[0].text

            # Try to extract JSON from response
            import re
            json_match = re.search(r'\[.*\]', result, re.DOTALL)
            if json_match:
                opportunities = json.loads(json_match.group())
                logger.info(f"Found {len(opportunities)} opportunities from Reddit")
                return opportunities
            else:
                logger.warning("Could not parse JSON from Claude response")
                return []

        except Exception as e:
            logger.error(f"Error discovering Reddit opportunities: {e}")
            return []

    def discover_all(self):
        """Run all discovery methods."""
        opportunities = []

        logger.info("🔍 Discovering market opportunities...")

        reddit_opps = self.discover_reddit_opportunities()
        opportunities.extend(reddit_opps)

        logger.info(f"✅ Found {len(opportunities)} opportunities total")

        return opportunities

    def score_and_prioritize(self, opportunities):
        """Score all opportunities and prioritize."""
        scored = []

        for opp in opportunities:
            score = self.scorer.score_opportunity(opp)
            opp["scores"] = score
            scored.append(opp)

        # Sort by total score
        scored.sort(key=lambda x: x["scores"]["total_score"], reverse=True)

        return scored

    def publish_to_redis(self, opportunities):
        """Publish scored opportunities to NovaOS via Redis."""
        if not self.redis_client:
            logger.error("Redis client not available, cannot publish opportunities")
            return

        published_count = 0
        for opp in opportunities:
            if opp["scores"]["decision"] == "BUILD":
                try:
                    message = {
                        "timestamp": datetime.now().isoformat(),
                        "opportunity": opp,
                        "action": "build_product"
                    }

                    self.redis_client.publish("novaos:opportunities", json.dumps(message))

                    logger.info(f"📢 Published: {opp['problem']}")
                    logger.info(f"   Score: {opp['scores']['total_score']:.1f}/100")
                    logger.info(f"   Profit: ${opp['price'] * opp['estimated_customers'] * 12:,.0f}/year")

                    published_count += 1
                except Exception as e:
                    logger.error(f"Error publishing opportunity: {e}")

        logger.info(f"Published {published_count} BUILD opportunities to Redis")

    def run(self):
        """Main worker loop - called periodically by worker manager."""
        logger.info("="*60)
        logger.info("NovaOS Market Discovery Worker")
        logger.info("Goal: $2-10M profit by March 1, 2027")
        logger.info("="*60)

        # Discover opportunities
        opportunities = self.discover_all()

        if not opportunities:
            logger.warning("No opportunities discovered this cycle")
            return

        # Score and prioritize
        scored_opportunities = self.score_and_prioritize(opportunities)

        logger.info("="*60)
        logger.info("TOP OPPORTUNITIES")
        logger.info("="*60)

        for i, opp in enumerate(scored_opportunities[:5], 1):
            logger.info(f"\n{i}. {opp['problem']}")
            logger.info(f"   Source: {opp['source']}")
            logger.info(f"   Score: {opp['scores']['total_score']:.1f}/100")
            logger.info(f"   Decision: {opp['scores']['decision']}")
            logger.info(f"   Profit Potential: ${opp['price'] * opp['estimated_customers'] * 12:,.0f}/year")
            logger.info(f"   Build Time: {opp['build_time_days']} days")

        # Publish to NovaOS
        logger.info("="*60)
        logger.info("Publishing to NovaOS...")
        logger.info("="*60)

        self.publish_to_redis(scored_opportunities)

        logger.info("✅ Discovery cycle complete")


def main():
    """Standalone execution."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    worker = MarketDiscoveryWorker()
    worker.run()


if __name__ == "__main__":
    main()
