# NovaOS V2 Learning System - Setup Guide

## Installation

### 1. Install Dependencies

```bash
cd /Users/krissanders/novaos-v2
pip install -r requirements.txt
```

This installs:
- `chromadb>=0.4.22` - Local vector database
- `sentence-transformers>=2.2.2` - Embedding generation
- `numpy>=1.24.0` - Numerical operations

### 2. Verify Installation

```bash
python -c "import chromadb; import sentence_transformers; print('✓ Dependencies installed')"
```

### 3. Run Test Suite

```bash
python test_learning.py
```

Expected output:
```
============================================================
TEST 1: Initialize Learning System
============================================================
[Learning] Initializing sentence transformer...
[Learning] Initializing ChromaDB...
[Learning] Learning system initialized

Learning System Stats:
  Decisions in vector DB: 0
  Agents in vector DB: 0
  Opportunities in vector DB: 0
  Encoder Model: all-MiniLM-L6-v2
  ChromaDB Path: /Users/krissanders/novaos-v2/data/chroma_db

✓ Learning system initialized successfully

[... more tests ...]

============================================================
ALL TESTS PASSED ✓
============================================================
```

### 4. Run Integration Examples

```bash
python example_board_with_learning.py
```

Expected output:
```
======================================================================
EXAMPLE 1: Basic Decision with Learning Context
======================================================================

============================================================
BOARD DECISION: CFO
============================================================
Question: Should we increase marketing budget by $10,000 for Q2?
Type: budget_allocation

[Learning] Retrieving similar past decisions...

--- HISTORICAL CONTEXT ---
SIMILAR PAST DECISIONS (Last 3 times we faced something similar):
[... context ...]

[... decision process ...]

✓ Decision made: Approved with conditions
✓ Learning context was available

[... more examples ...]

======================================================================
ALL EXAMPLES COMPLETED SUCCESSFULLY ✓
======================================================================
```

## Directory Structure

After installation, you should have:

```
/Users/krissanders/novaos-v2/
├── core/
│   ├── __init__.py           # Updated with learning exports
│   ├── memory.py             # SQLite memory (existing)
│   ├── learning.py           # NEW: Learning system
│   └── LEARNING_README.md    # NEW: Quick reference
├── data/
│   ├── novaos.db            # SQLite database (existing)
│   └── chroma_db/           # NEW: ChromaDB storage (auto-created)
│       ├── chroma.sqlite3
│       └── [collection files]
├── requirements.txt          # Updated with new dependencies
├── test_learning.py          # NEW: Test suite
├── example_board_with_learning.py  # NEW: Integration examples
├── LEARNING_INTEGRATION.md   # NEW: Full integration guide
└── LEARNING_SETUP.md        # This file
```

## First-Time Setup

### Option 1: Fresh Start (No Existing Data)

Just start using the system:

```python
from core.learning import get_learning

learning = get_learning()
# System is ready!
```

### Option 2: Backfill from Existing SQLite Data

If you already have decisions/agents/opportunities in SQLite:

```python
from core.learning import get_learning

learning = get_learning()

# Sync last 30 days
counts = learning.sync_from_sqlite(days=30)

print(f"Synced:")
print(f"  Decisions: {counts['decisions']}")
print(f"  Agents: {counts['agents']}")
print(f"  Opportunities: {counts['opportunities']}")
```

### Option 3: Sync Everything

To backfill ALL historical data:

```python
from core.learning import get_learning

learning = get_learning()

# Sync last 365 days (or more if needed)
counts = learning.sync_from_sqlite(days=365)
```

## Quick Start Usage

### 1. Before Board Decision

```python
from core.learning import get_decision_context

# Get context from similar past decisions
context = get_decision_context(
    "Should we hire a new sales agent?",
    decision_type="hiring"
)

# Include in board agent prompt
prompt = f"""
Question: Should we hire a new sales agent?

Historical Context:
{context}

Please provide your recommendation.
"""
```

### 2. After Board Decision

```python
from core.memory import get_memory
from core.learning import get_learning

memory = get_memory()
learning = get_learning()

# Log in SQLite
decision_id = memory.log_decision(
    agent="CFO",
    decision_type="hiring",
    question="Should we hire a new sales agent?",
    decision="Approved",
    reasoning="Team at capacity, projected 3:1 ROI",
    tokens_used=2000,
    cost=0.08
)

# Store in learning system
learning.store_decision(
    decision_id=decision_id,
    context="Hiring decision for sales team",
    outcome=None,  # Update later
    metrics={'projected_roi': 3.0}
)
```

### 3. Update with Outcome

```python
# When you know the result
memory.update_decision_outcome(
    decision_id,
    "Hired successfully - Generated $120k in Q1"
)

# Re-store with outcome
learning.store_decision(
    decision_id=decision_id,
    context="",
    outcome="Hired successfully - Generated $120k in Q1",
    metrics={'actual_revenue': 120000, 'actual_roi': 4.8}
)
```

### 4. Weekly Review

```python
from core.learning import weekly_analysis

# Run analysis
analysis = weekly_analysis()

# Print recommendations
print("Weekly Recommendations:")
for rec in analysis['recommendations']:
    print(f"  • {rec}")
```

## Configuration

### Default Paths

The system uses these default paths:

```python
NovaLearning(
    db_path="/Users/krissanders/novaos-v2/data/novaos.db",
    chroma_path="/Users/krissanders/novaos-v2/data/chroma_db"
)
```

### Custom Paths

To use custom paths:

```python
from core.learning import NovaLearning

learning = NovaLearning(
    db_path="/custom/path/to/novaos.db",
    chroma_path="/custom/path/to/chroma_db"
)
```

### Embedding Model

Default model is `all-MiniLM-L6-v2`. To use a different model:

```python
# In core/learning.py, change line 38:
self.encoder = SentenceTransformer('all-MiniLM-L6-v2')

# To (for example):
self.encoder = SentenceTransformer('all-mpnet-base-v2')  # Higher quality, slower
```

Available models:
- `all-MiniLM-L6-v2` - Fast, efficient (default)
- `all-mpnet-base-v2` - Higher quality, slower
- `all-MiniLM-L12-v2` - Balanced
- See: https://www.sbert.net/docs/pretrained_models.html

## Monitoring

### Check System Stats

```python
from core.learning import get_learning

learning = get_learning()
stats = learning.get_stats()

print(f"Decisions: {stats['collections']['decisions']}")
print(f"Agents: {stats['collections']['agents']}")
print(f"Opportunities: {stats['collections']['opportunities']}")
```

### View Recent Items

```python
from core.memory import get_memory

memory = get_memory()

# Recent decisions
decisions = memory.get_recent_decisions(limit=10)
for d in decisions:
    print(f"[{d['timestamp']}] {d['agent']}: {d['question']}")

# Recent agents
agents = memory.get_all_agents(status='active')
for a in agents:
    print(f"{a['name']} ({a['department']}): {a['roi']:.1f}% ROI")
```

## Maintenance

### Weekly Sync (Recommended)

```python
from core.learning import get_learning

learning = get_learning()

# Sync last 7 days to catch any updates
learning.sync_from_sqlite(days=7)
```

### Monthly Cleanup (Optional)

ChromaDB is append-only, so old versions of items accumulate. To clean up:

```python
# 1. Backup current data
import shutil
shutil.copytree(
    "/Users/krissanders/novaos-v2/data/chroma_db",
    "/Users/krissanders/novaos-v2/data/chroma_db.backup"
)

# 2. Reset and re-sync
from core.learning import NovaLearning

learning = NovaLearning()
learning.chroma_client.reset()  # Clear all data

# 3. Re-sync from SQLite
learning = NovaLearning()  # Re-initialize
learning.sync_from_sqlite(days=365)  # Sync all
```

### Backup Strategy

1. **SQLite**: Already backed up (primary data source)
2. **ChromaDB**: Can be regenerated from SQLite
3. **Optional**: Backup ChromaDB directory for faster recovery

```bash
# Backup ChromaDB
cp -r /Users/krissanders/novaos-v2/data/chroma_db \
      /Users/krissanders/novaos-v2/data/chroma_db.backup

# Restore if needed
rm -rf /Users/krissanders/novaos-v2/data/chroma_db
cp -r /Users/krissanders/novaos-v2/data/chroma_db.backup \
      /Users/krissanders/novaos-v2/data/chroma_db
```

## Troubleshooting

### Issue: "No module named 'chromadb'"

```bash
# Solution: Install dependencies
pip install chromadb sentence-transformers numpy
```

### Issue: "No module named 'sentence_transformers'"

```bash
# Solution: Install sentence-transformers
pip install sentence-transformers
```

### Issue: ChromaDB initialization errors

```bash
# Solution: Remove corrupted DB and reinitialize
rm -rf /Users/krissanders/novaos-v2/data/chroma_db

# Then run Python:
python -c "from core.learning import get_learning; get_learning().sync_from_sqlite(30)"
```

### Issue: Slow embedding generation

```python
# Cause: Running on CPU (expected)
# Solution: This is normal, ~14k sentences/sec on CPU

# Optional: Use GPU if available
# Install: pip install sentence-transformers[gpu]
# Model will automatically use CUDA if available
```

### Issue: High memory usage

```
# Cause: Embedding model loaded in memory
# Solution: This is normal (~100MB), no action needed
# Model stays loaded for performance
```

### Issue: "No similar decisions found"

```python
# Cause: Empty vector database
# Solution: Sync from SQLite
from core.learning import get_learning
learning = get_learning()
learning.sync_from_sqlite(days=30)
```

## Performance Tips

### 1. Batch Operations

```python
# GOOD: Batch processing
decision_ids = [1, 2, 3, 4, 5]
for decision_id in decision_ids:
    learning.store_decision(decision_id, ...)

# AVOID: Single items with delays
for decision_id in decision_ids:
    learning.store_decision(decision_id, ...)
    time.sleep(1)  # Unnecessary
```

### 2. Limit Query Results

```python
# GOOD: Specific limits
similar = learning.query_similar(query, limit=3)

# AVOID: Large result sets
similar = learning.query_similar(query, limit=100)  # Slower
```

### 3. Use Filters

```python
# GOOD: Filter at query time
similar = learning.query_similar(
    query,
    filters={"decision_type": "hiring"}
)

# AVOID: Filter after query
similar = learning.query_similar(query, limit=100)
filtered = [s for s in similar if s['metadata']['decision_type'] == 'hiring']
```

## Next Steps

1. **Run tests**: `python test_learning.py`
2. **Review examples**: `python example_board_with_learning.py`
3. **Read integration guide**: `LEARNING_INTEGRATION.md`
4. **Integrate with board**: See `example_board_with_learning.py`
5. **Set up weekly reports**: Schedule `weekly_analysis()`

## Resources

- Main code: `/Users/krissanders/novaos-v2/core/learning.py`
- Quick reference: `/Users/krissanders/novaos-v2/core/LEARNING_README.md`
- Integration guide: `/Users/krissanders/novaos-v2/LEARNING_INTEGRATION.md`
- Tests: `/Users/krissanders/novaos-v2/test_learning.py`
- Examples: `/Users/krissanders/novaos-v2/example_board_with_learning.py`

## Support

If you encounter issues:
1. Check test output: `python test_learning.py`
2. Verify stats: `learning.get_stats()`
3. Check logs: Look for `[Learning]` prefix
4. Review troubleshooting section above
5. Try fresh sync: `learning.sync_from_sqlite(days=30)`

## Success Criteria

You're ready when:
- [ ] `pip install -r requirements.txt` succeeds
- [ ] `python test_learning.py` passes all tests
- [ ] `python example_board_with_learning.py` runs without errors
- [ ] `learning.get_stats()` shows collections created
- [ ] `get_decision_context()` returns formatted results

Congratulations! Your NovaOS Learning System is ready for production use.
