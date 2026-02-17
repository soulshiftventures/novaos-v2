# DDS Integration Quick Reference

One-page reference for the complete DDS integration in NovaOS V2.

## Quick Start

```python
from integrations.dds import get_dds

dds = get_dds()
```

## Deploy Campaign (1 command)

```python
result = dds.deploy_campaign({
    'vertical': 'dentists',           # Required
    'location': 'Austin, TX',         # Required
    'prospect_count': 50,             # Default: 50
    'budget': 150,                    # Default: 100
    'sender_name': 'Your Name',       # Optional
    'sender_company': 'Your Company'  # Optional
})

campaign_id = result['campaign_id']
```

## Campaign Control

```python
dds.start_campaign(campaign_id)   # Start/resume
dds.pause_campaign(campaign_id)   # Pause
dds.stop_campaign(campaign_id)    # Stop permanently
```

## Log Costs

```python
# Prospecting costs
dds.log_dds_costs(campaign_id, {
    'operation': 'prospecting',
    'provider': 'outscraper',
    'cost': 2.50,
    'details': {'prospects_scraped': 50}
})

# AI costs
dds.log_dds_costs(campaign_id, {
    'operation': 'scoring',
    'provider': 'anthropic',
    'cost': 0.15,
    'details': {
        'model': 'claude-3-5-haiku-20241022',
        'input_tokens': 25000,
        'output_tokens': 5000
    }
})

# Email costs
dds.log_dds_costs(campaign_id, {
    'operation': 'outreach',
    'provider': 'sendgrid',
    'cost': 0.06,
    'details': {'emails_sent': 60}
})
```

## Log Results

```python
# After prospecting
dds.log_dds_results(campaign_id, {
    'stage': 'prospecting',
    'leads_found': 50,
    'leads_qualified': 20,
    'emails_sent': 0,
    'emails_opened': 0,
    'emails_replied': 0,
    'revenue': 0
})

# After outreach
dds.log_dds_results(campaign_id, {
    'stage': 'outreach',
    'leads_found': 50,
    'leads_qualified': 20,
    'emails_sent': 60,
    'emails_opened': 18,
    'emails_replied': 3,
    'revenue': 0
})

# After closing
dds.log_dds_results(campaign_id, {
    'stage': 'closed',
    'leads_found': 50,
    'leads_qualified': 20,
    'emails_sent': 60,
    'emails_opened': 18,
    'emails_replied': 3,
    'revenue': 5000.00
})
```

## Get Metrics

```python
metrics = dds.calculate_lead_metrics(campaign_id)

# Access metrics
metrics['leads_generated']           # Total leads
metrics['leads_qualified']           # Qualified leads
metrics['qualification_rate']        # Percentage
metrics['cost_per_lead']             # $ per lead
metrics['cost_per_qualified_lead']   # $ per qualified lead
metrics['emails_sent']               # Total emails
metrics['open_rate']                 # Email open %
metrics['reply_rate']                # Email reply %
metrics['total_cost']                # Total $
metrics['revenue_generated']         # Revenue $
metrics['roi']                       # ROI %
```

## Get Status

```python
status = dds.get_campaign_status(campaign_id)

status['status']           # active, paused, stopped
status['metrics']          # All metrics
status['performance']      # Performance ratings
status['config']           # Campaign config
```

## Optimize

```python
optimization = dds.optimize_campaign(campaign_id)

optimization['priority']          # CRITICAL, HIGH, MEDIUM, LOW
optimization['recommendations']   # List of recommendations
optimization['suggested_actions'] # Actions to take
```

## Reports

```python
# Full report
report = dds.generate_campaign_report(campaign_id, 'full')

# Specific reports
cost_report = dds.generate_campaign_report(campaign_id, 'costs')
lead_report = dds.generate_campaign_report(campaign_id, 'leads')
outreach_report = dds.generate_campaign_report(campaign_id, 'outreach')

# All campaigns
all_report = dds.get_all_campaigns_report()
```

## Optimization - All Campaigns

```python
results = dds.optimize_all_campaigns()

results['critical_issues']              # Count
results['high_priority_issues']         # Count
results['campaigns_needing_attention']  # List
```

## Cost Estimation

```python
# Automatically done during deployment
# View in result['estimated_costs']

estimated_costs = {
    'scraping': 0.25,
    'website_analysis': 0.01,
    'lead_scoring': 0.01,
    'email_finding': 5.00,
    'outreach': 0.15,
    'total': 5.42,
    'cost_per_prospect': 0.11
}
```

## Thresholds

```python
# Default thresholds (can be modified)
dds.cost_per_lead_threshold = 20.00          # Alert if exceeded
dds.qualification_rate_threshold = 0.30      # Alert if below 30%
dds.outreach_success_threshold = 0.05        # Alert if below 5%
```

## Complete Workflow Example

```python
from integrations.dds import get_dds

# 1. Deploy
dds = get_dds()
result = dds.deploy_campaign({
    'vertical': 'dentists',
    'location': 'Austin, TX',
    'prospect_count': 50,
    'budget': 150
})
campaign_id = result['campaign_id']

# 2. Start
dds.start_campaign(campaign_id)

# 3. Log costs as you go
dds.log_dds_costs(campaign_id, {
    'operation': 'prospecting',
    'provider': 'outscraper',
    'cost': 2.50,
    'details': {'prospects': 50}
})

# 4. Log results
dds.log_dds_results(campaign_id, {
    'stage': 'prospecting',
    'leads_found': 50,
    'leads_qualified': 20,
    'emails_sent': 0,
    'emails_opened': 0,
    'emails_replied': 0,
    'revenue': 0
})

# 5. Continue with outreach...
dds.log_dds_costs(campaign_id, {
    'operation': 'outreach',
    'provider': 'sendgrid',
    'cost': 0.06,
    'details': {'emails': 60}
})

dds.log_dds_results(campaign_id, {
    'stage': 'outreach',
    'leads_found': 50,
    'leads_qualified': 20,
    'emails_sent': 60,
    'emails_opened': 18,
    'emails_replied': 3,
    'revenue': 0
})

# 6. Log revenue when deals close
dds.log_dds_results(campaign_id, {
    'stage': 'closed',
    'leads_found': 50,
    'leads_qualified': 20,
    'emails_sent': 60,
    'emails_opened': 18,
    'emails_replied': 3,
    'revenue': 5000.00
})

# 7. Check metrics
metrics = dds.calculate_lead_metrics(campaign_id)
print(f"ROI: {metrics['roi']:.1f}%")

# 8. Get optimization recommendations
optimization = dds.optimize_campaign(campaign_id)
for rec in optimization['recommendations']:
    print(f"- {rec['recommendation']}")

# 9. Generate report
report = dds.generate_campaign_report(campaign_id, 'full')
```

## Integration with NovaOS Memory

```python
from core.memory import get_memory

memory = get_memory()

# Query DDS data
sales_agents = memory.get_all_agents(department='sales')
dds_campaigns = [a for a in sales_agents if a['type'] == 'dds_campaign']

# Get costs
total_cost = memory.get_total_costs(department='sales')

# Get revenue
total_revenue = memory.get_total_revenue(department='sales')

# Get ROI
roi_data = memory.get_roi_by_department()['sales']
```

## Common Patterns

### Deploy Multiple Campaigns

```python
verticals = ['dentists', 'lawyers', 'contractors']
locations = ['Austin, TX', 'Dallas, TX', 'Houston, TX']

campaigns = []
for vertical in verticals:
    for location in locations:
        result = dds.deploy_campaign({
            'vertical': vertical,
            'location': location,
            'prospect_count': 50,
            'budget': 100
        })
        if result['status'] == 'deployed':
            campaigns.append(result['campaign_id'])
            dds.start_campaign(result['campaign_id'])
```

### Daily Optimization Check

```python
# Run daily
results = dds.optimize_all_campaigns()

if results['critical_issues'] > 0:
    print(f"⚠ {results['critical_issues']} campaigns need immediate attention!")

for campaign in results['campaigns_needing_attention']:
    if campaign['priority'] == 'CRITICAL':
        print(f"CRITICAL: {campaign['campaign_name']}")
        for rec in campaign['recommendations']:
            print(f"  - {rec['recommendation']}")
```

### Monitor ROI

```python
report = dds.get_all_campaigns_report()

for campaign in report['campaigns']:
    if campaign['roi'] < 0:
        print(f"⚠ Negative ROI: {campaign['campaign_name']}")
        dds.pause_campaign(campaign['campaign_id'])
    elif campaign['roi'] > 300:
        print(f"🚀 High performer: {campaign['campaign_name']}")
        print(f"   Consider scaling up!")
```

### Cost Tracking by Provider

```python
# Get all costs for a campaign
from core.memory import get_memory

memory = get_memory()
agent = memory.get_agent(campaign_id)

# Costs are automatically tracked in costs table
# Query using SQL or through memory methods
```

## Testing

```bash
# Run integration tests
cd /Users/krissanders/novaos-v2
python integrations/test_dds_integration.py

# Run example workflow
python integrations/dds_example_usage.py
```

## Error Handling

```python
# Check for errors
result = dds.deploy_campaign(config)

if result['status'] == 'error':
    print(f"Error: {result['message']}")

    if 'setup_instructions' in result:
        for instruction in result['setup_instructions']:
            print(instruction)

# Check if DDS available
if not dds.dds_available:
    print("DDS system not available")
    print(f"Expected at: {dds.dds_path}")
```

## Key Files

- **Integration**: `/Users/krissanders/novaos-v2/integrations/dds.py`
- **Tests**: `/Users/krissanders/novaos-v2/integrations/test_dds_integration.py`
- **Examples**: `/Users/krissanders/novaos-v2/integrations/dds_example_usage.py`
- **Documentation**: `/Users/krissanders/novaos-v2/integrations/DDS_INTEGRATION_README.md`
- **This Reference**: `/Users/krissanders/novaos-v2/integrations/DDS_QUICK_REFERENCE.md`

## Performance Tips

1. **Batch operations** when logging multiple costs/results
2. **Run optimization** on all campaigns daily
3. **Monitor cost per lead** - pause if exceeding $20
4. **Track qualification rate** - aim for 30%+
5. **Scale winners** - campaigns with ROI > 300%
6. **Use auto-optimization** - automatically pauses negative ROI campaigns

## Auto-Actions

The integration automatically:
- **Pauses campaigns** with negative ROI
- **Updates agent metrics** when costs/revenue logged
- **Calculates ROI** in real-time
- **Flags high performers** for scaling
- **Alerts** when thresholds exceeded

## Dashboard Integration

```python
# Display in Sales Dashboard
dds = get_dds()
report = dds.get_all_campaigns_report()

print(f"""
SALES DASHBOARD - DDS CAMPAIGNS
================================
Active Campaigns: {report['summary']['active_campaigns']}
Total Cost: ${report['summary']['total_cost']:,.2f}
Total Revenue: ${report['summary']['total_revenue']:,.2f}
Total Profit: ${report['summary']['profit']:,.2f}
ROI: {report['summary']['total_roi']:.1f}%
""")
```

---

**For full documentation, see**: `DDS_INTEGRATION_README.md`
