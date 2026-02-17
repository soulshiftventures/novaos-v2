# Sandbox Environment - Quick Start

Get started with the NovaOS Sandbox in 5 minutes.

## What is Sandbox?

A risk-free environment to test ideas, experiment with agents, and prototype projects before production deployment.

**Key Points:**
- Completely isolated from production
- No budget constraints (10x normal limits)
- Easy promotion to production when successful
- Safe to experiment and fail

## 5-Minute Quick Start

### 1. Check Sandbox Status

```bash
./cli.py sandbox status
```

This shows all sandbox projects (empty initially).

### 2. Create Your First Project

```bash
./cli.py sandbox create "My First Test" --description "Testing the sandbox"
```

You'll get:
- A unique project ID (e.g., `prj_abc12345`)
- A workspace directory
- An isolated environment

### 3. Deploy an Agent

```bash
./cli.py sandbox deploy prj_abc12345 dds_prospecting \
  --name "Test Agent" \
  --config '{"vertical":"dentists","location":"NYC"}'
```

Replace `prj_abc12345` with your actual project ID.

### 4. Check Your Project

```bash
./cli.py sandbox project prj_abc12345
```

See:
- Project details
- Deployed agents
- Metrics (cost, revenue, ROI)

### 5. Evaluate When Ready

After your agent has run and generated some data:

```bash
./cli.py sandbox eval prj_abc12345
```

You'll get:
- Evaluation results
- Promotion recommendation
- Pass/fail criteria

### 6. Promote or Kill

If successful:
```bash
./cli.py sandbox promote prj_abc12345
```

If not successful:
```bash
./cli.py sandbox kill prj_abc12345 --delete
```

## Common Workflows

### Testing a New Agent Configuration

```bash
# 1. Create project
./cli.py sandbox create "DDS Test"

# 2. Deploy with test config
./cli.py sandbox deploy prj_xxx dds_prospecting \
  --config '{"vertical":"dentists","prospect_count":100}'

# 3. Let it run...

# 4. Evaluate
./cli.py sandbox eval prj_xxx

# 5. Promote if good
./cli.py sandbox promote prj_xxx
```

### Comparing Multiple Approaches

```bash
# 1. Create project
./cli.py sandbox create "A/B Test"

# 2. Deploy multiple variants
./cli.py sandbox deploy prj_xxx agent_type --name "Variant A" --config '{...}'
./cli.py sandbox deploy prj_xxx agent_type --name "Variant B" --config '{...}'

# 3. Compare results
./cli.py sandbox project prj_xxx

# 4. Promote best performers
./cli.py sandbox promote prj_xxx
```

### Personal Learning Project

```bash
# 1. Create learning project
./cli.py sandbox create "Learning AI Agents"

# 2. Experiment freely
./cli.py sandbox deploy prj_xxx trend_monitor --config '{...}'

# 3. When done, clean up
./cli.py sandbox kill prj_xxx --delete
```

## Key Commands

| Command | Description |
|---------|-------------|
| `sandbox status` | Show all sandbox projects |
| `sandbox create <name>` | Create new project |
| `sandbox list` | List projects with metrics |
| `sandbox project <id>` | Show project details |
| `sandbox deploy <id> <type>` | Deploy agent in project |
| `sandbox eval <id>` | Evaluate project |
| `sandbox promote <id>` | Promote to production |
| `sandbox kill <id>` | Delete project |

## Tips

1. **Name Projects Descriptively**: Makes it easier to track multiple experiments
2. **Use Descriptions**: Document what you're testing
3. **Evaluate Before Promoting**: Always check results first
4. **Clean Up**: Don't accumulate failed projects
5. **Start Small**: Test with one agent before deploying many

## What Gets Promoted?

When you promote a project:
- ✓ Agents with positive ROI
- ✓ Agent configurations
- ✓ Successful strategies
- ✗ Failed/killed agents
- ✗ Negative ROI agents

## Costs

Sandbox uses real API calls (Anthropic), but:
- Costs tracked separately from production
- 10x normal token budgets
- Not added to production metrics
- Still real money, so test responsibly

## Safety

- **Zero production impact**: Completely isolated
- **Reversible**: Can kill projects without trace
- **Evaluation gate**: Must pass checks before promotion
- **Confirmation required**: Promotion needs your OK

## Next Steps

1. **Read Full Docs**: See `README.md` for details
2. **Run Examples**: Check `example_usage.py`
3. **Create Project**: Start your first experiment
4. **Join Discussion**: Share what you're testing

## Help

```bash
# Get help for any command
./cli.py sandbox --help
./cli.py sandbox create --help
./cli.py sandbox deploy --help
```

## Example Session

```bash
# Start
$ ./cli.py sandbox create "My Test"
✓ Created sandbox project: My Test
  Project ID: prj_f8a3b2c1

# Deploy
$ ./cli.py sandbox deploy prj_f8a3b2c1 dds_prospecting \
  --name "Test DDS" \
  --config '{"vertical":"dentists","location":"NYC"}'
✓ Deployed dds_prospecting agent in sandbox project: My Test
  Agent ID: sandbox_prj_f8a3b2c1_dds_prospecting_9a2b4c

# Check status
$ ./cli.py sandbox project prj_f8a3b2c1
Name: My Test
Total Agents: 1
Active Agents: 1
...

# After testing...
$ ./cli.py sandbox eval prj_f8a3b2c1
Recommendation: STRONGLY_RECOMMEND
Reason: Excellent ROI (450%) and all criteria passed

# Promote!
$ ./cli.py sandbox promote prj_f8a3b2c1
✓ PROJECT PROMOTED TO PRODUCTION
Agents Migrated: 1
```

That's it! You're ready to experiment in the sandbox.

**Remember**: The sandbox is for testing. Promote winners, kill losers, iterate fast.
