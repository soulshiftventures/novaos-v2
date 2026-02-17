# DDS Integration for NovaOS V2

Complete integration with the existing Data-Driven Sales (DDS) prospecting system at `/Users/krissanders/prospecting_agent/`

## Overview

The DDS Integration connects NovaOS V2 with the existing 4-agent DDS system:

1. **Prospecting Agent** - Google Maps scraping, website analysis, lead qualification
2. **Scoring Agent** - AI-powered lead scoring based on marketing gaps
3. **Research Agent** - Competitor analysis, market research
4. **Outreach Agent** - Automated email campaigns with tracking and follow-ups

**Ownership**: Sales Department

## Features

### 1. Campaign Deployment
- Deploy complete DDS campaigns with configuration
- Set vertical, location, prospect count, and budget
- Automatic cost estimation
- Budget validation before deployment
- Campaign tracking and status monitoring

### 2. Cost Tracking
- Log every DDS API call to NovaOS costs table
- Track costs by provider (Anthropic, Outscraper, Hunter.io, SendGrid)
- Calculate cost per lead and cost per qualified lead
- Budget monitoring and alerts
- Integration with NovaOS financial tracking

### 3. Performance Metrics
- Leads generated and qualified counts
- Qualification rate percentage
- Email outreach metrics (sent, opened, replied)
- Open rate and reply rate tracking
- Cost efficiency analysis
- Revenue attribution per campaign

### 4. ROI Calculation
- Real-time ROI tracking: `(revenue - costs) / costs * 100`
- Profit/loss analysis
- Cost per acquisition metrics
- Revenue per campaign
- Comparative campaign analysis

### 5. Auto-Optimization
- Automatic performance analysis
- Cost per lead threshold alerts (default: $20)
- Qualification rate monitoring (threshold: 30%)
- Outreach success rate tracking (threshold: 5%)
- Automatic campaign pause on negative ROI
- Scaling recommendations for high performers

### 6. Comprehensive Reporting
- Campaign status reports
- Lead quality analysis
- Cost efficiency reports
- ROI by campaign
- Full, cost-only, lead-only, and outreach-only reports
- All campaigns summary report

## Installation

### Prerequisites

1. **NovaOS V2** installed and configured
2. **DDS System** available at `/Users/krissanders/prospecting_agent/`
3. **Python 3.9+**
4. **SQLite3**

### Setup

The integration automatically checks for DDS availability on initialization. No additional setup required if DDS is properly installed.

```python
from integrations.dds import get_dds

dds = get_dds()
# Automatically checks DDS availability and initializes
```

## Usage

### 1. Deploy a Campaign

```python
from integrations.dds import get_dds

dds = get_dds()

result = dds.deploy_campaign({
    'vertical': 'dentists',
    'location': 'Austin, TX',
    'prospect_count': 50,
    'budget': 150,
    'campaign_name': 'Dentists Austin Q1',
    'sender_name': 'John Smith',
    'sender_company': 'Marketing Solutions Pro'
})

print(f"Campaign ID: {result['campaign_id']}")
print(f"Estimated Cost: ${result['estimated_costs']['total']:.2f}")
```

### 2. Start Campaign

```python
dds.start_campaign(campaign_id)
```

### 3. Log Costs

```python
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

# Log AI scoring costs
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
```

### 4. Log Results

```python
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

# After closing deals
dds.log_dds_results(campaign_id, {
    'stage': 'closed',
    'leads_found': 50,
    'leads_qualified': 20,
    'emails_sent': 60,
    'emails_opened': 18,
    'emails_replied': 3,
    'revenue': 5000.00  # Revenue from closed deals
})
```

### 5. Calculate Metrics

```python
metrics = dds.calculate_lead_metrics(campaign_id)

print(f"Leads Generated: {metrics['leads_generated']}")
print(f"Qualification Rate: {metrics['qualification_rate']:.1f}%")
print(f"Cost per Lead: ${metrics['cost_per_lead']:.2f}")
print(f"ROI: {metrics['roi']:.1f}%")
```

### 6. Get Campaign Status

```python
status = dds.get_campaign_status(campaign_id)

print(f"Status: {status['status']}")
print(f"Metrics: {status['metrics']}")
print(f"Performance: {status['performance']}")
```

### 7. Optimize Campaign

```python
optimization = dds.optimize_campaign(campaign_id)

print(f"Priority: {optimization['priority']}")
print(f"Recommendations: {len(optimization['recommendations'])}")

for rec in optimization['recommendations']:
    print(f"- {rec['issue']}: {rec['recommendation']}")
    print(f"  Expected Impact: {rec['expected_impact']}")
```

### 8. Generate Reports

```python
# Full report
full_report = dds.generate_campaign_report(campaign_id, 'full')

# Cost report only
cost_report = dds.generate_campaign_report(campaign_id, 'costs')

# Lead report only
lead_report = dds.generate_campaign_report(campaign_id, 'leads')

# Outreach report only
outreach_report = dds.generate_campaign_report(campaign_id, 'outreach')
```

### 9. All Campaigns Report

```python
report = dds.get_all_campaigns_report()

print(f"Total Campaigns: {report['summary']['total_campaigns']}")
print(f"Total Cost: ${report['summary']['total_cost']:.2f}")
print(f"Total Revenue: ${report['summary']['total_revenue']:.2f}")
print(f"Total ROI: {report['summary']['total_roi']:.1f}%")
```

### 10. Optimize All Campaigns

```python
results = dds.optimize_all_campaigns()

print(f"Critical Issues: {results['critical_issues']}")
print(f"High Priority: {results['high_priority_issues']}")

for campaign in results['campaigns_needing_attention']:
    print(f"\n{campaign['campaign_name']} - {campaign['priority']}")
    for rec in campaign['recommendations']:
        print(f"  - {rec['recommendation']}")
```

### 11. Pause/Resume Campaign

```python
# Pause
dds.pause_campaign(campaign_id)

# Resume
dds.start_campaign(campaign_id)

# Stop permanently
dds.stop_campaign(campaign_id)
```

## API Reference

### Core Methods

#### `deploy_campaign(config: Dict) -> Dict`
Deploy a new DDS campaign.

**Config Parameters:**
- `vertical`: Industry vertical (required)
- `location`: Geographic location (required)
- `prospect_count`: Number of prospects (default: 50)
- `budget`: Max budget in dollars (default: 100)
- `campaign_name`: Custom campaign name (optional)
- `sender_name`: Sender name for emails (optional)
- `sender_company`: Company name (optional)

**Returns:**
- `campaign_id`: Unique campaign identifier
- `status`: Deployment status
- `estimated_costs`: Cost breakdown
- `next_steps`: Actions to take

#### `start_campaign(campaign_id: str) -> Dict`
Start/resume a campaign.

#### `pause_campaign(campaign_id: str) -> Dict`
Pause a campaign temporarily.

#### `stop_campaign(campaign_id: str) -> Dict`
Stop a campaign permanently.

#### `log_dds_costs(campaign_id: str, costs: Dict) -> Dict`
Log DDS API costs.

**Cost Parameters:**
- `operation`: Type of operation (prospecting, scoring, outreach, etc.)
- `provider`: API provider (anthropic, outscraper, hunter_io, sendgrid)
- `cost`: Cost in dollars
- `details`: Additional details (dict)

#### `log_dds_results(campaign_id: str, results: Dict) -> Dict`
Log campaign results.

**Result Parameters:**
- `stage`: Campaign stage (prospecting, scoring, outreach, closed)
- `leads_found`: Total leads found
- `leads_qualified`: Qualified leads
- `emails_sent`: Emails sent
- `emails_opened`: Emails opened
- `emails_replied`: Replies received
- `revenue`: Revenue generated (dollars)

#### `calculate_lead_metrics(campaign_id: str) -> Dict`
Calculate comprehensive lead metrics.

**Returns:**
- `leads_generated`: Total leads
- `leads_qualified`: Qualified leads
- `qualification_rate`: Percentage
- `cost_per_lead`: Cost per lead
- `cost_per_qualified_lead`: Cost per qualified lead
- `emails_sent`: Total emails
- `open_rate`: Email open rate
- `reply_rate`: Email reply rate
- `total_cost`: Total campaign cost
- `revenue_generated`: Total revenue
- `roi`: Return on investment percentage

#### `get_campaign_status(campaign_id: str) -> Dict`
Get detailed campaign status.

#### `optimize_campaign(campaign_id: str) -> Dict`
Analyze and get optimization recommendations.

**Returns:**
- `current_performance`: Current metrics
- `recommendations`: List of recommendations with actions
- `suggested_actions`: Action codes (PAUSE_CAMPAIGN, SCALE_UP, etc.)
- `priority`: CRITICAL, HIGH, MEDIUM, or LOW

#### `optimize_all_campaigns() -> Dict`
Optimize all active campaigns.

#### `generate_campaign_report(campaign_id: str, report_type: str) -> Dict`
Generate campaign report.

**Report Types:**
- `'full'`: Complete report
- `'costs'`: Cost breakdown
- `'leads'`: Lead metrics
- `'outreach'`: Outreach performance

#### `get_all_campaigns_report() -> Dict`
Get summary report for all campaigns.

## Cost Estimation

The integration automatically estimates campaign costs based on:

1. **Google Maps Scraping**: $0.50 per 100 searches (Outscraper)
2. **Website Analysis**: ~500 tokens per site (Claude Haiku)
3. **Lead Scoring**: ~300 tokens per lead (Claude Haiku)
4. **Email Finding**: ~$10 per 100 emails (Hunter.io)
5. **Email Outreach**: $0.001 per email (SendGrid)

Example for 50 prospects:
- Scraping: $0.25
- Website Analysis: $0.01
- Lead Scoring: $0.006
- Email Finding: $5.00
- Outreach (150 emails): $0.15
- **Total: ~$5.42**

## Thresholds & Alerts

### Default Thresholds

- **Cost per Lead**: $20.00 (alert if exceeded)
- **Qualification Rate**: 30% (alert if below)
- **Outreach Success Rate**: 5% (alert if below)

### Auto-Actions

- **Negative ROI**: Campaign automatically paused
- **High Performance** (ROI > 300%): Scale-up recommendation
- **Cost Overrun**: Budget exceeded alert

## Integration with NovaOS Memory

All DDS operations integrate with NovaOS memory system:

- **Agents Table**: Campaign registration and tracking
- **Costs Table**: Every API call logged
- **Revenue Table**: Revenue attribution
- **System Metrics**: Performance metrics storage

Query DDS data via NovaOS memory:

```python
from core.memory import get_memory

memory = get_memory()

# Get all DDS campaigns
campaigns = memory.get_all_agents(department='sales')
dds_campaigns = [c for c in campaigns if c['type'] == 'dds_campaign']

# Get total DDS costs
total_cost = memory.get_total_costs(department='sales')

# Get DDS revenue
total_revenue = memory.get_total_revenue(department='sales')

# Get ROI by department
roi = memory.get_roi_by_department()['sales']
```

## DDS System Integration

### 4 Agent System

1. **Prospecting Agent** (`src/main.py`)
   - Google Maps business scraping
   - Website analysis and scoring
   - Social media presence check
   - Ad spending detection
   - Contact information finding

2. **Scoring Agent** (`src/lead_scorer.py`)
   - Marketing gap analysis
   - Lead quality scoring
   - Qualification thresholds
   - Priority ranking

3. **Research Agent** (`src/website_analyzer.py`, etc.)
   - Competitor research
   - Market analysis
   - Website quality assessment
   - Tech stack detection

4. **Outreach Agent** (`src/outreach_agent.py`)
   - Email campaign management
   - Tracking and analytics
   - Follow-up sequences
   - Response monitoring

### DDS Database Integration

The integration can read from existing DDS databases:
- `ops.db`: Operations tracking
- `campaigns.db`: Campaign management

Additional campaign details automatically pulled when available.

## Example Workflow

See complete workflow in `dds_example_usage.py`:

```bash
cd /Users/krissanders/novaos-v2
python integrations/dds_example_usage.py
```

This runs a complete DDS integration workflow:
1. Deploy campaign
2. Start and monitor
3. Log costs and results
4. Calculate metrics
5. Get optimization recommendations
6. Log revenue
7. Generate reports
8. Optimize all campaigns
9. Pause and resume operations

## Performance Optimization

### Best Practices

1. **Set Realistic Budgets**: Start with $50-100 for 50 prospects
2. **Monitor Cost per Lead**: Keep below $20
3. **Track Qualification Rates**: Target 30%+ qualification
4. **Optimize Outreach**: A/B test templates for 5%+ reply rate
5. **Use Auto-Optimization**: Run daily optimization checks

### Scaling High Performers

When a campaign achieves:
- ROI > 300%
- Cost per lead < $15
- Qualification rate > 40%

**Scale up by:**
- Increasing prospect count 2-3x
- Expanding to similar locations
- Replicating strategy to related verticals

## Troubleshooting

### DDS System Not Found

```python
result = dds.deploy_campaign(config)
if result['status'] == 'error':
    print(result['message'])
    print(result['setup_instructions'])
```

### Budget Exceeded

```python
if result['status'] == 'error' and 'budget' in result['message']:
    print(f"Estimated: ${result['estimated_costs']['total']:.2f}")
    print(f"Budget: ${result['budget']:.2f}")
    # Increase budget or reduce prospect count
```

### Campaign Not Found

```python
status = dds.get_campaign_status(campaign_id)
if 'error' in status.get('status', ''):
    print("Campaign not found. Check campaign_id")
```

## Dashboard Integration

The Sales Department dashboard can display DDS metrics:

```python
# In Sales Department dashboard
from integrations.dds import get_dds

dds = get_dds()
report = dds.get_all_campaigns_report()

# Display in dashboard
print(f"Active DDS Campaigns: {report['summary']['active_campaigns']}")
print(f"Total Revenue: ${report['summary']['total_revenue']:,.2f}")
print(f"ROI: {report['summary']['total_roi']:.1f}%")
```

## Future Enhancements

Potential improvements:
1. Real-time DDS execution from NovaOS
2. Automated campaign deployment based on opportunities
3. ML-based optimization recommendations
4. A/B testing framework integration
5. Multi-channel outreach (LinkedIn, SMS)
6. CRM integration for lead management

## Support

For issues or questions:
1. Check DDS system at `/Users/krissanders/prospecting_agent/`
2. Review NovaOS logs at `/Users/krissanders/novaos-v2/logs/`
3. Verify database at `/Users/krissanders/novaos-v2/data/novaos.db`

## License

Part of NovaOS V2 - Internal Use Only
