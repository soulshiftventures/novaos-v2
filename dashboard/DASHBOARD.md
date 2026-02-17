# NovaOS V2 Visual Dashboard

A real-time web dashboard for monitoring and managing your NovaOS AI business orchestration platform.

## Overview

The NovaOS dashboard provides a visual interface to monitor system health, agent performance, financial metrics, and business opportunities in real-time.

**Key Features:**
- Real-time metrics with auto-refresh (30s intervals)
- Dark mode interface optimized for extended viewing
- Mobile-responsive design
- CSV export functionality
- Interactive charts and visualizations
- Agent hierarchy visualization

## Quick Start

### Starting the Dashboard

```bash
# From the NovaOS V2 directory
python3 cli.py dashboard start
```

The dashboard will start on **http://localhost:5001**

### Stopping the Dashboard

```bash
python3 cli.py dashboard stop
```

### Checking Status

```bash
python3 cli.py dashboard status
```

## Dashboard Pages

### 1. Home - System Overview

**URL:** http://localhost:5001/

**Features:**
- Hero metrics: Revenue, Costs, ROI
- System health indicator (healthy/warning/critical)
- Active agent count
- System alerts and warnings
- Quick navigation to other pages

**Metrics:**
- Today's revenue and costs
- Weekly and monthly aggregates
- AI cost percentage (target: <5% of revenue)
- Overall system ROI

### 2. Agent Map

**URL:** http://localhost:5001/agents

**Features:**
- All agents organized by department
- Visual status indicators:
  - 🟢 Green = Active
  - 🟡 Yellow = Paused
  - 🔴 Red = Killed
- Click any agent for detailed metrics
- Filter by department or status
- Export agent data to CSV

**Agent Details Modal:**
- Token usage and budget
- Cost tracking
- Revenue generated
- ROI calculation
- Recent activity log

### 3. Financial Dashboard

**URL:** http://localhost:5001/financial

**Features:**
- Total revenue, costs, profit, and ROI
- 30-day revenue trend chart
- 30-day cost trend chart
- ROI by department (bar chart)
- Top 5 revenue generators
- Top 5 cost centers
- Cost spike alerts

**Charts:**
- Revenue trend (line chart)
- Cost trend (line chart)
- Department ROI comparison (bar chart)

### 4. Opportunities Pipeline

**URL:** http://localhost:5001/opportunities

**Features:**
- All opportunities identified by CMO
- Status breakdown:
  - Identified
  - Researching
  - Testing
  - Deployed
  - Successful
  - Failed
- Pipeline visualization (funnel chart)
- Potential revenue estimates
- Confidence scores
- Market analysis data

## API Endpoints

All API endpoints return JSON data.

### System Data
- `GET /api/overview` - System overview metrics
- `GET /api/alerts` - Recent system alerts

### Agent Data
- `GET /api/agents` - All agents by department
- `GET /api/agents/<agent_id>` - Detailed agent info

### Financial Data
- `GET /api/financial/summary` - Financial summary
- `GET /api/financial/trends` - 30-day trends
- `GET /api/financial/departments` - ROI by department
- `GET /api/financial/top-agents` - Top performers

### Opportunities Data
- `GET /api/opportunities` - All opportunities
- `GET /api/opportunities/<opp_id>` - Opportunity details

### Export Endpoints
- `GET /api/export/financial` - Download financial data CSV
- `GET /api/export/agents` - Download agents data CSV
- `GET /api/export/opportunities` - Download opportunities CSV

## Configuration

### Port Configuration

By default, the dashboard runs on port **5001** (to avoid conflicts with macOS AirPlay which uses 5000).

To change the port, set the environment variable:

```bash
export NOVAOS_DASHBOARD_PORT=8080
python3 cli.py dashboard start
```

### Database Connection

The dashboard reads from: `/Users/krissanders/novaos-v2/data/novaos.db`

To change the database path, edit `dashboard/api.py`:

```python
def __init__(self, db_path: str = "/path/to/your/novaos.db"):
```

### Auto-Refresh Interval

Default: 30 seconds

To change, edit the JavaScript in each HTML template:

```javascript
let countdown = 30; // Change this value
```

## Technology Stack

- **Backend:** Flask 3.0
- **Database:** SQLite3
- **Frontend:** Bootstrap 5.3 (dark theme)
- **Charts:** Chart.js 4.4
- **Icons:** Bootstrap Icons
- **HTTP Client:** Requests (for CLI status check)

## File Structure

```
/dashboard/
├── app.py                  # Flask application & routes
├── api.py                  # Data layer & business logic
├── start.sh               # Bash startup script
├── templates/
│   ├── index.html         # Home page
│   ├── agents.html        # Agent map page
│   ├── financial.html     # Financial dashboard
│   └── opportunities.html # Opportunities pipeline
├── static/
│   ├── css/
│   │   └── style.css      # Custom dark theme styles
│   └── js/
│       └── charts.js      # Chart utilities & helpers
└── DASHBOARD.md           # This documentation
```

## Keyboard Shortcuts

- `Ctrl + R` - Manual refresh
- `Cmd/Ctrl + K` - Focus search/filter (when available)
- `Esc` - Close modals

## Troubleshooting

### Port Already in Use

If you see "Address already in use" error:

**Option 1:** Kill the process using the port
```bash
lsof -ti:5001 | xargs kill
```

**Option 2:** Use a different port
```bash
export NOVAOS_DASHBOARD_PORT=8080
python3 cli.py dashboard start
```

**Option 3:** Disable macOS AirPlay Receiver
Go to: System Preferences → General → AirDrop & Handoff → Disable AirPlay Receiver

### Dashboard Won't Start

1. Check Flask is installed:
```bash
pip3 install -r requirements.txt
```

2. Check database exists:
```bash
ls -la /Users/krissanders/novaos-v2/data/novaos.db
```

3. Check for errors:
```bash
cd /Users/krissanders/novaos-v2/dashboard
python3 app.py
```

### No Data Showing

The dashboard reads from the SQLite database. If tables are empty, metrics will show $0.00 or 0 agents.

To populate test data, run:
```bash
python3 cli.py deploy sales <agent_type>
```

### Charts Not Rendering

1. Check Chart.js is loading (check browser console)
2. Verify Chart.js CDN is accessible
3. Clear browser cache

## Performance Notes

- Auto-refresh polls every 30 seconds
- Database queries are optimized with indexes
- Large datasets (>1000 agents) may slow page load
- Consider pagination for production deployments

## Security Notes

⚠️ **Development Mode Only**

The dashboard runs in Flask debug mode by default. This is **NOT suitable for production**.

For production deployment:
1. Set `debug=False` in `app.py`
2. Use a production WSGI server (Gunicorn, uWSGI)
3. Add authentication/authorization
4. Enable HTTPS
5. Set up proper logging

Example production command:
```bash
gunicorn -w 4 -b 0.0.0.0:5001 app:app
```

## Future Enhancements

Planned features:
- [ ] Real-time WebSocket updates (no polling)
- [ ] User authentication
- [ ] Multi-user support with roles
- [ ] Historical data comparison
- [ ] Custom date range filters
- [ ] Downloadable reports (PDF)
- [ ] Email alerts for critical issues
- [ ] Mobile app
- [ ] Dark/Light theme toggle

## Support

For issues or questions:
1. Check this documentation
2. Review `/dashboard/README.md`
3. Check `/dashboard/QUICKSTART.md`
4. Open an issue in the repository

## License

Part of NovaOS V2 - AI Business Orchestration Platform
