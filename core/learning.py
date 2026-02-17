"""
NovaOS V2 Learning System
Vector storage + Pattern analysis using ChromaDB
"""

import sqlite3
import json
import chromadb
from chromadb.config import Settings
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path
from sentence_transformers import SentenceTransformer
import numpy as np
from collections import defaultdict


def safe_datetime_now():
    """Get current datetime with fallback for timestamp overflow"""
    try:
        return safe_datetime_now()
    except (OSError, OverflowError, ValueError):
        from datetime import datetime as dt
        return dt(2025, 1, 1, 0, 0, 0)



class NovaLearning:
    """
    Learning system that stores and retrieves decisions, deployments, and opportunities
    Uses ChromaDB for vector storage and pattern analysis
    """

    def __init__(
        self,
        db_path: str = "/Users/krissanders/novaos-v2/data/novaos.db",
        chroma_path: str = "/Users/krissanders/novaos-v2/data/chroma_db"
    ):
        """Initialize learning system with SQLite and ChromaDB"""
        self.db_path = db_path
        self.chroma_path = chroma_path

        # Initialize sentence transformer for embeddings
        print("[Learning] Initializing sentence transformer...")
        self.encoder = SentenceTransformer('all-MiniLM-L6-v2')  # Fast, efficient embeddings

        # Initialize ChromaDB
        print("[Learning] Initializing ChromaDB...")
        self.chroma_client = chromadb.PersistentClient(
            path=chroma_path,
            settings=Settings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )

        # Create or get collections
        self.decisions_collection = self.chroma_client.get_or_create_collection(
            name="decisions",
            metadata={"description": "Board decisions with context and outcomes"}
        )

        self.agents_collection = self.chroma_client.get_or_create_collection(
            name="agent_deployments",
            metadata={"description": "Agent deployments with configs and performance"}
        )

        self.opportunities_collection = self.chroma_client.get_or_create_collection(
            name="opportunities",
            metadata={"description": "Market opportunities with evaluations"}
        )

        # SQLite connection
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row

        print("[Learning] Learning system initialized")

    # === DECISION STORAGE ===

    def store_decision(
        self,
        decision_id: int,
        context: str,
        outcome: Optional[str] = None,
        metrics: Optional[Dict] = None
    ) -> bool:
        """
        Store a decision in vector database for future retrieval

        Args:
            decision_id: ID from decisions table in SQLite
            context: The decision context (question + reasoning)
            outcome: Result of the decision
            metrics: cost, revenue, ROI, tokens_used, etc.

        Returns:
            True if stored successfully
        """
        try:
            # Get decision from SQLite
            cursor = self.conn.cursor()
            cursor.execute("SELECT * FROM decisions WHERE id = ?", (decision_id,))
            decision = cursor.fetchone()

            if not decision:
                print(f"[Learning] Decision {decision_id} not found in database")
                return False

            decision_dict = dict(decision)

            # Build searchable text
            searchable_text = f"""
            Decision Type: {decision_dict['decision_type']}
            Question: {decision_dict['question']}
            Decision: {decision_dict['decision']}
            Reasoning: {decision_dict.get('reasoning', 'N/A')}
            Agent: {decision_dict['agent']}
            """

            if outcome:
                searchable_text += f"\nOutcome: {outcome}"

            # Generate embedding
            embedding = self.encoder.encode(searchable_text).tolist()

            # Prepare metadata
            metadata = {
                "decision_id": str(decision_id),
                "timestamp": decision_dict['timestamp'],
                "agent": decision_dict['agent'],
                "decision_type": decision_dict['decision_type'],
                "cost": float(decision_dict.get('cost', 0.0)),
                "tokens_used": int(decision_dict.get('tokens_used', 0)),
                "has_outcome": "yes" if outcome else "no"
            }

            # Add metrics if provided
            if metrics:
                for key, value in metrics.items():
                    if isinstance(value, (int, float)):
                        metadata[f"metric_{key}"] = float(value)

            # Store in ChromaDB
            self.decisions_collection.add(
                embeddings=[embedding],
                documents=[searchable_text],
                metadatas=[metadata],
                ids=[f"decision_{decision_id}"]
            )

            print(f"[Learning] Stored decision {decision_id} in vector database")
            return True

        except Exception as e:
            print(f"[Learning] Error storing decision {decision_id}: {e}")
            return False

    def store_agent_deployment(
        self,
        agent_id: str,
        config: Dict,
        performance: Dict
    ) -> bool:
        """
        Store agent deployment data for learning

        Args:
            agent_id: Agent identifier
            config: Agent configuration (department, type, budget, etc.)
            performance: Performance metrics (tokens_used, cost, revenue, ROI)

        Returns:
            True if stored successfully
        """
        try:
            # Get agent from SQLite
            cursor = self.conn.cursor()
            cursor.execute("SELECT * FROM agents WHERE id = ?", (agent_id,))
            agent = cursor.fetchone()

            if not agent:
                print(f"[Learning] Agent {agent_id} not found in database")
                return False

            agent_dict = dict(agent)

            # Build searchable text
            searchable_text = f"""
            Agent: {agent_dict['name']}
            Type: {agent_dict['type']}
            Department: {agent_dict.get('department', 'N/A')}
            Status: {agent_dict['status']}
            Deployed: {agent_dict['deployed_at']}
            Token Budget: {agent_dict.get('token_budget', 0)}
            Tokens Used: {performance.get('tokens_used', agent_dict.get('tokens_used', 0))}
            Total Cost: ${performance.get('cost', agent_dict.get('total_cost', 0.0)):.2f}
            Revenue: ${performance.get('revenue', agent_dict.get('revenue_generated', 0.0)):.2f}
            ROI: {performance.get('roi', agent_dict.get('roi', 0.0)):.1f}%
            """

            if config:
                searchable_text += f"\nConfig: {json.dumps(config)}"

            # Generate embedding
            embedding = self.encoder.encode(searchable_text).tolist()

            # Prepare metadata
            metadata = {
                "agent_id": agent_id,
                "agent_name": agent_dict['name'],
                "agent_type": agent_dict['type'],
                "department": agent_dict.get('department', 'unknown'),
                "status": agent_dict['status'],
                "deployed_at": agent_dict['deployed_at'],
                "tokens_used": int(performance.get('tokens_used', agent_dict.get('tokens_used', 0))),
                "cost": float(performance.get('cost', agent_dict.get('total_cost', 0.0))),
                "revenue": float(performance.get('revenue', agent_dict.get('revenue_generated', 0.0))),
                "roi": float(performance.get('roi', agent_dict.get('roi', 0.0)))
            }

            # Store in ChromaDB with safe timestamp
            try:
                ts = int(safe_datetime_now().timestamp())
            except (OSError, OverflowError, ValueError):
                ts = int(datetime(2025, 1, 1).timestamp())

            self.agents_collection.add(
                embeddings=[embedding],
                documents=[searchable_text],
                metadatas=[metadata],
                ids=[f"agent_{agent_id}_{ts}"]
            )

            print(f"[Learning] Stored agent deployment {agent_id} in vector database")
            return True

        except Exception as e:
            print(f"[Learning] Error storing agent deployment {agent_id}: {e}")
            return False

    def store_opportunity(
        self,
        opp_id: int,
        source: str,
        evaluation: Dict,
        outcome: Optional[str] = None
    ) -> bool:
        """
        Store opportunity data for learning

        Args:
            opp_id: Opportunity ID from SQLite
            source: Where the opportunity came from
            evaluation: CMO's evaluation (priority, confidence, potential revenue)
            outcome: What happened (pursued, passed, succeeded, failed)

        Returns:
            True if stored successfully
        """
        try:
            # Get opportunity from SQLite
            cursor = self.conn.cursor()
            cursor.execute("SELECT * FROM opportunities WHERE id = ?", (opp_id,))
            opp = cursor.fetchone()

            if not opp:
                print(f"[Learning] Opportunity {opp_id} not found in database")
                return False

            opp_dict = dict(opp)

            # Build searchable text
            searchable_text = f"""
            Opportunity: {opp_dict['title']}
            Description: {opp_dict['description']}
            Source: {source}
            Status: {opp_dict['status']}
            Priority: {opp_dict.get('priority', 'N/A')}
            Market Size: {opp_dict.get('market_size', 'N/A')}
            Competitive Analysis: {opp_dict.get('competitive_analysis', 'N/A')}
            Potential Revenue: ${opp_dict.get('potential_revenue', 0.0)}
            Confidence: {opp_dict.get('confidence_score', 0.0)}
            """

            if outcome:
                searchable_text += f"\nOutcome: {outcome}"

            # Generate embedding
            embedding = self.encoder.encode(searchable_text).tolist()

            # Prepare metadata
            metadata = {
                "opp_id": str(opp_id),
                "timestamp": opp_dict['timestamp'],
                "source": source,
                "status": opp_dict['status'],
                "priority": int(opp_dict.get('priority', 3)),
                "potential_revenue": float(opp_dict.get('potential_revenue', 0.0)),
                "confidence_score": float(opp_dict.get('confidence_score', 0.0)),
                "has_outcome": "yes" if outcome else "no"
            }

            # Store in ChromaDB
            self.opportunities_collection.add(
                embeddings=[embedding],
                documents=[searchable_text],
                metadatas=[metadata],
                ids=[f"opportunity_{opp_id}"]
            )

            print(f"[Learning] Stored opportunity {opp_id} in vector database")
            return True

        except Exception as e:
            print(f"[Learning] Error storing opportunity {opp_id}: {e}")
            return False

    # === RETRIEVAL FOR DECISION-MAKING ===

    def query_similar(
        self,
        query_text: str,
        collection_type: str = "decisions",
        limit: int = 5,
        filters: Optional[Dict] = None
    ) -> List[Dict]:
        """
        Query for similar past decisions/agents/opportunities

        Args:
            query_text: The question or context to search for
            collection_type: "decisions", "agents", or "opportunities"
            limit: How many results to return
            filters: Optional metadata filters

        Returns:
            List of similar items with metadata and relevance scores
        """
        try:
            # Select collection
            if collection_type == "decisions":
                collection = self.decisions_collection
            elif collection_type == "agents":
                collection = self.agents_collection
            elif collection_type == "opportunities":
                collection = self.opportunities_collection
            else:
                print(f"[Learning] Invalid collection type: {collection_type}")
                return []

            # Generate query embedding
            query_embedding = self.encoder.encode(query_text).tolist()

            # Query ChromaDB
            results = collection.query(
                query_embeddings=[query_embedding],
                n_results=limit,
                where=filters if filters else None
            )

            # Format results
            similar_items = []
            if results['documents'] and len(results['documents']) > 0:
                for i in range(len(results['documents'][0])):
                    item = {
                        'content': results['documents'][0][i],
                        'metadata': results['metadatas'][0][i],
                        'distance': results['distances'][0][i] if 'distances' in results else 0.0,
                        'relevance': 1.0 - (results['distances'][0][i] if 'distances' in results else 0.0)
                    }
                    similar_items.append(item)

            return similar_items

        except Exception as e:
            print(f"[Learning] Error querying similar items: {e}")
            return []

    def get_similar_decisions(
        self,
        question: str,
        decision_type: Optional[str] = None,
        limit: int = 3
    ) -> str:
        """
        Get similar past decisions formatted for board context
        Returns: Human-readable summary for board agents
        """
        filters = {}
        if decision_type:
            filters['decision_type'] = decision_type

        similar = self.query_similar(question, "decisions", limit, filters)

        if not similar:
            return "No similar past decisions found."

        summary = f"SIMILAR PAST DECISIONS (Last {limit} times we faced something similar):\n\n"

        for i, item in enumerate(similar, 1):
            meta = item['metadata']
            summary += f"{i}. [{meta['timestamp']}] {meta['agent']} - {meta['decision_type']}\n"
            summary += f"   Cost: ${meta['cost']:.2f} | Tokens: {meta['tokens_used']}\n"
            summary += f"   Outcome: {meta.get('has_outcome', 'unknown')}\n"
            summary += f"   Relevance: {item['relevance']:.1%}\n\n"

        return summary

    # === PATTERN ANALYSIS ===

    def analyze_weekly(self) -> Dict[str, Any]:
        """
        Perform weekly analysis of patterns
        Returns: Insights and recommendations
        """
        print("[Learning] Running weekly analysis...")

        analysis = {
            "timestamp": safe_datetime_now().isoformat(),
            "period": "last_7_days",
            "decisions": self._analyze_decisions(),
            "agents": self._analyze_agents(),
            "opportunities": self._analyze_opportunities(),
            "recommendations": []
        }

        # Generate recommendations based on patterns
        analysis['recommendations'] = self._generate_recommendations(analysis)

        return analysis

    def _analyze_decisions(self) -> Dict:
        """Analyze decision patterns"""
        cursor = self.conn.cursor()
        week_ago = (safe_datetime_now() - timedelta(days=7)).isoformat()

        # Get decisions from last week
        cursor.execute("""
            SELECT decision_type, COUNT(*) as count,
                   AVG(cost) as avg_cost,
                   SUM(cost) as total_cost,
                   AVG(tokens_used) as avg_tokens
            FROM decisions
            WHERE timestamp >= ?
            GROUP BY decision_type
        """, (week_ago,))

        results = cursor.fetchall()

        decision_patterns = {
            "total_decisions": sum(row['count'] for row in results),
            "by_type": {},
            "total_cost": 0.0,
            "avg_tokens_per_decision": 0.0
        }

        for row in results:
            decision_patterns['by_type'][row['decision_type']] = {
                'count': row['count'],
                'avg_cost': float(row['avg_cost'] or 0.0),
                'total_cost': float(row['total_cost'] or 0.0),
                'avg_tokens': int(row['avg_tokens'] or 0)
            }
            decision_patterns['total_cost'] += float(row['total_cost'] or 0.0)

        if decision_patterns['total_decisions'] > 0:
            cursor.execute("""
                SELECT AVG(tokens_used) as avg_tokens
                FROM decisions
                WHERE timestamp >= ?
            """, (week_ago,))
            avg_result = cursor.fetchone()
            decision_patterns['avg_tokens_per_decision'] = int(avg_result['avg_tokens'] or 0)

        return decision_patterns

    def _analyze_agents(self) -> Dict:
        """Analyze agent performance patterns"""
        cursor = self.conn.cursor()

        # Get all active agents
        cursor.execute("""
            SELECT department,
                   COUNT(*) as agent_count,
                   SUM(total_cost) as total_cost,
                   SUM(revenue_generated) as total_revenue,
                   AVG(roi) as avg_roi
            FROM agents
            WHERE status = 'active'
            GROUP BY department
        """)

        results = cursor.fetchall()

        agent_patterns = {
            "total_agents": 0,
            "by_department": {},
            "high_performers": [],
            "low_performers": []
        }

        for row in results:
            dept = row['department'] or 'unassigned'
            agent_patterns['total_agents'] += row['agent_count']
            agent_patterns['by_department'][dept] = {
                'count': row['agent_count'],
                'total_cost': float(row['total_cost'] or 0.0),
                'total_revenue': float(row['total_revenue'] or 0.0),
                'avg_roi': float(row['avg_roi'] or 0.0)
            }

        # Find high and low performers
        cursor.execute("""
            SELECT id, name, department, roi, total_cost, revenue_generated
            FROM agents
            WHERE status = 'active' AND total_cost > 0
            ORDER BY roi DESC
            LIMIT 5
        """)

        agent_patterns['high_performers'] = [
            {
                'id': row['id'],
                'name': row['name'],
                'department': row['department'],
                'roi': float(row['roi']),
                'cost': float(row['total_cost']),
                'revenue': float(row['revenue_generated'])
            }
            for row in cursor.fetchall()
        ]

        cursor.execute("""
            SELECT id, name, department, roi, total_cost, revenue_generated
            FROM agents
            WHERE status = 'active' AND total_cost > 0
            ORDER BY roi ASC
            LIMIT 5
        """)

        agent_patterns['low_performers'] = [
            {
                'id': row['id'],
                'name': row['name'],
                'department': row['department'],
                'roi': float(row['roi']),
                'cost': float(row['total_cost']),
                'revenue': float(row['revenue_generated'])
            }
            for row in cursor.fetchall()
        ]

        return agent_patterns

    def _analyze_opportunities(self) -> Dict:
        """Analyze opportunity patterns"""
        cursor = self.conn.cursor()
        week_ago = (safe_datetime_now() - timedelta(days=7)).isoformat()

        # Get opportunities by status
        cursor.execute("""
            SELECT status,
                   COUNT(*) as count,
                   AVG(confidence_score) as avg_confidence,
                   AVG(potential_revenue) as avg_revenue
            FROM opportunities
            WHERE timestamp >= ?
            GROUP BY status
        """, (week_ago,))

        results = cursor.fetchall()

        opp_patterns = {
            "total_opportunities": sum(row['count'] for row in results),
            "by_status": {},
            "avg_confidence": 0.0,
            "total_potential_revenue": 0.0
        }

        for row in results:
            opp_patterns['by_status'][row['status']] = {
                'count': row['count'],
                'avg_confidence': float(row['avg_confidence'] or 0.0),
                'avg_revenue': float(row['avg_revenue'] or 0.0)
            }

        # Get overall averages
        cursor.execute("""
            SELECT AVG(confidence_score) as avg_confidence,
                   SUM(potential_revenue) as total_revenue
            FROM opportunities
            WHERE timestamp >= ?
        """, (week_ago,))

        avg_result = cursor.fetchone()
        opp_patterns['avg_confidence'] = float(avg_result['avg_confidence'] or 0.0)
        opp_patterns['total_potential_revenue'] = float(avg_result['total_revenue'] or 0.0)

        return opp_patterns

    def _generate_recommendations(self, analysis: Dict) -> List[str]:
        """Generate actionable recommendations from analysis"""
        recommendations = []

        # Decision recommendations
        decisions = analysis['decisions']
        if decisions['total_cost'] > 100.0:  # High decision costs
            recommendations.append(
                f"HIGH DECISION COSTS: Spent ${decisions['total_cost']:.2f} on decisions this week. "
                f"Consider batching similar decisions or using cheaper models for routine choices."
            )

        # Agent recommendations
        agents = analysis['agents']
        if agents['low_performers']:
            low_roi_agents = [a for a in agents['low_performers'] if a['roi'] < 0]
            if low_roi_agents:
                recommendations.append(
                    f"NEGATIVE ROI AGENTS: {len(low_roi_agents)} agents with negative ROI. "
                    f"Review: {', '.join(a['name'] for a in low_roi_agents[:3])}. "
                    f"Consider reallocation or shutdown."
                )

        if agents['high_performers']:
            top_performer = agents['high_performers'][0]
            recommendations.append(
                f"HIGH ROI OPPORTUNITY: {top_performer['name']} ({top_performer['department']}) "
                f"has {top_performer['roi']:.1f}% ROI. Consider increasing budget or replicating strategy."
            )

        # Opportunity recommendations
        opps = analysis['opportunities']
        if opps['total_opportunities'] == 0:
            recommendations.append(
                "NO NEW OPPORTUNITIES: CMO hasn't identified opportunities this week. "
                "Consider running market scan or reviewing prospecting strategy."
            )
        elif opps['avg_confidence'] < 0.5:
            recommendations.append(
                f"LOW CONFIDENCE OPPORTUNITIES: Average confidence score {opps['avg_confidence']:.1%}. "
                f"May need better market research or clearer evaluation criteria."
            )

        # Cost/Revenue balance
        total_cost = sum(
            dept['total_cost']
            for dept in agents['by_department'].values()
        )
        total_revenue = sum(
            dept['total_revenue']
            for dept in agents['by_department'].values()
        )

        if total_cost > 0:
            overall_roi = ((total_revenue - total_cost) / total_cost) * 100
            if overall_roi < 0:
                recommendations.append(
                    f"NEGATIVE OVERALL ROI: System is at {overall_roi:.1f}% ROI. "
                    f"Revenue (${total_revenue:.2f}) < Costs (${total_cost:.2f}). "
                    f"Urgent: Review agent allocation and revenue generation strategies."
                )
            elif overall_roi > 200:
                recommendations.append(
                    f"EXCEPTIONAL ROI: System achieving {overall_roi:.1f}% ROI. "
                    f"Consider scaling successful strategies and increasing investment."
                )

        if not recommendations:
            recommendations.append(
                "SYSTEM HEALTHY: No critical issues detected. Continue monitoring performance."
            )

        return recommendations

    def get_patterns(self, pattern_type: str = "all") -> Dict:
        """
        Get identified patterns from historical data

        Args:
            pattern_type: "decisions", "agents", "opportunities", or "all"

        Returns:
            Dictionary of patterns and insights
        """
        patterns = {
            "timestamp": safe_datetime_now().isoformat(),
            "pattern_type": pattern_type
        }

        if pattern_type in ["decisions", "all"]:
            patterns['decision_patterns'] = self._get_decision_patterns()

        if pattern_type in ["agents", "all"]:
            patterns['agent_patterns'] = self._get_agent_patterns()

        if pattern_type in ["opportunities", "all"]:
            patterns['opportunity_patterns'] = self._get_opportunity_patterns()

        return patterns

    def _get_decision_patterns(self) -> Dict:
        """Extract decision-making patterns"""
        cursor = self.conn.cursor()

        # Most common decision types
        cursor.execute("""
            SELECT decision_type, COUNT(*) as count
            FROM decisions
            GROUP BY decision_type
            ORDER BY count DESC
            LIMIT 5
        """)

        patterns = {
            "most_common_types": [
                {'type': row['decision_type'], 'count': row['count']}
                for row in cursor.fetchall()
            ]
        }

        # Average cost by decision type
        cursor.execute("""
            SELECT decision_type,
                   AVG(cost) as avg_cost,
                   COUNT(*) as count
            FROM decisions
            WHERE cost > 0
            GROUP BY decision_type
            ORDER BY avg_cost DESC
        """)

        patterns['cost_by_type'] = [
            {
                'type': row['decision_type'],
                'avg_cost': float(row['avg_cost']),
                'count': row['count']
            }
            for row in cursor.fetchall()
        ]

        return patterns

    def _get_agent_patterns(self) -> Dict:
        """Extract agent performance patterns"""
        cursor = self.conn.cursor()

        # ROI by department
        cursor.execute("""
            SELECT department,
                   AVG(roi) as avg_roi,
                   COUNT(*) as agent_count
            FROM agents
            WHERE status = 'active'
            GROUP BY department
            ORDER BY avg_roi DESC
        """)

        patterns = {
            "roi_by_department": [
                {
                    'department': row['department'] or 'unassigned',
                    'avg_roi': float(row['avg_roi'] or 0.0),
                    'agent_count': row['agent_count']
                }
                for row in cursor.fetchall()
            ]
        }

        # Cost efficiency by agent type
        cursor.execute("""
            SELECT type,
                   AVG(total_cost) as avg_cost,
                   AVG(revenue_generated) as avg_revenue,
                   COUNT(*) as count
            FROM agents
            WHERE status = 'active'
            GROUP BY type
            ORDER BY avg_revenue DESC
        """)

        patterns['efficiency_by_type'] = [
            {
                'type': row['type'],
                'avg_cost': float(row['avg_cost'] or 0.0),
                'avg_revenue': float(row['avg_revenue'] or 0.0),
                'count': row['count']
            }
            for row in cursor.fetchall()
        ]

        return patterns

    def _get_opportunity_patterns(self) -> Dict:
        """Extract opportunity patterns"""
        cursor = self.conn.cursor()

        # Success rate by source
        cursor.execute("""
            SELECT source,
                   COUNT(*) as total,
                   SUM(CASE WHEN status = 'pursued' THEN 1 ELSE 0 END) as pursued,
                   AVG(confidence_score) as avg_confidence
            FROM opportunities
            GROUP BY source
            ORDER BY total DESC
        """)

        patterns = {
            "by_source": [
                {
                    'source': row['source'],
                    'total': row['total'],
                    'pursued': row['pursued'],
                    'pursuit_rate': (row['pursued'] / row['total'] * 100) if row['total'] > 0 else 0.0,
                    'avg_confidence': float(row['avg_confidence'] or 0.0)
                }
                for row in cursor.fetchall()
            ]
        }

        # Average potential revenue by status
        cursor.execute("""
            SELECT status,
                   COUNT(*) as count,
                   AVG(potential_revenue) as avg_revenue
            FROM opportunities
            GROUP BY status
            ORDER BY avg_revenue DESC
        """)

        patterns['revenue_by_status'] = [
            {
                'status': row['status'],
                'count': row['count'],
                'avg_revenue': float(row['avg_revenue'] or 0.0)
            }
            for row in cursor.fetchall()
        ]

        return patterns

    # === UTILITY METHODS ===

    def sync_from_sqlite(self, days: int = 7) -> Dict[str, int]:
        """
        Sync recent data from SQLite to ChromaDB
        Useful for backfilling or updates

        Args:
            days: How many days back to sync

        Returns:
            Dictionary with counts of synced items
        """
        print(f"[Learning] Syncing data from last {days} days...")

        since = (safe_datetime_now() - timedelta(days=days)).isoformat()
        cursor = self.conn.cursor()

        counts = {
            'decisions': 0,
            'agents': 0,
            'opportunities': 0
        }

        # Sync decisions
        cursor.execute("""
            SELECT id FROM decisions WHERE timestamp >= ?
        """, (since,))

        for row in cursor.fetchall():
            if self.store_decision(row['id'], "", None, None):
                counts['decisions'] += 1

        # Sync agents
        cursor.execute("""
            SELECT id FROM agents WHERE deployed_at >= ?
        """, (since,))

        for row in cursor.fetchall():
            agent = self.conn.cursor().execute(
                "SELECT * FROM agents WHERE id = ?", (row['id'],)
            ).fetchone()
            agent_dict = dict(agent)

            config = json.loads(agent_dict['config']) if agent_dict.get('config') else {}
            performance = {
                'tokens_used': agent_dict.get('tokens_used', 0),
                'cost': agent_dict.get('total_cost', 0.0),
                'revenue': agent_dict.get('revenue_generated', 0.0),
                'roi': agent_dict.get('roi', 0.0)
            }

            if self.store_agent_deployment(row['id'], config, performance):
                counts['agents'] += 1

        # Sync opportunities
        cursor.execute("""
            SELECT id, source FROM opportunities WHERE timestamp >= ?
        """, (since,))

        for row in cursor.fetchall():
            if self.store_opportunity(row['id'], row['source'], {}, None):
                counts['opportunities'] += 1

        print(f"[Learning] Sync complete: {counts}")
        return counts

    def get_stats(self) -> Dict:
        """Get learning system statistics"""
        return {
            "collections": {
                "decisions": self.decisions_collection.count(),
                "agents": self.agents_collection.count(),
                "opportunities": self.opportunities_collection.count()
            },
            "encoder_model": "all-MiniLM-L6-v2",
            "chroma_path": self.chroma_path,
            "db_path": self.db_path
        }

    def close(self):
        """Close connections"""
        if self.conn:
            self.conn.close()
        print("[Learning] Learning system closed")


# === SINGLETON INSTANCE ===

_learning_instance = None

def get_learning() -> NovaLearning:
    """Get or create learning instance"""
    global _learning_instance
    if _learning_instance is None:
        _learning_instance = NovaLearning()
    return _learning_instance


# === CONVENIENCE FUNCTIONS ===

def store_decision(decision_id: int, outcome: str = None, metrics: Dict = None) -> bool:
    """Convenience function to store a decision"""
    learning = get_learning()
    return learning.store_decision(decision_id, "", outcome, metrics)


def get_decision_context(question: str, decision_type: str = None) -> str:
    """
    Get context from similar past decisions for board agents
    This is the key integration point for board decision-making
    """
    learning = get_learning()
    return learning.get_similar_decisions(question, decision_type, limit=3)


def weekly_analysis() -> Dict:
    """Run weekly analysis and get recommendations"""
    learning = get_learning()
    return learning.analyze_weekly()


def get_recommendations() -> List[str]:
    """Get current recommendations based on patterns"""
    analysis = weekly_analysis()
    return analysis.get('recommendations', [])
