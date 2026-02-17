"""
Example: Board Decision-Making with Learning System Integration

This demonstrates how to integrate the learning system with board decisions
to provide context from past decisions and store outcomes for future learning.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from core.memory import get_memory
from core.learning import get_learning, get_decision_context
from datetime import datetime


class EnhancedBoard:
    """
    Board with integrated learning system
    Demonstrates best practices for decision-making with historical context
    """

    def __init__(self):
        self.memory = get_memory()
        self.learning = get_learning()

    def make_decision_with_learning(
        self,
        agent: str,
        decision_type: str,
        question: str,
        additional_context: str = ""
    ) -> dict:
        """
        Make a board decision enhanced with learning from past decisions

        This is the key integration pattern:
        1. Retrieve similar past decisions
        2. Include in decision context
        3. Make decision
        4. Store for future learning
        """

        print("\n" + "="*60)
        print(f"BOARD DECISION: {agent}")
        print("="*60)
        print(f"Question: {question}")
        print(f"Type: {decision_type}")

        # STEP 1: Get learning context from similar past decisions
        print("\n[Learning] Retrieving similar past decisions...")
        learning_context = get_decision_context(question, decision_type)

        print("\n--- HISTORICAL CONTEXT ---")
        print(learning_context)

        # STEP 2: Build enhanced decision context
        full_context = f"""
QUESTION: {question}

HISTORICAL CONTEXT FROM PAST DECISIONS:
{learning_context}

ADDITIONAL CONTEXT:
{additional_context}

Based on the historical patterns and current context, please provide:
1. Your recommendation (Approve/Reject/Table)
2. Detailed reasoning
3. Risk assessment
4. Expected outcome
        """

        # STEP 3: In a real system, this would call the board agent
        # For this example, we'll simulate a decision
        print("\n[Board] Agent analyzing decision...")

        # Simulated decision (in production, this would be an LLM call)
        decision = self._simulate_agent_decision(agent, decision_type, question)

        print("\n--- DECISION ---")
        print(f"Recommendation: {decision['recommendation']}")
        print(f"Reasoning: {decision['reasoning']}")
        print(f"Risk Level: {decision['risk_level']}")

        # STEP 4: Log decision in SQLite
        print("\n[Memory] Logging decision...")
        decision_id = self.memory.log_decision(
            agent=agent,
            decision_type=decision_type,
            question=question,
            decision=decision['recommendation'],
            reasoning=decision['reasoning'],
            tokens_used=decision['tokens_used'],
            cost=decision['cost']
        )

        print(f"[Memory] Decision logged with ID: {decision_id}")

        # STEP 5: Store in learning system for future reference
        print("[Learning] Storing in vector database...")
        success = self.learning.store_decision(
            decision_id=decision_id,
            context=f"{question} - {additional_context}",
            outcome=None,  # Will be updated later
            metrics={
                'risk_level': decision['risk_level'],
                'confidence': decision['confidence']
            }
        )

        if success:
            print("[Learning] ✓ Stored successfully")
        else:
            print("[Learning] ✗ Storage failed")

        return {
            'decision_id': decision_id,
            'recommendation': decision['recommendation'],
            'reasoning': decision['reasoning'],
            'learning_context_provided': learning_context != "No similar past decisions found."
        }

    def update_decision_outcome(
        self,
        decision_id: int,
        outcome: str,
        actual_metrics: dict = None
    ):
        """
        Update decision with actual outcome for learning
        Call this after you know the result of a decision
        """

        print(f"\n[Learning] Updating outcome for decision {decision_id}")

        # Update SQLite
        self.memory.update_decision_outcome(decision_id, outcome)

        # Re-store in learning system with outcome
        # This creates a new vector entry with the complete information
        self.learning.store_decision(
            decision_id=decision_id,
            context="",  # Will be pulled from SQLite
            outcome=outcome,
            metrics=actual_metrics
        )

        print(f"[Learning] ✓ Outcome updated: {outcome}")

    def _simulate_agent_decision(self, agent: str, decision_type: str, question: str) -> dict:
        """
        Simulate an agent decision
        In production, this would be replaced with actual LLM call
        """

        # Simulate different decisions based on agent and type
        decisions = {
            'CFO': {
                'budget_allocation': {
                    'recommendation': 'Approved with conditions',
                    'reasoning': 'ROI projections are positive, but require monthly checkpoints',
                    'risk_level': 'Medium',
                    'confidence': 0.75
                },
                'hiring': {
                    'recommendation': 'Approved',
                    'reasoning': 'Team capacity is constrained, projected 3:1 ROI on hire',
                    'risk_level': 'Low',
                    'confidence': 0.85
                }
            },
            'CEO': {
                'strategic_direction': {
                    'recommendation': 'Approved',
                    'reasoning': 'Aligns with long-term vision and market opportunities',
                    'risk_level': 'Medium',
                    'confidence': 0.80
                }
            },
            'CMO': {
                'marketing_campaign': {
                    'recommendation': 'Approved',
                    'reasoning': 'Target market analysis shows strong potential',
                    'risk_level': 'Low',
                    'confidence': 0.90
                }
            }
        }

        # Get decision or use default
        agent_decisions = decisions.get(agent, {})
        decision = agent_decisions.get(decision_type, {
            'recommendation': 'Table for further review',
            'reasoning': 'Need more information to make informed decision',
            'risk_level': 'Unknown',
            'confidence': 0.50
        })

        # Add simulated token usage and cost
        decision['tokens_used'] = 2000
        decision['cost'] = 0.08

        return decision


def example_1_basic_decision():
    """Example 1: Basic decision with learning context"""

    print("\n" + "="*70)
    print("EXAMPLE 1: Basic Decision with Learning Context")
    print("="*70)

    board = EnhancedBoard()

    # Make a budget decision
    result = board.make_decision_with_learning(
        agent="CFO",
        decision_type="budget_allocation",
        question="Should we increase marketing budget by $10,000 for Q2?",
        additional_context="""
        Current marketing budget: $25,000/quarter
        Last quarter ROI: 2.5x
        CMO requesting increase for expanded campaign
        Available cash: $100,000
        """
    )

    print(f"\n✓ Decision made: {result['recommendation']}")
    print(f"✓ Learning context was {'available' if result['learning_context_provided'] else 'not available'}")

    # Simulate waiting for outcome...
    print("\n[Simulating 30 days passing...]")

    # Update with actual outcome
    board.update_decision_outcome(
        decision_id=result['decision_id'],
        outcome="Success - Campaign generated $35,000 in new revenue, 3.5x ROI",
        actual_metrics={
            'actual_revenue': 35000.0,
            'actual_roi': 3.5,
            'implementation_days': 30
        }
    )


def example_2_hiring_decision():
    """Example 2: Hiring decision"""

    print("\n" + "="*70)
    print("EXAMPLE 2: Hiring Decision with Historical Context")
    print("="*70)

    board = EnhancedBoard()

    result = board.make_decision_with_learning(
        agent="CFO",
        decision_type="hiring",
        question="Should we hire a senior sales agent at $80k/year?",
        additional_context="""
        Current sales team: 3 agents
        Average deal size: $25k
        Sales cycle: 60 days
        Team at capacity, missing opportunities
        Projected: +$300k revenue/year from new hire
        """
    )

    print(f"\n✓ Decision made: {result['recommendation']}")


def example_3_multiple_decisions_with_learning():
    """Example 3: Multiple decisions showing learning accumulation"""

    print("\n" + "="*70)
    print("EXAMPLE 3: Multiple Decisions - Learning Accumulation")
    print("="*70)

    board = EnhancedBoard()

    # Decision 1: Small marketing budget
    print("\n--- DECISION 1: Small Marketing Budget ---")
    result1 = board.make_decision_with_learning(
        agent="CFO",
        decision_type="marketing_campaign",
        question="Should we run a $2,000 LinkedIn ad campaign?",
        additional_context="Testing new market segment"
    )

    board.update_decision_outcome(
        decision_id=result1['decision_id'],
        outcome="Success - Generated 50 leads, 5 conversions, $8k revenue",
        actual_metrics={'revenue': 8000, 'roi': 4.0}
    )

    # Decision 2: Medium marketing budget (will see Decision 1 in context)
    print("\n--- DECISION 2: Medium Marketing Budget ---")
    result2 = board.make_decision_with_learning(
        agent="CFO",
        decision_type="marketing_campaign",
        question="Should we scale up to $5,000 LinkedIn ad campaign?",
        additional_context="Same market segment, proven success"
    )

    board.update_decision_outcome(
        decision_id=result2['decision_id'],
        outcome="Success - Generated 120 leads, 12 conversions, $18k revenue",
        actual_metrics={'revenue': 18000, 'roi': 3.6}
    )

    # Decision 3: Large marketing budget (will see Decisions 1 & 2 in context)
    print("\n--- DECISION 3: Large Marketing Budget ---")
    result3 = board.make_decision_with_learning(
        agent="CFO",
        decision_type="marketing_campaign",
        question="Should we invest $20,000 in comprehensive LinkedIn campaign?",
        additional_context="Scaling proven strategy, expecting 3-4x ROI based on history"
    )

    print("\n✓ Learning system now has 3 related decisions in context")
    print("✓ Future similar decisions will benefit from this accumulated knowledge")


def example_4_weekly_review():
    """Example 4: Weekly board review with learning insights"""

    print("\n" + "="*70)
    print("EXAMPLE 4: Weekly Board Review with Learning Insights")
    print("="*70)

    board = EnhancedBoard()

    # Run weekly analysis
    print("\n[Learning] Running weekly analysis...")
    analysis = board.learning.analyze_weekly()

    print("\n--- WEEKLY PERFORMANCE SUMMARY ---")
    print(f"Period: {analysis['period']}")
    print(f"\nDecisions Made: {analysis['decisions']['total_decisions']}")
    print(f"Decision Cost: ${analysis['decisions']['total_cost']:.2f}")

    print(f"\nActive Agents: {analysis['agents']['total_agents']}")

    if analysis['agents']['high_performers']:
        print("\nTop Performing Agents:")
        for agent in analysis['agents']['high_performers'][:3]:
            print(f"  • {agent['name']}: {agent['roi']:.1f}% ROI")

    print("\n--- STRATEGIC RECOMMENDATIONS ---")
    for i, rec in enumerate(analysis['recommendations'], 1):
        print(f"{i}. {rec}")

    # Get patterns
    print("\n--- IDENTIFIED PATTERNS ---")
    patterns = board.learning.get_patterns("all")

    if patterns.get('decision_patterns', {}).get('cost_by_type'):
        print("\nDecision Cost Patterns:")
        for item in patterns['decision_patterns']['cost_by_type'][:3]:
            print(f"  • {item['type']}: ${item['avg_cost']:.2f} avg")

    if patterns.get('agent_patterns', {}).get('roi_by_department'):
        print("\nROI by Department:")
        for item in patterns['agent_patterns']['roi_by_department']:
            print(f"  • {item['department']}: {item['avg_roi']:.1f}%")


def run_all_examples():
    """Run all integration examples"""

    print("\n" + "="*70)
    print("NOVAOS V2 - BOARD + LEARNING SYSTEM INTEGRATION EXAMPLES")
    print("="*70)

    try:
        # Run examples
        example_1_basic_decision()
        example_2_hiring_decision()
        example_3_multiple_decisions_with_learning()
        example_4_weekly_review()

        print("\n" + "="*70)
        print("ALL EXAMPLES COMPLETED SUCCESSFULLY ✓")
        print("="*70)

        print("\n=== INTEGRATION SUMMARY ===")
        print("\nThe learning system provides:")
        print("  1. Historical context for better decisions")
        print("  2. Pattern recognition across decisions")
        print("  3. ROI tracking and optimization")
        print("  4. Weekly strategic recommendations")
        print("\nKey integration points:")
        print("  • get_decision_context() - before decisions")
        print("  • store_decision() - after decisions")
        print("  • update_decision_outcome() - when results known")
        print("  • analyze_weekly() - for strategic review")
        print("\nNext steps:")
        print("  • Integrate with actual board agents")
        print("  • Set up automated weekly reports")
        print("  • Create decision dashboard")
        print("  • Configure outcome tracking")

    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    run_all_examples()
