"""
DDS Integration Example Usage
Demonstrates how to use the complete DDS integration in NovaOS V2
"""

from integrations.dds import get_dds
from core.memory import get_memory


def example_1_deploy_simple_campaign():
    """Example 1: Deploy a simple DDS campaign"""
    print("\n" + "="*60)
    print("EXAMPLE 1: Deploy Simple Campaign")
    print("="*60 + "\n")

    dds = get_dds()

    # Deploy a campaign for dentists in Austin
    result = dds.deploy_campaign({
        'vertical': 'dentists',
        'location': 'Austin, TX',
        'prospect_count': 50,
        'budget': 150,
        'sender_name': 'John Smith',
        'sender_company': 'Marketing Solutions Pro'
    })

    print(f"Status: {result['status']}")
    print(f"Campaign ID: {result.get('campaign_id')}")
    print(f"Estimated Costs: ${result.get('estimated_costs', {}).get('total', 0):.2f}")
    print(f"\nNext Steps:")
    for step in result.get('next_steps', []):
        print(f"  {step}")

    return result.get('campaign_id')


def example_2_start_and_monitor_campaign(campaign_id):
    """Example 2: Start campaign and monitor status"""
    print("\n" + "="*60)
    print("EXAMPLE 2: Start and Monitor Campaign")
    print("="*60 + "\n")

    dds = get_dds()

    # Start the campaign
    start_result = dds.start_campaign(campaign_id)
    print(f"Campaign Status: {start_result['status']}")

    # Get campaign status
    status = dds.get_campaign_status(campaign_id)
    print(f"\nCampaign: {status['campaign_name']}")
    print(f"Status: {status['status']}")
    print(f"Config: {status['config']}")


def example_3_log_costs_and_results(campaign_id):
    """Example 3: Log DDS costs and results"""
    print("\n" + "="*60)
    print("EXAMPLE 3: Log Costs and Results")
    print("="*60 + "\n")

    dds = get_dds()

    # Log prospecting costs
    dds.log_dds_costs(campaign_id, {
        'operation': 'prospecting',
        'provider': 'outscraper',
        'cost': 2.50,
        'details': {
            'prospects_scraped': 50,
            'api_calls': 5
        }
    })
    print("Logged prospecting costs: $2.50")

    # Log scoring costs (Anthropic)
    dds.log_dds_costs(campaign_id, {
        'operation': 'scoring',
        'provider': 'anthropic',
        'cost': 0.15,
        'details': {
            'model': 'claude-3-5-haiku-20241022',
            'input_tokens': 25000,
            'output_tokens': 5000,
            'prospects_scored': 50
        }
    })
    print("Logged scoring costs: $0.15")

    # Log email finding costs
    dds.log_dds_costs(campaign_id, {
        'operation': 'email_finding',
        'provider': 'hunter_io',
        'cost': 5.00,
        'details': {
            'emails_found': 45,
            'credits_used': 50
        }
    })
    print("Logged email finding costs: $5.00")

    # Log campaign results
    dds.log_dds_results(campaign_id, {
        'stage': 'prospecting',
        'leads_found': 50,
        'leads_qualified': 20,
        'emails_sent': 0,
        'emails_opened': 0,
        'emails_replied': 0,
        'revenue': 0
    })
    print("Logged prospecting results: 50 leads found, 20 qualified")

    # Log outreach costs
    dds.log_dds_costs(campaign_id, {
        'operation': 'outreach',
        'provider': 'sendgrid',
        'cost': 0.06,
        'details': {
            'emails_sent': 60,  # 20 qualified * 3 emails each
            'cost_per_email': 0.001
        }
    })
    print("Logged outreach costs: $0.06")

    # Log outreach results
    dds.log_dds_results(campaign_id, {
        'stage': 'outreach',
        'leads_found': 50,
        'leads_qualified': 20,
        'emails_sent': 60,
        'emails_opened': 18,
        'emails_replied': 3,
        'revenue': 0
    })
    print("Logged outreach results: 60 emails sent, 18 opened, 3 replied")


def example_4_calculate_metrics(campaign_id):
    """Example 4: Calculate lead metrics"""
    print("\n" + "="*60)
    print("EXAMPLE 4: Calculate Lead Metrics")
    print("="*60 + "\n")

    dds = get_dds()

    metrics = dds.calculate_lead_metrics(campaign_id)

    print(f"Campaign: {metrics['campaign_name']}")
    print(f"\nLead Generation:")
    print(f"  Total Leads: {metrics['leads_generated']}")
    print(f"  Qualified Leads: {metrics['leads_qualified']}")
    print(f"  Qualification Rate: {metrics['qualification_rate']:.1f}%")

    print(f"\nOutreach Performance:")
    print(f"  Emails Sent: {metrics['emails_sent']}")
    print(f"  Open Rate: {metrics['open_rate']:.1f}%")
    print(f"  Reply Rate: {metrics['reply_rate']:.1f}%")

    print(f"\nFinancial Metrics:")
    print(f"  Total Cost: ${metrics['total_cost']:.2f}")
    print(f"  Cost per Lead: ${metrics['cost_per_lead']:.2f}")
    print(f"  Cost per Qualified Lead: ${metrics['cost_per_qualified_lead']:.2f}")
    print(f"  Revenue: ${metrics['revenue_generated']:.2f}")
    print(f"  ROI: {metrics['roi']:.1f}%")


def example_5_optimize_campaign(campaign_id):
    """Example 5: Get optimization recommendations"""
    print("\n" + "="*60)
    print("EXAMPLE 5: Campaign Optimization")
    print("="*60 + "\n")

    dds = get_dds()

    optimization = dds.optimize_campaign(campaign_id)

    print(f"Campaign: {optimization['campaign_name']}")
    print(f"Priority: {optimization['priority']}")

    print(f"\nCurrent Performance:")
    for key, value in optimization['current_performance'].items():
        print(f"  {key}: {value}")

    print(f"\nRecommendations ({len(optimization['recommendations'])}):")
    for i, rec in enumerate(optimization['recommendations'], 1):
        print(f"\n  {i}. {rec['issue']} (Severity: {rec['severity']})")
        print(f"     Current: {rec['current_value']} | Threshold: {rec['threshold']}")
        print(f"     Action: {rec['recommendation']}")
        print(f"     Expected Impact: {rec['expected_impact']}")

    print(f"\nSuggested Actions: {', '.join(optimization['suggested_actions'])}")

    if 'auto_action_taken' in optimization:
        print(f"\nAUTO ACTION: {optimization['auto_action_taken']}")


def example_6_log_revenue(campaign_id):
    """Example 6: Log revenue from campaign"""
    print("\n" + "="*60)
    print("EXAMPLE 6: Log Revenue")
    print("="*60 + "\n")

    dds = get_dds()

    # Simulate closing deals from the campaign
    dds.log_dds_results(campaign_id, {
        'stage': 'closed',
        'leads_found': 50,
        'leads_qualified': 20,
        'emails_sent': 60,
        'emails_opened': 18,
        'emails_replied': 3,
        'revenue': 5000.00  # 1 client closed at $5000
    })

    print("Logged revenue: $5,000.00")

    # Recalculate metrics with revenue
    metrics = dds.calculate_lead_metrics(campaign_id)
    print(f"\nUpdated Metrics:")
    print(f"  Total Cost: ${metrics['total_cost']:.2f}")
    print(f"  Revenue: ${metrics['revenue_generated']:.2f}")
    print(f"  Profit: ${metrics['revenue_generated'] - metrics['total_cost']:.2f}")
    print(f"  ROI: {metrics['roi']:.1f}%")


def example_7_generate_reports(campaign_id):
    """Example 7: Generate different types of reports"""
    print("\n" + "="*60)
    print("EXAMPLE 7: Generate Reports")
    print("="*60 + "\n")

    dds = get_dds()

    # Cost report
    print("COST REPORT:")
    cost_report = dds.generate_campaign_report(campaign_id, 'costs')
    print(f"  Total Cost: {cost_report['total_cost']}")
    print(f"  Cost per Lead: {cost_report['cost_per_lead']}")
    print(f"  Cost Efficiency: {cost_report['cost_efficiency']}")

    # Lead report
    print("\nLEAD REPORT:")
    lead_report = dds.generate_campaign_report(campaign_id, 'leads')
    print(f"  Leads Generated: {lead_report['leads_generated']}")
    print(f"  Qualification Rate: {lead_report['qualification_rate']}")
    print(f"  Quality Assessment: {lead_report['quality_assessment']}")

    # Outreach report
    print("\nOUTREACH REPORT:")
    outreach_report = dds.generate_campaign_report(campaign_id, 'outreach')
    print(f"  Emails Sent: {outreach_report['emails_sent']}")
    print(f"  Open Rate: {outreach_report['open_rate']}")
    print(f"  Reply Rate: {outreach_report['reply_rate']}")
    print(f"  Effectiveness: {outreach_report['effectiveness']}")

    # Full report
    print("\nFULL REPORT:")
    full_report = dds.generate_campaign_report(campaign_id, 'full')
    print(f"  Status: {full_report['status']}")
    print(f"  Performance Ratings:")
    for key, value in full_report['performance_ratings'].items():
        print(f"    {key}: {value}")


def example_8_all_campaigns_report():
    """Example 8: Get report for all campaigns"""
    print("\n" + "="*60)
    print("EXAMPLE 8: All Campaigns Report")
    print("="*60 + "\n")

    dds = get_dds()

    report = dds.get_all_campaigns_report()

    print("SUMMARY:")
    print(f"  Total Campaigns: {report['summary']['total_campaigns']}")
    print(f"  Active Campaigns: {report['summary']['active_campaigns']}")
    print(f"  Total Cost: ${report['summary']['total_cost']:.2f}")
    print(f"  Total Revenue: ${report['summary']['total_revenue']:.2f}")
    print(f"  Total ROI: {report['summary']['total_roi']:.1f}%")
    print(f"  Profit: ${report['summary']['profit']:.2f}")

    print("\nCAMPAIGNS:")
    for campaign in report['campaigns']:
        print(f"  - {campaign['campaign_name']}")
        print(f"    Status: {campaign['status']}")
        print(f"    Leads: {campaign['leads_generated']} ({campaign['qualified_leads']} qualified)")
        print(f"    Cost: ${campaign['cost']:.2f} | Revenue: ${campaign['revenue']:.2f}")
        print(f"    ROI: {campaign['roi']:.1f}%\n")


def example_9_optimize_all_campaigns():
    """Example 9: Optimize all active campaigns"""
    print("\n" + "="*60)
    print("EXAMPLE 9: Optimize All Campaigns")
    print("="*60 + "\n")

    dds = get_dds()

    results = dds.optimize_all_campaigns()

    print(f"Campaigns Analyzed: {results['total_campaigns_analyzed']}")
    print(f"Critical Issues: {results['critical_issues']}")
    print(f"High Priority Issues: {results['high_priority_issues']}")

    print("\nCAMPAIGNS NEEDING ATTENTION:")
    for campaign in results['campaigns_needing_attention']:
        print(f"\n  {campaign['campaign_name']} - Priority: {campaign['priority']}")
        print(f"  Recommendations: {len(campaign['recommendations'])}")
        for rec in campaign['recommendations']:
            print(f"    - {rec['issue']}: {rec['recommendation']}")


def example_10_pause_and_resume(campaign_id):
    """Example 10: Pause and resume campaigns"""
    print("\n" + "="*60)
    print("EXAMPLE 10: Pause and Resume")
    print("="*60 + "\n")

    dds = get_dds()

    # Pause campaign
    pause_result = dds.pause_campaign(campaign_id)
    print(f"Pause Status: {pause_result['status']}")
    print(f"Message: {pause_result['message']}")

    # Check status
    status = dds.get_campaign_status(campaign_id)
    print(f"\nCampaign Status: {status['status']}")

    # Resume campaign
    resume_result = dds.start_campaign(campaign_id)
    print(f"\nResume Status: {resume_result['status']}")

    # Check status again
    status = dds.get_campaign_status(campaign_id)
    print(f"Campaign Status: {status['status']}")


def run_complete_workflow():
    """Run a complete DDS integration workflow"""
    print("\n" + "="*80)
    print(" "*20 + "DDS INTEGRATION COMPLETE WORKFLOW")
    print("="*80 + "\n")

    # 1. Deploy campaign
    campaign_id = example_1_deploy_simple_campaign()

    if not campaign_id:
        print("\nError: Campaign deployment failed")
        return

    # 2. Start and monitor
    example_2_start_and_monitor_campaign(campaign_id)

    # 3. Log costs and results
    example_3_log_costs_and_results(campaign_id)

    # 4. Calculate metrics
    example_4_calculate_metrics(campaign_id)

    # 5. Get optimization recommendations
    example_5_optimize_campaign(campaign_id)

    # 6. Log revenue (simulate closed deal)
    example_6_log_revenue(campaign_id)

    # 7. Generate various reports
    example_7_generate_reports(campaign_id)

    # 8. All campaigns report
    example_8_all_campaigns_report()

    # 9. Optimize all campaigns
    example_9_optimize_all_campaigns()

    # 10. Pause and resume
    example_10_pause_and_resume(campaign_id)

    print("\n" + "="*80)
    print(" "*25 + "WORKFLOW COMPLETED")
    print("="*80 + "\n")


if __name__ == "__main__":
    run_complete_workflow()
