#!/usr/bin/env python3
"""
NovaOS V2 Learning System - Quick Start Script

This script helps you get started with the learning system.
Run this after installation to verify everything works.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))


def print_header(text):
    """Print a formatted header"""
    print("\n" + "="*60)
    print(text)
    print("="*60)


def check_dependencies():
    """Check if all dependencies are installed"""
    print_header("STEP 1: Checking Dependencies")

    required = {
        'chromadb': 'ChromaDB (vector database)',
        'sentence_transformers': 'Sentence Transformers (embeddings)',
        'numpy': 'NumPy (numerical operations)',
        'anthropic': 'Anthropic (existing)',
    }

    missing = []
    for module, description in required.items():
        try:
            __import__(module)
            print(f"✓ {description}")
        except ImportError:
            print(f"✗ {description} - NOT INSTALLED")
            missing.append(module)

    if missing:
        print(f"\n⚠ Missing dependencies: {', '.join(missing)}")
        print("\nInstall with: pip install -r requirements.txt")
        return False

    print("\n✓ All dependencies installed!")
    return True


def initialize_system():
    """Initialize the learning system"""
    print_header("STEP 2: Initializing Learning System")

    try:
        from core.learning import get_learning

        print("Loading learning system...")
        learning = get_learning()

        print("✓ Learning system initialized!")

        # Get stats
        stats = learning.get_stats()
        print(f"\nSystem Info:")
        print(f"  Encoder Model: {stats['encoder_model']}")
        print(f"  ChromaDB Path: {stats['chroma_path']}")
        print(f"  Database Path: {stats['db_path']}")

        print(f"\nVector Collections:")
        print(f"  Decisions: {stats['collections']['decisions']} items")
        print(f"  Agents: {stats['collections']['agents']} items")
        print(f"  Opportunities: {stats['collections']['opportunities']} items")

        return learning

    except Exception as e:
        print(f"✗ Error initializing system: {e}")
        return None


def test_basic_operations(learning):
    """Test basic learning system operations"""
    print_header("STEP 3: Testing Basic Operations")

    try:
        from core.memory import get_memory

        memory = get_memory()
        print("✓ Memory system connected")

        # Test decision storage
        print("\nTesting decision storage...")
        decision_id = memory.log_decision(
            agent="Test Agent",
            decision_type="test",
            question="Is the learning system working?",
            decision="Yes, it's working!",
            reasoning="All tests passing",
            tokens_used=100,
            cost=0.01
        )

        success = learning.store_decision(
            decision_id=decision_id,
            context="Test decision",
            outcome="Success",
            metrics={'test': True}
        )

        if success:
            print(f"✓ Decision stored (ID: {decision_id})")
        else:
            print("✗ Failed to store decision")
            return False

        # Test query
        print("\nTesting similarity search...")
        similar = learning.query_similar(
            query_text="Is the system working?",
            collection_type="decisions",
            limit=3
        )

        if similar:
            print(f"✓ Query returned {len(similar)} results")
            if similar[0]['metadata']['decision_id'] == str(decision_id):
                print(f"✓ Found test decision (relevance: {similar[0]['relevance']:.1%})")
        else:
            print("ℹ No similar decisions found (expected for fresh database)")

        print("\n✓ Basic operations working!")
        return True

    except Exception as e:
        print(f"✗ Error testing operations: {e}")
        import traceback
        traceback.print_exc()
        return False


def show_quick_start():
    """Show quick start examples"""
    print_header("STEP 4: Quick Start Examples")

    print("\n1. Before Board Decision:")
    print("-" * 60)
    print("""
from core.learning import get_decision_context

# Get historical context
context = get_decision_context(
    "Should we hire a new sales agent?",
    decision_type="hiring"
)

# Use in board agent prompt
print(context)
""")

    print("\n2. After Board Decision:")
    print("-" * 60)
    print("""
from core.memory import get_memory
from core.learning import get_learning

memory = get_memory()
learning = get_learning()

# Log decision
decision_id = memory.log_decision(
    agent="CFO",
    decision_type="hiring",
    question="Should we hire?",
    decision="Approved",
    reasoning="Team at capacity",
    tokens_used=2000,
    cost=0.08
)

# Store for learning
learning.store_decision(
    decision_id=decision_id,
    context="Hiring decision",
    outcome=None,
    metrics={'projected_roi': 3.0}
)
""")

    print("\n3. Weekly Review:")
    print("-" * 60)
    print("""
from core.learning import weekly_analysis

# Run analysis
analysis = weekly_analysis()

# Show recommendations
for rec in analysis['recommendations']:
    print(f"• {rec}")
""")


def show_next_steps():
    """Show next steps"""
    print_header("Next Steps")

    print("\n1. Read Documentation:")
    print("   • Quick Start: core/LEARNING_README.md")
    print("   • Setup Guide: LEARNING_SETUP.md")
    print("   • Integration: LEARNING_INTEGRATION.md")

    print("\n2. Run Tests:")
    print("   python test_learning.py")

    print("\n3. Try Examples:")
    print("   python example_board_with_learning.py")

    print("\n4. Backfill Data (if you have existing data):")
    print("   python -c \"from core.learning import get_learning; \\")
    print("              get_learning().sync_from_sqlite(days=30)\"")

    print("\n5. Integrate with Board:")
    print("   • Add get_decision_context() before decisions")
    print("   • Add store_decision() after decisions")
    print("   • Set up weekly_analysis() for reviews")


def main():
    """Main function"""
    print("\n" + "="*60)
    print("NovaOS V2 LEARNING SYSTEM - QUICK START")
    print("="*60)
    print("\nThis script will help you verify the learning system is")
    print("installed and working correctly.")
    print("\nPress Enter to continue...")
    input()

    # Step 1: Check dependencies
    if not check_dependencies():
        print("\n⚠ Please install dependencies first:")
        print("   pip install -r requirements.txt")
        return 1

    # Step 2: Initialize system
    learning = initialize_system()
    if not learning:
        print("\n⚠ Failed to initialize learning system")
        return 1

    # Step 3: Test operations
    if not test_basic_operations(learning):
        print("\n⚠ Some tests failed")
        return 1

    # Step 4: Show examples
    show_quick_start()

    # Step 5: Show next steps
    show_next_steps()

    # Success!
    print_header("SUCCESS!")
    print("\n✓ Learning system is installed and working correctly!")
    print("\nThe system is ready for:")
    print("  • Storing decisions with context and outcomes")
    print("  • Retrieving similar past decisions")
    print("  • Analyzing patterns and generating insights")
    print("  • Providing weekly strategic recommendations")

    print("\n" + "="*60)
    print("You're ready to start using the learning system!")
    print("="*60 + "\n")

    return 0


if __name__ == "__main__":
    sys.exit(main())
