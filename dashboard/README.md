# NovaOS V2 Visual Dashboard

A Flask-based web dashboard for monitoring NovaOS V2 agent performance, financials, and opportunities.

## Features

- **System Overview** - Real-time revenue, costs, ROI, and system health
- **Agent Map** - Visual hierarchy of all agents by department with status indicators
- **Financial Dashboard** - Revenue/cost trends, ROI analysis, top performing agents
- **Opportunities Pipeline** - CMO-identified opportunities with status tracking

## Quick Start

### 1. Install Dependencies

```bash
cd /Users/krissanders/novaos-v2
pip install -r requirements.txt
```

### 2. Run Dashboard

```bash
cd /Users/krissanders/novaos-v2/dashboard
python app.py
```

### 3. Access Dashboard

Open your browser to: **http://localhost:5000**

## Dashboard Pages

### Homepage (/)
- Big numbers: Revenue, Costs, ROI
- System health indicator
- Active agents count
- Recent alerts

### Agent Map (/agents)
- All agents organized by department
- Real-time status (active/paused/killed)
- Click agent for detailed metrics
- Export to CSV

### Financial (/financial)
- 30-day revenue and cost trends
- ROI by department (bar chart)
- Top 5 revenue generators
- Most expensive 5 agents
- Export to CSV

### Opportunities (/opportunities)
- Pipeline visualization
- Status breakdown
- Filter by status
- Click opportunity for full analysis
- Export to CSV

## API Endpoints

All data is available via JSON API:

- `GET /api/overview` - System overview
- `GET /api/agents` - All agents
- `GET /api/agents/<id>` - Agent details
- `GET /api/financial/summary` - Financial summary
- `GET /api/financial/trends` - 30-day trends
- `GET /api/financial/departments` - ROI by department
- `GET /api/financial/top-agents` - Top performers
- `GET /api/opportunities` - All opportunities
- `GET /api/opportunities/<id>` - Opportunity details
- `GET /api/alerts` - System alerts

## Features

- **Auto-refresh**: Every 30 seconds
- **Dark mode**: Default theme
- **Mobile responsive**: Basic mobile support
- **Export**: CSV export for all data
- **Real-time**: Live data from SQLite database

## Tech Stack

- **Backend**: Flask 3.0
- **Database**: SQLite (reads from `/Users/krissanders/novaos-v2/data/novaos.db`)
- **Frontend**: Vanilla JavaScript + Bootstrap 5
- **Charts**: Chart.js 4.4
- **No build process**: Pure HTML/CSS/JS

## Color Coding

### ROI
- **Green**: ≥300% (excellent)
- **Yellow**: 100-300% (good)
- **Red**: <100% (needs improvement)

### System Health
- **Healthy**: Costs <10% of revenue
- **Warning**: Costs 10-20% of revenue
- **Critical**: Costs >20% or ROI <100%

### Agent Status
- **Green dot**: Active
- **Yellow dot**: Paused
- **Red dot**: Killed

## Development

The dashboard reads directly from the NovaOS database. No migrations or setup needed.

### File Structure

```
dashboard/
├── app.py              # Flask application & routes
├── api.py              # API data layer
├── templates/          # HTML templates
│   ├── index.html      # Homepage
│   ├── agents.html     # Agent map
│   ├── financial.html  # Financial dashboard
│   └── opportunities.html  # Opportunities
├── static/
│   ├── css/
│   │   └── style.css   # Dark theme styles
│   └── js/
│       └── charts.js   # Chart utilities
└── README.md
```

## Troubleshooting

### Port already in use
If port 5000 is taken, edit `app.py` and change:
```python
app.run(host='0.0.0.0', port=5000, debug=True)
```

### Database not found
Ensure `/Users/krissanders/novaos-v2/data/novaos.db` exists.

### No data showing
The dashboard reads from the database. If no data appears, the database may be empty. Run NovaOS agents to populate data.

## Notes

- Dashboard is read-only (no data modification)
- All times shown in system timezone
- CSV exports include all historical data
- Charts limited to 30 days for performance
