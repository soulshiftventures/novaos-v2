# NovaOS V2 - Quick Start Guide

## 🚀 Get Started in 5 Minutes

### Step 1: Set Up Environment

```bash
cd /Users/krissanders/novaos-v2

# Ensure Anthropic API key is set
export ANTHROPIC_API_KEY="your-key-here"

# Or add to ~/.zshrc for permanent setup
echo 'export ANTHROPIC_API_KEY="your-key-here"' >> ~/.zshrc
source ~/.zshrc
```

### Step 2: Install Dependencies

```bash
pip install anthropic
```

### Step 3: Create Alias (Optional but Recommended)

```bash
echo 'alias nova="/Users/krissanders/novaos-v2/cli.py"' >> ~/.zshrc
source ~/.zshrc

# Now you can use 'nova' instead of './cli.py'
```

### Step 4: Verify Installation

```bash
nova status
```

You should see the NovaOS dashboard!

## 📚 Essential Commands

### System Overview

```bash
# Full system status
nova status

# Cost breakdown
nova costs

# Revenue tracking
nova revenue

# Board status
nova board
```

### Deploy Your First Agent

```bash
# Deploy a trend monitoring agent
nova deploy research trend_monitor --config='{"topic":"AI automation","sources":["twitter","reddit"]}'

# Deploy DDS prospecting
nova deploy sales dds --config='{"vertical":"dentists","location":"Austin","prospect_count":25,"budget":50}'

# Deploy content creator
nova deploy marketing content_creator --config='{"platform":"twitter","topic":"AI business automation"}'
```

### Make Strategic Decisions

```bash
# CEO decision
nova decide "Should we target the crypto arbitrage market?"

# R&D Expert Council analysis
nova council "Is building an AI-powered email outreach tool a good opportunity?"
```

### Monitor Agents

```bash
# List all agents
nova agents

# View specific agent
nova agent <agent_id>

# Check department ROI
nova roi sales

# Check agent ROI
nova roi <agent_id>
```

### Optimize Costs

```bash
# Run auto-optimization
nova optimize

# Pause an agent
nova pause <agent_id>

# Resume an agent
nova resume <agent_id>

# Kill an agent permanently
nova kill <agent_id>
```

## 🎯 Your First 30 Minutes

### Minute 0-5: Setup
- Install dependencies
- Set API key
- Verify with `nova status`

### Minute 5-10: Deploy Test Agents
```bash
# Start with research (low cost)
nova deploy research trend_monitor --config='{"topic":"business automation"}'

# Deploy a monitoring agent
nova deploy operations system_monitor
```

### Minute 10-15: Make a Decision
```bash
# Ask CEO to evaluate an opportunity
nova decide "Should we build an automated content generation service?"

# Get Expert Council opinion
nova council "What's the best strategy for rapid revenue growth?"
```

### Minute 15-20: Check Costs
```bash
# See what you've spent
nova costs

# Check if on track
nova revenue

# Full system overview
nova status
```

### Minute 20-25: Deploy Revenue Agent
```bash
# Deploy DDS (if you have prospects to target)
nova deploy sales dds --config='{"vertical":"dentists","location":"Austin"}'

# Or deploy a content agent for marketing
nova deploy marketing content_creator --config='{"platform":"twitter","topic":"AI automation"}'
```

### Minute 25-30: Monitor & Optimize
```bash
# List all agents
nova agents

# Check ROI
nova roi sales

# Optimize if needed
nova optimize
```

## 🎓 Pro Tips

### Token Efficiency
- **Start small**: Deploy 1-2 agents first
- **Monitor closely**: Check costs frequently
- **Kill fast**: If ROI negative, pause immediately
- **Scale winners**: If agent has >300% ROI, scale it

### Cost Management
- Target: <5% of revenue on AI costs
- Alert threshold: 10% of revenue
- Auto-pause: Agents negative >3 days
- Daily budget: Check `nova costs --period today`

### Revenue Generation
- **DDS**: Best for B2B lead generation
- **Content**: Best for inbound marketing
- **Trend monitoring**: Find opportunities early
- **Council**: Validate before big bets

### Workflow
1. **Morning**: Check `nova status`
2. **Deploy**: Add agents based on opportunities
3. **Monitor**: Check `nova costs` throughout day
4. **Optimize**: Run `nova optimize` daily
5. **Evening**: Review `nova revenue`

## 🚨 Common Issues

### "ANTHROPIC_API_KEY not set"
```bash
export ANTHROPIC_API_KEY="your-key-here"
```

### "No module named 'anthropic'"
```bash
pip install anthropic
```

### "Database locked"
Wait a few seconds and retry. SQLite is single-writer.

### High costs
```bash
# Check what's expensive
nova costs

# Optimize immediately
nova optimize

# Pause expensive agents
nova agents
nova pause <agent_id>
```

## 📊 Understanding the Dashboard

### System Health Status
- **EXCELLENT**: >60% high performers, on track
- **GOOD**: >40% high performers, on track
- **FAIR**: >20% high performers
- **POOR**: <20% high performers

### Agent Performance
- **High Performer**: ROI >300%
- **Good**: ROI 100-300%
- **Low**: ROI 0-100%
- **Negative**: ROI <0% (pause/kill)

### Financial Status
- **HEALTHY**: AI costs <5% revenue
- **WARNING**: AI costs 5-10% revenue
- **CRITICAL**: AI costs >10% revenue

## 🎯 First Week Goals

### Day 1
- ✅ Setup complete
- ✅ 2-3 test agents deployed
- ✅ Understand dashboard
- Target: Spend <$5

### Day 2-3
- ✅ Deploy first revenue agent (DDS or content)
- ✅ Make first $50 revenue
- ✅ Monitor costs closely
- Target: ROI >200%

### Day 4-5
- ✅ Scale winning agents
- ✅ Pause/kill losers
- ✅ First Expert Council session
- Target: $200 revenue, <$10 costs

### Day 6-7
- ✅ Optimize workflow
- ✅ Deploy 5-10 agents
- ✅ Hit $500 weekly target
- Target: <5% AI cost ratio

## 💡 Next Steps

After mastering basics:

1. **Automate**: Set up cron jobs for monitoring
2. **Scale**: Deploy more high-ROI agents
3. **Optimize**: Tune token budgets per agent
4. **Integrate**: Connect more data sources
5. **Build**: Create custom agent types

## 📞 Need Help?

Check:
1. This guide
2. README.md for detailed docs
3. `nova status` for system health
4. `nova board` for strategic overview

## 🎉 Ready to Launch!

You're now ready to build a $200K/month AI business.

**Remember**:
- Deploy smart
- Optimize ruthlessly
- Scale what works
- Keep costs under 5%

Let's go! 🚀

```bash
nova status
```
