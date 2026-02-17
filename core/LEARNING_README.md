# NovaOS V2 Learning System

## Quick Start

```python
from core.learning import get_learning, get_decision_context

# Initialize (automatic, singleton)
learning = get_learning()

# Before board decision: Get similar past decisions
context = get_decision_context(
    "Should we hire a new sales agent?",
    decision_type="hiring"
)

# After board decision: Store for learning
learning.store_decision(
    decision_id=123,
    context="Hiring decision for sales team",
    outcome="Hired - Agent generated $50k in 3 months",
    metrics={'revenue': 50000, 'roi': 4.0}
)

# Weekly analysis
analysis = learning.analyze_weekly()
print(analysis['recommendations'])
```

## Installation

```bash
pip install -r requirements.txt
```

This installs:
- `chromadb` - Local vector database (free, no API)
- `sentence-transformers` - Embeddings (local, no API)
- `numpy` - Numerical operations

## What It Does

### 1. Learns from Every Decision
- Stores decisions with context and outcomes
- Tracks costs, tokens, ROI
- Enables semantic search for similar decisions

### 2. Provides Historical Context
Before making a decision, retrieves similar past decisions:
```
"Last 3 times we did something similar:
 1. [2024-01-15] CFO approved $5k marketing budget
    Outcome: 3.5x ROI, generated $17.5k
 2. [2024-02-01] CFO approved $10k sales hire
    Outcome: 4.2x ROI, generated $42k in Q1
 3. [2024-02-10] CFO rejected $20k tool purchase
    Outcome: Found cheaper alternative saving $15k"
```

### 3. Analyzes Patterns Weekly
Automatic analysis identifies:
- High-ROI strategies
- Money pits to avoid
- Optimal timing patterns
- Agent performance trends

### 4. Generates Recommendations
Example recommendations:
```
"HIGH ROI OPPORTUNITY: Sales Prospector has 342% ROI.
 Consider increasing budget or replicating strategy."

"NEGATIVE ROI AGENTS: Marketing Bot at -25% ROI.
 Consider reallocation or shutdown."

"LOW CONFIDENCE OPPORTUNITIES: Avg confidence 45%.
 Need better market research or evaluation criteria."
```

## Core Methods

### Storage

```python
# Store decision
learning.store_decision(
    decision_id=123,
    context="Budget allocation for Q2",
    outcome="Approved - Revenue increased 20%",
    metrics={'revenue': 50000, 'roi': 3.0}
)

# Store agent deployment
learning.store_agent_deployment(
    agent_id="sales_001",
    config={'focus': 'B2B SaaS'},
    performance={'tokens_used': 10000, 'cost': 5.0, 'revenue': 20000, 'roi': 3.0}
)

# Store opportunity
learning.store_opportunity(
    opp_id=456,
    source="LinkedIn prospecting",
    evaluation={'confidence': 0.85, 'potential_revenue': 100000},
    outcome="Pursued - Deal closed at $95k"
)
```

### Retrieval

```python
# Get similar decisions (formatted for board)
context = learning.get_similar_decisions(
    "Should we increase marketing budget?",
    decision_type="budget_allocation",
    limit=3
)

# Query vector database directly
similar = learning.query_similar(
    query_text="B2B SaaS sales strategy",
    collection_type="agents",
    limit=5
)
```

### Analysis

```python
# Weekly analysis
analysis = learning.analyze_weekly()
# Returns: {
#   'decisions': {...},
#   'agents': {...},
#   'opportunities': {...},
#   'recommendations': [...]
# }

# Extract patterns
patterns = learning.get_patterns("all")
# Returns: {
#   'decision_patterns': {...},
#   'agent_patterns': {...},
#   'opportunity_patterns': {...}
# }
```

### Utility

```python
# Sync from SQLite (backfill)
counts = learning.sync_from_sqlite(days=30)

# Get statistics
stats = learning.get_stats()
# Returns: {
#   'collections': {
#     'decisions': 45,
#     'agents': 12,
#     'opportunities': 23
#   },
#   'encoder_model': 'all-MiniLM-L6-v2',
#   ...
# }
```

## Integration Pattern

### Complete Decision Workflow

```python
from core.memory import get_memory
from core.learning import get_learning, get_decision_context

memory = get_memory()
learning = get_learning()

# 1. BEFORE DECISION: Get historical context
question = "Should we hire a new developer?"
historical_context = get_decision_context(question, "hiring")

# 2. MAKE DECISION (with context)
# [Include historical_context in board agent prompt]

# 3. AFTER DECISION: Log in SQLite
decision_id = memory.log_decision(
    agent="CFO",
    decision_type="hiring",
    question=question,
    decision="Approved - hire at $90k/year",
    reasoning="Team capacity constrained, projected 3:1 ROI",
    tokens_used=2000,
    cost=0.08
)

# 4. STORE FOR LEARNING: Add to vector database
learning.store_decision(
    decision_id=decision_id,
    context="Hiring decision for engineering team",
    outcome=None,  # Update later
    metrics={'budget': 90000, 'projected_roi': 3.0}
)

# 5. LATER: Update with actual outcome
memory.update_decision_outcome(
    decision_id,
    "Hired successfully - Developer increased velocity 40%"
)

# Re-store with outcome for better learning
learning.store_decision(
    decision_id=decision_id,
    context="",
    outcome="Hired successfully - Developer increased velocity 40%",
    metrics={'actual_roi': 4.2}
)
```

## Performance

### Speed
- **Embedding generation**: ~14,000 sentences/second
- **Similarity search**: <100ms per query
- **Weekly analysis**: ~1-2 seconds for 1000 decisions

### Storage
- **Memory**: ~100MB for embedding model
- **Disk**: ~1KB per stored item
- **Scalability**: Handles 100K+ items easily

### Cost
- **Zero API costs**: Everything runs locally
- **No internet required**: Fully offline capable
- **Free forever**: ChromaDB and sentence-transformers are open source

## Architecture

```
┌─────────────────────────────────────┐
│        NovaOS Learning System        │
├─────────────────────────────────────┤
│                                      │
│  ┌────────────┐    ┌─────────────┐ │
│  │  SQLite    │───▶│  ChromaDB   │ │
│  │ (Source)   │    │  (Vectors)  │ │
│  └────────────┘    └─────────────┘ │
│         │                 │          │
│         └────────┬────────┘          │
│                  │                   │
│         ┌────────▼────────┐         │
│         │  all-MiniLM-L6  │         │
│         │   (Embeddings)  │         │
│         └─────────────────┘         │
│                                      │
│  Collections:                        │
│  • decisions (context + outcomes)    │
│  • agents (configs + performance)    │
│  • opportunities (evals + results)   │
│                                      │
└─────────────────────────────────────┘
```

## ChromaDB Collections

### 1. Decisions Collection
Stores: Board decisions with full context
```python
{
    'document': 'Decision: Should we... Reasoning: ... Outcome: ...',
    'metadata': {
        'decision_id': '123',
        'agent': 'CFO',
        'decision_type': 'budget_allocation',
        'cost': 0.05,
        'tokens_used': 1500,
        'has_outcome': 'yes'
    },
    'embedding': [0.123, -0.456, ...]  # 384 dimensions
}
```

### 2. Agents Collection
Stores: Agent deployments with performance
```python
{
    'document': 'Agent: Sales Prospector... Type: prospecting... ROI: 340%...',
    'metadata': {
        'agent_id': 'sales_001',
        'agent_name': 'Sales Prospector',
        'department': 'Sales',
        'tokens_used': 25000,
        'cost': 12.50,
        'revenue': 50000.0,
        'roi': 340.0
    },
    'embedding': [0.789, -0.234, ...]
}
```

### 3. Opportunities Collection
Stores: Market opportunities with evaluations
```python
{
    'document': 'Opportunity: Enterprise AI... Source: LinkedIn... Confidence: 0.85...',
    'metadata': {
        'opp_id': '456',
        'source': 'LinkedIn prospecting',
        'status': 'pursued',
        'priority': 1,
        'potential_revenue': 250000.0,
        'confidence_score': 0.85,
        'has_outcome': 'yes'
    },
    'embedding': [0.345, -0.678, ...]
}
```

## Testing

Run the comprehensive test suite:

```bash
python test_learning.py
```

This tests:
1. System initialization
2. Decision storage
3. Agent deployment tracking
4. Opportunity learning
5. Similarity queries
6. Weekly analysis
7. Pattern extraction
8. SQLite sync

## Examples

Run integration examples:

```bash
python example_board_with_learning.py
```

This demonstrates:
1. Basic decision with learning context
2. Hiring decision with history
3. Multiple decisions showing learning accumulation
4. Weekly board review with insights

## Best Practices

### 1. Always Provide Context Before Decisions
```python
# GOOD
context = get_decision_context(question, decision_type)
# [Include in board agent prompt]

# BAD
# Make decision without checking history
```

### 2. Update Outcomes When Known
```python
# GOOD
learning.store_decision(decision_id, context, outcome="Success - 3x ROI", metrics={...})

# BAD
learning.store_decision(decision_id, context, outcome=None)  # Never updated
```

### 3. Run Weekly Analysis
```python
# GOOD - Regular review
analysis = learning.analyze_weekly()
for rec in analysis['recommendations']:
    print(rec)

# BAD - Never review patterns
```

### 4. Sync Regularly
```python
# GOOD - Keep vector DB updated
learning.sync_from_sqlite(days=7)  # Weekly

# BAD - Vector DB gets stale
```

### 5. Use Specific Decision Types
```python
# GOOD - Specific types for better matching
decision_type="budget_allocation"
decision_type="hiring_engineering"

# BAD - Generic types
decision_type="decision"
decision_type="general"
```

## Troubleshooting

### No Similar Decisions Found
```python
# Cause: Empty vector database
# Solution: Sync from SQLite
learning.sync_from_sqlite(days=30)
```

### Slow Performance
```python
# Cause: Large batch operations
# Solution: Process in smaller batches
for decision_id in decision_ids[:100]:  # Batch of 100
    learning.store_decision(decision_id, ...)
```

### Memory Warnings
```python
# Cause: Normal for ML models
# Solution: ~100MB is expected, no action needed
```

### ChromaDB Errors
```python
# Cause: Corrupted database
# Solution: Reset and re-sync
import shutil
shutil.rmtree("/path/to/chroma_db")
learning = NovaLearning()  # Creates fresh DB
learning.sync_from_sqlite(days=30)
```

## Advanced Usage

### Custom Filters
```python
# Query only successful decisions
similar = learning.query_similar(
    "Marketing budget allocation",
    collection_type="decisions",
    filters={"has_outcome": "yes"}
)

# Query high-ROI agents only
similar = learning.query_similar(
    "B2B sales agent",
    collection_type="agents",
    filters={"department": "Sales"}
)
```

### Batch Processing
```python
# Efficiently process multiple items
from core.memory import get_memory

memory = get_memory()
decisions = memory.get_recent_decisions(limit=100)

for decision in decisions:
    learning.store_decision(
        decision['id'],
        decision['question'],
        decision.get('outcome')
    )
```

### Custom Analysis Periods
```python
# Analyze specific time periods
cursor = learning.conn.cursor()
cursor.execute("""
    SELECT * FROM decisions
    WHERE timestamp BETWEEN ? AND ?
""", (start_date, end_date))
```

## API Reference

See `LEARNING_INTEGRATION.md` for complete API documentation.

## Support

- Test script: `python test_learning.py`
- Examples: `python example_board_with_learning.py`
- Integration guide: `LEARNING_INTEGRATION.md`
- Main code: `core/learning.py`

## Future Roadmap

Planned enhancements:
- [ ] Multi-modal learning (images, documents)
- [ ] Real-time pattern alerts
- [ ] Predictive ROI forecasting
- [ ] A/B testing framework
- [ ] Cross-agent collaboration insights
- [ ] Decision simulation mode
- [ ] Custom embedding models
- [ ] Export/import learning data
