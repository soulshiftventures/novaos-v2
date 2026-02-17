"""
Test DDS Integration
Quick verification that DDS integration is working correctly
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from integrations.dds import get_dds
from core.memory import get_memory


def test_1_initialization():
    """Test 1: DDS Integration Initialization"""
    print("\n" + "="*60)
    print("TEST 1: DDS Integration Initialization")
    print("="*60)

    try:
        dds = get_dds()
        print("✓ DDS integration initialized")
        print(f"✓ DDS Path: {dds.dds_path}")
        print(f"✓ DDS Available: {dds.dds_available}")

        if not dds.dds_available:
            print("\n⚠ WARNING: DDS system not available")
            print(f"  Expected path: {dds.dds_path}")
            print("  This is expected if DDS is not installed")
            print("  Integration will work with placeholders")

        return True
    except Exception as e:
        print(f"✗ Error: {e}")
        return False


def test_2_memory_integration():
    """Test 2: Memory System Integration"""
    print("\n" + "="*60)
    print("TEST 2: Memory System Integration")
    print("="*60)

    try:
        memory = get_memory()
        print("✓ Memory system accessible")

        # Check tables
        agents = memory.get_all_agents()
        print(f"✓ Agents table accessible: {len(agents)} agents")

        return True
    except Exception as e:
        print(f"✗ Error: {e}")
        return False


def test_3_cost_estimation():
    """Test 3: Cost Estimation"""
    print("\n" + "="*60)
    print("TEST 3: Cost Estimation")
    print("="*60)

    try:
        dds = get_dds()

        # Estimate costs for 50 prospects
        costs = dds._estimate_campaign_costs(50, 'dentists')

        print("✓ Cost estimation working")
        print(f"  Scraping: ${costs['scraping']:.2f}")
        print(f"  Website Analysis: ${costs['website_analysis']:.2f}")
        print(f"  Lead Scoring: ${costs['lead_scoring']:.2f}")
        print(f"  Email Finding: ${costs['email_finding']:.2f}")
        print(f"  Outreach: ${costs['outreach']:.2f}")
        print(f"  TOTAL: ${costs['total']:.2f}")
        print(f"  Cost per Prospect: ${costs['cost_per_prospect']:.2f}")

        return True
    except Exception as e:
        print(f"✗ Error: {e}")
        return False


def test_4_campaign_deployment():
    """Test 4: Campaign Deployment"""
    print("\n" + "="*60)
    print("TEST 4: Campaign Deployment")
    print("="*60)

    try:
        dds = get_dds()

        # Deploy test campaign
        result = dds.deploy_campaign({
            'vertical': 'test_vertical',
            'location': 'test_location',
            'prospect_count': 10,
            'budget': 50,
            'campaign_name': 'Test Campaign',
            'sender_name': 'Test Sender',
            'sender_company': 'Test Company'
        })

        print(f"✓ Campaign deployment: {result['status']}")

        if result['status'] == 'deployed':
            print(f"  Campaign ID: {result['campaign_id']}")
            print(f"  Estimated Cost: ${result['estimated_costs']['total']:.2f}")
            return result['campaign_id']
        elif result['status'] == 'error':
            print(f"  Message: {result['message']}")
            if not dds.dds_available:
                print("  ⚠ This is expected without DDS system installed")
            return None
        else:
            print(f"  Unexpected status: {result['status']}")
            return None

    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return None


def test_5_cost_logging(campaign_id):
    """Test 5: Cost Logging"""
    print("\n" + "="*60)
    print("TEST 5: Cost Logging")
    print("="*60)

    if not campaign_id:
        print("⊘ Skipped - No campaign ID")
        return False

    try:
        dds = get_dds()

        # Log test cost
        result = dds.log_dds_costs(campaign_id, {
            'operation': 'test_operation',
            'provider': 'test_provider',
            'cost': 1.00,
            'details': {'test': 'data'}
        })

        print(f"✓ Cost logging: {result['status']}")
        print(f"  Cost ID: {result['cost_id']}")
        print(f"  Cost: ${result['cost']:.2f}")

        return True
    except Exception as e:
        print(f"✗ Error: {e}")
        return False


def test_6_results_logging(campaign_id):
    """Test 6: Results Logging"""
    print("\n" + "="*60)
    print("TEST 6: Results Logging")
    print("="*60)

    if not campaign_id:
        print("⊘ Skipped - No campaign ID")
        return False

    try:
        dds = get_dds()

        # Log test results
        result = dds.log_dds_results(campaign_id, {
            'stage': 'test_stage',
            'leads_found': 10,
            'leads_qualified': 5,
            'emails_sent': 15,
            'emails_opened': 7,
            'emails_replied': 2,
            'revenue': 100.00
        })

        print(f"✓ Results logging: {result['status']}")
        print(f"  Campaign ID: {result['campaign_id']}")
        print(f"  Stage: {result['stage']}")

        return True
    except Exception as e:
        print(f"✗ Error: {e}")
        return False


def test_7_metrics_calculation(campaign_id):
    """Test 7: Metrics Calculation"""
    print("\n" + "="*60)
    print("TEST 7: Metrics Calculation")
    print("="*60)

    if not campaign_id:
        print("⊘ Skipped - No campaign ID")
        return False

    try:
        dds = get_dds()

        # Calculate metrics
        metrics = dds.calculate_lead_metrics(campaign_id)

        if 'error' in metrics.get('status', ''):
            print(f"✗ Error: {metrics['message']}")
            return False

        print("✓ Metrics calculation working")
        print(f"  Leads Generated: {metrics['leads_generated']}")
        print(f"  Leads Qualified: {metrics['leads_qualified']}")
        print(f"  Qualification Rate: {metrics['qualification_rate']:.1f}%")
        print(f"  Cost per Lead: ${metrics['cost_per_lead']:.2f}")
        print(f"  ROI: {metrics['roi']:.1f}%")

        return True
    except Exception as e:
        print(f"✗ Error: {e}")
        return False


def test_8_campaign_status(campaign_id):
    """Test 8: Campaign Status"""
    print("\n" + "="*60)
    print("TEST 8: Campaign Status")
    print("="*60)

    if not campaign_id:
        print("⊘ Skipped - No campaign ID")
        return False

    try:
        dds = get_dds()

        # Get status
        status = dds.get_campaign_status(campaign_id)

        if 'error' in status.get('status', ''):
            print(f"✗ Error: {status['message']}")
            return False

        print("✓ Campaign status retrieval working")
        print(f"  Campaign: {status['campaign_name']}")
        print(f"  Status: {status['status']}")
        print(f"  Performance:")
        for key, value in status['performance'].items():
            print(f"    {key}: {value}")

        return True
    except Exception as e:
        print(f"✗ Error: {e}")
        return False


def test_9_optimization(campaign_id):
    """Test 9: Campaign Optimization"""
    print("\n" + "="*60)
    print("TEST 9: Campaign Optimization")
    print("="*60)

    if not campaign_id:
        print("⊘ Skipped - No campaign ID")
        return False

    try:
        dds = get_dds()

        # Get optimization recommendations
        optimization = dds.optimize_campaign(campaign_id)

        print("✓ Optimization analysis working")
        print(f"  Priority: {optimization['priority']}")
        print(f"  Recommendations: {len(optimization['recommendations'])}")

        if optimization['recommendations']:
            print("\n  Sample Recommendation:")
            rec = optimization['recommendations'][0]
            print(f"    Issue: {rec['issue']}")
            print(f"    Severity: {rec['severity']}")

        return True
    except Exception as e:
        print(f"✗ Error: {e}")
        return False


def test_10_reporting(campaign_id):
    """Test 10: Report Generation"""
    print("\n" + "="*60)
    print("TEST 10: Report Generation")
    print("="*60)

    if not campaign_id:
        print("⊘ Skipped - No campaign ID")
        return False

    try:
        dds = get_dds()

        # Generate different report types
        full_report = dds.generate_campaign_report(campaign_id, 'full')
        cost_report = dds.generate_campaign_report(campaign_id, 'costs')
        lead_report = dds.generate_campaign_report(campaign_id, 'leads')
        outreach_report = dds.generate_campaign_report(campaign_id, 'outreach')

        print("✓ Report generation working")
        print(f"  Full report: {full_report['report_type']}")
        print(f"  Cost report: {cost_report['report_type']}")
        print(f"  Lead report: {lead_report['report_type']}")
        print(f"  Outreach report: {outreach_report['report_type']}")

        return True
    except Exception as e:
        print(f"✗ Error: {e}")
        return False


def test_11_all_campaigns_report():
    """Test 11: All Campaigns Report"""
    print("\n" + "="*60)
    print("TEST 11: All Campaigns Report")
    print("="*60)

    try:
        dds = get_dds()

        # Get all campaigns report
        report = dds.get_all_campaigns_report()

        print("✓ All campaigns report working")
        print(f"  Total Campaigns: {report['summary']['total_campaigns']}")
        print(f"  Active Campaigns: {report['summary']['active_campaigns']}")
        print(f"  Total Cost: ${report['summary']['total_cost']:.2f}")
        print(f"  Total Revenue: ${report['summary']['total_revenue']:.2f}")
        print(f"  Total ROI: {report['summary']['total_roi']:.1f}%")

        return True
    except Exception as e:
        print(f"✗ Error: {e}")
        return False


def test_12_cleanup(campaign_id):
    """Test 12: Cleanup Test Campaign"""
    print("\n" + "="*60)
    print("TEST 12: Cleanup")
    print("="*60)

    if not campaign_id:
        print("⊘ Skipped - No campaign ID")
        return False

    try:
        dds = get_dds()

        # Stop the test campaign
        result = dds.stop_campaign(campaign_id)

        print(f"✓ Campaign cleanup: {result['status']}")

        return True
    except Exception as e:
        print(f"✗ Error: {e}")
        return False


def run_all_tests():
    """Run all DDS integration tests"""
    print("\n" + "="*80)
    print(" "*25 + "DDS INTEGRATION TESTS")
    print("="*80)

    results = {}

    # Run tests
    results['initialization'] = test_1_initialization()
    results['memory_integration'] = test_2_memory_integration()
    results['cost_estimation'] = test_3_cost_estimation()

    campaign_id = test_4_campaign_deployment()

    results['cost_logging'] = test_5_cost_logging(campaign_id)
    results['results_logging'] = test_6_results_logging(campaign_id)
    results['metrics_calculation'] = test_7_metrics_calculation(campaign_id)
    results['campaign_status'] = test_8_campaign_status(campaign_id)
    results['optimization'] = test_9_optimization(campaign_id)
    results['reporting'] = test_10_reporting(campaign_id)
    results['all_campaigns_report'] = test_11_all_campaigns_report()
    results['cleanup'] = test_12_cleanup(campaign_id)

    # Summary
    print("\n" + "="*80)
    print(" "*30 + "TEST SUMMARY")
    print("="*80)

    passed = sum(1 for v in results.values() if v)
    total = len(results)

    print(f"\nTests Passed: {passed}/{total}")

    for test_name, result in results.items():
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"  {status}: {test_name}")

    if passed == total:
        print("\n🎉 All tests passed!")
    else:
        print(f"\n⚠ {total - passed} test(s) failed")

    print("\n" + "="*80 + "\n")

    return passed == total


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
