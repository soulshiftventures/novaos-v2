#!/usr/bin/env python3
"""
NovaOS V2 Sandbox - Example Usage
Demonstrates sandbox workflow for testing ideas
"""

from sandbox.manager import get_sandbox


def example_basic_workflow():
    """Example: Basic sandbox workflow"""
    print("=" * 60)
    print("Example 1: Basic Sandbox Workflow")
    print("=" * 60)

    # Get sandbox manager
    sandbox = get_sandbox()

    # 1. Create a project
    print("\n1. Creating sandbox project...")
    project_id = sandbox.create_project(
        name="Test DDS Configuration",
        description="Testing new prospecting parameters for dentist vertical"
    )

    # 2. Deploy an agent
    print("\n2. Deploying test agent...")
    agent_id = sandbox.deploy_agent(
        project_id=project_id,
        agent_type="dds_prospecting",
        config={
            "name": "DDS Test Agent",
            "vertical": "dentists",
            "location": "NYC",
            "prospect_count": 50,
            "test_mode": True
        }
    )

    # 3. Simulate some usage (in real scenario, agent would run and generate data)
    print("\n3. Agent would run tests here...")
    print("   (In production, this is where you'd let the agent work)")

    # Get project to see current state
    project = sandbox.get_project(project_id)
    print(f"\n4. Current project state:")
    print(f"   Name: {project.name}")
    print(f"   ID: {project.project_id}")
    print(f"   Deployed Agents: {len(project.deployed_agents)}")

    return project_id


def example_evaluation():
    """Example: Evaluate a project"""
    print("\n" + "=" * 60)
    print("Example 2: Evaluate Project")
    print("=" * 60)

    sandbox = get_sandbox()

    # Get first active project
    projects = sandbox.list_projects()
    if not projects:
        print("No projects to evaluate")
        return

    project = projects[0]
    project_id = project['id']

    print(f"\nEvaluating project: {project['name']}")

    # Evaluate
    evaluation = sandbox.evaluate_project(project_id)

    print(f"\nRecommendation: {evaluation['recommendation']}")
    print(f"Reason: {evaluation['reason']}")

    print("\nCriteria:")
    for criterion, data in evaluation['criteria'].items():
        status = "✓" if data['pass'] else "✗"
        print(f"  {status} {criterion}: {data['value']} (threshold: {data['threshold']})")

    return evaluation


def example_multi_agent_project():
    """Example: Project with multiple agents"""
    print("\n" + "=" * 60)
    print("Example 3: Multi-Agent Sandbox Project")
    print("=" * 60)

    sandbox = get_sandbox()

    # Create project
    print("\n1. Creating multi-agent test project...")
    project_id = sandbox.create_project(
        name="Multi-Agent Content Strategy",
        description="Testing different content strategies across platforms"
    )

    # Deploy multiple agents
    print("\n2. Deploying multiple agents...")

    agents = [
        {
            "type": "content_creator",
            "config": {
                "name": "LinkedIn Daily",
                "platform": "linkedin",
                "frequency": "daily",
                "topic": "AI trends"
            }
        },
        {
            "type": "content_creator",
            "config": {
                "name": "Twitter Hourly",
                "platform": "twitter",
                "frequency": "hourly",
                "topic": "AI trends"
            }
        },
        {
            "type": "trend_monitor",
            "config": {
                "name": "AI Trend Monitor",
                "topic": "artificial intelligence",
                "sources": ["twitter", "reddit", "news"]
            }
        }
    ]

    for agent_config in agents:
        agent_id = sandbox.deploy_agent(
            project_id=project_id,
            agent_type=agent_config["type"],
            config=agent_config["config"]
        )
        print(f"   ✓ Deployed: {agent_config['config']['name']}")

    # Get project status
    project = sandbox.get_project(project_id)
    agents_list = project.list_agents()

    print(f"\n3. Project Status:")
    print(f"   Total Agents: {len(agents_list)}")
    for agent in agents_list:
        print(f"   - {agent['name']} ({agent['type']})")

    return project_id


def example_experiment_tracking():
    """Example: Track specific experiments"""
    print("\n" + "=" * 60)
    print("Example 4: Experiment Tracking")
    print("=" * 60)

    sandbox = get_sandbox()

    # Create project
    print("\n1. Creating experiment project...")
    project_id = sandbox.create_project(
        name="Budget Optimization Experiment",
        description="Testing impact of different token budgets on lead quality"
    )

    # Log first experiment
    print("\n2. Running Experiment 1: Baseline (1000 tokens)...")
    exp1_id = sandbox.log_experiment(
        project_id=project_id,
        name="Baseline Budget",
        hypothesis="Standard 1000 token budget provides acceptable lead quality",
        config={"token_budget": 1000}
    )

    # Simulate completing experiment
    sandbox.complete_experiment(
        experiment_id=exp1_id,
        results={
            "lead_quality_score": 7.2,
            "cost_per_lead": 2.50,
            "total_leads": 40
        },
        success=True
    )

    # Log second experiment
    print("\n3. Running Experiment 2: 2x Budget (2000 tokens)...")
    exp2_id = sandbox.log_experiment(
        project_id=project_id,
        name="Double Budget",
        hypothesis="Doubling token budget will improve lead quality significantly",
        config={"token_budget": 2000}
    )

    sandbox.complete_experiment(
        experiment_id=exp2_id,
        results={
            "lead_quality_score": 8.5,
            "cost_per_lead": 3.20,
            "total_leads": 45
        },
        success=True
    )

    # Get results
    project = sandbox.get_project(project_id)
    results = project.get_results()

    print("\n4. Experiment Results:")
    for exp in results['experiments']:
        print(f"\n   {exp['name']}:")
        print(f"     Hypothesis: {exp['hypothesis']}")
        print(f"     Success: {exp['success']}")
        if exp['results']:
            import json
            results_data = json.loads(exp['results'])
            for key, value in results_data.items():
                print(f"     {key}: {value}")

    return project_id


def example_summary():
    """Example: Get sandbox summary"""
    print("\n" + "=" * 60)
    print("Example 5: Sandbox Summary")
    print("=" * 60)

    sandbox = get_sandbox()
    summary = sandbox.get_summary()

    print(f"\nSandbox Environment Summary:")
    print(f"  Total Projects: {summary['total_projects']}")
    print(f"  Active Projects: {summary['active_projects']}")
    print(f"  Promoted Projects: {summary['promoted_projects']}")
    print(f"  Total Agents: {summary['total_agents']}")
    print(f"  Total Cost: ${summary['total_cost']:.2f}")

    if summary['projects']:
        print(f"\n  Projects:")
        for project in summary['projects']:
            status_icon = {
                'active': '▶',
                'promoted': '✓',
                'deleted': '⨯'
            }.get(project['status'], '?')

            print(f"    {status_icon} {project['name']}")
            print(f"       ID: {project['id']}")
            print(f"       Status: {project['status']}")


def main():
    """Run all examples"""
    print("\n" + "=" * 60)
    print("NovaOS V2 Sandbox - Example Usage")
    print("=" * 60)

    print("\nThese examples demonstrate the sandbox workflow:")
    print("1. Creating projects")
    print("2. Deploying agents")
    print("3. Evaluating results")
    print("4. Tracking experiments")
    print("5. Getting summaries")

    # Note: In a real scenario, you'd run these one at a time
    # and agents would actually perform work between steps

    try:
        # Example 1: Basic workflow
        project_id_1 = example_basic_workflow()

        # Example 2: Evaluation
        # (would need actual agent activity to have meaningful results)
        # example_evaluation()

        # Example 3: Multi-agent project
        project_id_3 = example_multi_agent_project()

        # Example 4: Experiment tracking
        project_id_4 = example_experiment_tracking()

        # Example 5: Summary
        example_summary()

        print("\n" + "=" * 60)
        print("Examples Complete!")
        print("=" * 60)

        print("\nNext steps:")
        print("  1. Let agents run and generate data")
        print("  2. Evaluate projects: ./cli.py sandbox eval <project_id>")
        print("  3. Promote successful projects: ./cli.py sandbox promote <project_id>")
        print("  4. Clean up failed projects: ./cli.py sandbox kill <project_id>")

    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
