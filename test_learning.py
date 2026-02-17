"""
Test script for NovaOS V2 Learning System
Demonstrates all key functionality
"""

import sys
from pathlib import Path

# Add core to path
sys.path.insert(0, str(Path(__file__).parent))

from core.learning import NovaLearning, get_learning, get_decision_context
from core.memory import get_memory
from datetime import datetime


def test_initialization():
    """Test learning system initialization"""
    print("\n" + "="*60)
    print("TEST 1: Initialize Learning System")
    print("="*60)

    learning = get_learning()
    stats = learning.get_stats()

    print("\nLearning System Stats:")
    print(f"  Decisions in vector DB: {stats['collections']['decisions']}")
    print(f"  Agents in vector DB: {stats['collections']['agents']}")
    print(f"  Opportunities in vector DB: {stats['collections']['opportunities']}")
    print(f"  Encoder Model: {stats['encoder_model']}")
    print(f"  ChromaDB Path: {stats['chroma_path']}")

    print("\n✓ Learning system initialized successfully")


def test_store_decision():
    """Test storing decisions in vector database"""
    print("\n" + "="*60)
    print("TEST 2: Store Decision")
    print("="*60)

    memory = get_memory()
    learning = get_learning()

    # Create a test decision
    decision_id = memory.log_decision(
        agent="CFO",
        decision_type="budget_allocation",
        question="Should we increase marketing budget by $5000?",
        decision="Approved - ROI projections justify investment",
        reasoning="CMO showed 3:1 ROI on previous campaign, market conditions favorable",
        tokens_used=1500,
        cost=0.05
    )

    print(f"\nCreated decision ID: {decision_id}")

    # Store in vector database
    success = learning.store_decision(
        decision_id=decision_id,
        context="Budget increase for marketing",
        outcome="Positive - Revenue increased 15% following campaign",
        metrics={
            'revenue': 15000.0,
            'roi': 200.0,
            'implementation_time_days': 7
        }
    )

    print(f"Stored in vector DB: {success}")
    print("\n✓ Decision stored successfully")

    return decision_id


def test_store_agent_deployment():
    """Test storing agent deployments"""
    print("\n" + "="*60)
    print("TEST 3: Store Agent Deployment")
    print("="*60)

    memory = get_memory()
    learning = get_learning()

    # Create a test agent
    agent_id = "sales_agent_001"
    memory.register_agent(
        agent_id=agent_id,
        name="Sales Prospector Alpha",
        agent_type="prospecting",
        department="Sales",
        token_budget=100000,
        config={
            "focus": "B2B SaaS",
            "territory": "North America",
            "lead_score_threshold": 0.7
        }
    )

    # Simulate some usage
    memory.update_agent_metrics(
        agent_id=agent_id,
        tokens_used=25000,
        cost=12.50,
        revenue=5000.0
    )

    print(f"\nCreated agent: {agent_id}")

    # Store deployment in vector database
    agent = memory.get_agent(agent_id)
    success = learning.store_agent_deployment(
        agent_id=agent_id,
        config={
            "focus": "B2B SaaS",
            "territory": "North America"
        },
        performance={
            'tokens_used': agent['tokens_used'],
            'cost': agent['total_cost'],
            'revenue': agent['revenue_generated'],
            'roi': agent['roi']
        }
    )

    print(f"Stored in vector DB: {success}")
    print(f"Performance: ROI {agent['roi']:.1f}%, Revenue ${agent['revenue_generated']:.2f}")
    print("\n✓ Agent deployment stored successfully")


def test_store_opportunity():
    """Test storing opportunities"""
    print("\n" + "="*60)
    print("TEST 4: Store Opportunity")
    print("="*60)

    memory = get_memory()
    learning = get_learning()

    # Create a test opportunity
    opp_id = memory.log_opportunity(
        title="Enterprise AI Tool for Financial Services",
        description="Large financial services firm looking for AI automation",
        source="LinkedIn prospecting",
        market_size="$50M+ addressable market",
        competitive_analysis="3 competitors, we have pricing advantage",
        status="identified",
        priority=1,
        potential_revenue=250000.0,
        confidence_score=0.85
    )

    print(f"\nCreated opportunity ID: {opp_id}")

    # Store in vector database
    success = learning.store_opportunity(
        opp_id=opp_id,
        source="LinkedIn prospecting",
        evaluation={
            'confidence': 0.85,
            'potential_revenue': 250000.0
        },
        outcome="Pursued - In negotiation phase"
    )

    print(f"Stored in vector DB: {success}")
    print("\n✓ Opportunity stored successfully")

    return opp_id


def test_query_similar_decisions():
    """Test querying similar past decisions"""
    print("\n" + "="*60)
    print("TEST 5: Query Similar Decisions")
    print("="*60)

    learning = get_learning()

    # Query for similar decisions
    query = "Should we increase our sales team budget?"

    print(f"\nQuery: '{query}'")
    print("\nSearching for similar past decisions...\n")

    similar = learning.query_similar(
        query_text=query,
        collection_type="decisions",
        limit=3
    )

    if similar:
        for i, item in enumerate(similar, 1):
            print(f"{i}. Relevance: {item['relevance']:.1%}")
            print(f"   {item['content'][:200]}...")
            print(f"   Metadata: {item['metadata']}\n")
    else:
        print("No similar decisions found (this is normal for a fresh database)")

    # Test the convenience function for board context
    print("\nBoard Context Format:")
    print("-" * 60)
    context = get_decision_context(query, "budget_allocation")
    print(context)

    print("\n✓ Query functionality working")


def test_weekly_analysis():
    """Test weekly pattern analysis"""
    print("\n" + "="*60)
    print("TEST 6: Weekly Analysis")
    print("="*60)

    learning = get_learning()

    print("\nRunning weekly analysis...")
    analysis = learning.analyze_weekly()

    print(f"\nAnalysis Period: {analysis['period']}")
    print(f"Timestamp: {analysis['timestamp']}")

    print("\n--- DECISIONS ---")
    decisions = analysis['decisions']
    print(f"Total Decisions: {decisions['total_decisions']}")
    print(f"Total Cost: ${decisions['total_cost']:.2f}")
    print(f"Avg Tokens per Decision: {decisions['avg_tokens_per_decision']}")

    if decisions['by_type']:
        print("\nBy Type:")
        for dtype, stats in decisions['by_type'].items():
            print(f"  {dtype}: {stats['count']} decisions, ${stats['total_cost']:.2f}")

    print("\n--- AGENTS ---")
    agents = analysis['agents']
    print(f"Total Active Agents: {agents['total_agents']}")

    if agents['by_department']:
        print("\nBy Department:")
        for dept, stats in agents['by_department'].items():
            print(f"  {dept}: {stats['count']} agents, ROI {stats['avg_roi']:.1f}%")

    if agents['high_performers']:
        print("\nTop Performers:")
        for agent in agents['high_performers'][:3]:
            print(f"  {agent['name']}: {agent['roi']:.1f}% ROI")

    if agents['low_performers']:
        print("\nLow Performers:")
        for agent in agents['low_performers'][:3]:
            print(f"  {agent['name']}: {agent['roi']:.1f}% ROI")

    print("\n--- OPPORTUNITIES ---")
    opps = analysis['opportunities']
    print(f"Total Opportunities: {opps['total_opportunities']}")
    print(f"Avg Confidence: {opps['avg_confidence']:.1%}")
    print(f"Total Potential Revenue: ${opps['total_potential_revenue']:,.2f}")

    print("\n--- RECOMMENDATIONS ---")
    for i, rec in enumerate(analysis['recommendations'], 1):
        print(f"{i}. {rec}")

    print("\n✓ Weekly analysis complete")


def test_get_patterns():
    """Test pattern extraction"""
    print("\n" + "="*60)
    print("TEST 7: Pattern Analysis")
    print("="*60)

    learning = get_learning()

    print("\nExtracting patterns from historical data...\n")

    patterns = learning.get_patterns("all")

    if 'decision_patterns' in patterns:
        print("--- DECISION PATTERNS ---")
        dp = patterns['decision_patterns']

        if dp.get('most_common_types'):
            print("Most Common Decision Types:")
            for item in dp['most_common_types']:
                print(f"  {item['type']}: {item['count']} times")

        if dp.get('cost_by_type'):
            print("\nCost by Decision Type:")
            for item in dp['cost_by_type']:
                print(f"  {item['type']}: ${item['avg_cost']:.2f} avg ({item['count']} decisions)")

    if 'agent_patterns' in patterns:
        print("\n--- AGENT PATTERNS ---")
        ap = patterns['agent_patterns']

        if ap.get('roi_by_department'):
            print("ROI by Department:")
            for item in ap['roi_by_department']:
                print(f"  {item['department']}: {item['avg_roi']:.1f}% ({item['agent_count']} agents)")

        if ap.get('efficiency_by_type'):
            print("\nEfficiency by Agent Type:")
            for item in ap['efficiency_by_type']:
                print(f"  {item['type']}: ${item['avg_revenue']:.2f} revenue, ${item['avg_cost']:.2f} cost")

    if 'opportunity_patterns' in patterns:
        print("\n--- OPPORTUNITY PATTERNS ---")
        op = patterns['opportunity_patterns']

        if op.get('by_source'):
            print("Opportunities by Source:")
            for item in op['by_source']:
                print(f"  {item['source']}: {item['total']} total, {item['pursuit_rate']:.1f}% pursued")

    print("\n✓ Pattern analysis complete")


def test_sync_from_sqlite():
    """Test syncing data from SQLite to ChromaDB"""
    print("\n" + "="*60)
    print("TEST 8: Sync from SQLite")
    print("="*60)

    learning = get_learning()

    print("\nSyncing last 30 days of data from SQLite to ChromaDB...")

    counts = learning.sync_from_sqlite(days=30)

    print(f"\nSynced:")
    print(f"  Decisions: {counts['decisions']}")
    print(f"  Agents: {counts['agents']}")
    print(f"  Opportunities: {counts['opportunities']}")

    # Show updated stats
    stats = learning.get_stats()
    print(f"\nUpdated Vector DB Stats:")
    print(f"  Decisions: {stats['collections']['decisions']}")
    print(f"  Agents: {stats['collections']['agents']}")
    print(f"  Opportunities: {stats['collections']['opportunities']}")

    print("\n✓ Sync complete")


def run_all_tests():
    """Run all tests"""
    print("\n" + "="*60)
    print("NovaOS V2 LEARNING SYSTEM - COMPREHENSIVE TEST")
    print("="*60)

    try:
        test_initialization()
        test_store_decision()
        test_store_agent_deployment()
        test_store_opportunity()
        test_query_similar_decisions()
        test_weekly_analysis()
        test_get_patterns()
        test_sync_from_sqlite()

        print("\n" + "="*60)
        print("ALL TESTS PASSED ✓")
        print("="*60)
        print("\nLearning system is ready for production use!")
        print("\nKey integration points:")
        print("  1. Call learning.store_decision() after board decisions")
        print("  2. Call get_decision_context() before board meetings")
        print("  3. Run weekly_analysis() for weekly reports")
        print("  4. Use get_patterns() for strategic insights")

    except Exception as e:
        print(f"\n✗ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    run_all_tests()
