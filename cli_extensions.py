"""
NovaOS V2 CLI Extensions
Additional commands for Learning, Dashboard, Sandbox, and DDS
"""

import sys
import argparse
from typing import Dict, Any


# === LEARNING COMMANDS ===

def cmd_learn_store(args):
    """Store learning outcome"""
    from core.learning import get_learning
    import json

    learning = get_learning()

    # Parse outcome and metrics if provided
    outcome = args.outcome
    metrics = None
    if args.metrics:
        try:
            metrics = json.loads(args.metrics)
        except:
            print(f"Warning: Could not parse metrics JSON")

    # Store decision with outcome
    result = learning.store_decision(
        decision_id=int(args.decision_id),
        context="",  # Context already in DB
        outcome=outcome,
        metrics=metrics
    )

    if result:
        print(f"✓ Outcome stored for decision {args.decision_id}")
        print(f"  Outcome: {outcome}")
    else:
        print(f"✗ Failed to store outcome")


def cmd_learn_query(args):
    """Query similar situations"""
    from core.learning import get_learning

    learning = get_learning()
    results = learning.query_similar(
        query_text=args.query,
        collection_type="decisions",
        limit=args.limit or 5
    )

    print(f"\n🔍 Similar situations to: '{args.query}'\n")

    if not results:
        print("No similar situations found.")
        return

    for i, result in enumerate(results, 1):
        meta = result['metadata']
        print(f"{i}. [{meta.get('timestamp', 'N/A')}] {meta.get('agent', 'Unknown')} - {meta.get('decision_type', 'N/A')}")
        print(f"   Cost: ${meta.get('cost', 0):.2f} | Tokens: {meta.get('tokens_used', 0)}")
        print(f"   Has Outcome: {meta.get('has_outcome', 'unknown')}")
        print(f"   Relevance: {result.get('relevance', 0):.1%}\n")


def cmd_learn_analyze(args):
    """Run weekly analysis"""
    from core.learning import get_learning
    import json

    learning = get_learning()
    analysis = learning.analyze_weekly()

    print("\n📊 Weekly Learning Analysis\n")
    print(f"Period: {analysis['period']}")
    print(f"Timestamp: {analysis['timestamp']}")

    # Decisions
    print("\n=== DECISIONS ===")
    decisions = analysis['decisions']
    print(f"Total Decisions: {decisions['total_decisions']}")
    print(f"Total Cost: ${decisions['total_cost']:.2f}")
    print(f"Avg Tokens per Decision: {decisions['avg_tokens_per_decision']}")
    if decisions['by_type']:
        print("\nBy Type:")
        for dtype, data in decisions['by_type'].items():
            print(f"  {dtype}: {data['count']} decisions, ${data['total_cost']:.2f}")

    # Agents
    print("\n=== AGENTS ===")
    agents = analysis['agents']
    print(f"Total Active Agents: {agents['total_agents']}")
    if agents['high_performers']:
        print("\nTop Performers:")
        for agent in agents['high_performers'][:3]:
            print(f"  • {agent['name']} ({agent['department']}): {agent['roi']:.1f}% ROI")
    if agents['low_performers']:
        print("\nLow Performers:")
        for agent in agents['low_performers'][:3]:
            print(f"  • {agent['name']} ({agent['department']}): {agent['roi']:.1f}% ROI")

    # Opportunities
    print("\n=== OPPORTUNITIES ===")
    opps = analysis['opportunities']
    print(f"Total Opportunities: {opps['total_opportunities']}")
    print(f"Avg Confidence: {opps['avg_confidence']:.1%}")
    print(f"Total Potential Revenue: ${opps['total_potential_revenue']:.2f}")

    # Recommendations
    print("\n=== RECOMMENDATIONS ===")
    for item in analysis['recommendations']:
        print(f"→ {item}")


def cmd_learn_patterns(args):
    """Identify patterns"""
    from core.learning import get_learning

    learning = get_learning()
    pattern_type = args.type if hasattr(args, 'type') else 'all'
    patterns = learning.get_patterns(pattern_type=pattern_type)

    print(f"\n🎯 Identified Patterns ({patterns['pattern_type']})\n")

    # Decision patterns
    if 'decision_patterns' in patterns:
        print("=== DECISION PATTERNS ===")
        dec_patterns = patterns['decision_patterns']

        if dec_patterns.get('most_common_types'):
            print("\nMost Common Decision Types:")
            for item in dec_patterns['most_common_types']:
                print(f"  • {item['type']}: {item['count']} times")

        if dec_patterns.get('cost_by_type'):
            print("\nCost by Decision Type:")
            for item in dec_patterns['cost_by_type']:
                print(f"  • {item['type']}: ${item['avg_cost']:.2f} avg ({item['count']} decisions)")

    # Agent patterns
    if 'agent_patterns' in patterns:
        print("\n=== AGENT PATTERNS ===")
        agent_patterns = patterns['agent_patterns']

        if agent_patterns.get('roi_by_department'):
            print("\nROI by Department:")
            for dept in agent_patterns['roi_by_department']:
                print(f"  • {dept['department']}: {dept['avg_roi']:.1f}% avg ROI ({dept['agent_count']} agents)")

        if agent_patterns.get('efficiency_by_type'):
            print("\nEfficiency by Agent Type:")
            for item in agent_patterns['efficiency_by_type']:
                print(f"  • {item['type']}: ${item['avg_revenue']:.2f} revenue, ${item['avg_cost']:.2f} cost ({item['count']} agents)")

    # Opportunity patterns
    if 'opportunity_patterns' in patterns:
        print("\n=== OPPORTUNITY PATTERNS ===")
        opp_patterns = patterns['opportunity_patterns']

        if opp_patterns.get('by_source'):
            print("\nBy Source:")
            for item in opp_patterns['by_source']:
                print(f"  • {item['source']}: {item['total']} total, {item['pursuit_rate']:.1f}% pursued")

        if opp_patterns.get('revenue_by_status'):
            print("\nRevenue by Status:")
            for item in opp_patterns['revenue_by_status']:
                print(f"  • {item['status']}: ${item['avg_revenue']:.2f} avg ({item['count']} opportunities)")


# === DASHBOARD COMMANDS ===

def cmd_dashboard_start(args):
    """Start dashboard server"""
    import subprocess
    import os

    dashboard_path = "/Users/krissanders/novaos-v2/dashboard"

    print("🚀 Starting NovaOS Dashboard...")
    print(f"   URL: http://localhost:{args.port or 5000}")
    print("\n   Press Ctrl+C to stop\n")

    os.chdir(dashboard_path)
    subprocess.run([sys.executable, "app.py", "--port", str(args.port or 5000)])


def cmd_dashboard_stop(args):
    """Stop dashboard server"""
    import subprocess

    print("⏹ Stopping NovaOS Dashboard...")

    # Find and kill Flask process
    try:
        subprocess.run(["pkill", "-f", "flask"])
        print("✓ Dashboard stopped")
    except:
        print("No dashboard process found")


# === SANDBOX COMMANDS ===

def cmd_sandbox_create(args):
    """Create sandbox project"""
    from sandbox.manager import get_sandbox

    sandbox = get_sandbox()
    project_id = sandbox.create_project(args.name, args.description or "")

    print(f"✓ Sandbox project created: {args.name}")
    print(f"  Project ID: {project_id}")
    print(f"  Description: {args.description or 'None'}")


def cmd_sandbox_deploy(args):
    """Deploy agent in sandbox"""
    from sandbox.manager import get_sandbox

    sandbox = get_sandbox()

    import json
    config = {}
    if args.config:
        try:
            config = json.loads(args.config)
        except:
            for pair in args.config.split(','):
                if '=' in pair:
                    key, value = pair.split('=', 1)
                    config[key.strip()] = value.strip()

    agent_id = sandbox.deploy_agent(
        project_name=args.project,
        agent_type=args.type,
        config=config
    )

    print(f"✓ Agent deployed in sandbox: {args.project}")
    print(f"  Agent ID: {agent_id}")
    print(f"  Type: {args.type}")


def cmd_sandbox_list(args):
    """List sandbox projects"""
    from sandbox.manager import get_sandbox

    sandbox = get_sandbox()
    projects = sandbox.list_projects()

    print("\n🧪 Sandbox Projects\n")

    if not projects:
        print("No sandbox projects yet. Create one with: nova sandbox create <name>")
        return

    for project in projects:
        print(f"• {project['name']} (ID: {project['id']})")
        print(f"  Description: {project['description']}")
        print(f"  Agents: {project['agent_count']}")
        print(f"  Status: {project['status']}")
        print()


def cmd_sandbox_evaluate(args):
    """Evaluate sandbox project"""
    from sandbox.manager import get_sandbox

    sandbox = get_sandbox()
    evaluation = sandbox.evaluate_project(args.project)

    print(f"\n📋 Sandbox Project Evaluation: {args.project}\n")
    print(f"Recommendation: {evaluation['recommendation']}")
    print(f"Reasoning: {evaluation['reasoning']}")

    if evaluation['metrics']:
        print("\nMetrics:")
        for key, value in evaluation['metrics'].items():
            print(f"  {key}: {value}")


def cmd_sandbox_promote(args):
    """Promote sandbox project to production"""
    from sandbox.manager import get_sandbox

    sandbox = get_sandbox()
    result = sandbox.promote_project(args.project)

    print(f"✓ Project promoted to production: {args.project}")
    print(f"  Production Agent ID: {result['agent_id']}")
    print(f"  Department: {result['department']}")


def cmd_sandbox_kill(args):
    """Kill sandbox project"""
    from sandbox.manager import get_sandbox

    sandbox = get_sandbox()
    sandbox.kill_project(args.project)

    print(f"⨯ Sandbox project deleted: {args.project}")


# === DDS COMMANDS ===

def cmd_dds_deploy(args):
    """Deploy DDS campaign"""
    from integrations.dds import get_dds

    dds = get_dds()

    config = {
        'vertical': args.vertical,
        'location': args.location,
        'prospect_count': args.count or 50,
        'budget': args.budget or 50
    }

    result = dds.deploy_prospecting_campaign(config)

    print(f"🎯 DDS Campaign Deployed")
    print(f"   Vertical: {args.vertical}")
    print(f"   Location: {args.location}")
    print(f"   Target: {config['prospect_count']} prospects")
    print(f"   Budget: ${config['budget']}")

    if result['status'] == 'deployed':
        print(f"   Campaign ID: {result.get('campaign_id', 'N/A')}")
    else:
        print(f"   Status: {result['status']}")


def cmd_dds_status(args):
    """Get DDS campaign status"""
    from integrations.dds import get_dds

    dds = get_dds()
    status = dds.get_dds_status()

    print("\n📊 DDS Campaign Status\n")
    print(f"Total Campaigns: {status['total_campaigns']}")
    print(f"Active: {status['active_campaigns']}")
    print(f"Total Cost: ${status['total_cost']:.2f}")
    print(f"Total Revenue: ${status['total_revenue']:.2f}")
    print(f"ROI: {status['roi']:.1f}%")

    if status['campaigns']:
        print("\nCampaigns:")
        for campaign in status['campaigns']:
            print(f"  • {campaign['name']}")
            print(f"    Status: {campaign['status']}")
            print(f"    Cost: ${campaign['cost']:.2f} | Revenue: ${campaign['revenue']:.2f} | ROI: {campaign['roi']:.1f}%")


def cmd_dds_report(args):
    """Generate DDS report"""
    from integrations.dds import get_dds

    dds = get_dds()
    report = dds.generate_report(args.campaign_id if hasattr(args, 'campaign_id') else None)

    print("\n📈 DDS Performance Report\n")
    print(f"Leads Generated: {report['leads_generated']}")
    print(f"Qualified Leads: {report['qualified_leads']}")
    print(f"Qualification Rate: {report['qualification_rate']:.1f}%")
    print(f"Outreach Success Rate: {report['outreach_success_rate']:.1f}%")
    print(f"Cost per Lead: ${report['cost_per_lead']:.2f}")
    print(f"Cost per Qualified Lead: ${report['cost_per_qualified_lead']:.2f}")
    print(f"Revenue Generated: ${report['revenue_generated']:.2f}")
    print(f"ROI: {report['roi']:.1f}%")

    if report.get('recommendations'):
        print("\nRecommendations:")
        for rec in report['recommendations']:
            print(f"  • {rec}")


# === COMMAND REGISTRATION ===

def register_learning_commands(subparsers):
    """Register learning commands"""
    learn_parser = subparsers.add_parser('learn', help='Learning system commands')
    learn_subparsers = learn_parser.add_subparsers(dest='learn_command')

    # learn store
    store_parser = learn_subparsers.add_parser('store', help='Store decision outcome')
    store_parser.add_argument('decision_id', help='Decision ID')
    store_parser.add_argument('outcome', help='Outcome description')
    store_parser.add_argument('--metrics', help='Metrics as JSON (e.g., {"revenue": 1000, "roi": 5.0})')

    # learn query
    query_parser = learn_subparsers.add_parser('query', help='Query similar situations')
    query_parser.add_argument('query', help='Query text')
    query_parser.add_argument('--limit', type=int, default=5, help='Number of results (default: 5)')

    # learn analyze
    learn_subparsers.add_parser('analyze', help='Run weekly analysis')

    # learn patterns
    patterns_parser = learn_subparsers.add_parser('patterns', help='Identify patterns')
    patterns_parser.add_argument('--type', choices=['decisions', 'agents', 'opportunities', 'all'],
                                  default='all', help='Pattern type to show (default: all)')

    return {
        'store': cmd_learn_store,
        'query': cmd_learn_query,
        'analyze': cmd_learn_analyze,
        'patterns': cmd_learn_patterns
    }


def register_dashboard_commands(subparsers):
    """Register dashboard commands"""
    dashboard_parser = subparsers.add_parser('dashboard', help='Dashboard commands')
    dashboard_subparsers = dashboard_parser.add_subparsers(dest='dashboard_command')

    # dashboard start
    start_parser = dashboard_subparsers.add_parser('start', help='Start dashboard')
    start_parser.add_argument('--port', type=int, default=5000, help='Port number')

    # dashboard stop
    dashboard_subparsers.add_parser('stop', help='Stop dashboard')

    return {
        'start': cmd_dashboard_start,
        'stop': cmd_dashboard_stop
    }


def register_sandbox_commands(subparsers):
    """Register sandbox commands"""
    sandbox_parser = subparsers.add_parser('sandbox', help='Sandbox environment commands')
    sandbox_subparsers = sandbox_parser.add_subparsers(dest='sandbox_command')

    # sandbox create
    create_parser = sandbox_subparsers.add_parser('create', help='Create sandbox project')
    create_parser.add_argument('name', help='Project name')
    create_parser.add_argument('--description', help='Project description')

    # sandbox deploy
    deploy_parser = sandbox_subparsers.add_parser('deploy', help='Deploy agent in sandbox')
    deploy_parser.add_argument('project', help='Project name')
    deploy_parser.add_argument('--type', required=True, help='Agent type')
    deploy_parser.add_argument('--config', help='Agent config (JSON)')

    # sandbox list
    sandbox_subparsers.add_parser('list', help='List sandbox projects')

    # sandbox evaluate
    eval_parser = sandbox_subparsers.add_parser('evaluate', help='Evaluate project')
    eval_parser.add_argument('project', help='Project name')

    # sandbox promote
    promote_parser = sandbox_subparsers.add_parser('promote', help='Promote to production')
    promote_parser.add_argument('project', help='Project name')

    # sandbox kill
    kill_parser = sandbox_subparsers.add_parser('kill', help='Kill sandbox project')
    kill_parser.add_argument('project', help='Project name')

    return {
        'create': cmd_sandbox_create,
        'deploy': cmd_sandbox_deploy,
        'list': cmd_sandbox_list,
        'evaluate': cmd_sandbox_evaluate,
        'promote': cmd_sandbox_promote,
        'kill': cmd_sandbox_kill
    }


def register_dds_commands(subparsers):
    """Register DDS commands"""
    dds_parser = subparsers.add_parser('dds', help='DDS integration commands')
    dds_subparsers = dds_parser.add_subparsers(dest='dds_command')

    # dds deploy
    deploy_parser = dds_subparsers.add_parser('deploy', help='Deploy DDS campaign')
    deploy_parser.add_argument('--vertical', required=True, help='Industry vertical')
    deploy_parser.add_argument('--location', required=True, help='Geographic location')
    deploy_parser.add_argument('--count', type=int, help='Number of prospects')
    deploy_parser.add_argument('--budget', type=float, help='Budget limit')

    # dds status
    dds_subparsers.add_parser('status', help='Get DDS status')

    # dds report
    report_parser = dds_subparsers.add_parser('report', help='Generate DDS report')
    report_parser.add_argument('--campaign-id', help='Specific campaign ID')

    return {
        'deploy': cmd_dds_deploy,
        'status': cmd_dds_status,
        'report': cmd_dds_report
    }
