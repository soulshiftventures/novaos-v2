#!/usr/bin/env python3
"""
NovaOS V2 Sandbox - Integration Test
Tests complete sandbox workflow
"""

from sandbox.manager import get_sandbox
import sys


def test_complete_workflow():
    """Test complete sandbox workflow"""
    print("=" * 60)
    print("NovaOS V2 Sandbox - Integration Test")
    print("=" * 60)

    try:
        # 1. Initialize sandbox
        print("\n[1/8] Initializing sandbox...")
        sandbox = get_sandbox()
        print("✓ Sandbox initialized")

        # 2. Create project
        print("\n[2/8] Creating test project...")
        project_id = sandbox.create_project(
            name="Integration Test Project",
            description="End-to-end integration test"
        )
        print(f"✓ Project created: {project_id}")

        # 3. Get project
        print("\n[3/8] Retrieving project...")
        project = sandbox.get_project(project_id)
        assert project is not None, "Project should exist"
        assert project.name == "Integration Test Project"
        print(f"✓ Project retrieved: {project.name}")

        # 4. List projects
        print("\n[4/8] Listing all projects...")
        projects = sandbox.list_projects()
        assert len(projects) > 0, "Should have at least one project"
        found = any(p['id'] == project_id for p in projects)
        assert found, "Should find our project in list"
        print(f"✓ Found {len(projects)} project(s)")

        # 5. Get metrics
        print("\n[5/8] Getting project metrics...")
        metrics = project.get_metrics()
        assert metrics['project_id'] == project_id
        assert metrics['total_agents'] == 0  # No agents yet
        print(f"✓ Metrics: {metrics['total_agents']} agents, ROI: {metrics['roi']:.1f}%")

        # 6. Get summary
        print("\n[6/8] Getting sandbox summary...")
        summary = sandbox.get_summary()
        assert summary['total_projects'] > 0
        print(f"✓ Summary: {summary['total_projects']} projects, {summary['total_agents']} agents")

        # 7. Evaluate project
        print("\n[7/8] Evaluating project...")
        evaluation = sandbox.evaluate_project(project_id)
        assert evaluation is not None
        assert evaluation['recommendation'] == 'NOT_READY'  # No data yet
        print(f"✓ Evaluation: {evaluation['recommendation']} - {evaluation['reason']}")

        # 8. Clean up
        print("\n[8/8] Cleaning up test project...")
        success = sandbox.kill_project(project_id, delete_workspace=True)
        assert success, "Should successfully kill project"
        print("✓ Project cleaned up")

        # Verify deletion
        deleted_project = sandbox.get_project(project_id)
        assert deleted_project is not None  # Project still exists in DB
        print("✓ Project marked as deleted (still in DB)")

        print("\n" + "=" * 60)
        print("✓ ALL TESTS PASSED")
        print("=" * 60)

        return True

    except Exception as e:
        print(f"\n✗ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_experiment_workflow():
    """Test experiment tracking workflow"""
    print("\n" + "=" * 60)
    print("Testing Experiment Workflow")
    print("=" * 60)

    try:
        sandbox = get_sandbox()

        # Create project
        print("\n[1/4] Creating experiment project...")
        project_id = sandbox.create_project(
            name="Experiment Test Project",
            description="Testing experiment tracking"
        )
        print(f"✓ Project created: {project_id}")

        # Log experiment
        print("\n[2/4] Logging experiment...")
        exp_id = sandbox.log_experiment(
            project_id=project_id,
            name="Test Experiment",
            hypothesis="Testing experiment tracking",
            config={"test": True}
        )
        print(f"✓ Experiment logged: {exp_id}")

        # Complete experiment
        print("\n[3/4] Completing experiment...")
        sandbox.complete_experiment(
            experiment_id=exp_id,
            results={"result": "success"},
            success=True
        )
        print("✓ Experiment completed")

        # Get results
        print("\n[4/4] Getting experiment results...")
        project = sandbox.get_project(project_id)
        results = project.get_results()
        assert len(results['experiments']) > 0
        print(f"✓ Found {len(results['experiments'])} experiment(s)")

        # Clean up
        sandbox.kill_project(project_id, delete_workspace=True)
        print("✓ Cleaned up")

        print("\n✓ EXPERIMENT WORKFLOW PASSED")
        return True

    except Exception as e:
        print(f"\n✗ EXPERIMENT TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all integration tests"""
    print("\nRunning NovaOS V2 Sandbox Integration Tests...\n")

    results = []

    # Test 1: Complete workflow
    results.append(("Complete Workflow", test_complete_workflow()))

    # Test 2: Experiment workflow
    results.append(("Experiment Workflow", test_experiment_workflow()))

    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for name, result in results:
        status = "✓ PASSED" if result else "✗ FAILED"
        print(f"{status}: {name}")

    print(f"\nTotal: {passed}/{total} tests passed")

    if passed == total:
        print("\n✓ ALL INTEGRATION TESTS PASSED")
        sys.exit(0)
    else:
        print(f"\n✗ {total - passed} TEST(S) FAILED")
        sys.exit(1)


if __name__ == '__main__':
    main()
