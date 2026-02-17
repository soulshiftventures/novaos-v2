"""
NovaOS V2 Visual Dashboard
Flask Web Application
"""

from flask import Flask, render_template, jsonify
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from api import DashboardAPI

app = Flask(__name__)
api = DashboardAPI()


# === PAGE ROUTES ===

@app.route('/')
def index():
    """Homepage - System Overview"""
    return render_template('index.html')


@app.route('/agents')
def agents():
    """Agent Map - Visual Hierarchy"""
    return render_template('agents.html')


@app.route('/financial')
def financial():
    """Financial Dashboard"""
    return render_template('financial.html')


@app.route('/opportunities')
def opportunities():
    """Opportunities Pipeline"""
    return render_template('opportunities.html')


# === API ENDPOINTS ===

@app.route('/api/overview')
def api_overview():
    """System overview data"""
    return jsonify(api.get_overview())


@app.route('/api/agents')
def api_agents():
    """All agents data"""
    return jsonify(api.get_agents())


@app.route('/api/agents/<agent_id>')
def api_agent_detail(agent_id):
    """Individual agent details"""
    return jsonify(api.get_agent_detail(agent_id))


@app.route('/api/financial/summary')
def api_financial_summary():
    """Financial summary"""
    return jsonify(api.get_financial_summary())


@app.route('/api/financial/trends')
def api_financial_trends():
    """Revenue and cost trends (last 30 days)"""
    return jsonify(api.get_financial_trends())


@app.route('/api/financial/departments')
def api_financial_departments():
    """ROI by department"""
    return jsonify(api.get_department_roi())


@app.route('/api/financial/top-agents')
def api_top_agents():
    """Top performing agents"""
    return jsonify(api.get_top_agents())


@app.route('/api/opportunities')
def api_opportunities():
    """All opportunities"""
    return jsonify(api.get_opportunities())


@app.route('/api/opportunities/<int:opp_id>')
def api_opportunity_detail(opp_id):
    """Individual opportunity details"""
    return jsonify(api.get_opportunity_detail(opp_id))


@app.route('/api/alerts')
def api_alerts():
    """Recent system alerts"""
    return jsonify(api.get_alerts())


@app.route('/api/export/financial')
def api_export_financial():
    """Export financial data as CSV"""
    return api.export_financial_csv()


@app.route('/api/export/agents')
def api_export_agents():
    """Export agents data as CSV"""
    return api.export_agents_csv()


@app.route('/api/export/opportunities')
def api_export_opportunities():
    """Export opportunities data as CSV"""
    return api.export_opportunities_csv()


# === ERROR HANDLERS ===

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found'}), 404


@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500


# === RUN ===

if __name__ == '__main__':
    import os

    # Allow port override via environment variable
    port = int(os.environ.get('NOVAOS_DASHBOARD_PORT', 5001))

    print("=" * 60)
    print("NovaOS V2 Visual Dashboard")
    print("=" * 60)
    print(f"Starting server on http://localhost:{port}")
    print("Press Ctrl+C to stop")
    print("=" * 60)

    app.run(host='0.0.0.0', port=port, debug=True)
