# NovaOS V2 - Autonomous Agent Deployment System

Complete autonomous agent deployment system that runs 24/7 without human intervention.

## Overview

This system enables fully autonomous agent operations with:
- **24/7 Background Workers** - Agents run continuously with auto-restart
- **ROI-Based Decision Making** - Auto-scale winners, auto-kill losers
- **Revenue Tracking** - Real-time attribution and profitability
- **Platform Integrations** - Stripe, Gumroad, SendGrid, Twitter, Web Scraping
- **Deployment Automation** - One-command deploy to local, Docker, or cloud

## Quick Start

### 1. Setup Environment

```bash
# Copy environment template
cp .env.example .env

# Edit .env and add your API keys
nano .env
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Deploy Workers

```bash
# Start all background workers
./nova workers start

# Check worker status
./nova workers status
```

### 4. Enable Autonomous Mode

```bash
# Enable autonomous decision-making
./nova autonomous enable

# Check autonomous status
./nova autonomous status
```

## Architecture

### Background Worker System

**Location:** `/workers/`

Components:
- `base_worker.py` - Base worker class with auto-restart, monitoring, crash recovery
- `manager.py` - Worker lifecycle management, scaling, health checks
- `worker_monitor.py` - Resource tracking, cost monitoring, ROI calculations

Features:
- Auto-restart on failure (configurable crash limit)
- Resource monitoring (CPU, memory, threads)
- Cost tracking per worker
- ROI calculation and alerts
- Heartbeat monitoring
- Configurable run intervals

### Autonomous Decision Engine

**Location:** `/core/autonomous.py`

Makes autonomous decisions about:
- **Scale Up** - When ROI > 300% and success rate > 80%
- **Kill** - When ROI < 0% (negative profit)
- **Deploy** - When expected ROI > 150%
- **Pause** - When budget exceeded

Decision process:
1. Analyze all workers (minimum 20 runs required)
2. Calculate ROI, profit, success rate
3. Generate recommendations
4. Auto-execute if under approval threshold ($50)
5. Queue for approval if over threshold

### Revenue Tracking

**Location:** `/core/revenue_tracker.py`

Tracks:
- Revenue from all sources (Stripe, Gumroad, etc.)
- Per-agent attribution
- Real-time profitability
- Cash flow analysis
- Auto-reinvestment calculations

### Platform Integrations

**Location:** `/platforms/`

Integrations:

#### Stripe (`stripe_integration.py`)
- Payment processing
- Subscription management
- Revenue tracking
- Webhook handling

#### Gumroad (`gumroad_integration.py`)
- Digital product sales
- Sales tracking
- License verification

#### SendGrid (`sendgrid_integration.py`)
- Transactional emails
- Marketing campaigns
- Template management
- Email analytics

#### Twitter (`twitter_integration.py`)
- Post tweets and threads
- Search tweets
- Get mentions
- Track engagement

#### Web Scraper (`web_scraper.py`)
- HTML scraping with BeautifulSoup
- Rate limiting
- Data extraction
- List/table scraping

## CLI Commands

### Worker Management

```bash
# Start all workers
./nova workers start

# Stop all workers
./nova workers stop

# Show worker status
./nova workers status

# Scale a worker (create 2x instances)
./nova workers scale worker_id --multiplier=2

# Check worker health
./nova workers health
```

### Autonomous Mode

```bash
# Enable autonomous decision-making
./nova autonomous enable

# Disable autonomous mode
./nova autonomous disable

# Show autonomous status
./nova autonomous status

# Run analysis cycle manually
./nova autonomous run
```

### Existing Commands

```bash
# System status
./nova status

# Deploy agent
./nova deploy sales outbound_agent

# Show agents
./nova agents

# Dashboard
./nova dashboard start
```

## Deployment

### Local Deployment

```bash
./deploy.sh local
./nova workers start
```

### Docker Deployment

```bash
# Start with Docker Compose
./deploy.sh docker start

# View logs
./deploy.sh docker logs

# Stop containers
./deploy.sh docker stop
```

### AWS Deployment

```bash
# Deploy to AWS ECS
./deploy.sh aws

# Requires AWS CLI configured with:
# - AWS_ACCESS_KEY_ID
# - AWS_SECRET_ACCESS_KEY
# - AWS_REGION
```

## Configuration

### Environment Variables

Key variables in `.env`:

```bash
# Core
ANTHROPIC_API_KEY=your_key
AUTONOMOUS_ENABLED=true
MAX_DAILY_BUDGET=100.0

# Thresholds
MIN_ROI_THRESHOLD=150.0    # 150% ROI minimum
SCALE_ROI_THRESHOLD=300.0  # 300% ROI to scale
KILL_ROI_THRESHOLD=0.0     # Negative ROI to kill

# Platform API Keys
STRIPE_API_KEY=sk_test_...
GUMROAD_ACCESS_TOKEN=...
SENDGRID_API_KEY=SG...
TWITTER_BEARER_TOKEN=...
```

### Autonomous Configuration

Adjust thresholds in `.env`:

- `MAX_DAILY_BUDGET` - Maximum daily spend
- `MIN_ROI_THRESHOLD` - Minimum ROI to keep agents (150%)
- `SCALE_ROI_THRESHOLD` - ROI needed to trigger scaling (300%)
- `KILL_ROI_THRESHOLD` - ROI threshold to trigger killing (0%)
- `REQUIRE_APPROVAL_ABOVE` - Cost threshold requiring approval ($50)

## Safety & Guardrails

### Budget Protection
- Daily budget limits enforced
- Auto-pause when budget exceeded
- Per-worker budget limits available

### Decision Approval
- Decisions over $50 require human approval
- View pending approvals: `./nova autonomous status`
- System logs all decisions for audit

### Crash Protection
- Max 5 crashes before worker stopped
- 5-minute cooldown after crash
- Auto-restart configurable per worker

### ROI Thresholds
- Minimum 150% ROI to deploy new agents
- 300% ROI to trigger auto-scaling
- Negative ROI triggers immediate kill

## Monitoring

### Worker Health

```bash
# Check all worker health
./nova workers health

# Shows:
# - Healthy/unhealthy count
# - Workers needing restart
# - Workers with issues
```

### Cost Monitoring

Workers automatically track:
- Total runs
- Success/failure rate
- Revenue generated
- Costs incurred
- ROI percentage
- Profit/loss

### Real-Time Alerts

System generates alerts for:
- Negative ROI (CRITICAL)
- Low ROI < 100% (WARNING)
- Budget exceeded (CRITICAL)
- High crash rate > 20% (CRITICAL)

## Example Workflows

### Deploy and Monitor Agent

```bash
# 1. Deploy agent
./nova deploy sales email_outreach --config '{"target":"b2b"}'

# 2. Start as background worker
./nova workers start

# 3. Monitor performance
./nova workers status

# 4. Enable autonomous management
./nova autonomous enable

# System will now auto-scale or kill based on ROI
```

### Autonomous Operation

```bash
# 1. Enable autonomous mode
./nova autonomous enable

# 2. System runs continuously:
#    - Monitors all workers
#    - Calculates ROI every cycle
#    - Scales high performers (>300% ROI)
#    - Kills low performers (<0% ROI)
#    - Stays within budget

# 3. Check status anytime
./nova autonomous status

# 4. Review decisions
./nova autonomous status
# Shows pending approvals and recent decisions
```

### Revenue Tracking

```bash
# Revenue is tracked automatically from:
# - Stripe payments
# - Gumroad sales
# - Manual tracking

# View in system status
./nova status

# Detailed breakdown
./nova revenue
```

## Development

### Creating Custom Workers

```python
from workers.base_worker import BaseWorker

class MyCustomWorker(BaseWorker):
    def run(self):
        # Your work logic here

        # Track revenue/cost
        revenue = 10.0  # Revenue generated
        cost = 0.05     # AI cost incurred

        return {
            'revenue': revenue,
            'cost': cost
        }

# Register with manager
from workers.manager import get_worker_manager

manager = get_worker_manager()
manager.register_worker_class('my_worker', MyCustomWorker)

# Deploy
worker = manager.deploy_worker(
    worker_type='my_worker',
    worker_id='worker_1',
    name='My Custom Worker'
)
```

### Custom Platform Integration

```python
from platforms.stripe_integration import StripeIntegration

stripe = StripeIntegration()

# Track payment
revenue = stripe.get_revenue(days=7)

# Record in revenue tracker
from core.revenue_tracker import get_revenue_tracker

tracker = get_revenue_tracker()
tracker.track_event(
    amount=revenue['total'],
    source='stripe',
    agent_id='worker_1'
)
```

## Troubleshooting

### Workers Not Starting

```bash
# Check worker status
./nova workers status

# Check for errors
./nova workers health

# Restart crashed workers
./nova workers stop
./nova workers start
```

### Autonomous Not Making Decisions

Common reasons:
1. Not enough data (need 20+ runs)
2. ROI below thresholds
3. Budget exceeded
4. Autonomous mode disabled

```bash
# Check status
./nova autonomous status

# Ensure enabled
./nova autonomous enable

# Run analysis manually
./nova autonomous run
```

### High Costs

```bash
# Check cost breakdown
./nova costs

# Review worker performance
./nova workers status

# Pause high-cost workers
./nova pause worker_id

# Lower daily budget
# Edit .env: MAX_DAILY_BUDGET=50.0
```

## Best Practices

1. **Start Small** - Begin with low budgets ($10-20/day)
2. **Monitor Closely** - Check status regularly initially
3. **Set Conservative Thresholds** - Higher ROI requirements = safer
4. **Enable Gradually** - Test workers before enabling autonomous mode
5. **Review Decisions** - Check autonomous decisions daily
6. **Track Revenue** - Ensure revenue attribution is working
7. **Use Approvals** - Keep approval threshold low initially ($20-30)

## Production Deployment

### Pre-Launch Checklist

- [ ] All API keys configured in `.env`
- [ ] Budget limits set appropriately
- [ ] ROI thresholds configured
- [ ] Workers tested in sandbox first
- [ ] Revenue tracking verified
- [ ] Monitoring alerts configured
- [ ] Backup/recovery plan in place

### Launch Steps

1. Deploy to production environment
2. Start with 1-2 workers
3. Monitor for 24-48 hours
4. Enable autonomous mode with low budget
5. Gradually increase budget as confidence grows
6. Add more workers based on ROI

### Monitoring Production

```bash
# Daily checks
./nova status
./nova workers status
./nova autonomous status

# Weekly reviews
./nova costs --period=week
./nova revenue

# Monthly optimization
./nova autonomous run
# Review and approve high-impact decisions
```

## Support

For issues or questions:
1. Check logs in `/logs/`
2. Run health checks: `./nova workers health`
3. Review autonomous decisions: `./nova autonomous status`
4. Check system status: `./nova status`

## Security Notes

- Never commit `.env` file (contains API keys)
- Use environment variables for secrets
- Enable approval for high-cost decisions
- Monitor for unusual spending patterns
- Review autonomous decisions regularly
- Use separate API keys for testing/production

## Roadmap

Future enhancements:
- [ ] Multi-region deployment
- [ ] Advanced ML-based ROI prediction
- [ ] Webhook integrations for real-time events
- [ ] Mobile app for monitoring
- [ ] Advanced analytics dashboard
- [ ] A/B testing framework
- [ ] Auto-optimization of worker parameters

---

**Built with NovaOS V2** - Autonomous AI Business Orchestration Platform
