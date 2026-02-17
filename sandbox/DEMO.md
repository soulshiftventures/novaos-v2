# NovaOS V2 Sandbox Environment - Complete Demo

This demo walkthrough shows the complete sandbox workflow from project creation through R&D Council evaluation to production promotion.

## Overview

The sandbox environment provides:
- ✅ **Isolated workspace** with separate database
- ✅ **No production constraints** - experiment freely
- ✅ **Project management** - create, test, evaluate
- ✅ **Agent deployment** - deploy agents without budget limits
- ✅ **R&D Council evaluation** - expert analysis before promotion
- ✅ **Smooth promotion** - migrate successful projects to production

## Complete Workflow

### 1. Check Sandbox Status

```bash
cd /Users/krissanders/novaos-v2
./cli.py sandbox status
```

This shows:
- Total sandbox projects
- Active projects
- Deployed agents
- Total cost

### 2. Create a New Sandbox Project

```bash
./cli.py sandbox create "AI Content Generator" --description="Test automated content creation for marketing"
```

This will:
- Generate a unique project ID (e.g., `prj_abc12345`)
- Create an isolated workspace directory
- Register the project in sandbox.db
- No impact on production

**Note the project ID** - you'll need it for subsequent commands.

### 3. Deploy Agents in the Sandbox

Deploy agents to test your concept:

```bash
# Example: Deploy a content creator agent
./cli.py sandbox deploy prj_abc12345 content_creator \
  --name="Blog Writer" \
  --config='{"topic":"AI trends", "tone":"professional"}'
```

This:
- Creates agent with ID: `sandbox_prj_abc12345_content_creator_xyz123`
- Assigns 10x normal token budget (for testing)
- Registers in "sandbox" department (isolated)
- Tracks all costs separately

### 4. List Sandbox Projects

```bash
./cli.py sandbox list
```

Shows all projects with:
- Project name and ID
- Status (active/promoted/deleted)
- Number of agents
- Cost, revenue, ROI

### 5. View Project Details

```bash
./cli.py sandbox project prj_abc12345
```

Displays:
- Project metadata
- All deployed agents
- Agent performance metrics
- Total project metrics

### 6. Quick Evaluation (Free)

Before spending on R&D Council, do a quick metrics check:

```bash
./cli.py sandbox eval prj_abc12345
```

This shows:
- **Metrics**: ROI, profit, cost, revenue, agents
- **Criteria**:
  - ✓/✗ Positive ROI
  - ✓/✗ Profitable
  - ✓/✗ Has active agents
  - ✓/✗ Has sufficient data
- **Basic Recommendation**: STRONGLY_RECOMMEND / RECOMMEND / CONSIDER / NOT_READY

**Cost: FREE** (metrics-based only)

### 7. Comprehensive Evaluation (R&D Council)

For deeper strategic analysis, use the R&D Expert Council:

```bash
./cli.py sandbox eval prj_abc12345 --council
```

This provides:

#### Metrics Analysis
Same as quick evaluation

#### R&D Expert Council Analysis
Four expert perspectives:

1. **Thiel (Contrarian/Monopoly)**: Is this creating a monopoly position? What's the contrarian insight?

2. **Musk (First Principles/Speed)**: Can we break this down to fundamentals? How can we move faster?

3. **Graham (Fundamentals/PMF)**: Do users actually want this? Is there product-market fit?

4. **Taleb (Risk/Antifragility)**: What are the risks? How can we benefit from uncertainty?

#### Consensus
Synthesized recommendation from all four perspectives with specific action items.

#### Final Recommendation
- **PROMOTE**: Both metrics and council agree - ready for production
- **PROMOTE_WITH_CAUTION**: Metrics good, but council identified considerations
- **HOLD**: Make improvements based on council feedback
- **DO_NOT_PROMOTE**: Not ready - needs significant work

**Cost: ~$0.50** (worth it for strategic projects)

### 8. Promote to Production

If evaluation looks good:

```bash
./cli.py sandbox promote prj_abc12345
```

This wizard will:
1. Re-evaluate the project
2. Warn if NOT_READY (can override)
3. Migrate profitable agents (ROI > 0)
4. Remove sandbox metadata
5. Register in production database
6. Assign to proper departments
7. Mark project as "promoted"

**Migrated agents start fresh** in production with their proven configurations.

### 9. Kill Failed Projects

If a project doesn't work out:

```bash
./cli.py sandbox kill prj_abc12345
```

Optionally delete workspace:

```bash
./cli.py sandbox kill prj_abc12345 --delete
```

This:
- Kills all project agents
- Marks project as "deleted"
- Optionally removes workspace files
- No production impact

## Example Use Cases

### Use Case 1: Test New Agent Type

```bash
# Create project
PROJECT_ID=$(./cli.py sandbox create "DDS Prospecting Test" \
  --description="Test new vertical targeting" | grep "Project ID:" | awk '{print $3}')

# Deploy experimental agent
./cli.py sandbox deploy $PROJECT_ID dds_prospecting \
  --name="Dentist Prospector" \
  --config='{"vertical":"dentists", "region":"northeast"}'

# Let it run for a day...

# Quick eval
./cli.py sandbox eval $PROJECT_ID

# If promising, deep eval
./cli.py sandbox eval $PROJECT_ID --council

# If good, promote
./cli.py sandbox promote $PROJECT_ID
```

### Use Case 2: A/B Test Agent Configurations

```bash
# Create project
PROJECT_ID=$(./cli.py sandbox create "Content Strategy A/B Test" \
  --description="Compare aggressive vs conservative content")

# Deploy variant A
./cli.py sandbox deploy $PROJECT_ID content_creator \
  --name="Aggressive" \
  --config='{"tone":"bold", "frequency":"daily"}'

# Deploy variant B
./cli.py sandbox deploy $PROJECT_ID content_creator \
  --name="Conservative" \
  --config='{"tone":"professional", "frequency":"weekly"}'

# Let both run, compare metrics
./cli.py sandbox project $PROJECT_ID

# Evaluate with council
./cli.py sandbox eval $PROJECT_ID --council

# Promote only the winning variant
```

### Use Case 3: Personal Passion Project

```bash
# Create personal project
./cli.py sandbox create "AI Music Generator" \
  --description="Personal project: generate background music"

# Deploy experimental agents
./cli.py sandbox deploy $PROJECT_ID music_generator \
  --config='{"genre":"ambient", "mood":"calm"}'

# Test without production pressure
# No revenue tracking required
# No ROI concerns

# Only promote if it becomes viable
```

## Evaluation Decision Tree

```
┌─────────────────────┐
│  Deploy in Sandbox  │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│   Let Agents Run    │
│   (Test Period)     │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│   Quick Eval (FREE) │
└──────────┬──────────┘
           │
      ┌────┴────┐
      │         │
   NOT READY  PROMISING
      │         │
      ▼         ▼
   KILL    ┌─────────────────────┐
   OR      │ Council Eval ($0.50)│
   ITERATE └──────────┬──────────┘
                      │
              ┌───────┴───────┐
              │               │
           PROMOTE          HOLD
              │               │
              ▼               ▼
     ┌─────────────┐   ITERATE & RE-EVAL
     │ PRODUCTION  │
     └─────────────┘
```

## Best Practices

### 1. Start Small
- Create one project at a time
- Test with single agent first
- Scale after validation

### 2. Use Quick Eval First
- Free metrics check
- Identifies obvious failures quickly
- Save council cost for promising projects

### 3. Use Council for Strategic Decisions
- Projects with high investment potential
- Before major resource commitment
- When metrics are mixed (need expert view)

### 4. Document Experiments
- Use descriptive project names
- Add detailed descriptions
- Track what you're testing

### 5. Clean Up Failed Projects
- Kill unsuccessful experiments
- Delete workspaces to save space
- Keep sandbox organized

### 6. Monitor Costs
- Even sandbox costs real money
- Check project metrics regularly
- Kill runaway agents quickly

### 7. Promote Selectively
- Only promote proven concepts
- Trust the evaluation process
- Council recommendations are valuable

## CLI Command Reference

### Sandbox Status
```bash
./cli.py sandbox status
```

### Project Management
```bash
# Create
./cli.py sandbox create "Project Name" --description="Description"

# List all
./cli.py sandbox list

# View details
./cli.py sandbox project <project_id>

# Kill
./cli.py sandbox kill <project_id>
./cli.py sandbox kill <project_id> --delete  # Delete workspace too
```

### Agent Deployment
```bash
./cli.py sandbox deploy <project_id> <agent_type> \
  --name="Agent Name" \
  --config='{"key": "value"}'
```

### Evaluation
```bash
# Quick (free)
./cli.py sandbox eval <project_id>

# Comprehensive (with R&D Council)
./cli.py sandbox eval <project_id> --council
```

### Promotion
```bash
./cli.py sandbox promote <project_id>
```

## Troubleshooting

### "Project not found"
- Check project ID with `./cli.py sandbox list`
- Ensure you're using the correct project ID

### "Agent deployment failed"
- Verify agent type is valid
- Check config JSON syntax
- Review error message

### "Evaluation shows NOT_READY"
- Check if agents are running
- Verify sufficient test data (cost > 0)
- May need more testing time

### "Council evaluation failed"
- Check API key is configured
- Verify internet connection
- May need to retry

## Cost Management

### Sandbox Costs
- **Project creation**: FREE
- **Agent deployment**: FREE (registration only)
- **Agent operations**: Varies by usage
- **Quick evaluation**: FREE
- **Council evaluation**: ~$0.50 per project
- **Promotion**: FREE

### Cost Optimization Tips
1. Use quick eval before council eval
2. Kill underperforming agents quickly
3. Monitor sandbox status regularly
4. Only promote after council approval
5. Delete failed projects promptly

## What's Next?

After mastering the sandbox:
1. **Production deployment**: Scale successful agents
2. **Department integration**: Assign to Sales, Marketing, etc.
3. **Budget management**: Set token budgets
4. **ROI optimization**: Use auto-optimization
5. **Dashboard monitoring**: Visual tracking

## Support

- **Documentation**: `/sandbox/README.md`, `/sandbox/ARCHITECTURE.md`
- **Examples**: `/sandbox/example_usage.py`
- **CLI Help**: `./cli.py sandbox --help`
- **Issues**: Report bugs or suggestions

---

## Quick Start Commands

```bash
# 1. Create project
./cli.py sandbox create "My Test" --description="Testing new idea"

# 2. Deploy agent (replace PROJECT_ID)
./cli.py sandbox deploy PROJECT_ID agent_type --name="Test Agent"

# 3. Quick eval
./cli.py sandbox eval PROJECT_ID

# 4. Council eval (if promising)
./cli.py sandbox eval PROJECT_ID --council

# 5. Promote (if approved)
./cli.py sandbox promote PROJECT_ID
```

**You're ready to experiment safely!** 🚀
