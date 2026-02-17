# NovaOS V2 Sandbox - User Guide

## What is the Sandbox?

The sandbox is your **safe experimentation space** where you can:
- ✅ Test wild ideas without risking production
- ✅ Deploy agents with no budget limits
- ✅ Get expert R&D Council evaluation
- ✅ Promote successful projects to production

## 5-Minute Quick Start

### 1. Create a Project

```bash
cd /Users/krissanders/novaos-v2
./cli.py sandbox create "My Test Project" --description="What I'm testing"
```

Copy the **Project ID** (looks like `prj_abc12345`)

### 2. Deploy an Agent

```bash
./cli.py sandbox deploy prj_abc12345 agent_type --name="Test Agent"
```

Replace `prj_abc12345` with your project ID and `agent_type` with the agent you want (e.g., `content_creator`, `dds_prospecting`).

### 3. Evaluate Your Project

**Quick check (free):**
```bash
./cli.py sandbox eval prj_abc12345
```

**Deep analysis with R&D Council (~$0.50):**
```bash
./cli.py sandbox eval prj_abc12345 --council
```

### 4. Promote or Kill

**If successful:**
```bash
./cli.py sandbox promote prj_abc12345
```

**If failed:**
```bash
./cli.py sandbox kill prj_abc12345
```

## Common Commands

```bash
# See all sandbox projects
./cli.py sandbox list

# See project details
./cli.py sandbox project prj_abc12345

# Check sandbox status
./cli.py sandbox status
```

## R&D Council Evaluation

The R&D Council provides expert analysis from 4 perspectives:

1. **Thiel** - Contrarian monopoly thinking
2. **Musk** - First principles and speed
3. **Graham** - Startup fundamentals and PMF
4. **Taleb** - Risk management and antifragility

Use council evaluation when:
- ✅ Project shows promise (positive basic metrics)
- ✅ You're considering production promotion
- ✅ You need strategic guidance
- ✅ Metrics are mixed and you need expert insight

**Cost: ~$0.50 per evaluation** (worth it for important decisions)

## Evaluation Recommendations

### PROMOTE
Both metrics and council agree - ready for production immediately.

### PROMOTE_WITH_CAUTION
Metrics are good, but council identified some considerations. Review their recommendations first.

### HOLD
Make improvements based on council feedback before promoting.

### DO_NOT_PROMOTE
Not ready for production - needs significant work or should be abandoned.

## Tips

💡 **Use quick eval first** - It's free and catches obvious issues

💡 **Use council for important projects** - Worth the cost for strategic decisions

💡 **Clean up failed projects** - Keep your sandbox organized

💡 **Monitor costs** - Even sandbox costs real money

💡 **Document your experiments** - Use clear names and descriptions

## Workflow

```
1. Create Project
   ↓
2. Deploy Agents
   ↓
3. Quick Eval (free)
   ↓
4a. Council Eval ($0.50) → 4b. Kill Failed Project
   ↓                              ↓
5. Promote to Production      Clean Up
```

## Example: Test New Agent

```bash
# Create
./cli.py sandbox create "DDS Test" --description="Test dentist prospecting"

# Deploy
./cli.py sandbox deploy prj_abc12345 dds_prospecting \
  --name="Dentist Bot" \
  --config='{"vertical":"dentists"}'

# Wait... let it run for a bit...

# Quick eval
./cli.py sandbox eval prj_abc12345

# If looks good, council eval
./cli.py sandbox eval prj_abc12345 --council

# If approved, promote
./cli.py sandbox promote prj_abc12345
```

## Help

```bash
# General help
./cli.py --help

# Sandbox help
./cli.py sandbox --help

# Specific command help
./cli.py sandbox create --help
```

## Full Documentation

- **Complete Demo**: `/sandbox/DEMO.md`
- **Architecture**: `/sandbox/ARCHITECTURE.md`
- **Detailed Guide**: `/sandbox/README.md`
- **Examples**: `/sandbox/example_usage.py`

---

**Ready to experiment!** 🚀
