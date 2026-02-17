# QuickStart: Autonomous Agent Deployment

Get your autonomous agent system running in 5 minutes.

## 1. Setup (1 minute)

```bash
cd novaos-v2

# Copy environment template
cp .env.example .env

# Install dependencies
pip install -r requirements.txt
```

## 2. Configure (2 minutes)

Edit `.env` with your API keys:

```bash
# Required
ANTHROPIC_API_KEY=your_anthropic_key

# Optional (add as needed)
STRIPE_API_KEY=sk_test_...
GUMROAD_ACCESS_TOKEN=...
SENDGRID_API_KEY=SG...
TWITTER_BEARER_TOKEN=...

# Budget settings
MAX_DAILY_BUDGET=100.0
MIN_ROI_THRESHOLD=150.0
```

## 3. Deploy Workers (1 minute)

```bash
# Deploy an agent (creates worker)
./nova deploy sales outbound_agent

# Start all workers in background
./nova workers start

# Check status
./nova workers status
```

## 4. Enable Autonomous Mode (1 minute)

```bash
# Enable autonomous decision-making
./nova autonomous enable

# Check status
./nova autonomous status
```

## 5. Monitor

```bash
# Check system status
./nova status

# Check worker performance
./nova workers status

# Check autonomous decisions
./nova autonomous status
```

## What Happens Now?

The system will:

1. **Run Workers 24/7** - Your agents run continuously in the background
2. **Track Revenue & Costs** - Every operation is tracked for ROI
3. **Make Autonomous Decisions**:
   - **Scale Up** agents with >300% ROI automatically
   - **Kill** agents with negative ROI automatically
   - **Stay Within Budget** - Never exceeds your daily limit
4. **Request Approval** for decisions over $50

## Common Commands

```bash
# Worker Management
./nova workers start          # Start all workers
./nova workers stop           # Stop all workers
./nova workers status         # Show performance
./nova workers health         # Check health

# Autonomous Mode
./nova autonomous enable      # Turn on auto-decisions
./nova autonomous disable     # Turn off
./nova autonomous status      # Show decisions
./nova autonomous run         # Run analysis manually

# System
./nova status                 # Overall status
./nova costs                  # Cost breakdown
./nova revenue               # Revenue tracking
```

## Production Deployment

### Docker (Recommended)

```bash
# One-command deployment
./deploy.sh docker start

# View logs
./deploy.sh docker logs

# Stop
./deploy.sh docker stop
```

### AWS

```bash
# Deploy to AWS ECS
./deploy.sh aws
```

## Safety Features

✅ **Budget Protection** - Daily spend limits enforced
✅ **Approval Required** - High-cost decisions need approval
✅ **Crash Recovery** - Auto-restart on failures
✅ **ROI Thresholds** - Won't scale low performers
✅ **Audit Trail** - All decisions logged

## Troubleshooting

**Workers not starting?**
```bash
./nova workers health
```

**High costs?**
```bash
./nova costs
./nova pause agent_id  # Pause expensive agent
```

**No autonomous decisions?**
- Need 20+ runs per worker first
- Check ROI meets thresholds
- Ensure budget available

## Next Steps

1. Monitor for 24-48 hours
2. Review autonomous decisions daily
3. Adjust thresholds in `.env` as needed
4. Add more workers as ROI proves out
5. Gradually increase budget

## Full Documentation

See `AUTONOMOUS_DEPLOYMENT.md` for complete documentation.

---

**You're now running a fully autonomous AI business! 🚀**
