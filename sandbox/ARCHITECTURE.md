# Sandbox Environment - Architecture

Technical documentation for the NovaOS V2 Sandbox Environment.

## Overview

The Sandbox Environment provides an isolated workspace for experimentation, prototyping, and testing before production deployment. It implements a complete project lifecycle from creation through evaluation to production promotion.

## Architecture

### High-Level Design

```
┌─────────────────────────────────────────────────────────┐
│                    NovaOS V2                             │
│  ┌──────────────┐                  ┌──────────────┐    │
│  │  Production  │                  │   Sandbox    │    │
│  │              │                  │              │    │
│  │  novaos.db   │                  │  sandbox.db  │    │
│  │              │                  │              │    │
│  │  Real agents │◄─── Promotion ──│ Test agents  │    │
│  │  Real costs  │                  │ Test costs   │    │
│  │  Real revenue│                  │ Test revenue │    │
│  └──────────────┘                  └──────────────┘    │
└─────────────────────────────────────────────────────────┘
```

### Component Structure

```
/sandbox/
├── __init__.py              # Package initialization
├── manager.py               # Core sandbox manager
│   ├── SandboxMemory        # Isolated database layer
│   ├── SandboxProject       # Project representation
│   └── SandboxManager       # Main manager class
├── sandbox.db              # Isolated SQLite database
├── projects/               # Project workspaces
│   └── prj_<id>/          # Individual project directories
├── README.md               # User documentation
├── QUICKSTART.md           # Quick start guide
├── ARCHITECTURE.md         # This file
└── example_usage.py        # Example code
```

## Database Schema

### Sandbox-Specific Tables

#### sandbox_projects
```sql
CREATE TABLE sandbox_projects (
    id TEXT PRIMARY KEY,              -- prj_<uuid>
    name TEXT NOT NULL,               -- Project name
    description TEXT,                 -- Project description
    status TEXT NOT NULL,             -- active|promoted|deleted
    created_at TEXT NOT NULL,         -- ISO timestamp
    workspace_path TEXT,              -- File system path
    deployed_agents TEXT,             -- JSON array of agent IDs
    results TEXT,                     -- JSON evaluation results
    evaluation TEXT,                  -- JSON evaluation data
    promoted_at TEXT                  -- ISO timestamp when promoted
)
```

#### sandbox_experiments
```sql
CREATE TABLE sandbox_experiments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id TEXT NOT NULL,         -- Foreign key to sandbox_projects
    name TEXT NOT NULL,               -- Experiment name
    hypothesis TEXT,                  -- What you're testing
    config TEXT,                      -- JSON configuration
    results TEXT,                     -- JSON results
    started_at TEXT NOT NULL,         -- ISO timestamp
    completed_at TEXT,                -- ISO timestamp
    success BOOLEAN,                  -- Success flag
    FOREIGN KEY (project_id) REFERENCES sandbox_projects(id)
)
```

### Inherited Tables

The sandbox inherits all production tables (decisions, agents, costs, revenue, etc.) but writes to a separate database file.

## Classes

### SandboxMemory

Extends `NovaMemory` with sandbox-specific tables and methods.

**Key Methods:**
- `_initialize_db()`: Creates sandbox and production tables
- Inherits all methods from `NovaMemory`

### SandboxProject

Represents a single sandbox project with isolated workspace.

**Attributes:**
- `project_id`: Unique project identifier
- `name`: Human-readable name
- `description`: Project description
- `workspace_path`: File system workspace directory
- `memory`: Reference to SandboxMemory
- `deployed_agents`: List of agent IDs

**Key Methods:**
- `get_metrics()`: Calculate project metrics (cost, revenue, ROI)
- `deploy_agent(agent_type, name, config)`: Deploy agent in project
- `list_agents()`: List all agents in project
- `get_results()`: Get complete project results for evaluation

### SandboxManager

Main manager class for sandbox operations.

**Key Methods:**

#### Project Management
- `create_project(name, description)`: Create new sandbox project
- `get_project(project_id)`: Retrieve project by ID
- `list_projects()`: List all projects with metrics
- `kill_project(project_id, delete_workspace)`: Delete project

#### Agent Deployment
- `deploy_agent(project_id, agent_type, config)`: Deploy agent in project

#### Experimentation
- `log_experiment(project_id, name, hypothesis, config)`: Log experiment
- `complete_experiment(experiment_id, results, success)`: Mark experiment complete

#### Evaluation & Promotion
- `evaluate_project(project_id)`: Evaluate project for promotion
- `promote_project(project_id)`: Promote successful project to production

#### Reporting
- `get_summary()`: Get sandbox environment summary

## Data Flow

### 1. Project Creation

```
User Request
    ↓
SandboxManager.create_project()
    ↓
Generate unique project ID (prj_<uuid>)
    ↓
Create workspace directory
    ↓
Insert into sandbox_projects table
    ↓
Return project ID
```

### 2. Agent Deployment

```
User Request
    ↓
SandboxManager.deploy_agent()
    ↓
Get project
    ↓
SandboxProject.deploy_agent()
    ↓
Generate sandbox agent ID (sandbox_<project_id>_<type>_<uuid>)
    ↓
Register in agents table (sandbox database)
    ↓
Update project.deployed_agents
    ↓
Return agent ID
```

### 3. Evaluation

```
User Request
    ↓
SandboxManager.evaluate_project()
    ↓
Get project metrics (cost, revenue, ROI, agents)
    ↓
Check evaluation criteria:
  - Positive ROI?
  - Profitable?
  - Active agents?
  - Sufficient data?
    ↓
Calculate recommendation:
  - STRONGLY_RECOMMEND (ROI > 300% + all pass)
  - RECOMMEND (ROI > 0% + all pass)
  - CONSIDER (positive ROI, some pass)
  - NOT_READY (not meeting criteria)
    ↓
Save evaluation to project
    ↓
Return evaluation
```

### 4. Promotion to Production

```
User Request
    ↓
SandboxManager.promote_project()
    ↓
Evaluate project (if not already done)
    ↓
Check recommendation (warn if NOT_READY)
    ↓
Get production memory instance
    ↓
For each agent in project:
  - Skip if not active/paused
  - Skip if negative ROI
  - Generate new production agent ID
  - Remove sandbox metadata from config
  - Register in production database
  - Track migration
    ↓
Mark project as "promoted"
    ↓
Return migration results
```

## Agent ID Conventions

### Sandbox Agents
```
sandbox_<project_id>_<agent_type>_<uuid>
```

Example: `sandbox_prj_abc123_dds_prospecting_9a2b4c`

### Production Agents
```
<agent_type>_<uuid>
```

Example: `dds_prospecting_7f3e2a1d`

## Isolation Mechanisms

### 1. Separate Database
- Production: `/data/novaos.db`
- Sandbox: `/sandbox/sandbox.db`
- No connection between databases
- Complete data isolation

### 2. Agent Naming
- Sandbox agents prefixed with `sandbox_`
- Easy to identify sandbox vs production
- Prevents accidental mixing

### 3. Department Separation
- All sandbox agents in "sandbox" department
- Production agents in real departments
- Prevents metric contamination

### 4. Config Metadata
- Sandbox agents have `sandbox_mode: true` in config
- `sandbox_project: <project_id>` in config
- Removed during promotion

## Budget & Token Management

### Token Budgets

Sandbox agents receive 10x normal token budgets:

```python
# Production agent
token_budget = EXECUTION_AGENT_BUDGET  # e.g., 1000

# Sandbox agent
token_budget = EXECUTION_AGENT_BUDGET * 10  # e.g., 10,000
```

This allows more aggressive testing without hitting limits.

### Cost Tracking

- All API costs tracked in sandbox database
- Not added to production cost metrics
- Enables accurate ROI calculation
- Helps evaluate production viability

## Evaluation Criteria

### Criteria Checked

1. **Positive ROI**: `revenue > costs`
2. **Profitability**: `profit > 0`
3. **Active Agents**: At least one active agent
4. **Sufficient Data**: Some costs incurred (testing occurred)

### Recommendation Logic

```python
if all_criteria_pass and roi > 300:
    return "STRONGLY_RECOMMEND"
elif all_criteria_pass and roi > 0:
    return "RECOMMEND"
elif positive_roi and has_data:
    return "CONSIDER"
else:
    return "NOT_READY"
```

## CLI Integration

### Command Structure

```
./cli.py sandbox <command> [arguments]
```

### Available Commands

| Command | Handler | Description |
|---------|---------|-------------|
| `status` | `cmd_sandbox_status` | Show sandbox summary |
| `create` | `cmd_sandbox_create` | Create new project |
| `list` | `cmd_sandbox_list` | List all projects |
| `project` | `cmd_sandbox_project` | Show project details |
| `deploy` | `cmd_sandbox_deploy` | Deploy agent in project |
| `eval` | `cmd_sandbox_eval` | Evaluate project |
| `promote` | `cmd_sandbox_promote` | Promote to production |
| `kill` | `cmd_sandbox_kill` | Delete project |

### Command Flow

```
cli.py main()
    ↓
Parse arguments
    ↓
Check if command == 'sandbox'
    ↓
Parse sandbox_command
    ↓
Route to sandbox handler
    ↓
Call SandboxManager method
    ↓
Format and display results
```

## Promotion Migration

### What Gets Migrated

✓ **Migrated:**
- Agents with positive ROI
- Agent configurations
- Agent type information
- Department assignments

✗ **Not Migrated:**
- Historical cost data
- Historical revenue data
- Failed agents
- Negative ROI agents
- Sandbox metadata

### Migration Process

1. Filter agents (positive ROI, active/paused)
2. Generate new production agent IDs
3. Clean configuration (remove sandbox metadata)
4. Register in production database
5. Track migration results
6. Mark project as promoted

## Error Handling

### Common Errors

1. **Project Not Found**
   ```python
   if not project:
       raise ValueError(f"Project {project_id} not found")
   ```

2. **Agent Registration Failed**
   ```python
   if not success:
       raise Exception(f"Failed to register sandbox agent {agent_id}")
   ```

3. **Database Errors**
   - Handled by sqlite3 exceptions
   - Transactions rolled back on failure

### Safety Checks

- Evaluation before promotion
- User confirmation for promotion
- Workspace deletion confirmation
- ROI checks before migration

## Performance Considerations

### Database

- Single SQLite file per sandbox
- Separate from production (no locking conflicts)
- Indexed on project_id and agent_id
- Vacuum periodically for cleanup

### Workspace

- One directory per project
- No shared state between projects
- Easy cleanup with `--delete` flag

### Memory

- Singleton SandboxManager instance
- Projects loaded on demand
- Metrics calculated on request

## Extension Points

### Custom Evaluation Criteria

Add new criteria in `evaluate_project()`:

```python
# Check custom criterion
meets_custom = custom_check(project)
evaluation['criteria']['custom_check'] = {
    'pass': meets_custom,
    'value': custom_value,
    'threshold': custom_threshold
}
```

### Custom Agent Types

Deploy any agent type that production supports:

```python
agent_id = sandbox.deploy_agent(
    project_id=project_id,
    agent_type="my_custom_agent",
    config={...}
)
```

### Custom Experiments

Track custom experiment data:

```python
experiment_id = sandbox.log_experiment(
    project_id=project_id,
    name="Custom Test",
    hypothesis="Testing custom approach",
    config={"custom_param": value}
)
```

## Security

### Isolation

- Separate database file
- No cross-contamination with production
- Workspace directories isolated

### Access Control

- Same access as production NovaOS
- No additional authentication needed
- File system permissions apply

### Data Protection

- Sandbox data not in production DB
- Easy to delete entire sandbox
- No impact on production data

## Testing

### Unit Tests

Test individual components:

```python
def test_create_project():
    sandbox = get_sandbox()
    project_id = sandbox.create_project("Test", "Desc")
    assert project_id.startswith("prj_")
```

### Integration Tests

Test full workflows:

```python
def test_full_workflow():
    # Create, deploy, evaluate, promote
    sandbox = get_sandbox()
    project_id = sandbox.create_project("Test", "Desc")
    agent_id = sandbox.deploy_agent(project_id, "type", {})
    eval = sandbox.evaluate_project(project_id)
    assert eval is not None
```

### CLI Tests

Test CLI commands:

```bash
./cli.py sandbox create "Test"
./cli.py sandbox list
./cli.py sandbox status
```

## Future Enhancements

1. **Time-Limited Experiments**: Auto-kill after duration
2. **Experiment Templates**: Pre-configured test scenarios
3. **Comparison Tools**: Compare multiple projects
4. **Automatic Rollback**: Revert if promoted agent fails
5. **Sandbox Snapshots**: Save/restore project states
6. **Cost Limits**: Optional per-project budget caps
7. **Scheduled Evaluations**: Auto-evaluate on schedule
8. **Notifications**: Alert on experiment completion

## API Reference

See `manager.py` docstrings for complete API documentation.

### Key Signatures

```python
class SandboxManager:
    def create_project(name: str, description: str = None) -> str
    def get_project(project_id: str) -> Optional[SandboxProject]
    def list_projects() -> List[Dict]
    def deploy_agent(project_id: str, agent_type: str, config: Dict = None) -> str
    def evaluate_project(project_id: str) -> Dict[str, Any]
    def promote_project(project_id: str, production_memory_path: str = None) -> Dict[str, Any]
    def kill_project(project_id: str, delete_workspace: bool = False) -> bool
    def get_summary() -> Dict[str, Any]
```

## Troubleshooting

### Issue: Project not found
**Solution**: Check project ID with `sandbox list`

### Issue: Agent deployment fails
**Solution**: Verify agent type is valid, check config format

### Issue: Promotion fails
**Solution**: Run evaluation first, check for positive ROI

### Issue: Database locked
**Solution**: Close other connections, restart if needed

## Best Practices

1. **One Experiment Per Project**: Keep projects focused
2. **Clear Naming**: Use descriptive project names
3. **Document Hypotheses**: Use descriptions and experiments
4. **Evaluate First**: Always evaluate before promoting
5. **Clean Up**: Delete failed projects promptly
6. **Monitor Costs**: Even sandbox costs real money
7. **Iterative Testing**: Create, test, evaluate, promote, repeat

## Conclusion

The Sandbox Environment provides a complete, isolated workspace for safe experimentation. Its architecture ensures zero production impact while maintaining easy promotion of successful experiments. The system is designed for rapid iteration, safe testing, and smooth production integration.
