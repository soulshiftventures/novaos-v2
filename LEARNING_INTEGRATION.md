# NovaOS V2 Learning System Integration Guide

## Overview

The Learning System provides vector-based memory and pattern analysis for NovaOS V2. It learns from every decision, agent deployment, and opportunity to improve future decision-making.

## Architecture

```
┌─────────────────────────────────────────────────────┐
│                   LEARNING SYSTEM                    │
├─────────────────────────────────────────────────────┤
│                                                       │
│  ┌──────────────┐     ┌────────────────┐           │
│  │   SQLite     │────▶│   ChromaDB     │           │
│  │  (Structured)│     │   (Vectors)    │           │
│  └──────────────┘     └────────────────┘           │
│         │                      │                     │
│         │                      │                     │
│  ┌──────▼──────────────────────▼────────┐           │
│  │   Sentence Transformers              │           │
│  │   (all-MiniLM-L6-v2)                │           │
│  └──────────────────────────────────────┘           │
│                                                       │
├─────────────────────────────────────────────────────┤
│                  KEY FEATURES                         │
├─────────────────────────────────────────────────────┤
│                                                       │
│  • Vector storage with ChromaDB (local, free)        │
│  • Semantic search for similar decisions             │
│  • Weekly pattern analysis                           │
│  • ROI tracking and recommendations                  │
│  • Integration with existing SQLite data             │
│                                                       │
└─────────────────────────────────────────────────────┘
```

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

Dependencies added:
- `chromadb>=0.4.22` - Local vector database
- `sentence-transformers>=2.2.2` - Embedding generation
- `numpy>=1.24.0` - Numerical operations

2. The system will automatically create the ChromaDB storage directory at:
```
/Users/krissanders/novaos-v2/data/chroma_db/
```

## Core Components

### 1. Vector Storage

Three collections in ChromaDB:
- **decisions**: Board decisions with context and outcomes
- **agent_deployments**: Agent configs and performance metrics
- **opportunities**: Market opportunities with evaluations

### 2. Embedding Model

Uses `all-MiniLM-L6-v2`:
- Fast: 14,000+ sentences/second
- Efficient: 384-dimensional embeddings
- Good quality: 0.68 performance on semantic similarity tasks
- Local: No API calls, completely free

### 3. Pattern Analysis

Weekly automatic analysis provides:
- Decision cost trends
- Agent ROI by department
- Opportunity conversion rates
- Actionable recommendations

## Integration Points

### 1. Board Decision-Making

**Before a decision**: Retrieve similar past decisions

```python
from core.learning import get_decision_context

# In board agent prompt/context
question = "Should we hire a new sales agent?"
context = get_decision_context(question, decision_type="hiring")

# Returns formatted summary:
# "SIMILAR PAST DECISIONS (Last 3 times we faced something similar):
#  1. [2024-02-10] CFO - hiring
#     Cost: $0.05 | Tokens: 1500
#     Outcome: yes
#     Relevance: 87.5%"
```

**After a decision**: Store for learning

```python
from core.memory import get_memory
from core.learning import get_learning

# 1. Log decision in SQLite (already doing this)
memory = get_memory()
decision_id = memory.log_decision(
    agent="CFO",
    decision_type="hiring",
    question="Should we hire a new sales agent?",
    decision="Approved - hire with $50k budget",
    reasoning="Sales team overloaded, projected 3:1 ROI",
    tokens_used=2000,
    cost=0.08
)

# 2. Store in vector database for learning
learning = get_learning()
learning.store_decision(
    decision_id=decision_id,
    context="Hiring decision for sales",
    outcome=None,  # Update later with actual outcome
    metrics={'budget': 50000, 'projected_roi': 3.0}
)

# 3. Later, update with outcome
memory.update_decision_outcome(
    decision_id,
    "Hired successfully - agent generated $150k in 3 months"
)
```

### 2. Agent Deployment Tracking

**When deploying an agent**:

```python
from core.memory import get_memory
from core.learning import get_learning

memory = get_memory()
learning = get_learning()

# 1. Register agent (already doing this)
agent_id = "sales_agent_001"
memory.register_agent(
    agent_id=agent_id,
    name="Sales Prospector",
    agent_type="prospecting",
    department="Sales",
    token_budget=100000,
    config={'focus': 'B2B SaaS'}
)

# 2. Store deployment in learning system
learning.store_agent_deployment(
    agent_id=agent_id,
    config={'focus': 'B2B SaaS', 'territory': 'North America'},
    performance={'tokens_used': 0, 'cost': 0, 'revenue': 0, 'roi': 0}
)
```

**Periodic updates** (e.g., daily):

```python
# Get current agent state
agent = memory.get_agent(agent_id)

# Update in learning system
learning.store_agent_deployment(
    agent_id=agent_id,
    config={'focus': 'B2B SaaS'},
    performance={
        'tokens_used': agent['tokens_used'],
        'cost': agent['total_cost'],
        'revenue': agent['revenue_generated'],
        'roi': agent['roi']
    }
)
```

### 3. Opportunity Learning

**When CMO identifies opportunity**:

```python
from core.memory import get_memory
from core.learning import get_learning

memory = get_memory()
learning = get_learning()

# 1. Log opportunity (already doing this)
opp_id = memory.log_opportunity(
    title="Enterprise AI Tool for Healthcare",
    description="Large hospital network looking for AI automation",
    source="LinkedIn prospecting",
    market_size="$100M addressable",
    status="identified",
    priority=1,
    potential_revenue=500000.0,
    confidence_score=0.9
)

# 2. Store in learning system
learning.store_opportunity(
    opp_id=opp_id,
    source="LinkedIn prospecting",
    evaluation={
        'confidence': 0.9,
        'potential_revenue': 500000.0
    },
    outcome=None  # Update later
)

# 3. Later, update with outcome
memory.update_opportunity_status(opp_id, "pursued", assigned_to="sales_team")
learning.store_opportunity(
    opp_id=opp_id,
    source="LinkedIn prospecting",
    evaluation={'confidence': 0.9},
    outcome="Pursued - Deal closed at $450k"
)
```

### 4. Weekly Analysis

**Automated weekly reports**:

```python
from core.learning import get_learning

learning = get_learning()

# Run analysis
analysis = learning.analyze_weekly()

# Get recommendations
recommendations = analysis['recommendations']

# Example output:
# [
#   "HIGH ROI OPPORTUNITY: Sales Prospector (Sales) has 342.5% ROI.
#    Consider increasing budget or replicating strategy.",
#
#   "NEGATIVE ROI AGENTS: 2 agents with negative ROI.
#    Review: Marketing Bot, Support Agent. Consider reallocation or shutdown."
# ]

# Use recommendations in board meeting
print("Weekly Recommendations:")
for rec in recommendations:
    print(f"  - {rec}")
```

### 5. Pattern Extraction

**Get strategic insights**:

```python
from core.learning import get_learning

learning = get_learning()

# Get all patterns
patterns = learning.get_patterns("all")

# Decision patterns
if 'decision_patterns' in patterns:
    print("Most expensive decision types:")
    for item in patterns['decision_patterns']['cost_by_type']:
        print(f"  {item['type']}: ${item['avg_cost']:.2f}")

# Agent patterns
if 'agent_patterns' in patterns:
    print("\nBest ROI by department:")
    for item in patterns['agent_patterns']['roi_by_department']:
        print(f"  {item['department']}: {item['avg_roi']:.1f}%")

# Opportunity patterns
if 'opportunity_patterns' in patterns:
    print("\nBest opportunity sources:")
    for item in patterns['opportunity_patterns']['by_source']:
        print(f"  {item['source']}: {item['pursuit_rate']:.1f}% pursued")
```

## Usage Examples

### Example 1: Board Meeting with Learning Context

```python
from core.learning import get_decision_context
from core.board import BoardAgent

# Get CFO
cfo = BoardAgent("CFO", "Claude Opus 4.5")

# Question for board
question = "Should we invest $10k in Google Ads campaign?"

# Get learning context
learning_context = get_decision_context(
    question,
    decision_type="marketing_investment"
)

# Build enhanced prompt
prompt = f"""
You are the CFO of NovaOS. The board is asking:

{question}

Here's what we learned from similar past decisions:

{learning_context}

Current financial state:
- Available budget: $50k
- Monthly revenue: $25k
- Marketing ROI last quarter: 2.5x

Based on past learnings and current state, what's your recommendation?
"""

response = cfo.query(prompt)
```

### Example 2: Automated Weekly Board Report

```python
from core.learning import get_learning
from datetime import datetime

def generate_weekly_report():
    learning = get_learning()
    analysis = learning.analyze_weekly()

    report = f"""
    NOVAOS WEEKLY PERFORMANCE REPORT
    Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}

    === DECISIONS ===
    Total Decisions: {analysis['decisions']['total_decisions']}
    Total Cost: ${analysis['decisions']['total_cost']:.2f}
    Avg Tokens: {analysis['decisions']['avg_tokens_per_decision']}

    === AGENTS ===
    Active Agents: {analysis['agents']['total_agents']}

    Top Performers:
    """

    for agent in analysis['agents']['high_performers'][:3]:
        report += f"\n  - {agent['name']}: {agent['roi']:.1f}% ROI (${agent['revenue']:.2f} revenue)"

    report += "\n\n=== RECOMMENDATIONS ===\n"
    for rec in analysis['recommendations']:
        report += f"\n  - {rec}"

    return report

# Use in dashboard or email
weekly_report = generate_weekly_report()
print(weekly_report)
```

### Example 3: Query Similar Agent Deployments

```python
from core.learning import get_learning

learning = get_learning()

# Before deploying a new agent, check similar deployments
similar_agents = learning.query_similar(
    query_text="B2B SaaS sales prospecting agent",
    collection_type="agents",
    limit=3
)

print("Similar agent deployments:")
for agent in similar_agents:
    meta = agent['metadata']
    print(f"\n{meta['agent_name']} ({meta['department']})")
    print(f"  ROI: {meta['roi']:.1f}%")
    print(f"  Cost: ${meta['cost']:.2f}")
    print(f"  Revenue: ${meta['revenue']:.2f}")
    print(f"  Relevance: {agent['relevance']:.1%}")
```

## API Reference

### NovaLearning Class

```python
from core.learning import NovaLearning

learning = NovaLearning(
    db_path="/path/to/novaos.db",
    chroma_path="/path/to/chroma_db"
)
```

#### Methods

**store_decision(decision_id, context, outcome=None, metrics=None)**
- Store decision in vector database
- Returns: bool (success)

**store_agent_deployment(agent_id, config, performance)**
- Store agent deployment data
- Returns: bool (success)

**store_opportunity(opp_id, source, evaluation, outcome=None)**
- Store opportunity data
- Returns: bool (success)

**query_similar(query_text, collection_type="decisions", limit=5, filters=None)**
- Query for similar items
- Returns: List[Dict] with content, metadata, relevance

**get_similar_decisions(question, decision_type=None, limit=3)**
- Get formatted decision context for board
- Returns: str (formatted summary)

**analyze_weekly()**
- Run weekly pattern analysis
- Returns: Dict with patterns and recommendations

**get_patterns(pattern_type="all")**
- Extract patterns from data
- Returns: Dict with decision, agent, opportunity patterns

**sync_from_sqlite(days=7)**
- Sync recent data from SQLite
- Returns: Dict with sync counts

**get_stats()**
- Get system statistics
- Returns: Dict with collection counts

### Convenience Functions

```python
from core.learning import (
    get_learning,           # Get singleton instance
    store_decision,         # Quick decision storage
    get_decision_context,   # Quick context retrieval
    weekly_analysis,        # Run weekly analysis
    get_recommendations     # Get recommendations only
)
```

## Performance Considerations

### Embedding Generation
- **Speed**: ~14,000 sentences/second
- **Memory**: ~100MB for model
- **Local**: No API calls, no costs

### ChromaDB Storage
- **Disk Usage**: ~1KB per item
- **Query Speed**: <100ms for similarity search
- **Scalability**: Handles 100K+ items easily

### SQLite Integration
- **Read Only**: Learning system only reads from SQLite
- **No Conflicts**: Safe to run alongside other operations
- **Sync**: Periodic sync recommended (weekly)

## Best Practices

1. **Store after completion**: Store decisions after they're made, not before
2. **Update outcomes**: Always update outcomes when known for better learning
3. **Regular sync**: Run `sync_from_sqlite()` weekly to keep vector DB updated
4. **Use context**: Always include learning context in board decisions
5. **Monitor recommendations**: Review weekly recommendations for strategic insights

## Troubleshooting

### Issue: "No similar decisions found"
- **Cause**: Fresh database with no data
- **Solution**: Run `sync_from_sqlite(days=30)` to backfill

### Issue: Slow embedding generation
- **Cause**: CPU limitations
- **Solution**: Model is already optimized; consider batching operations

### Issue: ChromaDB errors
- **Cause**: Corrupted database
- **Solution**: Delete chroma_db directory and re-sync

### Issue: High memory usage
- **Cause**: Large number of items in memory
- **Solution**: Normal for ML models; ~100MB is expected

## Future Enhancements

Potential improvements:
- Multi-modal learning (images, documents)
- Real-time pattern detection
- Predictive analytics (forecast ROI)
- A/B testing framework
- Cross-agent collaboration learning

## Support

For issues or questions:
1. Check test script: `python test_learning.py`
2. Review logs: Look for `[Learning]` prefix
3. Check stats: `learning.get_stats()`
4. Verify sync: `learning.sync_from_sqlite()`
