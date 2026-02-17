#!/usr/bin/env python3
"""
NovaOS V2 CLI - AI Business Orchestration Platform
Command-line interface for managing NovaOS
"""

import sys
import argparse
import json
from typing import Dict, Any
from datetime import datetime

# Import core modules
from core.board import get_board
from core.departments import get_departments
from core.agent_factory import get_factory, AgentTemplates
from core.memory import get_memory
from integrations.monitoring import get_monitor
from config.financial_targets import get_current_target
from sandbox.manager import get_sandbox
from workers.manager import get_worker_manager
from workers.worker_monitor import get_worker_monitor
from core.autonomous import get_autonomous_engine


def print_header(title: str):
    """Print formatted header"""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60 + "\n")


def print_section(title: str):
    """Print section header"""
    print(f"\n--- {title} ---")


def format_currency(amount: float) -> str:
    """Format currency"""
    return f"${amount:,.2f}"


def format_percent(value: float) -> str:
    """Format percentage"""
    return f"{value:.1f}%"


# === COMMAND HANDLERS ===

def cmd_status(args):
    """Show complete system status"""
    print_header("NovaOS System Status")

    monitor = get_monitor()
    status = monitor.status()

    # System overview
    system = status['system']
    print_section("System Health")
    print(f"Health: {system['system_health']}")
    print(f"Timestamp: {system['timestamp']}")

    # Agents
    agents = system['agents']
    print_section("Agents")
    print(f"Total: {agents['total']}")
    print(f"  Active: {agents['active']}")
    print(f"  Paused: {agents['paused']}")
    print(f"  Killed: {agents['killed']}")
    print(f"\nPerformance:")
    print(f"  High Performers (ROI >300%): {agents['high_performers']}")
    print(f"  Low Performers (ROI <100%): {agents['low_performers']}")
    print(f"  Negative ROI: {agents['negative_performers']}")

    # Financials
    financials = system['financials']
    print_section("Financials")
    print(f"Revenue: {format_currency(financials['total_revenue'])}")
    print(f"AI Costs: {format_currency(financials['total_costs'])}")
    print(f"Profit: {format_currency(financials['profit'])}")
    print(f"ROI: {format_percent(financials['roi'])}")
    print(f"AI Cost %: {format_percent(financials['ai_cost_percent'])} (target: <5%)")

    # Targets
    targets = system['targets']
    print_section("Target Tracking")
    print(f"Monthly Target: {format_currency(targets['monthly_target'])}")
    print(f"Current: {format_currency(targets['current_revenue'])}")
    print(f"Progress: {format_percent(targets['percent_of_expected'])} of expected")
    print(f"Status: {targets['status'].upper()}")

    # Recommendations
    if system['recommendations']:
        print_section("Recommendations")
        for i, rec in enumerate(system['recommendations'], 1):
            print(f"{i}. {rec}")

    # Cost alerts
    cost_alerts = status['costs'].get('alerts', [])
    if cost_alerts:
        print_section("ALERTS")
        for alert in cost_alerts:
            print(f"[{alert['severity']}] {alert['message']}")
            print(f"   Action: {alert['action']}")


def cmd_costs(args):
    """Show AI cost breakdown"""
    print_header("AI Cost Dashboard")

    monitor = get_monitor()
    costs = monitor.costs(period=args.period if hasattr(args, 'period') else 'today')

    # Summary
    summary = costs['summary']
    print_section("Summary")
    print(f"Total Revenue: {format_currency(summary['total_revenue'])}")
    print(f"Total AI Costs: {format_currency(summary['total_ai_costs'])}")
    print(f"Net Profit: {format_currency(summary['net_profit'])}")
    print(f"AI Cost %: {format_percent(summary['ai_cost_percent'])} (target: <5%)")
    print(f"ROI: {format_percent(summary['overall_roi'])}")
    print(f"Status: {summary['status']}")

    # Cost breakdown by department
    breakdown = costs['cost_breakdown']
    if breakdown:
        print_section("Cost Breakdown by Department")
        for dept, data in breakdown.items():
            print(f"{dept.title()}:")
            print(f"  Cost: {format_currency(data['cost'])}")
            print(f"  Tokens: {data['tokens']:,}")

    # Most expensive agents
    expensive = costs['most_expensive_agents']
    if expensive:
        print_section("Most Expensive Agents")
        for i, agent in enumerate(expensive, 1):
            print(f"{i}. {agent['name']} ({agent['department']})")
            print(f"   Cost: {format_currency(agent['cost'])} | "
                  f"Revenue: {format_currency(agent['revenue'])} | "
                  f"ROI: {format_percent(agent['roi'])}")

    # Alerts
    alerts = costs.get('alerts', [])
    if alerts:
        print_section("ALERTS")
        for alert in alerts:
            print(f"[{alert['severity']}] {alert['message']}")
            print(f"   Action: {alert['action']}")


def cmd_revenue(args):
    """Show revenue tracking"""
    print_header("Revenue Dashboard")

    monitor = get_monitor()
    revenue = monitor.revenue()

    print_section("Summary")
    print(f"Total Revenue: {format_currency(revenue['total_revenue'])}")
    print(f"Monthly Target: {format_currency(revenue['monthly_target'])}")
    print(f"Daily Target: {format_currency(revenue['daily_target'])}")
    print(f"Profit: {format_currency(revenue['profit'])}")
    print(f"Burn Rate: {format_currency(revenue['burn_rate'])}")

    # Tracking
    tracking = revenue['tracking']
    print_section("Target Tracking")
    print(f"Status: {tracking['status'].upper()}")
    print(f"Progress: {format_percent(tracking['percent_of_expected'])} of expected")
    print(f"On Track: {'YES' if tracking['on_track'] else 'NO'}")

    # Department breakdown
    dept_revenue = revenue['department_breakdown']
    if dept_revenue:
        print_section("Revenue by Department")
        for dept, amount in sorted(dept_revenue.items(), key=lambda x: x[1], reverse=True):
            print(f"{dept.title()}: {format_currency(amount)}")

    # Top agents
    top_agents = revenue['top_revenue_generators']
    if top_agents:
        print_section("Top Revenue Generators")
        for i, agent in enumerate(top_agents, 1):
            print(f"{i}. {agent['name']} ({agent['department']})")
            print(f"   Revenue: {format_currency(agent['revenue'])} | "
                  f"Cost: {format_currency(agent['cost'])} | "
                  f"ROI: {format_percent(agent['roi'])}")

    # Recommendations
    if revenue.get('recommendations'):
        print_section("Recommendations")
        for i, rec in enumerate(revenue['recommendations'], 1):
            print(f"{i}. {rec}")


def cmd_board_status(args):
    """Show board agent status"""
    print_header("Board Status")

    board = get_board()
    status = board.get_status()

    print(f"Timestamp: {status['timestamp']}")
    print(f"Board Active: {status['board_active']}")

    # Operational health
    print_section("Operational Health (COO)")
    coo = status['operational_health']
    print(coo['status'])

    # Financial health
    print_section("Financial Health (CFO)")
    cfo = status['financial_health']
    print(cfo['analysis'])


def cmd_board_decide(args):
    """Make a board decision"""
    print_header("CEO Decision")

    board = get_board()
    result = board.ceo.make_decision(args.question)

    print(f"DECISION: {result['decision']}")
    print(f"\nReasoning:\n{result['reasoning']}")
    print(f"\nTokens Used: {result['tokens_used']}")
    print(f"Cost: {format_currency(result['cost'])}")


def cmd_deploy(args):
    """Deploy an agent"""
    print_header(f"Deploying {args.agent_type} Agent")

    factory = get_factory()
    departments = get_departments()

    # Get department
    dept = departments.get_department(args.department)
    if not dept:
        print(f"Error: Unknown department '{args.department}'")
        print("Available: sales, marketing, product, operations, research")
        return

    # Parse config
    config = {}
    if hasattr(args, 'config') and args.config:
        try:
            config = json.loads(args.config)
        except:
            # Try as key=value pairs
            for pair in args.config.split(','):
                if '=' in pair:
                    key, value = pair.split('=', 1)
                    config[key.strip()] = value.strip()

    # Special handling for templates
    if args.agent_type == 'dds' and args.department == 'sales':
        result = dept.deploy_dds(config)
        print(f"✓ DDS agent deployed: {result['agent_id']}")
        return

    # Deploy generic agent
    agent_id = factory.deploy_agent(
        agent_type=args.agent_type,
        name=f"{args.agent_type}-{safe_datetime_now().strftime('%Y%m%d-%H%M%S')}",
        department=args.department,
        config=config
    )

    print(f"✓ Agent deployed successfully")
    print(f"  Agent ID: {agent_id}")


def cmd_agents_list(args):
    """List all agents"""
    print_header("Agent List")

    factory = get_factory()

    status_filter = args.status if hasattr(args, 'status') else None
    dept_filter = args.department if hasattr(args, 'department') else None

    agents = factory.list_agents(status=status_filter, department=dept_filter)

    if not agents:
        print("No agents found")
        return

    print(f"Found {len(agents)} agents\n")

    for agent in agents:
        status_icon = {
            'active': '▶',
            'paused': '⏸',
            'killed': '⨯'
        }.get(agent['status'], '?')

        print(f"{status_icon} {agent['name']} ({agent['agent_id']})")
        print(f"   Type: {agent['type']} | Dept: {agent['department']} | Status: {agent['status']}")
        print(f"   Cost: {format_currency(agent['cost'])} | "
              f"Revenue: {format_currency(agent['revenue'])} | "
              f"ROI: {format_percent(agent['roi'])}")
        print()


def cmd_agent_status(args):
    """Show detailed agent status"""
    print_header(f"Agent Status: {args.agent_id}")

    factory = get_factory()
    status = factory.get_agent_status(args.agent_id)

    if not status:
        print(f"Error: Agent {args.agent_id} not found")
        return

    print(f"Name: {status['name']}")
    print(f"Type: {status['type']}")
    print(f"Department: {status['department']}")
    print(f"Status: {status['status']}")
    print(f"Deployed: {status['deployed_at']}")
    print(f"Last Active: {status.get('last_active', 'Never')}")

    metrics = status['metrics']
    print_section("Metrics")
    print(f"Tokens Used: {metrics['tokens_used']:,} / {metrics['token_budget']:,} "
          f"({format_percent(metrics['budget_used_percent'])})")
    print(f"Total Cost: {format_currency(metrics['total_cost'])}")
    print(f"Revenue Generated: {format_currency(metrics['revenue_generated'])}")
    print(f"Profit: {format_currency(metrics['profit'])}")
    print(f"ROI: {format_percent(metrics['roi'])}")
    print(f"Performance: {metrics['performance']}")

    if status.get('config'):
        print_section("Configuration")
        print(json.dumps(status['config'], indent=2))


def cmd_agent_pause(args):
    """Pause an agent"""
    factory = get_factory()
    factory.pause_agent(args.agent_id)


def cmd_agent_resume(args):
    """Resume an agent"""
    factory = get_factory()
    factory.resume_agent(args.agent_id)


def cmd_agent_kill(args):
    """Kill an agent"""
    factory = get_factory()
    factory.kill_agent(args.agent_id)


def cmd_roi(args):
    """Show ROI for agent or department"""
    print_header(f"ROI Report: {args.target}")

    memory = get_memory()

    # Check if it's a department or agent
    departments = get_departments()
    dept = departments.get_department(args.target)

    if dept:
        # Department ROI
        metrics = dept.get_metrics()
        print_section(f"{args.target.title()} Department")
        print(f"Total Cost: {format_currency(metrics['total_cost'])}")
        print(f"Total Revenue: {format_currency(metrics['total_revenue'])}")
        print(f"ROI: {format_percent(metrics['roi'])}")
        print(f"Active Agents: {metrics['active_agents']}")
        print(f"Monthly Target: {format_currency(metrics['monthly_target'])}")
        print(f"Progress: {format_percent(metrics['target_progress'])}")
    else:
        # Agent ROI
        factory = get_factory()
        status = factory.get_agent_status(args.target)

        if not status:
            print(f"Error: '{args.target}' not found (not a department or agent ID)")
            return

        metrics = status['metrics']
        print_section(f"{status['name']}")
        print(f"Cost: {format_currency(metrics['total_cost'])}")
        print(f"Revenue: {format_currency(metrics['revenue_generated'])}")
        print(f"Profit: {format_currency(metrics['profit'])}")
        print(f"ROI: {format_percent(metrics['roi'])}")
        print(f"Performance: {metrics['performance']}")


def cmd_optimize(args):
    """Run cost optimization"""
    print_header("Cost Optimization")

    factory = get_factory()
    result = factory.auto_optimize_agents()

    print(f"Timestamp: {result['timestamp']}")
    print(f"Actions Taken: {result['actions_taken']}")
    print(f"Estimated Cost Saved: {format_currency(result['estimated_cost_saved'])}")
    print(f"Current AI Cost %: {format_percent(result['current_cost_percent'])}")

    if result['details']:
        print_section("Actions")
        for action in result['details']:
            print(f"• {action['agent_name']} ({action['agent_id']})")
            print(f"  Action: {action['action']}")
            print(f"  Reason: {action['reason']}")
            if 'cost_saved' in action:
                print(f"  Savings: {format_currency(action['cost_saved'])}")


def cmd_council(args):
    """Run R&D Expert Council analysis"""
    print_header("R&D Expert Council")

    try:
        from agents.council.expert_council import get_council

        council = get_council()
        result = council.analyze(args.question)

        print(f"Question: {args.question}\n")

        # Print each avatar's analysis
        for avatar_name, analysis in result['analyses'].items():
            print_section(f"{avatar_name.title()} Avatar")
            print(analysis)

        print_section("Consensus")
        print(result['consensus'])

        if result.get('action_items'):
            print_section("Action Items")
            for i, item in enumerate(result['action_items'], 1):
                print(f"{i}. {item}")

        print(f"\nTokens Used: {result['tokens_used']}")
        print(f"Cost: {format_currency(result['cost'])}")

    except ImportError:
        print("Error: R&D Expert Council not yet implemented")
        print("Run: nova deploy research council to set up")


# === SANDBOX COMMANDS ===

def cmd_sandbox_status(args):
    """Show sandbox environment status"""
    print_header("Sandbox Environment")

    sandbox = get_sandbox()
    summary = sandbox.get_summary()

    print_section("Summary")
    print(f"Total Projects: {summary['total_projects']}")
    print(f"  Active: {summary['active_projects']}")
    print(f"  Promoted: {summary['promoted_projects']}")
    print(f"Total Agents: {summary['total_agents']}")
    print(f"Total Cost: {format_currency(summary['total_cost'])}")
    print(f"\nNote: Sandbox costs are isolated (not tracked in production)")

    if summary['projects']:
        print_section("Projects")
        for project in summary['projects']:
            status_icon = {'active': '▶', 'promoted': '✓', 'deleted': '⨯'}.get(project['status'], '?')
            print(f"{status_icon} {project['name']} ({project['id']})")
            print(f"   Status: {project['status']} | Created: {project['created_at'][:10]}")

            if 'metrics' in project:
                metrics = project['metrics']
                print(f"   Agents: {metrics['total_agents']} | "
                      f"Cost: {format_currency(metrics['total_cost'])} | "
                      f"ROI: {format_percent(metrics['roi'])}")
            print()


def cmd_sandbox_create(args):
    """Create a new sandbox project"""
    print_header("Create Sandbox Project")

    sandbox = get_sandbox()
    project_id = sandbox.create_project(args.name, args.description)

    print(f"\n✓ Ready to experiment!")
    print(f"\nNext steps:")
    print(f"  1. Deploy agents: nova sandbox deploy {project_id} <agent_type>")
    print(f"  2. Test freely (no production impact)")
    print(f"  3. Evaluate: nova sandbox eval {project_id}")
    print(f"  4. Promote if successful: nova sandbox promote {project_id}")


def cmd_sandbox_list(args):
    """List sandbox projects"""
    print_header("Sandbox Projects")

    sandbox = get_sandbox()
    projects = sandbox.list_projects()

    if not projects:
        print("No sandbox projects found")
        print("\nCreate one: nova sandbox create <name>")
        return

    for project in projects:
        status_icon = {'active': '▶', 'promoted': '✓', 'deleted': '⨯'}.get(project['status'], '?')
        print(f"\n{status_icon} {project['name']}")
        print(f"   ID: {project['id']}")
        print(f"   Status: {project['status']}")
        print(f"   Created: {project['created_at']}")

        if project.get('description'):
            print(f"   Description: {project['description']}")

        if 'metrics' in project:
            metrics = project['metrics']
            print(f"   Metrics:")
            print(f"     Agents: {metrics['total_agents']} ({metrics['active_agents']} active)")
            print(f"     Cost: {format_currency(metrics['total_cost'])}")
            print(f"     Revenue: {format_currency(metrics['total_revenue'])}")
            print(f"     ROI: {format_percent(metrics['roi'])}")


def cmd_sandbox_project(args):
    """Show sandbox project details"""
    print_header(f"Sandbox Project: {args.project_id}")

    sandbox = get_sandbox()
    project = sandbox.get_project(args.project_id)

    if not project:
        print(f"Error: Project {args.project_id} not found")
        return

    print(f"Name: {project.name}")
    print(f"ID: {project.project_id}")
    print(f"Description: {project.description or 'None'}")
    print(f"Workspace: {project.workspace_path}")

    metrics = project.get_metrics()
    print_section("Metrics")
    print(f"Total Agents: {metrics['total_agents']}")
    print(f"Active Agents: {metrics['active_agents']}")
    print(f"Total Cost: {format_currency(metrics['total_cost'])}")
    print(f"Total Revenue: {format_currency(metrics['total_revenue'])}")
    print(f"Profit: {format_currency(metrics['profit'])}")
    print(f"ROI: {format_percent(metrics['roi'])}")

    agents = project.list_agents()
    if agents:
        print_section("Agents")
        for agent in agents:
            status_icon = {'active': '▶', 'paused': '⏸', 'killed': '⨯'}.get(agent['status'], '?')
            print(f"{status_icon} {agent['name']} ({agent['id']})")
            print(f"   Type: {agent['type']} | Status: {agent['status']}")
            print(f"   Cost: {format_currency(agent.get('total_cost', 0))} | "
                  f"ROI: {format_percent(agent.get('roi', 0))}")


def cmd_sandbox_deploy(args):
    """Deploy an agent in a sandbox project"""
    print_header("Deploy Sandbox Agent")

    sandbox = get_sandbox()

    # Parse config
    config = {}
    if hasattr(args, 'config') and args.config:
        try:
            config = json.loads(args.config)
        except:
            for pair in args.config.split(','):
                if '=' in pair:
                    key, value = pair.split('=', 1)
                    config[key.strip()] = value.strip()

    if hasattr(args, 'name') and args.name:
        config['name'] = args.name

    agent_id = sandbox.deploy_agent(args.project_id, args.agent_type, config)

    print(f"\n✓ Sandbox agent deployed!")
    print(f"  Agent ID: {agent_id}")
    print(f"\nNote: This agent runs in sandbox (no production impact)")


def cmd_sandbox_eval(args):
    """Evaluate a sandbox project"""
    use_council = getattr(args, 'council', False)

    if use_council:
        print_header(f"Comprehensive Evaluation (R&D Council): {args.project_id}")
    else:
        print_header(f"Quick Evaluation: {args.project_id}")

    sandbox = get_sandbox()
    evaluation = sandbox.evaluate_project(args.project_id, use_council=use_council)

    print(f"Project: {evaluation['project_name']}")
    print(f"Evaluated: {evaluation['evaluated_at']}")
    print(f"Evaluation Type: {evaluation.get('evaluation_type', 'quick')}\n")

    print_section("Metrics")
    metrics = evaluation['metrics']
    print(f"Total Agents: {metrics['total_agents']}")
    print(f"Active Agents: {metrics['active_agents']}")
    print(f"Total Cost: {format_currency(metrics['total_cost'])}")
    print(f"Revenue: {format_currency(metrics['total_revenue'])}")
    print(f"Profit: {format_currency(metrics['profit'])}")
    print(f"ROI: {format_percent(metrics['roi'])}")

    print_section("Evaluation Criteria")
    for criterion, data in evaluation['criteria'].items():
        status = "✓" if data['pass'] else "✗"
        print(f"{status} {criterion.replace('_', ' ').title()}")
        print(f"   Value: {data['value']} | Threshold: {data['threshold']}")

    # Show council analysis if available
    if 'council_analysis' in evaluation:
        print_section("R&D Expert Council Analysis")

        council = evaluation['council_analysis']

        # Show each avatar's view
        print("Expert Perspectives:\n")
        avatars = {'thiel': 'Thiel (Contrarian/Monopoly)',
                  'musk': 'Musk (First Principles/Speed)',
                  'graham': 'Graham (Fundamentals/PMF)',
                  'taleb': 'Taleb (Risk/Antifragility)'}

        for key, name in avatars.items():
            print(f"{name}:")
            print(f"  {council['analyses'][key]}\n")

        # Show consensus
        print("Consensus:")
        print(f"  {council['consensus']}\n")

        # Show action items
        if council['action_items']:
            print("Action Items:")
            for item in council['action_items']:
                print(f"  • {item}")
            print()

        # Show cost
        print(f"Council Analysis Cost: {format_currency(council['cost'])}\n")

    # Show final recommendation
    print_section("Final Recommendation")

    if 'final_recommendation' in evaluation:
        final = evaluation['final_recommendation']
        print(f"Decision: {final['decision']}")
        print(f"Confidence: {final['confidence']}")
        print(f"Reason: {final['reason']}\n")

        if final['decision'] == 'PROMOTE':
            print(f"✓ Ready to promote to production!")
            print(f"  Run: nova sandbox promote {args.project_id}")
        elif final['decision'] == 'PROMOTE_WITH_CAUTION':
            print(f"⚠ Can promote, but address council recommendations first")
            print(f"  Run: nova sandbox promote {args.project_id}")
        elif final['decision'] == 'HOLD':
            print(f"⏸ Hold - Make improvements based on council feedback")
        else:
            print(f"✗ Not ready for promotion - needs significant work")
    else:
        # Fallback to basic recommendation
        print(f"Status: {evaluation['recommendation']}")
        print(f"Reason: {evaluation['reason']}")

        if evaluation['recommendation'] in ['RECOMMEND', 'STRONGLY_RECOMMEND']:
            print(f"\n✓ Ready to promote to production!")
            print(f"  Run: nova sandbox promote {args.project_id}")

    # Show tip about council analysis
    if not use_council:
        print(f"\n💡 Tip: For deeper analysis, run: nova sandbox eval {args.project_id} --council")


def cmd_sandbox_promote(args):
    """Promote a sandbox project to production"""
    print_header(f"Promote Project to Production")

    sandbox = get_sandbox()
    result = sandbox.promote_project(args.project_id)

    if result['status'] == 'cancelled':
        print(f"Promotion cancelled: {result['reason']}")
        return

    print(f"\n✓ PROJECT PROMOTED TO PRODUCTION")
    print(f"\nProject: {result['project_name']}")
    print(f"Agents Migrated: {result['agents_migrated']}")

    if result['migrated_agents']:
        print_section("Migrated Agents")
        for agent in result['migrated_agents']:
            print(f"✓ {agent['name']}")
            print(f"   Production ID: {agent['production_id']}")
            print(f"   ROI: {format_percent(agent['roi'])}")


def cmd_sandbox_kill(args):
    """Kill a sandbox project"""
    sandbox = get_sandbox()

    confirm = input(f"Kill project {args.project_id}? (yes/no): ")
    if confirm.lower() != 'yes':
        print("Cancelled")
        return

    delete_workspace = False
    if hasattr(args, 'delete') and args.delete:
        delete_workspace = True

    success = sandbox.kill_project(args.project_id, delete_workspace)

    if success:
        print(f"✓ Project killed")
    else:
        print(f"Error killing project")


# === DASHBOARD COMMANDS ===

def cmd_dashboard_start(args):
    """Start the dashboard server"""
    import subprocess
    import os
    from pathlib import Path

    print_header("Starting NovaOS Dashboard")

    dashboard_dir = Path(__file__).parent / "dashboard"

    if not dashboard_dir.exists():
        print("Error: Dashboard directory not found")
        return

    # Use port 5001 by default (5000 often used by macOS AirPlay)
    port = 5001

    # Check if already running
    try:
        import requests
        response = requests.get(f"http://localhost:{port}/api/overview", timeout=1)
        if response.status_code == 200:
            print(f"Dashboard is already running at http://localhost:{port}")
            return
    except:
        pass

    print(f"\n✓ Starting Flask server on http://localhost:{port}")
    print("  Press Ctrl+C to stop\n")

    # Start the dashboard
    os.chdir(dashboard_dir)
    subprocess.run([sys.executable, "app.py"])


def cmd_dashboard_stop(args):
    """Stop the dashboard server"""
    import subprocess
    import signal

    print_header("Stopping NovaOS Dashboard")

    # Find and kill Flask process (try both port 5001 and 5000)
    try:
        # Try port 5001 first (default)
        result = subprocess.run(
            ["lsof", "-ti:5001"],
            capture_output=True,
            text=True
        )

        if not result.stdout.strip():
            # Try port 5000 as fallback
            result = subprocess.run(
                ["lsof", "-ti:5000"],
                capture_output=True,
                text=True
            )

        if result.stdout.strip():
            pid = result.stdout.strip()
            subprocess.run(["kill", pid])
            print(f"✓ Dashboard stopped (PID: {pid})")
        else:
            print("Dashboard is not running")
    except Exception as e:
        print(f"Error stopping dashboard: {e}")


def cmd_dashboard_status(args):
    """Check dashboard server status"""
    print_header("Dashboard Status")

    try:
        import requests

        # Try port 5001 first (default), then 5000
        for port in [5001, 5000]:
            try:
                response = requests.get(f"http://localhost:{port}/api/overview", timeout=1)
                if response.status_code == 200:
                    print("✓ Dashboard is RUNNING")
                    print(f"  URL: http://localhost:{port}")

                    data = response.json()
                    print(f"\n  System Health: {data['system_health']}")
                    print(f"  Active Agents: {data['active_agents']}")
                    return
            except requests.exceptions.ConnectionError:
                continue

        print("✗ Dashboard is NOT RUNNING")
        print("\nTo start: nova dashboard start")

    except ImportError:
        print("Error: requests library not installed")
        print("Run: pip install requests")
    except Exception as e:
        print(f"Error checking status: {e}")


# === WORKER COMMANDS ===

def cmd_workers_start(args):
    """Start all background workers"""
    print_header("Starting Background Workers")

    manager = get_worker_manager()

    if len(manager.workers) == 0:
        print("No workers configured. Deploy workers first.")
        print("\nExample: nova deploy sales outbound_agent")
        return

    manager.start_all()
    print(f"✓ Started {len(manager.workers)} workers")

    # Show status
    status = manager.get_status()
    print(f"\nRunning: {status['workers']['running']}")
    print(f"Paused: {status['workers']['paused']}")
    print(f"Stopped: {status['workers']['stopped']}")


def cmd_workers_stop(args):
    """Stop all background workers"""
    print_header("Stopping Background Workers")

    manager = get_worker_manager()
    manager.stop_all()

    print(f"✓ Stopped all workers")


def cmd_workers_status(args):
    """Show worker status"""
    print_header("Background Workers Status")

    manager = get_worker_manager()
    monitor = get_worker_monitor()

    status = manager.get_status()

    print_section("Overview")
    print(f"Total Workers: {status['workers']['total']}")
    print(f"  Running: {status['workers']['running']}")
    print(f"  Paused: {status['workers']['paused']}")
    print(f"  Stopped: {status['workers']['stopped']}")
    print(f"  Crashed: {status['workers']['crashed']}")

    print_section("Performance")
    print(f"Total Revenue: {format_currency(status['metrics']['total_revenue'])}")
    print(f"Total Cost: {format_currency(status['metrics']['total_cost'])}")
    print(f"Profit: {format_currency(status['metrics']['profit'])}")
    print(f"ROI: {format_percent(status['metrics']['roi'])}")

    print_section("Workers")
    for worker_status in status['workers_detail']:
        print(f"\n[{worker_status['worker_id']}] {worker_status['name']}")
        print(f"  Status: {worker_status['status']}")
        print(f"  Uptime: {worker_status['uptime']}")
        print(f"  ROI: {format_percent(worker_status['metrics']['roi'])}")
        print(f"  Profit: {format_currency(worker_status['metrics']['profit'])}")


def cmd_workers_scale(args):
    """Scale a worker"""
    print_header(f"Scaling Worker: {args.worker_id}")

    manager = get_worker_manager()

    try:
        manager.scale_worker(args.worker_id, args.multiplier)
        print(f"✓ Scaled {args.worker_id} to {args.multiplier}x")
    except Exception as e:
        print(f"Error: {e}")


def cmd_workers_health(args):
    """Check worker health"""
    print_header("Worker Health Check")

    manager = get_worker_manager()
    health = manager.health_check()

    print(f"Healthy Workers: {health['healthy']}")
    print(f"Unhealthy Workers: {health['unhealthy']}")

    if health['unhealthy_workers']:
        print_section("Unhealthy Workers")
        for worker_id in health['unhealthy_workers']:
            print(f"  - {worker_id}")

    if health['needs_restart']:
        print_section("Needs Restart")
        for worker_id in health['needs_restart']:
            print(f"  - {worker_id}")


# === AUTONOMOUS COMMANDS ===

def cmd_autonomous_enable(args):
    """Enable autonomous mode"""
    print_header("Enabling Autonomous Mode")

    engine = get_autonomous_engine()
    engine.enable()

    print("✓ Autonomous mode ENABLED")
    print("\nThe system will now:")
    print("  - Auto-scale high-ROI agents")
    print("  - Auto-kill underperforming agents")
    print("  - Make ROI-optimized decisions")
    print("\nWarning: Major decisions will still require approval")


def cmd_autonomous_disable(args):
    """Disable autonomous mode"""
    print_header("Disabling Autonomous Mode")

    engine = get_autonomous_engine()
    engine.disable()

    print("✓ Autonomous mode DISABLED")


def cmd_autonomous_status(args):
    """Show autonomous engine status"""
    print_header("Autonomous Engine Status")

    engine = get_autonomous_engine()
    status = engine.get_status()

    print_section("Status")
    print(f"Enabled: {'YES' if status['enabled'] else 'NO'}")

    print_section("Configuration")
    print(f"Max Daily Budget: {format_currency(status['config']['max_daily_budget'])}")
    print(f"Min ROI Threshold: {format_percent(status['config']['min_roi_threshold'])}")
    print(f"Scale ROI Threshold: {format_percent(status['config']['scale_roi_threshold'])}")
    print(f"Kill ROI Threshold: {format_percent(status['config']['kill_roi_threshold'])}")

    print_section("Budget")
    print(f"Spent Today: {format_currency(status['budget']['spent_today'])}")
    print(f"Remaining: {format_currency(status['budget']['remaining'])}")
    print(f"Usage: {format_percent(status['budget']['percent_used'])}")

    print_section("Decisions")
    print(f"Total Decisions: {status['decisions']['total']}")
    print(f"Today: {status['decisions']['today']}")
    print(f"Pending Approvals: {status['decisions']['pending_approvals']}")

    if status['pending_approvals']:
        print_section("Pending Approvals")
        for approval in status['pending_approvals']:
            print(f"\n  Type: {approval['type']}")
            print(f"  Target: {approval['target']}")
            print(f"  Reason: {approval['reason']}")
            print(f"  Expected ROI: {format_percent(approval['expected_roi'])}")
            print(f"  Cost Impact: {format_currency(approval['cost_impact'])}")


def cmd_autonomous_run(args):
    """Run autonomous analysis cycle"""
    print_header("Running Autonomous Analysis")

    engine = get_autonomous_engine()
    manager = get_worker_manager()
    monitor = get_worker_monitor()

    result = engine.run_analysis_cycle(manager, monitor)

    print(f"Analyzed: {len(result['analyses'])} workers")
    print(f"Decisions Made: {result['decisions_made']}")
    print(f"Pending Approvals: {result['pending_approvals']}")

    if result['decisions']:
        print_section("Decisions")
        for decision in result['decisions']:
            print(f"\n  {decision['type'].upper()}: {decision['target']}")
            print(f"  Reason: {decision['reason']}")
            print(f"  Expected ROI: {format_percent(decision['expected_roi'])}")
            print(f"  Cost Impact: {format_currency(decision['cost_impact'])}")
            print(f"  Requires Approval: {'YES' if decision['requires_approval'] else 'NO'}")


# === MAIN CLI ===

def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="NovaOS V2 - AI Business Orchestration Platform",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    subparsers = parser.add_subparsers(dest='command', help='Commands')

    # System commands
    subparsers.add_parser('status', help='Show complete system status')

    costs_parser = subparsers.add_parser('costs', help='Show AI cost breakdown')
    costs_parser.add_argument('--period', default='today', choices=['today', 'week', 'month'],
                            help='Time period')

    subparsers.add_parser('revenue', help='Show revenue tracking')

    # Board commands
    subparsers.add_parser('board', help='Show board status')

    decide_parser = subparsers.add_parser('decide', help='Make board decision')
    decide_parser.add_argument('question', help='Question or opportunity to evaluate')

    # Deployment
    deploy_parser = subparsers.add_parser('deploy', help='Deploy an agent')
    deploy_parser.add_argument('department', help='Department (sales, marketing, product, operations, research)')
    deploy_parser.add_argument('agent_type', help='Agent type')
    deploy_parser.add_argument('--config', help='Agent configuration (JSON or key=value pairs)')

    # Agent management
    agents_parser = subparsers.add_parser('agents', help='List agents')
    agents_parser.add_argument('--status', choices=['active', 'paused', 'killed'], help='Filter by status')
    agents_parser.add_argument('--department', help='Filter by department')

    agent_parser = subparsers.add_parser('agent', help='Show agent status')
    agent_parser.add_argument('agent_id', help='Agent ID')

    pause_parser = subparsers.add_parser('pause', help='Pause an agent')
    pause_parser.add_argument('agent_id', help='Agent ID')

    resume_parser = subparsers.add_parser('resume', help='Resume an agent')
    resume_parser.add_argument('agent_id', help='Agent ID')

    kill_parser = subparsers.add_parser('kill', help='Kill an agent')
    kill_parser.add_argument('agent_id', help='Agent ID')

    # Financial
    roi_parser = subparsers.add_parser('roi', help='Show ROI for agent or department')
    roi_parser.add_argument('target', help='Agent ID or department name')

    subparsers.add_parser('optimize', help='Run cost optimization')

    # R&D Council
    council_parser = subparsers.add_parser('council', help='Run R&D Expert Council analysis')
    council_parser.add_argument('question', help='Question to analyze')

    # Sandbox commands
    sandbox_parser = subparsers.add_parser('sandbox', help='Sandbox environment')
    sandbox_subparsers = sandbox_parser.add_subparsers(dest='sandbox_command', help='Sandbox commands')

    sandbox_subparsers.add_parser('status', help='Show sandbox status')

    sandbox_create_parser = sandbox_subparsers.add_parser('create', help='Create new sandbox project')
    sandbox_create_parser.add_argument('name', help='Project name')
    sandbox_create_parser.add_argument('--description', help='Project description')

    sandbox_subparsers.add_parser('list', help='List sandbox projects')

    sandbox_project_parser = sandbox_subparsers.add_parser('project', help='Show project details')
    sandbox_project_parser.add_argument('project_id', help='Project ID')

    sandbox_deploy_parser = sandbox_subparsers.add_parser('deploy', help='Deploy agent in sandbox')
    sandbox_deploy_parser.add_argument('project_id', help='Project ID')
    sandbox_deploy_parser.add_argument('agent_type', help='Agent type')
    sandbox_deploy_parser.add_argument('--name', help='Agent name')
    sandbox_deploy_parser.add_argument('--config', help='Agent configuration')

    sandbox_eval_parser = sandbox_subparsers.add_parser('eval', help='Evaluate project')
    sandbox_eval_parser.add_argument('project_id', help='Project ID')
    sandbox_eval_parser.add_argument('--council', action='store_true',
                                     help='Use R&D Council for deep analysis (costs ~$0.50)')

    sandbox_promote_parser = sandbox_subparsers.add_parser('promote', help='Promote project to production')
    sandbox_promote_parser.add_argument('project_id', help='Project ID')

    sandbox_kill_parser = sandbox_subparsers.add_parser('kill', help='Kill sandbox project')
    sandbox_kill_parser.add_argument('project_id', help='Project ID')
    sandbox_kill_parser.add_argument('--delete', action='store_true', help='Delete workspace directory')

    # Dashboard commands
    dashboard_parser = subparsers.add_parser('dashboard', help='Visual dashboard')
    dashboard_subparsers = dashboard_parser.add_subparsers(dest='dashboard_command', help='Dashboard commands')

    dashboard_subparsers.add_parser('start', help='Start dashboard server')
    dashboard_subparsers.add_parser('stop', help='Stop dashboard server')
    dashboard_subparsers.add_parser('status', help='Check dashboard status')

    # Worker commands
    workers_parser = subparsers.add_parser('workers', help='Background worker management')
    workers_subparsers = workers_parser.add_subparsers(dest='workers_command', help='Worker commands')

    workers_subparsers.add_parser('start', help='Start all workers')
    workers_subparsers.add_parser('stop', help='Stop all workers')
    workers_subparsers.add_parser('status', help='Show worker status')
    workers_subparsers.add_parser('health', help='Check worker health')

    workers_scale_parser = workers_subparsers.add_parser('scale', help='Scale a worker')
    workers_scale_parser.add_argument('worker_id', help='Worker ID')
    workers_scale_parser.add_argument('--multiplier', type=int, default=2, help='Scale multiplier')

    # Autonomous commands
    autonomous_parser = subparsers.add_parser('autonomous', help='Autonomous decision engine')
    autonomous_subparsers = autonomous_parser.add_subparsers(dest='autonomous_command', help='Autonomous commands')

    autonomous_subparsers.add_parser('enable', help='Enable autonomous mode')
    autonomous_subparsers.add_parser('disable', help='Disable autonomous mode')
    autonomous_subparsers.add_parser('status', help='Show autonomous status')
    autonomous_subparsers.add_parser('run', help='Run analysis cycle')

    # Learning commands (from cli_extensions)
    from cli_extensions import register_learning_commands
    learning_handlers = register_learning_commands(subparsers)

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    # Handle sandbox subcommands
    if args.command == 'sandbox':
        if not args.sandbox_command:
            sandbox_parser.print_help()
            return

        sandbox_handlers = {
            'status': cmd_sandbox_status,
            'create': cmd_sandbox_create,
            'list': cmd_sandbox_list,
            'project': cmd_sandbox_project,
            'deploy': cmd_sandbox_deploy,
            'eval': cmd_sandbox_eval,
            'promote': cmd_sandbox_promote,
            'kill': cmd_sandbox_kill
        }

        handler = sandbox_handlers.get(args.sandbox_command)
        if handler:
            try:
                handler(args)
            except Exception as e:
                print(f"\nError: {e}")
                import traceback
                traceback.print_exc()
        else:
            sandbox_parser.print_help()
        return

    # Handle dashboard subcommands
    if args.command == 'dashboard':
        if not args.dashboard_command:
            dashboard_parser.print_help()
            return

        dashboard_handlers = {
            'start': cmd_dashboard_start,
            'stop': cmd_dashboard_stop,
            'status': cmd_dashboard_status
        }

        handler = dashboard_handlers.get(args.dashboard_command)
        if handler:
            try:
                handler(args)
            except Exception as e:
                print(f"\nError: {e}")
                import traceback
                traceback.print_exc()
        else:
            dashboard_parser.print_help()
        return

    # Handle worker subcommands
    if args.command == 'workers':
        if not args.workers_command:
            workers_parser.print_help()
            return

        workers_handlers = {
            'start': cmd_workers_start,
            'stop': cmd_workers_stop,
            'status': cmd_workers_status,
            'scale': cmd_workers_scale,
            'health': cmd_workers_health
        }

        handler = workers_handlers.get(args.workers_command)
        if handler:
            try:
                handler(args)
            except Exception as e:
                print(f"\nError: {e}")
                import traceback
                traceback.print_exc()
        else:
            workers_parser.print_help()
        return

    # Handle autonomous subcommands
    if args.command == 'autonomous':
        if not args.autonomous_command:
            autonomous_parser.print_help()
            return

        autonomous_handlers = {
            'enable': cmd_autonomous_enable,
            'disable': cmd_autonomous_disable,
            'status': cmd_autonomous_status,
            'run': cmd_autonomous_run
        }

        handler = autonomous_handlers.get(args.autonomous_command)
        if handler:
            try:
                handler(args)
            except Exception as e:
                print(f"\nError: {e}")
                import traceback
                traceback.print_exc()
        else:
            autonomous_parser.print_help()
        return

    # Handle learning subcommands
    if args.command == 'learn':
        if not hasattr(args, 'learn_command') or not args.learn_command:
            print("Usage: nova learn {store|query|analyze|patterns}")
            print("\nCommands:")
            print("  store       Store decision outcome")
            print("  query       Query similar past situations")
            print("  analyze     Run weekly analysis")
            print("  patterns    Show identified patterns")
            return

        handler = learning_handlers.get(args.learn_command)
        if handler:
            try:
                handler(args)
            except Exception as e:
                print(f"\nError: {e}")
                import traceback
                traceback.print_exc()
        return

    # Route to command handler
    handlers = {
        'status': cmd_status,
        'costs': cmd_costs,
        'revenue': cmd_revenue,
        'board': cmd_board_status,
        'decide': cmd_board_decide,
        'deploy': cmd_deploy,
        'agents': cmd_agents_list,
        'agent': cmd_agent_status,
        'pause': cmd_agent_pause,
        'resume': cmd_agent_resume,
        'kill': cmd_agent_kill,
        'roi': cmd_roi,
        'optimize': cmd_optimize,
        'council': cmd_council
    }

    handler = handlers.get(args.command)
    if handler:
        try:
            handler(args)
        except Exception as e:
            print(f"\nError: {e}")
            import traceback


def safe_datetime_now():
    """Get current datetime with fallback for timestamp overflow"""
    try:
        return safe_datetime_now()
    except (OSError, OverflowError, ValueError):
        from datetime import datetime as dt
        return dt(2025, 1, 1, 0, 0, 0)

            traceback.print_exc()
    else:
        print(f"Unknown command: {args.command}")
        parser.print_help()


if __name__ == '__main__':
    main()
