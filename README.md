# NovaOS V2 - AI Business Orchestration Platform

**Token-efficient, self-sustaining AI business platform targeting $200K/month revenue**

## 🚀 QUICK DEPLOY (NEW!)

**ONE COMMAND - Deploy 18 revenue-generating agents to production:**

```bash
./deploy-one-command.sh
```

**Zero configuration. Fully automated. Revenue in 6 hours.**

- ✅ 18 autonomous revenue agents (AGGRESSIVE MODE)
- ✅ $200/day budget with security protections
- ✅ Expected: $4,000-19,000/month profit
- ✅ Telegram remote control included

📖 [Deploy Now Guide](DEPLOY_NOW.md) | [Full Production Guide](PRODUCTION_DEPLOYMENT.md)

---

## 🎯 Mission

Build an AI-powered business orchestration system that:
- Keeps AI costs under 5% of revenue
- Tracks every penny of API spend
- Makes data-driven decisions through board agents
- Deploys execution agents dynamically
- Achieves aggressive 10X growth targets

## 📊 Visual Dashboard

**NEW!** Monitor your entire NovaOS system with the real-time web dashboard:

```bash
python3 cli.py dashboard start
```

Access at: **http://localhost:5001**

**Features:** Real-time metrics • Agent monitoring • Financial analytics • Opportunity pipeline • CSV exports

📖 [Full Dashboard Documentation](dashboard/DASHBOARD.md)

## 💰 Financial Targets

- **Month 1**: $5,000
- **Month 3**: $15,000
- **Month 6**: $50,000
- **Month 12**: $200,000

**AI Cost Target**: <5% of revenue

## 🏗️ Architecture

```
NovaOS V2
├── Board Agents (Strategic)
│   ├── CEO - GO/NO-GO decisions
│   ├── CFO - Financial tracking & optimization
│   ├── CMO - Market opportunity scanning
│   ├── CTO - Technical feasibility
│   └── COO - System health & operations
│
├── Departments (Tactical)
│   ├── Sales - DDS prospecting, lead gen
│   ├── Marketing - Content, SEO, social
│   ├── Product - Digital products, SaaS
│   ├── Operations - Infrastructure, monitoring
│   └── Research - R&D Expert Council, analysis
│
├── Execution Agents (Dynamic)
│   └── Deployed on-demand per department needs
│
└── R&D Expert Council (Advisory)
    ├── Thiel Avatar - Contrarian monopoly thinking
    ├── Musk Avatar - First principles speed
    ├── Graham Avatar - Startup fundamentals
    └── Taleb Avatar - Risk management
```

## 🚀 Quick Start

### Installation

```bash
cd /Users/krissanders/novaos-v2

# Install dependencies
pip install anthropic

# Set API key
export ANTHROPIC_API_KEY="your-key-here"

# Make CLI executable
chmod +x cli.py

# Optional: Create alias
echo 'alias nova="/Users/krissanders/novaos-v2/cli.py"' >> ~/.zshrc
source ~/.zshrc
```

### First Commands

```bash
# System status
./cli.py status

# Cost dashboard
./cli.py costs

# Revenue tracking
./cli.py revenue

# Board status
./cli.py board

# Make a decision
./cli.py decide "Should we target crypto arbitrage market?"

# R&D Expert Council
./cli.py council "Is crypto arbitrage a good opportunity right now?"
```

## 📋 Common Operations

### Deploy Agents

```bash
# Deploy DDS prospecting
./cli.py deploy sales dds --config='{"vertical":"dentists","location":"Austin","prospect_count":50}'

# Deploy content creator
./cli.py deploy marketing content_creator --config='{"platform":"twitter","topic":"AI business"}'

# Deploy trend monitor
./cli.py deploy research trend_monitor --config='{"topic":"crypto arbitrage"}'
```

### Monitor Performance

```bash
# List all agents
./cli.py agents

# Agent details
./cli.py agent <agent_id>

# Department ROI
./cli.py roi sales

# Agent ROI
./cli.py roi <agent_id>
```

### Optimize Costs

```bash
# Run auto-optimization
./cli.py optimize

# Pause underperforming agent
./cli.py pause <agent_id>

# Resume agent
./cli.py resume <agent_id>

# Kill agent permanently
./cli.py kill <agent_id>
```

## 💰 Cost Tracking

Every API call is logged with:
- Model used
- Input/output tokens
- Cost calculated
- Agent attribution
- Department attribution

Access via:
- `./cli.py costs` - Dashboard
- SQLite database: `/Users/krissanders/novaos-v2/data/novaos.db`
- MCP memory integration (persistent across sessions)

## 🎛️ Key Features

### Token Efficiency

- **Board agents**: 500-2000 token budgets per operation
- **Council avatars**: 500 tokens max each
- **Execution agents**: 1000 token default budget
- **Aggressive caching**: Repeated queries cached
- **Batch processing**: Multiple ops in single call where possible

### Cost Optimization

- Real-time cost tracking
- Alert when AI costs > 10% of revenue
- Auto-pause negative ROI agents
- Department-level ROI tracking
- Agent-level performance metrics

### Self-Sustainability

- Track revenue vs costs
- Calculate ROI continuously
- Project future costs
- Alert on unsustainable trajectories
- Auto-optimize when thresholds exceeded

## 🗄️ Data Storage

### SQLite Database

- **decisions** - All board decisions
- **agents** - All deployed agents + metrics
- **costs** - Every API call logged
- **revenue** - All income tracked
- **opportunities** - CMO identified opportunities
- **council_sessions** - R&D council analyses
- **system_metrics** - Performance metrics

### MCP Integration

Strategic context persists across sessions via NovaOS Memory MCP server.

Board decisions, opportunities, and council sessions automatically saved.

## 🎯 DDS Integration

Existing DDS prospecting system at `/Users/krissanders/prospecting_agent/` is integrated.

Deploy DDS campaigns via Sales Department:

```bash
./cli.py deploy sales dds --config='{"vertical":"dentists","location":"Austin"}'
```

## 📊 Monitoring & Alerts

### System Health Checks

- **COO Agent**: Runs periodic health checks
- **CFO Agent**: Monitors financial metrics
- **Auto-optimization**: Triggers when costs spike

### Alert Thresholds

- AI costs > 10% of revenue → WARNING
- Any agent negative ROI > 3 days → PAUSE recommended
- Monthly budget > 80% used → ALERT

## 🎓 R&D Expert Council

Token-efficient advisory board with 4 expert avatars:

```bash
./cli.py council "Should we pivot to X?"
```

Each avatar gets 500 tokens max. Full session costs ~$0.50.

**Avatars:**
- **Thiel**: Contrarian, monopoly thinking
- **Musk**: First principles, aggressive speed
- **Graham**: Fundamentals, product-market fit
- **Taleb**: Risk management, antifragility

## 🔧 Configuration

Edit `/Users/krissanders/novaos-v2/config/settings.py` for:
- Model selection (Opus/Sonnet/Haiku)
- Token budgets
- Cost thresholds
- Department configs
- Feature flags

Edit `/Users/krissanders/novaos-v2/config/financial_targets.py` for:
- Revenue targets
- AI cost budgets
- Alert thresholds

## 📈 Success Metrics

After building, you should be able to:

1. ✅ `nova status` → See full system health
2. ✅ `nova deploy sales dds` → Deploy DDS prospecting
3. ✅ `nova costs` → See exact AI spend breakdown
4. ✅ `nova council "question"` → Get expert analysis
5. ✅ `nova roi sales` → See department profitability

System should:
- ✅ Track every penny of AI costs
- ✅ Alert when costs spike
- ✅ Show clear ROI for every agent
- ✅ Scale to $200K/month revenue
- ✅ Keep AI costs under $10K/month at scale

## 🚨 Important Notes

**Token Efficiency is CRITICAL**:
- This is not optional
- System will not be sustainable without it
- Every feature designed for cost optimization
- Survival depends on staying under 5% AI cost ratio

**Start Small, Scale Fast**:
- Deploy one agent at a time
- Monitor ROI closely
- Kill/pause underperformers quickly
- Scale what works

**Data-Driven Everything**:
- Every decision tracked
- Every cost logged
- Every agent measured
- ROI calculated continuously

## 📞 Support

Issues or questions? Check:
- This README
- System status: `./cli.py status`
- Cost dashboard: `./cli.py costs`
- Board health: `./cli.py board`

## 🎉 Let's Build

NovaOS V2 is ready to orchestrate your AI-powered business empire.

**Target: $200K/month revenue by Month 12**

**Constraint: <5% AI costs**

**Strategy: Deploy smart, optimize ruthlessly, scale what works**

Let's go! 🚀
