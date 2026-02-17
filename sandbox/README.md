# NovaOS V2 Sandbox Environment

**Isolated workspace for experimentation and prototyping**

## Overview

The Sandbox Environment provides a completely isolated space to test wild ideas, experiment with new AI capabilities, and prototype projects before committing production resources.

## Key Features

- **Isolated Database**: Separate `sandbox.db` - no production data contamination
- **No Budget Constraints**: Experiment freely (within reason - 10x normal token budgets)
- **Project-Based Organization**: Each project gets its own workspace
- **Easy Promotion**: One-command migration to production for successful projects
- **Risk-Free Testing**: Test without affecting production metrics, costs, or revenue tracking

## Use Cases

1. **Testing Wild Ideas**: Try experimental approaches without risk
2. **Personal Projects**: Passion projects that may not be business-critical
3. **Learning**: Explore new AI capabilities and techniques
4. **Prototyping**: Validate concepts before production deployment
5. **A/B Testing**: Compare different agent configurations

## Directory Structure

```
/sandbox/
├── manager.py           # Sandbox management system
├── sandbox.db          # Isolated SQLite database
├── projects/           # Project workspaces
│   ├── prj_abc123/    # Project workspace directory
│   ├── prj_def456/
└── README.md
```

## Quick Start

### 1. Create a Sandbox Project

```bash
./cli.py sandbox create "My Experiment" --description "Testing new prospecting agent config"
```

Output:
```
✓ Created sandbox project: My Experiment
  Project ID: prj_abc123
  Workspace: /Users/krissanders/novaos-v2/sandbox/projects/prj_abc123
```

### 2. Deploy Agents in Sandbox

```bash
# Deploy a test agent
./cli.py sandbox deploy prj_abc123 dds_prospecting \
  --name "Test DDS Agent" \
  --config '{"vertical":"dentists","location":"NYC"}'
```

### 3. Experiment Freely

Run your experiments, test configurations, iterate quickly. Costs are tracked separately from production.

### 4. Evaluate Results

```bash
./cli.py sandbox eval prj_abc123
```

Output shows:
- Project metrics (cost, revenue, ROI)
- Evaluation criteria (positive ROI, profitability, etc.)
- Recommendation (STRONGLY_RECOMMEND, RECOMMEND, CONSIDER, NOT_READY)

### 5. Promote to Production

If successful:
```bash
./cli.py sandbox promote prj_abc123
```

This migrates:
- Successful agents (positive ROI only)
- Configurations
- Best practices learned

### 6. Clean Up

If not successful:
```bash
./cli.py sandbox kill prj_abc123 --delete
```

## CLI Commands

### Sandbox Status
```bash
./cli.py sandbox status
```
Shows all sandbox projects and overall statistics.

### List Projects
```bash
./cli.py sandbox list
```
Lists all sandbox projects with metrics.

### Project Details
```bash
./cli.py sandbox project prj_abc123
```
Shows detailed information about a specific project.

### Deploy Agent
```bash
./cli.py sandbox deploy <project_id> <agent_type> [--name NAME] [--config CONFIG]
```

### Evaluate Project
```bash
./cli.py sandbox eval <project_id>
```

### Promote to Production
```bash
./cli.py sandbox promote <project_id>
```

### Kill Project
```bash
./cli.py sandbox kill <project_id> [--delete]
```
Use `--delete` to also remove workspace directory.

## Evaluation Criteria

Projects are evaluated on:

1. **Positive ROI**: Revenue > Costs
2. **Profitability**: Profit > 0
3. **Active Agents**: Has at least one active agent
4. **Sufficient Data**: Testing has occurred (costs incurred)

Recommendations:
- **STRONGLY_RECOMMEND**: ROI > 300% and all criteria passed
- **RECOMMEND**: ROI > 0% and all criteria passed
- **CONSIDER**: Positive ROI but missing some criteria
- **NOT_READY**: Not meeting criteria

## Promotion Process

When you promote a project:

1. **Evaluation**: System evaluates if ready for production
2. **Confirmation**: You confirm the promotion
3. **Agent Migration**: Successful agents migrate to production
   - Only agents with positive ROI
   - Only active/paused agents (not killed)
   - New production agent IDs generated
4. **Configuration Transfer**: Configs migrate with agents
5. **Project Marked**: Sandbox project marked as "promoted"

## Database Isolation

The sandbox uses a completely separate database (`sandbox.db`) with:
- Same schema as production
- Sandbox-specific tables (projects, experiments)
- No connection to production database
- Isolated cost/revenue tracking

This ensures:
- No pollution of production metrics
- Can test freely without consequences
- Clean slate for each project
- Easy cleanup

## Budget & Costs

Sandbox agents get:
- **10x normal token budgets** (vs production agents)
- **No strict cost limits** (within reason)
- **Isolated cost tracking** (not added to production)

This allows experimentation without financial anxiety.

## Best Practices

1. **Name Projects Clearly**: Use descriptive names
2. **Document Hypotheses**: Add descriptions explaining what you're testing
3. **Evaluate Before Promoting**: Always run evaluation first
4. **Clean Up Failed Projects**: Don't accumulate dead projects
5. **One Project Per Experiment**: Keep experiments isolated
6. **Track Results**: Use the experiments feature to log what you learn

## Python API

You can also use the sandbox programmatically:

```python
from sandbox.manager import get_sandbox

# Get sandbox manager
sandbox = get_sandbox()

# Create project
project_id = sandbox.create_project(
    name="My Experiment",
    description="Testing new approach"
)

# Deploy agent
agent_id = sandbox.deploy_agent(
    project_id=project_id,
    agent_type="dds_prospecting",
    config={"vertical": "dentists"}
)

# Get project
project = sandbox.get_project(project_id)
metrics = project.get_metrics()

# Evaluate
evaluation = sandbox.evaluate_project(project_id)

# Promote if successful
if evaluation['recommendation'] in ['RECOMMEND', 'STRONGLY_RECOMMEND']:
    result = sandbox.promote_project(project_id)
    print(f"Promoted! Migrated {result['agents_migrated']} agents")
```

## Experiments Feature

Track specific experiments within projects:

```python
# Log experiment
experiment_id = sandbox.log_experiment(
    project_id=project_id,
    name="Test 2x budget",
    hypothesis="Doubling token budget will improve lead quality",
    config={"token_budget": 20000}
)

# Complete experiment
sandbox.complete_experiment(
    experiment_id=experiment_id,
    results={"lead_quality": 8.5, "cost_per_lead": 2.30},
    success=True
)
```

## Integration with Production

Sandbox is designed to integrate seamlessly:

1. **Same Agent Types**: Use same agent types as production
2. **Compatible Configs**: Configurations transfer directly
3. **Smooth Promotion**: One command moves successful work to production
4. **No Manual Migration**: System handles all data transfer

## Examples

### Example 1: Test New DDS Configuration

```bash
# Create project
./cli.py sandbox create "DDS NYC Dentists Test"

# Deploy with test config
./cli.py sandbox deploy prj_abc123 dds_prospecting \
  --config '{"vertical":"dentists","location":"NYC","prospect_count":100}'

# Run tests, gather data...

# Evaluate
./cli.py sandbox eval prj_abc123
# Output: STRONGLY_RECOMMEND (ROI: 450%)

# Promote to production
./cli.py sandbox promote prj_abc123
```

### Example 2: Test Multiple Approaches

```bash
# Create project
./cli.py sandbox create "Content Strategy Test"

# Deploy multiple agents with different configs
./cli.py sandbox deploy prj_xyz789 content_creator \
  --name "LinkedIn Daily" \
  --config '{"platform":"linkedin","frequency":"daily"}'

./cli.py sandbox deploy prj_xyz789 content_creator \
  --name "Twitter Hourly" \
  --config '{"platform":"twitter","frequency":"hourly"}'

# Compare results
./cli.py sandbox project prj_xyz789

# Promote best performers
./cli.py sandbox promote prj_xyz789
```

### Example 3: Personal Learning Project

```bash
# Create learning project
./cli.py sandbox create "Learning AI Agents" \
  --description "Personal project to understand agent architectures"

# Experiment freely
./cli.py sandbox deploy prj_learning trend_monitor \
  --config '{"topic":"AI","sources":["twitter","reddit"]}'

# If just for learning, kill without promoting
./cli.py sandbox kill prj_learning --delete
```

## Safety Features

- **No Production Impact**: Completely isolated from production
- **Reversible**: Projects can be killed without trace
- **Evaluation Gate**: Must pass evaluation before promotion
- **Confirmation Required**: Promotion requires user confirmation
- **Selective Migration**: Only successful agents migrate

## Limitations

- Sandbox costs still use real API calls (Anthropic)
- Token budgets are 10x but not unlimited
- Can't promote agents with negative ROI
- Workspace cleanup is manual (with --delete flag)

## Tips

1. **Start Small**: Test with one agent before scaling
2. **Use Evaluation**: Always evaluate before promoting
3. **Check Metrics**: Monitor costs and ROI during testing
4. **Document Learning**: Use project descriptions to track insights
5. **Promote Winners**: Don't be afraid to promote successful experiments
6. **Kill Losers**: Clean up failed experiments promptly

## Support

For issues or questions:
- Check project metrics: `./cli.py sandbox project <project_id>`
- Review evaluation: `./cli.py sandbox eval <project_id>`
- Check sandbox status: `./cli.py sandbox status`
- Kill and restart if needed: `./cli.py sandbox kill <project_id>`

## Future Enhancements

Planned features:
- Time-limited experiments (auto-kill after duration)
- Experiment templates (pre-configured test scenarios)
- Comparison tools (compare multiple projects)
- Automatic rollback (if promoted agent performs poorly)
- Sandbox snapshots (save/restore project states)
- Cost limits per project (optional budget caps)
