# DDS Integration Architecture

## System Overview

```
┌─────────────────────────────────────────────────────────────────────────┐
│                            NovaOS V2                                    │
│                                                                         │
│  ┌───────────────────────────────────────────────────────────────┐    │
│  │                    Sales Department                            │    │
│  │  (Owns DDS Integration)                                        │    │
│  └───────────────────────────────────────────────────────────────┘    │
│                              │                                         │
│                              ▼                                         │
│  ┌───────────────────────────────────────────────────────────────┐    │
│  │              DDS Integration Module                            │    │
│  │         (integrations/dds.py - 858 lines)                      │    │
│  │                                                                 │    │
│  │  ┌─────────────────┐  ┌──────────────────┐  ┌──────────────┐ │    │
│  │  │   Campaign      │  │  Cost & Results  │  │ Optimization │ │    │
│  │  │   Management    │  │    Tracking      │  │  & Reports   │ │    │
│  │  └─────────────────┘  └──────────────────┘  └──────────────┘ │    │
│  └───────────────────────────────────────────────────────────────┘    │
│                              │                                         │
│                    ┌─────────┴─────────┐                              │
│                    ▼                   ▼                               │
│  ┌─────────────────────────┐  ┌────────────────────────────┐          │
│  │   NovaOS Memory         │  │    DDS System              │          │
│  │   (core/memory.py)      │  │    (prospecting_agent/)    │          │
│  │                         │  │                            │          │
│  │  ┌──────────────────┐  │  │  ┌──────────────────────┐  │          │
│  │  │  Agents Table    │  │  │  │ Prospecting Agent   │  │          │
│  │  ├──────────────────┤  │  │  ├──────────────────────┤  │          │
│  │  │  Costs Table     │  │  │  │ Scoring Agent       │  │          │
│  │  ├──────────────────┤  │  │  ├──────────────────────┤  │          │
│  │  │  Revenue Table   │  │  │  │ Research Agent      │  │          │
│  │  ├──────────────────┤  │  │  ├──────────────────────┤  │          │
│  │  │  Metrics Table   │  │  │  │ Outreach Agent      │  │          │
│  │  └──────────────────┘  │  │  └──────────────────────┘  │          │
│  │                         │  │                            │          │
│  │  novaos.db             │  │  ops.db / campaigns.db    │          │
│  └─────────────────────────┘  └────────────────────────────┘          │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

## Data Flow

### 1. Campaign Deployment Flow

```
User Request
    │
    ▼
deploy_campaign(config)
    │
    ├─► Validate config
    │   ├─► vertical
    │   ├─► location
    │   ├─► prospect_count
    │   └─► budget
    │
    ├─► Estimate costs
    │   ├─► Scraping: $0.50/100
    │   ├─► Analysis: tokens
    │   ├─► Scoring: tokens
    │   ├─► Email finding: $10/100
    │   └─► Outreach: $0.001/email
    │
    ├─► Validate budget
    │   └─► estimated_cost <= budget ?
    │
    ├─► Register agent
    │   └─► NovaMemory.register_agent()
    │
    └─► Return campaign_id
```

### 2. Cost Tracking Flow

```
DDS Operation (External)
    │
    ▼
log_dds_costs(campaign_id, costs)
    │
    ├─► Extract cost data
    │   ├─► operation
    │   ├─► provider
    │   ├─► cost
    │   └─► details (tokens, etc)
    │
    ├─► Log to costs table
    │   └─► NovaMemory.log_api_cost()
    │
    ├─► Update agent metrics
    │   └─► NovaMemory.update_agent_metrics()
    │
    └─► Check budget threshold
        └─► Alert if exceeded
```

### 3. Results Tracking Flow

```
DDS Results (External)
    │
    ▼
log_dds_results(campaign_id, results)
    │
    ├─► Extract results data
    │   ├─► stage
    │   ├─► leads_found
    │   ├─► leads_qualified
    │   ├─► emails (sent/opened/replied)
    │   └─► revenue
    │
    ├─► Log to system_metrics
    │   └─► NovaMemory.log_metric()
    │
    ├─► If revenue > 0
    │   ├─► Log to revenue table
    │   │   └─► NovaMemory.log_revenue()
    │   └─► Update agent metrics
    │       └─► NovaMemory.update_agent_metrics()
    │
    └─► Return confirmation
```

### 4. Metrics Calculation Flow

```
calculate_lead_metrics(campaign_id)
    │
    ├─► Get agent data
    │   └─► NovaMemory.get_agent()
    │
    ├─► Get stored metrics
    │   └─► NovaMemory.get_metrics()
    │
    ├─► Aggregate results
    │   ├─► leads_found
    │   ├─► leads_qualified
    │   ├─► emails_sent
    │   ├─► emails_opened
    │   └─► emails_replied
    │
    ├─► Calculate metrics
    │   ├─► qualification_rate = qualified / found * 100
    │   ├─► cost_per_lead = total_cost / leads_found
    │   ├─► cost_per_qualified_lead = total_cost / qualified
    │   ├─► open_rate = opened / sent * 100
    │   ├─► reply_rate = replied / sent * 100
    │   └─► roi = (revenue - cost) / cost * 100
    │
    └─► Return metrics dict
```

### 5. Optimization Flow

```
optimize_campaign(campaign_id)
    │
    ├─► Calculate metrics
    │   └─► calculate_lead_metrics()
    │
    ├─► Compare to thresholds
    │   ├─► cost_per_lead vs $20
    │   ├─► qualification_rate vs 30%
    │   ├─► outreach_success vs 5%
    │   └─► roi vs 0%
    │
    ├─► Generate recommendations
    │   ├─► Issue identification
    │   ├─► Severity assignment
    │   ├─► Action recommendation
    │   └─► Expected impact
    │
    ├─► Prioritize (CRITICAL/HIGH/MEDIUM/LOW)
    │
    ├─► Auto-actions
    │   └─► If ROI < 0: pause_campaign()
    │
    └─► Return optimization report
```

## Component Interactions

### DDS Integration ↔ NovaOS Memory

```
DDSIntegration                    NovaMemory
      │                               │
      ├─ register_agent() ───────────►│
      │                               │
      ├─ log_api_cost() ─────────────►│
      │                               │
      ├─ log_revenue() ──────────────►│
      │                               │
      ├─ log_metric() ───────────────►│
      │                               │
      ├─ get_agent() ◄───────────────┤
      │                               │
      ├─ get_all_agents() ◄──────────┤
      │                               │
      ├─ get_metrics() ◄─────────────┤
      │                               │
      └─ update_agent_status() ──────►│
```

### DDS Integration ↔ DDS System

```
DDSIntegration                    DDS System
      │                               │
      ├─ Check availability ─────────►│
      │  (dds_path.exists())          │
      │                               │
      ├─ Read config files ──────────►│
      │  (campaign configs)           │
      │                               │
      ├─ Query databases ────────────►│
      │  (ops.db, campaigns.db)       │
      │                               │
      └─ Return stats ◄───────────────┤
```

## Database Schema Integration

### NovaOS Database (novaos.db)

```sql
-- Agents Table
agents (
    id TEXT PRIMARY KEY,              -- campaign_id
    name TEXT,                        -- Campaign name
    type TEXT,                        -- 'dds_campaign'
    department TEXT,                  -- 'sales'
    status TEXT,                      -- 'active'/'paused'/'stopped'
    deployed_at TEXT,
    token_budget INTEGER,
    tokens_used INTEGER,
    total_cost REAL,                  -- Sum of all costs
    revenue_generated REAL,           -- Sum of all revenue
    roi REAL,                         -- (revenue - cost) / cost
    config TEXT,                      -- JSON config
    last_active TEXT
)

-- Costs Table
costs (
    id INTEGER PRIMARY KEY,
    timestamp TEXT,
    agent_id TEXT,                    -- campaign_id
    agent_name TEXT,
    department TEXT,                  -- 'sales'
    model TEXT,                       -- 'anthropic' / 'outscraper' etc
    operation TEXT,                   -- 'dds_prospecting' / 'dds_scoring'
    input_tokens INTEGER,
    output_tokens INTEGER,
    total_tokens INTEGER,
    cost REAL,                        -- Cost in dollars
    request_data TEXT,                -- JSON details
    FOREIGN KEY (agent_id) REFERENCES agents(id)
)

-- Revenue Table
revenue (
    id INTEGER PRIMARY KEY,
    timestamp TEXT,
    source TEXT,                      -- 'dds_campaign'
    agent_id TEXT,                    -- campaign_id
    department TEXT,                  -- 'sales'
    amount REAL,                      -- Revenue in dollars
    description TEXT,
    FOREIGN KEY (agent_id) REFERENCES agents(id)
)

-- System Metrics Table
system_metrics (
    id INTEGER PRIMARY KEY,
    timestamp TEXT,
    metric_name TEXT,                 -- 'dds_campaign_prospecting'
    metric_value REAL,
    metadata TEXT                     -- JSON with detailed metrics
)
```

### DDS Database (ops.db / campaigns.db)

```sql
-- Campaigns Table (in DDS)
campaigns (
    campaign_name TEXT PRIMARY KEY,
    niche TEXT,
    location TEXT,
    prospects_csv_path TEXT,
    sender_name TEXT,
    sender_company TEXT,
    status TEXT,
    total_prospects INT,
    emails_sent INT,
    emails_opened INT,
    emails_clicked INT,
    emails_replied INT
)
```

## Method Call Hierarchy

```
DDSIntegration
│
├── Campaign Management
│   ├── deploy_campaign()
│   │   ├── _estimate_campaign_costs()
│   │   └── memory.register_agent()
│   │
│   ├── start_campaign()
│   │   └── memory.update_agent_status()
│   │
│   ├── pause_campaign()
│   │   └── memory.update_agent_status()
│   │
│   └── stop_campaign()
│       ├── get_campaign_status()
│       └── memory.update_agent_status()
│
├── Cost & Results Tracking
│   ├── log_dds_costs()
│   │   ├── memory.log_api_cost()
│   │   └── memory.update_agent_metrics()
│   │
│   └── log_dds_results()
│       ├── memory.log_metric()
│       ├── memory.log_revenue()
│       └── memory.update_agent_metrics()
│
├── Metrics & Status
│   ├── calculate_lead_metrics()
│   │   ├── memory.get_agent()
│   │   └── memory.get_metrics()
│   │
│   └── get_campaign_status()
│       ├── calculate_lead_metrics()
│       └── _get_dds_database_stats()
│
├── Optimization
│   ├── optimize_campaign()
│   │   ├── calculate_lead_metrics()
│   │   └── pause_campaign() [if ROI < 0]
│   │
│   └── optimize_all_campaigns()
│       ├── memory.get_all_agents()
│       └── optimize_campaign() [for each]
│
└── Reporting
    ├── generate_campaign_report()
    │   ├── get_campaign_status()
    │   ├── _generate_cost_report()
    │   ├── _generate_lead_report()
    │   ├── _generate_outreach_report()
    │   └── _generate_full_report()
    │
    └── get_all_campaigns_report()
        ├── memory.get_all_agents()
        └── calculate_lead_metrics() [for each]
```

## State Machine

### Campaign Status States

```
┌─────────────┐
│   PENDING   │ (Initial state after deploy)
└──────┬──────┘
       │
       │ start_campaign()
       ▼
┌─────────────┐
│   ACTIVE    │◄───────┐
└──────┬──────┘        │
       │               │ start_campaign()
       │ pause_campaign()
       ▼               │
┌─────────────┐        │
│   PAUSED    │────────┘
└──────┬──────┘
       │
       │ stop_campaign()
       ▼
┌─────────────┐
│   STOPPED   │ (Final state)
└─────────────┘

Auto-transitions:
- ACTIVE → PAUSED (if ROI < 0 in optimization)
```

## Performance Metrics Pipeline

```
Campaign Execution
       │
       ▼
┌─────────────────────┐
│   Data Collection   │
├─────────────────────┤
│ • Leads found       │
│ • Leads qualified   │
│ • Emails sent       │
│ • Emails opened     │
│ • Emails replied    │
│ • Costs incurred    │
│ • Revenue generated │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ Metric Calculation  │
├─────────────────────┤
│ • Qualification %   │
│ • Cost per lead     │
│ • Open rate %       │
│ • Reply rate %      │
│ • ROI %             │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│   Threshold Check   │
├─────────────────────┤
│ • Cost per lead     │
│   vs $20            │
│ • Qualification     │
│   vs 30%            │
│ • Outreach success  │
│   vs 5%             │
│ • ROI vs 0%         │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Recommendations    │
├─────────────────────┤
│ • Issues identified │
│ • Actions suggested │
│ • Priority assigned │
│ • Auto-actions      │
└─────────────────────┘
```

## Cost Tracking Architecture

```
DDS Operation
    │
    ▼
┌──────────────────────────────────┐
│     Cost Classification          │
├──────────────────────────────────┤
│ Provider    │ Operation          │
├─────────────┼────────────────────┤
│ outscraper  │ dds_prospecting    │
│ anthropic   │ dds_scoring        │
│ hunter_io   │ dds_email_finding  │
│ sendgrid    │ dds_outreach       │
└──────────────┬───────────────────┘
               │
               ▼
┌──────────────────────────────────┐
│      Cost Aggregation            │
├──────────────────────────────────┤
│ By Campaign  │ By Provider       │
│ By Operation │ By Time Period    │
│ By Department│ Total             │
└──────────────┬───────────────────┘
               │
               ▼
┌──────────────────────────────────┐
│      Cost Analysis               │
├──────────────────────────────────┤
│ • Cost per lead                  │
│ • Cost per qualified lead        │
│ • Cost per email sent            │
│ • Cost per reply                 │
│ • Cost efficiency vs target      │
└──────────────┬───────────────────┘
               │
               ▼
┌──────────────────────────────────┐
│      Budget Control              │
├──────────────────────────────────┤
│ • Budget vs actual               │
│ • Overspend alerts               │
│ • Auto-pause on exceed           │
└──────────────────────────────────┘
```

## Integration Benefits

### For NovaOS
✅ **Complete DDS control** from NovaOS interface
✅ **Centralized cost tracking** across all operations
✅ **Unified metrics** and reporting
✅ **ROI visibility** for all sales activities
✅ **Auto-optimization** of campaigns
✅ **Budget management** and alerts

### For Sales Department
✅ **Owns complete DDS system**
✅ **Performance visibility**
✅ **Cost optimization**
✅ **Revenue attribution**
✅ **Campaign management**
✅ **Automated recommendations**

### For Business
✅ **Cost efficiency** tracking
✅ **ROI measurement** per campaign
✅ **Performance optimization**
✅ **Scalability** of winners
✅ **Risk management** (auto-pause losers)
✅ **Data-driven decisions**

## Security & Access Control

```
┌─────────────────────────────────────────┐
│         Sales Department                │
│         (Full Access)                   │
├─────────────────────────────────────────┤
│ • Deploy campaigns                      │
│ • Start/pause/stop                      │
│ • View all metrics                      │
│ • Access cost data                      │
│ • Generate reports                      │
│ • Modify thresholds                     │
└─────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────┐
│         CFO                             │
│         (Financial Oversight)           │
├─────────────────────────────────────────┤
│ • View costs                            │
│ • View ROI                              │
│ • View reports                          │
│ • Budget oversight                      │
└─────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────┐
│         CEO                             │
│         (Executive Summary)             │
├─────────────────────────────────────────┤
│ • View summary metrics                  │
│ • View ROI                              │
│ • Approve major campaigns               │
└─────────────────────────────────────────┘
```

---

**Architecture Version**: 1.0.0
**Last Updated**: February 16, 2026
**Status**: Production
