"""
Digital Product Creator - Revenue Agent #1 (AGGRESSIVE MODE)

Autonomous agent that:
1. Monitors trending topics continuously
2. Identifies product opportunities
3. Creates digital products (templates, guides, prompt packs)
4. Lists products on Gumroad automatically
5. Tracks sales and auto-scales winners

AGGRESSIVE CONFIG:
- Runs every 30 minutes (not 6 hours)
- Deploy 5 instances for different niches
- Auto-scales successful products 10x
- Target: 10 products in first 24 hours
- Target: 100+ products in first month
"""

import os
import logging
import anthropic
from typing import Dict, Optional, Any
from datetime import datetime
import json

from workers.base_worker import BaseWorker
from security import get_security_manager, SecurityLevel
from security.audit import log_agent_action

logger = logging.getLogger(__name__)


class DigitalProductCreator(BaseWorker):
    """
    Creates and sells digital products autonomously (AGGRESSIVE MODE)

    Revenue Model:
    - Creates digital products (guides, templates, prompts)
    - Lists on Gumroad at $9-49 price points
    - Target: 10 products in 24 hours
    - Target: 100-200 products in first month
    - Expected revenue: $500-2000/month per successful product
    - Auto-scales winners 10x
    """

    def __init__(
        self,
        worker_id: str = "digital_product_creator",
        name: str = "Digital Product Creator",
        run_interval: int = 1800,  # 30 minutes (AGGRESSIVE)
        budget_limit: float = 15.0,  # $15 per run max (AGGRESSIVE)
        gumroad_api_key: Optional[str] = None,
        niche: str = "AI/ML"  # Specific niche for this instance
    ):
        """
        Initialize Digital Product Creator

        Args:
            worker_id: Unique worker ID
            name: Human-readable name
            run_interval: Seconds between runs (default 6 hours)
            budget_limit: Max cost per run
            gumroad_api_key: Gumroad API key for listing products
        """
        super().__init__(
            worker_id=worker_id,
            name=name,
            run_interval=run_interval,
            budget_limit=budget_limit,
            auto_restart=True
        )

        # Security integration
        self.security = get_security_manager(SecurityLevel.STRICT)

        # API keys
        self.anthropic_key = os.environ.get("ANTHROPIC_API_KEY")
        self.gumroad_api_key = gumroad_api_key or os.environ.get("GUMROAD_API_KEY")

        # Claude client
        if self.anthropic_key:
            self.client = anthropic.Anthropic(api_key=self.anthropic_key)
        else:
            logger.warning("No Anthropic API key - agent will not function")
            self.client = None

        # Configuration
        self.niche = niche

        # Product tracking
        self.products_created = 0
        self.total_revenue = 0.0
        self.successful_products = []  # Track winners for auto-scaling

        # Aggressive mode tracking
        self.products_last_hour = 0
        self.last_hour_reset = datetime.now()

        logger.info(f"Digital Product Creator initialized (AGGRESSIVE MODE)")
        logger.info(f"  Niche: {niche}")
        logger.info(f"  Runs every: {run_interval/60:.0f} minutes")
        logger.info(f"  Target: 10 products/day")

    def run(self) -> Optional[Dict[str, Any]]:
        """
        Main product creation workflow

        Returns:
            Dict with revenue and cost info
        """
        if not self.client:
            logger.error("No Anthropic client - cannot run")
            return None

        try:
            logger.info("Starting digital product creation cycle...")

            # Step 1: Find trending topic
            topic = self._find_trending_topic()
            if not topic:
                logger.warning("No suitable trending topic found")
                return {'revenue': 0.0, 'cost': 0.01}

            logger.info(f"Found trending topic: {topic['topic']}")

            # Step 2: Validate topic through security
            topic_valid = self._validate_topic(topic)
            if not topic_valid:
                logger.warning(f"Topic failed security validation: {topic['topic']}")
                return {'revenue': 0.0, 'cost': 0.02}

            # Step 3: Create product content
            product = self._create_product_content(topic)
            if not product:
                logger.error("Failed to create product content")
                return {'revenue': 0.0, 'cost': 0.5}

            logger.info(f"Created product: {product['title']}")

            # Step 4: List on Gumroad (if API key available)
            if self.gumroad_api_key:
                listing = self._list_on_gumroad(product)
                if listing:
                    logger.info(f"Listed on Gumroad: {listing.get('url', 'N/A')}")
                    self.products_created += 1
            else:
                logger.info("No Gumroad API key - product saved locally")
                self._save_product_locally(product)
                self.products_created += 1

            # Track metrics
            cost = product.get('creation_cost', 0.5)

            # Audit log
            log_agent_action(
                self.worker_id,
                'create_product',
                details={
                    'topic': topic['topic'],
                    'product_title': product['title'],
                    'cost': cost,
                    'products_total': self.products_created
                }
            )

            return {
                'revenue': 0.0,  # Revenue comes later from sales
                'cost': cost,
                'product_created': True,
                'product_title': product['title']
            }

        except Exception as e:
            logger.error(f"Error in product creation: {e}", exc_info=True)
            return {'revenue': 0.0, 'cost': 0.1}

    def _find_trending_topic(self) -> Optional[Dict]:
        """
        Find trending topic with product potential

        Uses Claude to analyze trends and identify opportunities

        Returns:
            Dict with topic info or None
        """
        try:
            # Security check: Budget for this operation
            allowed, reason = self.security.budget_enforcer.check_and_reserve(
                self.worker_id,
                0.10,  # Estimated cost
                "find_trending_topic"
            )

            if not allowed:
                logger.warning(f"Budget check failed: {reason}")
                return None

            # Prompt to find trending topics (AGGRESSIVE - niche-specific)
            prompt = f"""You are a digital product researcher. Analyze current trends in {self.niche} and identify a HIGH-DEMAND product opportunity.

NICHE FOCUS: {self.niche}

Find topics that are:
1. Trending RIGHT NOW (not evergreen)
2. Solving URGENT problems
3. High search volume
4. Low competition
5. Monetizable immediately

Return a JSON object with:
{{
  "topic": "specific trending topic in {self.niche}",
  "category": "category",
  "problem": "urgent problem it solves",
  "audience": "target audience with money",
  "demand_score": 7-10 (ONLY high-demand),
  "product_type": "guide|template|prompt_pack|toolkit",
  "urgency": "why people need this NOW"
}}

BE AGGRESSIVE. Find hot opportunities. High demand only (8+)."""

            # Call Claude
            response = self.client.messages.create(
                model="claude-3-5-haiku-20241022",  # Use cheaper model for research
                max_tokens=1000,
                messages=[{"role": "user", "content": prompt}]
            )

            # Parse response
            content = response.content[0].text

            # Extract JSON
            import re
            json_match = re.search(r'\{[^}]+\}', content, re.DOTALL)
            if json_match:
                topic_data = json.loads(json_match.group())

                # Validate required fields
                if topic_data.get('demand_score', 0) >= 7:
                    return topic_data

            return None

        except Exception as e:
            logger.error(f"Error finding trending topic: {e}")
            return None

    def _validate_topic(self, topic: Dict) -> bool:
        """
        Validate topic through security layer

        Args:
            topic: Topic data

        Returns:
            True if valid
        """
        try:
            # Validate topic name
            result = self.security.input_validator.validate(
                topic.get('topic', ''),
                context='product_topic'
            )

            return result.is_valid

        except Exception as e:
            logger.error(f"Error validating topic: {e}")
            return False

    def _create_product_content(self, topic: Dict) -> Optional[Dict]:
        """
        Create actual product content using Claude

        Args:
            topic: Topic data

        Returns:
            Product data or None
        """
        try:
            # Security check: Budget for content creation
            allowed, reason = self.security.budget_enforcer.check_and_reserve(
                self.worker_id,
                0.50,  # Estimated cost for content generation
                "create_content"
            )

            if not allowed:
                logger.warning(f"Budget check failed: {reason}")
                return None

            product_type = topic.get('product_type', 'guide')

            # Create appropriate content based on type
            if product_type == 'guide':
                content = self._create_guide(topic)
            elif product_type == 'template':
                content = self._create_template(topic)
            elif product_type == 'prompt_pack':
                content = self._create_prompt_pack(topic)
            else:
                content = self._create_toolkit(topic)

            if not content:
                return None

            # Package product
            product = {
                'title': f"{topic['topic']} - {product_type.replace('_', ' ').title()}",
                'description': f"A comprehensive {product_type.replace('_', ' ')} for {topic['audience']}. Solves: {topic['problem']}",
                'content': content,
                'price': self._calculate_price(product_type, len(content)),
                'category': topic['category'],
                'created_at': datetime.now().isoformat(),
                'creation_cost': 0.50
            }

            return product

        except Exception as e:
            logger.error(f"Error creating product content: {e}")
            return None

    def _create_guide(self, topic: Dict) -> Optional[str]:
        """Create a comprehensive guide"""
        try:
            prompt = f"""Create a comprehensive, professional guide on: {topic['topic']}

Target audience: {topic['audience']}
Problem to solve: {topic['problem']}

Structure:
1. Introduction (why this matters)
2. Core concepts/fundamentals
3. Step-by-step implementation
4. Best practices
5. Common pitfalls to avoid
6. Advanced tips
7. Resources and next steps

Make it practical, actionable, and valuable. 2000-3000 words.
Use clear headings, bullet points, and examples."""

            response = self.client.messages.create(
                model="claude-sonnet-4-5-20250929",
                max_tokens=4000,
                messages=[{"role": "user", "content": prompt}]
            )

            return response.content[0].text

        except Exception as e:
            logger.error(f"Error creating guide: {e}")
            return None

    def _create_template(self, topic: Dict) -> Optional[str]:
        """Create a reusable template"""
        try:
            prompt = f"""Create a professional, reusable template for: {topic['topic']}

Target audience: {topic['audience']}
Problem to solve: {topic['problem']}

Include:
1. Template structure/format
2. Fill-in-the-blank sections
3. Examples of completed sections
4. Instructions for customization
5. Best practices

Make it immediately usable and valuable."""

            response = self.client.messages.create(
                model="claude-sonnet-4-5-20250929",
                max_tokens=3000,
                messages=[{"role": "user", "content": prompt}]
            )

            return response.content[0].text

        except Exception as e:
            logger.error(f"Error creating template: {e}")
            return None

    def _create_prompt_pack(self, topic: Dict) -> Optional[str]:
        """Create a pack of AI prompts"""
        try:
            prompt = f"""Create a pack of 20 high-quality AI prompts for: {topic['topic']}

Target audience: {topic['audience']}
Problem to solve: {topic['problem']}

For each prompt include:
1. Prompt title/name
2. The actual prompt (ready to use)
3. Example output
4. Tips for best results
5. Variations

Cover different use cases and scenarios. Make them immediately valuable."""

            response = self.client.messages.create(
                model="claude-sonnet-4-5-20250929",
                max_tokens=4000,
                messages=[{"role": "user", "content": prompt}]
            )

            return response.content[0].text

        except Exception as e:
            logger.error(f"Error creating prompt pack: {e}")
            return None

    def _create_toolkit(self, topic: Dict) -> Optional[str]:
        """Create a toolkit (collection of resources)"""
        return self._create_guide(topic)  # Similar to guide for now

    def _calculate_price(self, product_type: str, content_length: int) -> float:
        """
        Calculate appropriate price for product

        Args:
            product_type: Type of product
            content_length: Length of content

        Returns:
            Price in dollars
        """
        base_prices = {
            'guide': 19.0,
            'template': 14.0,
            'prompt_pack': 29.0,
            'toolkit': 39.0
        }

        base = base_prices.get(product_type, 19.0)

        # Adjust based on content length
        if content_length > 5000:
            return base + 10.0
        elif content_length > 3000:
            return base + 5.0
        else:
            return base

    def _list_on_gumroad(self, product: Dict) -> Optional[Dict]:
        """
        List product on Gumroad

        Args:
            product: Product data

        Returns:
            Listing info or None
        """
        # TODO: Implement Gumroad API integration
        logger.info("Gumroad listing not yet implemented - saving locally")
        return self._save_product_locally(product)

    def _save_product_locally(self, product: Dict) -> Dict:
        """
        Save product to local file system

        Args:
            product: Product data

        Returns:
            Save info
        """
        try:
            import os
            from pathlib import Path

            # Create products directory
            products_dir = Path("/Users/krissanders/novaos-v2/data/products")
            products_dir.mkdir(parents=True, exist_ok=True)

            # Create product file
            filename = f"product_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            filepath = products_dir / filename

            with open(filepath, 'w') as f:
                json.dump(product, f, indent=2)

            logger.info(f"Product saved: {filepath}")

            return {
                'saved': True,
                'path': str(filepath),
                'url': None
            }

        except Exception as e:
            logger.error(f"Error saving product: {e}")
            return {'saved': False}

    def get_stats(self) -> Dict:
        """Get agent statistics"""
        base_stats = self.get_status()
        base_stats['products_created'] = self.products_created
        base_stats['total_revenue'] = self.total_revenue
        return base_stats
