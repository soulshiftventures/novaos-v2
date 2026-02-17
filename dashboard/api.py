"""
NovaOS V2 Dashboard API
Data layer for dashboard endpoints
"""

import sqlite3
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from flask import Response
import io
import csv


class DashboardAPI:
    """API layer for dashboard data"""

    def __init__(self, db_path: str = "/Users/krissanders/novaos-v2/data/novaos.db"):
        self.db_path = db_path

    def _get_connection(self):
        """Get database connection"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _dict_from_row(self, row):
        """Convert sqlite Row to dict"""
        return dict(row) if row else None

    # === OVERVIEW DATA ===

    def get_overview(self) -> Dict:
        """Get system overview data for homepage"""
        conn = self._get_connection()
        cursor = conn.cursor()

        # Revenue (today, week, month)
        today = datetime.now().date().isoformat()
        week_ago = (datetime.now() - timedelta(days=7)).isoformat()
        month_ago = (datetime.now() - timedelta(days=30)).isoformat()

        cursor.execute("SELECT COALESCE(SUM(amount), 0) as total FROM revenue WHERE DATE(timestamp) = ?", (today,))
        revenue_today = cursor.fetchone()['total']

        cursor.execute("SELECT COALESCE(SUM(amount), 0) as total FROM revenue WHERE timestamp >= ?", (week_ago,))
        revenue_week = cursor.fetchone()['total']

        cursor.execute("SELECT COALESCE(SUM(amount), 0) as total FROM revenue WHERE timestamp >= ?", (month_ago,))
        revenue_month = cursor.fetchone()['total']

        # Costs (today, week, month)
        cursor.execute("SELECT COALESCE(SUM(cost), 0) as total FROM costs WHERE DATE(timestamp) = ?", (today,))
        cost_today = cursor.fetchone()['total']

        cursor.execute("SELECT COALESCE(SUM(cost), 0) as total FROM costs WHERE timestamp >= ?", (week_ago,))
        cost_week = cursor.fetchone()['total']

        cursor.execute("SELECT COALESCE(SUM(cost), 0) as total FROM costs WHERE timestamp >= ?", (month_ago,))
        cost_month = cursor.fetchone()['total']

        # Calculate cost percentages and ROI
        cost_percent_today = (cost_today / revenue_today * 100) if revenue_today > 0 else 0
        cost_percent_week = (cost_week / revenue_week * 100) if revenue_week > 0 else 0
        cost_percent_month = (cost_month / revenue_month * 100) if revenue_month > 0 else 0

        roi_today = ((revenue_today - cost_today) / cost_today * 100) if cost_today > 0 else 0
        roi_week = ((revenue_week - cost_week) / cost_week * 100) if cost_week > 0 else 0
        roi_month = ((revenue_month - cost_month) / cost_month * 100) if cost_month > 0 else 0

        # Active agents count
        cursor.execute("SELECT COUNT(*) as count FROM agents WHERE status = 'active'")
        active_agents = cursor.fetchone()['count']

        # System health (simple calculation)
        health = "healthy"
        if cost_percent_month > 10:
            health = "warning"
        if cost_percent_month > 20 or roi_month < 100:
            health = "critical"

        conn.close()

        return {
            "revenue": {
                "today": round(revenue_today, 2),
                "week": round(revenue_week, 2),
                "month": round(revenue_month, 2)
            },
            "costs": {
                "today": round(cost_today, 2),
                "week": round(cost_week, 2),
                "month": round(cost_month, 2)
            },
            "cost_percent": {
                "today": round(cost_percent_today, 2),
                "week": round(cost_percent_week, 2),
                "month": round(cost_percent_month, 2)
            },
            "roi": {
                "today": round(roi_today, 2),
                "week": round(roi_week, 2),
                "month": round(roi_month, 2)
            },
            "active_agents": active_agents,
            "system_health": health,
            "timestamp": datetime.now().isoformat()
        }

    # === AGENT DATA ===

    def get_agents(self) -> Dict:
        """Get all agents organized by department"""
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT id, name, type, department, status, deployed_at,
                   tokens_used, total_cost, revenue_generated, roi, last_active
            FROM agents
            ORDER BY department, name
        """)

        agents = [self._dict_from_row(row) for row in cursor.fetchall()]
        conn.close()

        # Organize by department
        departments = {}
        for agent in agents:
            dept = agent['department'] or 'unassigned'
            if dept not in departments:
                departments[dept] = []
            departments[dept].append(agent)

        return {
            "departments": departments,
            "total_agents": len(agents),
            "timestamp": datetime.now().isoformat()
        }

    def get_agent_detail(self, agent_id: str) -> Dict:
        """Get detailed agent information"""
        conn = self._get_connection()
        cursor = conn.cursor()

        # Get agent info
        cursor.execute("SELECT * FROM agents WHERE id = ?", (agent_id,))
        agent = self._dict_from_row(cursor.fetchone())

        if not agent:
            conn.close()
            return {"error": "Agent not found"}

        # Get recent costs
        cursor.execute("""
            SELECT timestamp, operation, cost, total_tokens
            FROM costs
            WHERE agent_id = ?
            ORDER BY timestamp DESC
            LIMIT 20
        """, (agent_id,))
        recent_costs = [self._dict_from_row(row) for row in cursor.fetchall()]

        # Get recent revenue
        cursor.execute("""
            SELECT timestamp, amount, description
            FROM revenue
            WHERE agent_id = ?
            ORDER BY timestamp DESC
            LIMIT 20
        """, (agent_id,))
        recent_revenue = [self._dict_from_row(row) for row in cursor.fetchall()]

        conn.close()

        return {
            "agent": agent,
            "recent_costs": recent_costs,
            "recent_revenue": recent_revenue,
            "timestamp": datetime.now().isoformat()
        }

    # === FINANCIAL DATA ===

    def get_financial_summary(self) -> Dict:
        """Get financial summary"""
        conn = self._get_connection()
        cursor = conn.cursor()

        # Total all-time
        cursor.execute("SELECT COALESCE(SUM(amount), 0) as total FROM revenue")
        total_revenue = cursor.fetchone()['total']

        cursor.execute("SELECT COALESCE(SUM(cost), 0) as total FROM costs")
        total_costs = cursor.fetchone()['total']

        total_profit = total_revenue - total_costs
        total_roi = ((total_profit / total_costs) * 100) if total_costs > 0 else 0

        conn.close()

        return {
            "total_revenue": round(total_revenue, 2),
            "total_costs": round(total_costs, 2),
            "total_profit": round(total_profit, 2),
            "total_roi": round(total_roi, 2),
            "timestamp": datetime.now().isoformat()
        }

    def get_financial_trends(self) -> Dict:
        """Get revenue and cost trends for last 30 days"""
        conn = self._get_connection()
        cursor = conn.cursor()

        # Last 30 days
        thirty_days_ago = (datetime.now() - timedelta(days=30)).date().isoformat()

        # Daily revenue
        cursor.execute("""
            SELECT DATE(timestamp) as date, SUM(amount) as total
            FROM revenue
            WHERE DATE(timestamp) >= ?
            GROUP BY DATE(timestamp)
            ORDER BY date
        """, (thirty_days_ago,))
        revenue_data = [self._dict_from_row(row) for row in cursor.fetchall()]

        # Daily costs
        cursor.execute("""
            SELECT DATE(timestamp) as date, SUM(cost) as total
            FROM costs
            WHERE DATE(timestamp) >= ?
            GROUP BY DATE(timestamp)
            ORDER BY date
        """, (thirty_days_ago,))
        cost_data = [self._dict_from_row(row) for row in cursor.fetchall()]

        conn.close()

        # Fill in missing dates with 0
        date_range = [(datetime.now().date() - timedelta(days=i)).isoformat() for i in range(30, -1, -1)]

        revenue_by_date = {row['date']: row['total'] for row in revenue_data}
        cost_by_date = {row['date']: row['total'] for row in cost_data}

        revenue_trend = [{"date": date, "amount": revenue_by_date.get(date, 0)} for date in date_range]
        cost_trend = [{"date": date, "amount": cost_by_date.get(date, 0)} for date in date_range]

        return {
            "revenue": revenue_trend,
            "costs": cost_trend,
            "timestamp": datetime.now().isoformat()
        }

    def get_department_roi(self) -> Dict:
        """Get ROI by department"""
        conn = self._get_connection()
        cursor = conn.cursor()

        # Revenue by department
        cursor.execute("""
            SELECT department, SUM(amount) as total_revenue
            FROM revenue
            GROUP BY department
        """)
        revenue_by_dept = {row['department'] or 'unassigned': row['total_revenue'] for row in cursor.fetchall()}

        # Costs by department
        cursor.execute("""
            SELECT department, SUM(cost) as total_cost
            FROM costs
            GROUP BY department
        """)
        cost_by_dept = {row['department'] or 'unassigned': row['total_cost'] for row in cursor.fetchall()}

        conn.close()

        # Calculate ROI
        departments = set(list(revenue_by_dept.keys()) + list(cost_by_dept.keys()))
        roi_data = []

        for dept in departments:
            revenue = revenue_by_dept.get(dept, 0)
            cost = cost_by_dept.get(dept, 0)
            profit = revenue - cost
            roi = ((profit / cost) * 100) if cost > 0 else 0

            roi_data.append({
                "department": dept,
                "revenue": round(revenue, 2),
                "cost": round(cost, 2),
                "profit": round(profit, 2),
                "roi": round(roi, 2)
            })

        # Sort by ROI descending
        roi_data.sort(key=lambda x: x['roi'], reverse=True)

        return {
            "departments": roi_data,
            "timestamp": datetime.now().isoformat()
        }

    def get_top_agents(self) -> Dict:
        """Get top 5 revenue and most expensive agents"""
        conn = self._get_connection()
        cursor = conn.cursor()

        # Top 5 by revenue
        cursor.execute("""
            SELECT id, name, department, revenue_generated, total_cost, roi
            FROM agents
            WHERE revenue_generated > 0
            ORDER BY revenue_generated DESC
            LIMIT 5
        """)
        top_revenue = [self._dict_from_row(row) for row in cursor.fetchall()]

        # Top 5 by cost
        cursor.execute("""
            SELECT id, name, department, total_cost, revenue_generated, roi
            FROM agents
            WHERE total_cost > 0
            ORDER BY total_cost DESC
            LIMIT 5
        """)
        most_expensive = [self._dict_from_row(row) for row in cursor.fetchall()]

        conn.close()

        return {
            "top_revenue": top_revenue,
            "most_expensive": most_expensive,
            "timestamp": datetime.now().isoformat()
        }

    # === OPPORTUNITIES DATA ===

    def get_opportunities(self) -> Dict:
        """Get all opportunities"""
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT *
            FROM opportunities
            ORDER BY priority DESC, timestamp DESC
        """)
        opportunities = [self._dict_from_row(row) for row in cursor.fetchall()]

        # Get status breakdown
        cursor.execute("""
            SELECT status, COUNT(*) as count
            FROM opportunities
            GROUP BY status
        """)
        status_breakdown = {row['status']: row['count'] for row in cursor.fetchall()}

        conn.close()

        return {
            "opportunities": opportunities,
            "status_breakdown": status_breakdown,
            "total": len(opportunities),
            "timestamp": datetime.now().isoformat()
        }

    def get_opportunity_detail(self, opp_id: int) -> Dict:
        """Get opportunity details"""
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM opportunities WHERE id = ?", (opp_id,))
        opportunity = self._dict_from_row(cursor.fetchone())

        conn.close()

        if not opportunity:
            return {"error": "Opportunity not found"}

        return {
            "opportunity": opportunity,
            "timestamp": datetime.now().isoformat()
        }

    # === ALERTS ===

    def get_alerts(self) -> Dict:
        """Get recent system alerts"""
        overview = self.get_overview()
        alerts = []

        # Check cost percentage
        if overview['cost_percent']['month'] > 10:
            alerts.append({
                "level": "warning",
                "message": f"AI costs at {overview['cost_percent']['month']:.1f}% of revenue (target <5%)",
                "timestamp": datetime.now().isoformat()
            })

        # Check ROI
        if overview['roi']['month'] < 300:
            alerts.append({
                "level": "warning",
                "message": f"Monthly ROI at {overview['roi']['month']:.0f}% (target >300%)",
                "timestamp": datetime.now().isoformat()
            })

        # Check system health
        if overview['system_health'] == 'critical':
            alerts.append({
                "level": "critical",
                "message": "System health critical - immediate attention required",
                "timestamp": datetime.now().isoformat()
            })

        return {
            "alerts": alerts,
            "timestamp": datetime.now().isoformat()
        }

    # === EXPORT FUNCTIONS ===

    def export_financial_csv(self) -> Response:
        """Export financial data as CSV"""
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT r.timestamp, r.source, r.department, r.amount, r.description,
                   c.cost as associated_cost
            FROM revenue r
            LEFT JOIN costs c ON DATE(r.timestamp) = DATE(c.timestamp) AND r.department = c.department
            ORDER BY r.timestamp DESC
        """)

        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(['Timestamp', 'Source', 'Department', 'Amount', 'Description', 'Associated Cost'])

        for row in cursor.fetchall():
            writer.writerow(row)

        conn.close()

        return Response(
            output.getvalue(),
            mimetype='text/csv',
            headers={'Content-Disposition': 'attachment; filename=novaos_financial.csv'}
        )

    def export_agents_csv(self) -> Response:
        """Export agents data as CSV"""
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT id, name, type, department, status, deployed_at,
                   tokens_used, total_cost, revenue_generated, roi, last_active
            FROM agents
            ORDER BY department, name
        """)

        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(['ID', 'Name', 'Type', 'Department', 'Status', 'Deployed At',
                        'Tokens Used', 'Total Cost', 'Revenue Generated', 'ROI', 'Last Active'])

        for row in cursor.fetchall():
            writer.writerow(row)

        conn.close()

        return Response(
            output.getvalue(),
            mimetype='text/csv',
            headers={'Content-Disposition': 'attachment; filename=novaos_agents.csv'}
        )

    def export_opportunities_csv(self) -> Response:
        """Export opportunities data as CSV"""
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT id, timestamp, title, description, source, status,
                   priority, potential_revenue, confidence_score
            FROM opportunities
            ORDER BY priority DESC, timestamp DESC
        """)

        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(['ID', 'Timestamp', 'Title', 'Description', 'Source',
                        'Status', 'Priority', 'Potential Revenue', 'Confidence Score'])

        for row in cursor.fetchall():
            writer.writerow(row)

        conn.close()

        return Response(
            output.getvalue(),
            mimetype='text/csv',
            headers={'Content-Disposition': 'attachment; filename=novaos_opportunities.csv'}
        )
