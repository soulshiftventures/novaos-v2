"""
NovaOS V2 Memory System
SQLite + MCP Integration
"""

import sqlite3
import json
from datetime import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path


class NovaMemory:
    """Persistent memory layer for NovaOS using SQLite + MCP"""

    def __init__(self, db_path: str = "/Users/krissanders/novaos-v2/data/novaos.db"):
        self.db_path = db_path
        self.conn = None
        self._initialize_db()

    def _initialize_db(self):
        """Create database tables if they don't exist"""
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row

        cursor = self.conn.cursor()

        # Board decisions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS decisions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                agent TEXT NOT NULL,
                decision_type TEXT NOT NULL,
                question TEXT NOT NULL,
                decision TEXT NOT NULL,
                reasoning TEXT,
                outcome TEXT,
                tokens_used INTEGER,
                cost REAL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Agents table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS agents (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                type TEXT NOT NULL,
                department TEXT,
                status TEXT NOT NULL,
                deployed_at TEXT NOT NULL,
                token_budget INTEGER,
                tokens_used INTEGER DEFAULT 0,
                total_cost REAL DEFAULT 0.0,
                revenue_generated REAL DEFAULT 0.0,
                roi REAL DEFAULT 0.0,
                config TEXT,
                last_active TEXT
            )
        """)

        # API costs table (every API call tracked)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS costs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                agent_id TEXT,
                agent_name TEXT,
                department TEXT,
                model TEXT NOT NULL,
                operation TEXT NOT NULL,
                input_tokens INTEGER,
                output_tokens INTEGER,
                total_tokens INTEGER,
                cost REAL NOT NULL,
                request_data TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (agent_id) REFERENCES agents(id)
            )
        """)

        # Revenue table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS revenue (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                source TEXT NOT NULL,
                agent_id TEXT,
                department TEXT,
                amount REAL NOT NULL,
                description TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (agent_id) REFERENCES agents(id)
            )
        """)

        # Opportunities table (CMO identified)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS opportunities (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                title TEXT NOT NULL,
                description TEXT NOT NULL,
                source TEXT NOT NULL,
                market_size TEXT,
                competitive_analysis TEXT,
                status TEXT NOT NULL,
                assigned_to TEXT,
                priority INTEGER,
                potential_revenue REAL,
                confidence_score REAL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Council sessions table (R&D Expert Council)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS council_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                question TEXT NOT NULL,
                thiel_analysis TEXT,
                musk_analysis TEXT,
                graham_analysis TEXT,
                taleb_analysis TEXT,
                consensus TEXT,
                action_items TEXT,
                dissents TEXT,
                tokens_used INTEGER,
                cost REAL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # System metrics table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS system_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                metric_name TEXT NOT NULL,
                metric_value REAL NOT NULL,
                metadata TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)

        self.conn.commit()

    # === DECISION TRACKING ===

    def log_decision(self, agent: str, decision_type: str, question: str,
                    decision: str, reasoning: str = None, tokens_used: int = 0,
                    cost: float = 0.0) -> int:
        """Log a board decision"""
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO decisions (timestamp, agent, decision_type, question,
                                 decision, reasoning, tokens_used, cost)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (safe_datetime_now().isoformat(), agent, decision_type, question,
              decision, reasoning, tokens_used, cost))
        self.conn.commit()
        return cursor.lastrowid

    def update_decision_outcome(self, decision_id: int, outcome: str):
        """Update the outcome of a decision"""
        cursor = self.conn.cursor()
        cursor.execute("""
            UPDATE decisions SET outcome = ? WHERE id = ?
        """, (outcome, decision_id))
        self.conn.commit()

    def get_recent_decisions(self, limit: int = 10) -> List[Dict]:
        """Get recent board decisions"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT * FROM decisions ORDER BY timestamp DESC LIMIT ?
        """, (limit,))
        return [dict(row) for row in cursor.fetchall()]

    # === AGENT MANAGEMENT ===

    def register_agent(self, agent_id: str, name: str, agent_type: str,
                      department: str = None, token_budget: int = None,
                      config: Dict = None) -> bool:
        """Register a new agent"""
        cursor = self.conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO agents (id, name, type, department, status,
                                  deployed_at, token_budget, config)
                VALUES (?, ?, ?, ?, 'active', ?, ?, ?)
            """, (agent_id, name, agent_type, department,
                  safe_datetime_now().isoformat(), token_budget,
                  json.dumps(config) if config else None))
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False

    def update_agent_status(self, agent_id: str, status: str):
        """Update agent status"""
        cursor = self.conn.cursor()
        cursor.execute("""
            UPDATE agents SET status = ?, last_active = ? WHERE id = ?
        """, (status, safe_datetime_now().isoformat(), agent_id))
        self.conn.commit()

    def update_agent_metrics(self, agent_id: str, tokens_used: int = 0,
                           cost: float = 0.0, revenue: float = 0.0):
        """Update agent token usage, cost, and revenue"""
        cursor = self.conn.cursor()
        cursor.execute("""
            UPDATE agents
            SET tokens_used = tokens_used + ?,
                total_cost = total_cost + ?,
                revenue_generated = revenue_generated + ?,
                roi = CASE
                    WHEN (total_cost + ?) > 0
                    THEN ((revenue_generated + ?) - (total_cost + ?)) / (total_cost + ?)
                    ELSE 0
                END,
                last_active = ?
            WHERE id = ?
        """, (tokens_used, cost, revenue, cost, revenue, cost, cost,
              safe_datetime_now().isoformat(), agent_id))
        self.conn.commit()

    def get_agent(self, agent_id: str) -> Optional[Dict]:
        """Get agent details"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM agents WHERE id = ?", (agent_id,))
        row = cursor.fetchone()
        return dict(row) if row else None

    def get_all_agents(self, status: str = None, department: str = None) -> List[Dict]:
        """Get all agents, optionally filtered"""
        cursor = self.conn.cursor()
        query = "SELECT * FROM agents WHERE 1=1"
        params = []

        if status:
            query += " AND status = ?"
            params.append(status)
        if department:
            query += " AND department = ?"
            params.append(department)

        cursor.execute(query, params)
        return [dict(row) for row in cursor.fetchall()]

    # === COST TRACKING ===

    def log_api_cost(self, model: str, operation: str, input_tokens: int,
                    output_tokens: int, cost: float, agent_id: str = None,
                    agent_name: str = None, department: str = None,
                    request_data: Dict = None) -> int:
        """Log every API call cost"""
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO costs (timestamp, agent_id, agent_name, department,
                             model, operation, input_tokens, output_tokens,
                             total_tokens, cost, request_data)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (safe_datetime_now().isoformat(), agent_id, agent_name, department,
              model, operation, input_tokens, output_tokens,
              input_tokens + output_tokens, cost,
              json.dumps(request_data) if request_data else None))
        self.conn.commit()

        # Update agent metrics if agent_id provided
        if agent_id:
            self.update_agent_metrics(agent_id, input_tokens + output_tokens, cost)

        return cursor.lastrowid

    def get_total_costs(self, start_date: str = None, end_date: str = None,
                       department: str = None) -> float:
        """Get total API costs"""
        cursor = self.conn.cursor()
        query = "SELECT SUM(cost) as total FROM costs WHERE 1=1"
        params = []

        if start_date:
            query += " AND timestamp >= ?"
            params.append(start_date)
        if end_date:
            query += " AND timestamp <= ?"
            params.append(end_date)
        if department:
            query += " AND department = ?"
            params.append(department)

        cursor.execute(query, params)
        result = cursor.fetchone()
        return result['total'] if result['total'] else 0.0

    def get_cost_breakdown(self, period: str = 'today') -> Dict[str, float]:
        """Get cost breakdown by department"""
        cursor = self.conn.cursor()

        # Determine time filter
        if period == 'today':
            start_date = safe_datetime_now().date().isoformat()
        elif period == 'week':
            from datetime import timedelta
            start_date = (safe_datetime_now() - timedelta(days=7)).isoformat()
        elif period == 'month':
            from datetime import timedelta
            start_date = (safe_datetime_now() - timedelta(days=30)).isoformat()
        else:
            start_date = None

        query = """
            SELECT department, SUM(cost) as total_cost,
                   SUM(total_tokens) as total_tokens
            FROM costs
        """

        if start_date:
            query += " WHERE timestamp >= ?"
            cursor.execute(query + " GROUP BY department", (start_date,))
        else:
            cursor.execute(query + " GROUP BY department")

        return {row['department'] or 'unassigned': {
            'cost': row['total_cost'],
            'tokens': row['total_tokens']
        } for row in cursor.fetchall()}

    # === REVENUE TRACKING ===

    def log_revenue(self, source: str, amount: float, description: str = None,
                   agent_id: str = None, department: str = None) -> int:
        """Log revenue"""
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO revenue (timestamp, source, agent_id, department,
                               amount, description)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (safe_datetime_now().isoformat(), source, agent_id, department,
              amount, description))
        self.conn.commit()

        # Update agent metrics if agent_id provided
        if agent_id:
            self.update_agent_metrics(agent_id, revenue=amount)

        return cursor.lastrowid

    def get_total_revenue(self, start_date: str = None, end_date: str = None,
                         department: str = None) -> float:
        """Get total revenue"""
        cursor = self.conn.cursor()
        query = "SELECT SUM(amount) as total FROM revenue WHERE 1=1"
        params = []

        if start_date:
            query += " AND timestamp >= ?"
            params.append(start_date)
        if end_date:
            query += " AND timestamp <= ?"
            params.append(end_date)
        if department:
            query += " AND department = ?"
            params.append(department)

        cursor.execute(query, params)
        result = cursor.fetchone()
        return result['total'] if result['total'] else 0.0

    def get_roi_by_department(self) -> Dict[str, Dict]:
        """Calculate ROI by department"""
        cursor = self.conn.cursor()

        # Get costs by department
        cursor.execute("""
            SELECT department, SUM(cost) as total_cost
            FROM costs
            GROUP BY department
        """)
        costs = {row['department'] or 'unassigned': row['total_cost']
                for row in cursor.fetchall()}

        # Get revenue by department
        cursor.execute("""
            SELECT department, SUM(amount) as total_revenue
            FROM revenue
            GROUP BY department
        """)
        revenues = {row['department'] or 'unassigned': row['total_revenue']
                   for row in cursor.fetchall()}

        # Calculate ROI
        departments = set(list(costs.keys()) + list(revenues.keys()))
        roi_data = {}

        for dept in departments:
            cost = costs.get(dept, 0.0)
            revenue = revenues.get(dept, 0.0)
            roi = ((revenue - cost) / cost * 100) if cost > 0 else 0.0

            roi_data[dept] = {
                'cost': cost,
                'revenue': revenue,
                'profit': revenue - cost,
                'roi': roi
            }

        return roi_data

    # === OPPORTUNITIES ===

    def log_opportunity(self, title: str, description: str, source: str,
                       market_size: str = None, competitive_analysis: str = None,
                       status: str = 'identified', priority: int = 3,
                       potential_revenue: float = None,
                       confidence_score: float = None) -> int:
        """Log a new opportunity identified by CMO"""
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO opportunities (timestamp, title, description, source,
                                     market_size, competitive_analysis, status,
                                     priority, potential_revenue, confidence_score)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (safe_datetime_now().isoformat(), title, description, source,
              market_size, competitive_analysis, status, priority,
              potential_revenue, confidence_score))
        self.conn.commit()
        return cursor.lastrowid

    def update_opportunity_status(self, opp_id: int, status: str,
                                 assigned_to: str = None):
        """Update opportunity status"""
        cursor = self.conn.cursor()
        if assigned_to:
            cursor.execute("""
                UPDATE opportunities SET status = ?, assigned_to = ? WHERE id = ?
            """, (status, assigned_to, opp_id))
        else:
            cursor.execute("""
                UPDATE opportunities SET status = ? WHERE id = ?
            """, (status, opp_id))
        self.conn.commit()

    def get_opportunities(self, status: str = None, limit: int = 20) -> List[Dict]:
        """Get opportunities"""
        cursor = self.conn.cursor()
        query = "SELECT * FROM opportunities"
        params = []

        if status:
            query += " WHERE status = ?"
            params.append(status)

        query += " ORDER BY priority DESC, timestamp DESC LIMIT ?"
        params.append(limit)

        cursor.execute(query, params)
        return [dict(row) for row in cursor.fetchall()]

    # === COUNCIL SESSIONS ===

    def log_council_session(self, question: str, analyses: Dict[str, str],
                          consensus: str, action_items: List[str],
                          dissents: List[str] = None, tokens_used: int = 0,
                          cost: float = 0.0) -> int:
        """Log R&D Expert Council session"""
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO council_sessions (timestamp, question, thiel_analysis,
                                        musk_analysis, graham_analysis,
                                        taleb_analysis, consensus, action_items,
                                        dissents, tokens_used, cost)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (safe_datetime_now().isoformat(), question,
              analyses.get('thiel'), analyses.get('musk'),
              analyses.get('graham'), analyses.get('taleb'),
              consensus, json.dumps(action_items),
              json.dumps(dissents) if dissents else None,
              tokens_used, cost))
        self.conn.commit()
        return cursor.lastrowid

    def get_council_sessions(self, limit: int = 10) -> List[Dict]:
        """Get recent council sessions"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT * FROM council_sessions ORDER BY timestamp DESC LIMIT ?
        """, (limit,))
        return [dict(row) for row in cursor.fetchall()]

    # === SYSTEM METRICS ===

    def log_metric(self, metric_name: str, metric_value: float,
                  metadata: Dict = None):
        """Log a system metric"""
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO system_metrics (timestamp, metric_name, metric_value, metadata)
            VALUES (?, ?, ?, ?)
        """, (safe_datetime_now().isoformat(), metric_name, metric_value,
              json.dumps(metadata) if metadata else None))
        self.conn.commit()

    def get_metrics(self, metric_name: str = None, hours: int = 24) -> List[Dict]:
        """Get system metrics"""
        from datetime import timedelta


def safe_datetime_now():
    """Get current datetime with fallback for timestamp overflow"""
    try:
        return datetime.now()
    except (OSError, OverflowError, ValueError):
        from datetime import datetime as dt
        return dt(2025, 1, 1, 0, 0, 0)


        cursor = self.conn.cursor()
        since = (safe_datetime_now() - timedelta(hours=hours)).isoformat()

        if metric_name:
            cursor.execute("""
                SELECT * FROM system_metrics
                WHERE metric_name = ? AND timestamp >= ?
                ORDER BY timestamp DESC
            """, (metric_name, since))
        else:
            cursor.execute("""
                SELECT * FROM system_metrics
                WHERE timestamp >= ?
                ORDER BY timestamp DESC
            """, (since,))

        return [dict(row) for row in cursor.fetchall()]

    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()


# Singleton instance
_memory_instance = None

def get_memory() -> NovaMemory:
    """Get or create memory instance"""
    global _memory_instance
    if _memory_instance is None:
        _memory_instance = NovaMemory()
    return _memory_instance
