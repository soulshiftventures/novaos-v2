# Dashboard Quick Start

## Launch Dashboard

**Method 1: Standalone launcher (recommended)**
```bash
cd /Users/krissanders/novaos-v2/dashboard
./nova-dashboard start
```

**Method 2: Via main CLI**
```bash
cd /Users/krissanders/novaos-v2
python3 cli.py dashboard start
```

Dashboard runs on: **http://localhost:5001**

## Stop Dashboard

```bash
cd /Users/krissanders/novaos-v2/dashboard
./nova-dashboard stop
```

## Check Status

```bash
cd /Users/krissanders/novaos-v2/dashboard
./nova-dashboard status
```

## Pages

1. **Home** (/) - System overview, health, alerts
2. **Agents** (/agents) - All agents by department with status
3. **Financial** (/financial) - Revenue, costs, ROI, trends
4. **Opportunities** (/opportunities) - CMO pipeline visualization

## Export Data

Each page has an "Export CSV" button in the top-right corner.

Or use API endpoints:
- http://localhost:5001/api/export/financial
- http://localhost:5001/api/export/agents
- http://localhost:5001/api/export/opportunities

## Troubleshooting

**Port already in use?**
```bash
lsof -ti:5001 | xargs kill
```

**Database not found?**
Check: `/Users/krissanders/novaos-v2/data/novaos.db`

**No data showing?**
Deploy some agents first:
```bash
python3 cli.py deploy sales dds
```

## Full Documentation

See [DASHBOARD.md](DASHBOARD.md) for complete documentation.
