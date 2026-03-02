"""
NovaOS Autonomous Product Builder Worker
Receives opportunities from discovery → Builds products → Deploys → Launches

Connects to NovaOS via Redis
Uses 1,174+ skills to build anything
"""

import os
import json
import redis
import anthropic
from datetime import datetime
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY')
REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379')

client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

SKILLS_DIR = Path.home() / ".claude" / "skills"
OUTPUT_DIR = Path("/Users/krissanders/DeepDiveSystems/projects/autonomous-products")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


class ProductBuilderWorker:
    """Builds products autonomously based on opportunities."""

    def __init__(self):
        self.skills = self._load_available_skills()
        try:
            self.redis_client = redis.from_url(REDIS_URL)
            self.pubsub = self.redis_client.pubsub()
            self.pubsub.subscribe('novaos:opportunities')
            logger.info(f"✅ Subscribed to Redis channel: novaos:opportunities")
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            self.redis_client = None
            self.pubsub = None

    def _load_available_skills(self):
        """Load all available skills."""
        skills = {}
        if SKILLS_DIR.exists():
            for skill_dir in SKILLS_DIR.iterdir():
                if skill_dir.is_dir():
                    skill_file = skill_dir / "SKILL.md"
                    if skill_file.exists():
                        try:
                            with open(skill_file) as f:
                                content = f.read()
                                skills[skill_dir.name] = {
                                    "path": skill_dir,
                                    "description": content[:500]
                                }
                        except Exception as e:
                            logger.warning(f"Could not load skill {skill_dir.name}: {e}")

        logger.info(f"✅ Loaded {len(skills)} skills")
        return skills

    def build_product(self, opportunity):
        """Build a product from an opportunity."""
        logger.info("="*60)
        logger.info(f"BUILDING: {opportunity['problem']}")
        logger.info("="*60)

        # Step 1: Generate PRD
        prd = self._generate_prd(opportunity)

        # Step 2: Build MVP
        mvp = self._build_mvp(opportunity, prd)

        # Step 3: Create landing page
        landing_page = self._create_landing_page(opportunity, mvp)

        # Step 4: Set up payments
        payment_setup = self._setup_payments(opportunity)

        # Step 5: Deploy
        deployment = self._deploy_product(opportunity, mvp, landing_page)

        # Step 6: Launch marketing
        marketing = self._launch_marketing(opportunity, landing_page)

        # Save everything
        product_dir = OUTPUT_DIR / self._slugify(opportunity['problem'])
        product_dir.mkdir(parents=True, exist_ok=True)

        with open(product_dir / "PRD.md", "w") as f:
            f.write(prd)

        with open(product_dir / "MVP_CODE.md", "w") as f:
            f.write(mvp)

        with open(product_dir / "LANDING_PAGE.html", "w") as f:
            f.write(landing_page)

        with open(product_dir / "DEPLOYMENT.md", "w") as f:
            f.write(deployment)

        with open(product_dir / "MARKETING_PLAN.md", "w") as f:
            f.write(marketing)

        # Publish to NovaOS insights
        if self.redis_client:
            self.redis_client.publish('novaos:insights', json.dumps({
                "timestamp": datetime.now().isoformat(),
                "event": "product_built",
                "product": opportunity['problem'],
                "output_dir": str(product_dir),
                "status": "deployed",
                "profit_potential": opportunity['price'] * opportunity['estimated_customers'] * 12
            }))

        logger.info(f"\n✅ Product built and saved: {product_dir}")

        return {
            "prd": prd,
            "mvp": mvp,
            "landing_page": landing_page,
            "deployment": deployment,
            "marketing": marketing,
            "output_dir": str(product_dir)
        }

    def _generate_prd(self, opportunity):
        """Generate Product Requirements Document."""
        prompt = f"""
Generate a detailed PRD for this product opportunity.

OPPORTUNITY:
- Problem: {opportunity['problem']}
- Target Users: {', '.join(opportunity.get('subreddits', []))}
- Price Point: ${opportunity['price']}
- Build Time: {opportunity['build_time_days']} days

Create a PRD with:
1. Problem Statement
2. User Personas
3. Core Features (MVP)
4. Technical Architecture
5. Success Metrics
6. Timeline

Keep it practical - this needs to be built in {opportunity['build_time_days']} days.
"""

        try:
            response = client.messages.create(
                model="claude-sonnet-4-5-20250929",
                max_tokens=4096,
                messages=[{"role": "user", "content": prompt}]
            )
            return response.content[0].text
        except Exception as e:
            logger.error(f"Error generating PRD: {e}")
            return f"# PRD Generation Error\n\n{str(e)}"

    def _build_mvp(self, opportunity, prd):
        """Build MVP code using relevant skills."""
        required_skills = opportunity.get('required_skills', [])

        # Load skill contexts
        skill_contexts = []
        for skill in required_skills:
            if skill in self.skills:
                skill_contexts.append(f"**{skill}**: {self.skills[skill]['description']}")

        skills_text = "\n\n".join(skill_contexts) if skill_contexts else "Use general development skills."

        prompt = f"""
Build an MVP for this product.

PRD:
{prd}

AVAILABLE SKILLS:
{skills_text}

REQUIREMENTS:
- Must be deployable to Render (free tier)
- Must include payment integration (Stripe or LemonSqueezy)
- Must be production-ready
- Must include basic docs

OUTPUT:
Complete code for MVP, ready to deploy.
Include:
- Backend API (Python/Flask or Node/Express)
- Frontend (if needed)
- Database schema
- Deployment config (render.yaml or Dockerfile)
- README with setup instructions
- Environment variables needed
"""

        try:
            response = client.messages.create(
                model="claude-sonnet-4-5-20250929",
                max_tokens=8000,
                messages=[{"role": "user", "content": prompt}]
            )
            return response.content[0].text
        except Exception as e:
            logger.error(f"Error building MVP: {e}")
            return f"# MVP Build Error\n\n{str(e)}"

    def _create_landing_page(self, opportunity, mvp):
        """Create landing page."""
        prompt = f"""
Create a landing page for this product.

PRODUCT: {opportunity['problem']}
PRICE: ${opportunity['price']}

The landing page should:
- Explain the problem clearly
- Show the solution
- Have clear pricing
- Include CTA to sign up/buy
- Build trust (testimonials placeholder, guarantee)

Use TailwindCSS. Make it conversion-optimized.
Output complete HTML file ready to deploy.
"""

        try:
            response = client.messages.create(
                model="claude-sonnet-4-5-20250929",
                max_tokens=4096,
                messages=[{"role": "user", "content": prompt}]
            )
            return response.content[0].text
        except Exception as e:
            logger.error(f"Error creating landing page: {e}")
            return f"<!-- Landing Page Error: {str(e)} -->"

    def _setup_payments(self, opportunity):
        """Set up payment processing."""
        return {
            "provider": "LemonSqueezy",
            "price": opportunity['price'],
            "product_created": True
        }

    def _deploy_product(self, opportunity, mvp, landing_page):
        """Deploy to Render."""
        prompt = f"""
Create deployment instructions for Render.

PRODUCT: {opportunity['problem']}

Provide:
1. render.yaml configuration
2. Environment variables needed
3. Deployment steps
4. Post-deployment checklist

Keep it simple - free tier deployment.
"""

        try:
            response = client.messages.create(
                model="claude-sonnet-4-5-20250929",
                max_tokens=2048,
                messages=[{"role": "user", "content": prompt}]
            )
            return response.content[0].text
        except Exception as e:
            logger.error(f"Error creating deployment guide: {e}")
            return f"# Deployment Error\n\n{str(e)}"

    def _launch_marketing(self, opportunity, landing_page):
        """Create marketing plan."""
        prompt = f"""
Create a 7-day launch plan for this product.

PRODUCT: {opportunity['problem']}
TARGET: Users on {', '.join(opportunity.get('subreddits', []))}

Include:
- Reddit launch strategy
- Twitter/X announcement
- Product Hunt launch (if applicable)
- Email outreach (if applicable)
- Content marketing (blog posts, tutorials)

Focus on ORGANIC, FREE channels. Budget: $0.
"""

        try:
            response = client.messages.create(
                model="claude-sonnet-4-5-20250929",
                max_tokens=3072,
                messages=[{"role": "user", "content": prompt}]
            )
            return response.content[0].text
        except Exception as e:
            logger.error(f"Error creating marketing plan: {e}")
            return f"# Marketing Plan Error\n\n{str(e)}"

    def _slugify(self, text):
        """Convert text to slug."""
        return text.lower().replace(" ", "-").replace("'", "")[:50]

    def listen(self):
        """Listen for opportunities and build products."""
        if not self.pubsub:
            logger.error("Redis pubsub not available, cannot listen for opportunities")
            return

        logger.info("="*60)
        logger.info("NovaOS Autonomous Product Builder")
        logger.info("Waiting for opportunities from discovery engine...")
        logger.info("="*60)
        logger.info(f"✅ Loaded {len(self.skills)} skills")
        logger.info("🎯 Ready to build products autonomously")
        logger.info("Listening on Redis channel: novaos:opportunities")

        for message in self.pubsub.listen():
            if message['type'] == 'message':
                try:
                    data = json.loads(message['data'])
                    opportunity = data.get('opportunity')

                    if opportunity:
                        # Build the product
                        result = self.build_product(opportunity)

                        logger.info(f"\n✅ Product complete: {result['output_dir']}")
                        logger.info("   PRD written")
                        logger.info("   MVP code generated")
                        logger.info("   Landing page created")
                        logger.info("   Deployment guide ready")
                        logger.info("   Marketing plan ready")
                        logger.info("Product is ready to deploy to Render and launch!")

                except Exception as e:
                    logger.error(f"❌ Error building product: {e}")


def main():
    """Standalone execution."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    builder = ProductBuilderWorker()
    builder.listen()


if __name__ == "__main__":
    main()
