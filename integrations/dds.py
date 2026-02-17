"""
NovaOS V2 - DDS Integration
Complete integration with existing DDS (Data-Driven Sales) prospecting system

Integrates all 4 DDS agents:
1. Prospecting Agent - Google Maps scraping, website analysis, lead qualification
2. Scoring Agent - Lead scoring based on marketing gaps
3. Research Agent - Competitor analysis, market research
4. Outreach Agent - Email campaigns, tracking, follow-ups

Sales Department owns this integration.
"""

import sys
import os
import json
import sqlite3
from typing import Dict, Any, List, Optional
from pathlib import Path
from datetime import datetime, timedelta
import logging

from core.memory import get_memory
from config.settings import DDS_PATH, MODELS


def safe_datetime_now():
    """Get current datetime with fallback for timestamp overflow"""
    try:
        return datetime.now()
    except (OSError, OverflowError, ValueError):
        from datetime import datetime as dt
        return dt(2025, 1, 1, 0, 0, 0)


logger = logging.getLogger(__name__)


class DDSIntegration:
    """Complete integration with existing DDS prospecting system"""

    def __init__(self):
        self.dds_path = DDS_PATH
        self.memory = get_memory()
        self.dds_available = False
        self.dds_db_path = None

        # Cost thresholds
        self.cost_per_lead_threshold = 20.00  # Alert if cost per lead exceeds $20
        self.qualification_rate_threshold = 0.30  # Alert if < 30% qualification rate
        self.outreach_success_threshold = 0.05  # Alert if < 5% response rate

        # Check DDS availability
        self._check_dds_availability()

    def _check_dds_availability(self):
        """Check if DDS system is available and accessible"""
        if not self.dds_path.exists():
            logger.warning(f"DDS system not found at {self.dds_path}")
            return

        # Check for key DDS files
        required_files = [
            'src/main.py',
            'src/lead_scorer.py',
            'src/outreach_agent.py',
            'src/campaign_manager.py'
        ]

        for file in required_files:
            file_path = self.dds_path / file
            if not file_path.exists():
                logger.warning(f"Missing DDS file: {file}")
                return

        # Check for DDS databases
        ops_db = self.dds_path / 'ops.db'
        campaigns_db = self.dds_path / 'campaigns.db'

        if ops_db.exists():
            self.dds_db_path = str(ops_db)
        elif campaigns_db.exists():
            self.dds_db_path = str(campaigns_db)

        # Add DDS to Python path
        sys.path.insert(0, str(self.dds_path / 'src'))

        self.dds_available = True
        logger.info(f"DDS system available at {self.dds_path}")

    # ==================== CAMPAIGN DEPLOYMENT ====================

    def deploy_campaign(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Deploy a complete DDS prospecting campaign

        Config parameters:
        - vertical: Industry vertical (e.g., "dentists", "lawyers", "contractors")
        - location: Geographic location (e.g., "Austin, TX")
        - prospect_count: Number of prospects to find (default: 50)
        - budget: Maximum budget in dollars (default: 100)
        - campaign_name: Optional custom name
        - sender_name: Name for outreach emails
        - sender_company: Company name for outreach

        Returns:
        - campaign_id: Unique campaign identifier
        - status: Deployment status
        - config: Campaign configuration
        - estimated_costs: Cost breakdown
        """

        # Extract config
        vertical = config.get('vertical', 'default')
        location = config.get('location', 'default')
        count = config.get('prospect_count', 50)
        budget = config.get('budget', 100)
        campaign_name = config.get('campaign_name', f"DDS-{vertical}-{location}-{safe_datetime_now().strftime('%Y%m%d')}")
        sender_name = config.get('sender_name', 'Sales Team')
        sender_company = config.get('sender_company', 'Deep Dive Systems')

        # Check DDS availability
        if not self.dds_available:
            return {
                "status": "error",
                "message": f"DDS system not available at {self.dds_path}",
                "recommendation": "Ensure DDS system is properly installed",
                "setup_instructions": [
                    "1. Clone DDS system to the configured path",
                    "2. Install DDS dependencies: pip install -r requirements.txt",
                    "3. Configure DDS .env file with API keys",
                    "4. Retry deployment"
                ]
            }

        # Generate campaign ID
        campaign_id = f"dds_{vertical}_{location}_{safe_datetime_now().strftime('%Y%m%d_%H%M%S')}".lower().replace(' ', '_')

        # Estimate costs
        estimated_costs = self._estimate_campaign_costs(count, vertical)

        # Check budget
        if estimated_costs['total'] > budget:
            return {
                "status": "error",
                "message": "Estimated costs exceed budget",
                "estimated_costs": estimated_costs,
                "budget": budget,
                "recommendation": f"Increase budget to ${estimated_costs['total']:.2f} or reduce prospect count"
            }

        # Register agent in NovaOS
        agent_config = {
            'vertical': vertical,
            'location': location,
            'prospect_count': count,
            'budget': budget,
            'campaign_name': campaign_name,
            'sender_name': sender_name,
            'sender_company': sender_company,
            'estimated_costs': estimated_costs,
            'dds_path': str(self.dds_path)
        }

        self.memory.register_agent(
            agent_id=campaign_id,
            name=campaign_name,
            agent_type='dds_campaign',
            department='sales',
            token_budget=estimated_costs.get('anthropic_tokens', 50000),
            config=agent_config
        )

        logger.info(f"Deployed DDS campaign: {campaign_id}")

        return {
            "status": "deployed",
            "campaign_id": campaign_id,
            "campaign_name": campaign_name,
            "config": {
                "vertical": vertical,
                "location": location,
                "prospect_count": count,
                "budget": budget
            },
            "estimated_costs": estimated_costs,
            "next_steps": [
                f"1. Run prospecting: cd {self.dds_path} && python src/main.py --campaign {campaign_name}",
                f"2. Monitor via: novaos.get_campaign_status('{campaign_id}')",
                "3. Start outreach: python src/outreach_agent.py --campaign {campaign_name}",
                "4. Track results in NovaOS dashboard"
            ],
            "dds_integration": {
                "prospecting_agent": "Ready",
                "scoring_agent": "Ready",
                "research_agent": "Ready",
                "outreach_agent": "Ready"
            }
        }

    def start_campaign(self, campaign_id: str) -> Dict[str, Any]:
        """Start a deployed campaign"""
        agent = self.memory.get_agent(campaign_id)

        if not agent:
            return {"status": "error", "message": "Campaign not found"}

        self.memory.update_agent_status(campaign_id, 'active')

        return {
            "status": "started",
            "campaign_id": campaign_id,
            "message": "Campaign activated. Monitor progress with get_campaign_status()"
        }

    def pause_campaign(self, campaign_id: str) -> Dict[str, Any]:
        """Pause an active campaign"""
        agent = self.memory.get_agent(campaign_id)

        if not agent:
            return {"status": "error", "message": "Campaign not found"}

        self.memory.update_agent_status(campaign_id, 'paused')

        return {
            "status": "paused",
            "campaign_id": campaign_id,
            "message": "Campaign paused. Resume with start_campaign()"
        }

    def stop_campaign(self, campaign_id: str) -> Dict[str, Any]:
        """Stop a campaign permanently"""
        agent = self.memory.get_agent(campaign_id)

        if not agent:
            return {"status": "error", "message": "Campaign not found"}

        self.memory.update_agent_status(campaign_id, 'stopped')

        # Generate final report
        final_report = self.get_campaign_status(campaign_id)

        return {
            "status": "stopped",
            "campaign_id": campaign_id,
            "message": "Campaign stopped",
            "final_report": final_report
        }

    # ==================== COST TRACKING ====================

    def log_dds_costs(self, campaign_id: str, costs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Log DDS API costs to NovaOS cost tracking

        Costs should include:
        - operation: Type of operation (prospecting, scoring, outreach, etc.)
        - provider: API provider (anthropic, outscraper, hunter_io, etc.)
        - cost: Cost in dollars
        - details: Additional cost details
        """

        operation = costs.get('operation', 'unknown')
        provider = costs.get('provider', 'unknown')
        cost = costs.get('cost', 0.0)
        details = costs.get('details', {})

        # Determine model based on provider
        if provider == 'anthropic':
            model = details.get('model', MODELS['sonnet']['id'])
            input_tokens = details.get('input_tokens', 0)
            output_tokens = details.get('output_tokens', 0)
        else:
            model = provider
            input_tokens = 0
            output_tokens = 0

        # Log to costs table
        cost_id = self.memory.log_api_cost(
            model=model,
            operation=f"dds_{operation}",
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            cost=cost,
            agent_id=campaign_id,
            agent_name=self.memory.get_agent(campaign_id)['name'] if self.memory.get_agent(campaign_id) else None,
            department='sales',
            request_data=details
        )

        # Check cost threshold
        agent = self.memory.get_agent(campaign_id)
        if agent:
            total_cost = agent.get('total_cost', 0)
            config = json.loads(agent.get('config', '{}'))
            budget = config.get('budget', 100)

            if total_cost > budget:
                logger.warning(f"Campaign {campaign_id} exceeded budget: ${total_cost:.2f} / ${budget:.2f}")

        return {
            "status": "logged",
            "cost_id": cost_id,
            "campaign_id": campaign_id,
            "cost": cost,
            "operation": operation,
            "provider": provider
        }

    def log_dds_results(self, campaign_id: str, results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Log DDS campaign results

        Results should include:
        - stage: Campaign stage (prospecting, scoring, outreach)
        - leads_found: Number of leads found
        - leads_qualified: Number of qualified leads
        - emails_sent: Number of emails sent
        - emails_opened: Number of emails opened
        - emails_replied: Number of replies
        - revenue: Revenue generated (if any)
        """

        stage = results.get('stage', 'unknown')
        leads_found = results.get('leads_found', 0)
        leads_qualified = results.get('leads_qualified', 0)
        emails_sent = results.get('emails_sent', 0)
        emails_opened = results.get('emails_opened', 0)
        emails_replied = results.get('emails_replied', 0)
        revenue = results.get('revenue', 0.0)

        # Log revenue if any
        if revenue > 0:
            self.memory.log_revenue(
                source="dds_campaign",
                amount=revenue,
                description=f"DDS campaign revenue: {campaign_id}",
                agent_id=campaign_id,
                department='sales'
            )

            self.memory.update_agent_metrics(
                agent_id=campaign_id,
                revenue=revenue
            )

        # Store results in system metrics
        self.memory.log_metric(
            metric_name=f"dds_campaign_{stage}",
            metric_value=leads_found,
            metadata={
                'campaign_id': campaign_id,
                'stage': stage,
                'leads_found': leads_found,
                'leads_qualified': leads_qualified,
                'emails_sent': emails_sent,
                'emails_opened': emails_opened,
                'emails_replied': emails_replied,
                'revenue': revenue
            }
        )

        return {
            "status": "logged",
            "campaign_id": campaign_id,
            "stage": stage,
            "results": results
        }

    # ==================== PERFORMANCE METRICS ====================

    def calculate_lead_metrics(self, campaign_id: str) -> Dict[str, Any]:
        """
        Calculate comprehensive lead metrics for a campaign

        Returns:
        - leads_generated: Total leads found
        - leads_qualified: Number of qualified leads
        - qualification_rate: % of leads that qualified
        - cost_per_lead: Cost to acquire each lead
        - cost_per_qualified_lead: Cost per qualified lead
        - emails_sent: Total emails sent
        - open_rate: Email open rate
        - reply_rate: Email reply rate
        - outreach_success_rate: % of prospects engaged
        - revenue_generated: Revenue from campaign
        - roi: Return on investment %
        """

        agent = self.memory.get_agent(campaign_id)

        if not agent:
            return {"status": "error", "message": "Campaign not found"}

        # Get campaign metrics from stored data
        metrics = self.memory.get_metrics(metric_name=f"dds_campaign_*", hours=720)  # Last 30 days
        campaign_metrics = [m for m in metrics if campaign_id in m.get('metadata', '{}')]

        # Aggregate results
        leads_found = 0
        leads_qualified = 0
        emails_sent = 0
        emails_opened = 0
        emails_replied = 0

        for metric in campaign_metrics:
            metadata = json.loads(metric.get('metadata', '{}'))
            if metadata.get('campaign_id') == campaign_id:
                leads_found += metadata.get('leads_found', 0)
                leads_qualified += metadata.get('leads_qualified', 0)
                emails_sent += metadata.get('emails_sent', 0)
                emails_opened += metadata.get('emails_opened', 0)
                emails_replied += metadata.get('emails_replied', 0)

        # Get cost and revenue
        total_cost = agent.get('total_cost', 0)
        revenue = agent.get('revenue_generated', 0)

        # Calculate metrics
        qualification_rate = (leads_qualified / leads_found * 100) if leads_found > 0 else 0
        cost_per_lead = (total_cost / leads_found) if leads_found > 0 else 0
        cost_per_qualified_lead = (total_cost / leads_qualified) if leads_qualified > 0 else 0
        open_rate = (emails_opened / emails_sent * 100) if emails_sent > 0 else 0
        reply_rate = (emails_replied / emails_sent * 100) if emails_sent > 0 else 0
        outreach_success_rate = reply_rate
        roi = ((revenue - total_cost) / total_cost * 100) if total_cost > 0 else 0

        return {
            "campaign_id": campaign_id,
            "campaign_name": agent['name'],
            "leads_generated": leads_found,
            "leads_qualified": leads_qualified,
            "qualification_rate": round(qualification_rate, 2),
            "cost_per_lead": round(cost_per_lead, 2),
            "cost_per_qualified_lead": round(cost_per_qualified_lead, 2),
            "emails_sent": emails_sent,
            "emails_opened": emails_opened,
            "emails_replied": emails_replied,
            "open_rate": round(open_rate, 2),
            "reply_rate": round(reply_rate, 2),
            "outreach_success_rate": round(outreach_success_rate, 2),
            "total_cost": round(total_cost, 2),
            "revenue_generated": round(revenue, 2),
            "roi": round(roi, 2),
            "status": agent['status']
        }

    def get_campaign_status(self, campaign_id: str) -> Dict[str, Any]:
        """Get detailed status of a DDS campaign"""

        agent = self.memory.get_agent(campaign_id)

        if not agent:
            return {"status": "error", "message": "Campaign not found"}

        # Get lead metrics
        metrics = self.calculate_lead_metrics(campaign_id)

        # Get config
        config = json.loads(agent.get('config', '{}'))

        # Check DDS database for additional details
        dds_details = self._get_dds_database_stats(campaign_id)

        return {
            "campaign_id": campaign_id,
            "campaign_name": agent['name'],
            "status": agent['status'],
            "deployed_at": agent['deployed_at'],
            "last_active": agent.get('last_active'),
            "config": {
                "vertical": config.get('vertical'),
                "location": config.get('location'),
                "prospect_count": config.get('prospect_count'),
                "budget": config.get('budget')
            },
            "metrics": metrics,
            "dds_details": dds_details,
            "performance": {
                "cost_efficiency": "Good" if metrics['cost_per_lead'] < self.cost_per_lead_threshold else "Poor",
                "qualification_quality": "Good" if metrics['qualification_rate'] > self.qualification_rate_threshold * 100 else "Poor",
                "outreach_effectiveness": "Good" if metrics['outreach_success_rate'] > self.outreach_success_threshold * 100 else "Poor"
            }
        }

    def get_all_campaigns_report(self) -> Dict[str, Any]:
        """Generate comprehensive report for all DDS campaigns"""

        # Get all DDS agents
        agents = self.memory.get_all_agents(department="sales")
        dds_campaigns = [a for a in agents if a['type'] == 'dds_campaign']

        # Aggregate metrics
        total_campaigns = len(dds_campaigns)
        active_campaigns = len([a for a in dds_campaigns if a['status'] == 'active'])
        total_cost = sum(a.get('total_cost', 0) for a in dds_campaigns)
        total_revenue = sum(a.get('revenue_generated', 0) for a in dds_campaigns)
        total_roi = ((total_revenue - total_cost) / total_cost * 100) if total_cost > 0 else 0

        # Get individual campaign summaries
        campaign_summaries = []
        for agent in dds_campaigns:
            metrics = self.calculate_lead_metrics(agent['id'])
            campaign_summaries.append({
                "campaign_id": agent['id'],
                "campaign_name": agent['name'],
                "status": agent['status'],
                "leads_generated": metrics['leads_generated'],
                "qualified_leads": metrics['leads_qualified'],
                "cost": metrics['total_cost'],
                "revenue": metrics['revenue_generated'],
                "roi": metrics['roi']
            })

        return {
            "summary": {
                "total_campaigns": total_campaigns,
                "active_campaigns": active_campaigns,
                "total_cost": round(total_cost, 2),
                "total_revenue": round(total_revenue, 2),
                "total_roi": round(total_roi, 2),
                "profit": round(total_revenue - total_cost, 2)
            },
            "campaigns": campaign_summaries,
            "generated_at": safe_datetime_now().isoformat()
        }

    # ==================== AUTO-OPTIMIZATION ====================

    def optimize_campaign(self, campaign_id: str) -> Dict[str, Any]:
        """
        Analyze campaign performance and generate optimization recommendations

        Analyzes:
        - Cost per lead vs threshold
        - Qualification rate
        - Outreach success rate
        - ROI

        Returns actionable recommendations
        """

        metrics = self.calculate_lead_metrics(campaign_id)

        if 'error' in metrics.get('status', ''):
            return metrics

        recommendations = []
        actions = []

        # Check cost per lead
        if metrics['cost_per_lead'] > self.cost_per_lead_threshold:
            recommendations.append({
                "issue": "High cost per lead",
                "current_value": f"${metrics['cost_per_lead']:.2f}",
                "threshold": f"${self.cost_per_lead_threshold:.2f}",
                "severity": "high",
                "recommendation": "Reduce prospect count, refine targeting criteria, or optimize search queries",
                "expected_impact": "Reduce cost per lead by 30-50%"
            })
            actions.append("REDUCE_COSTS")

        # Check qualification rate
        if metrics['qualification_rate'] < self.qualification_rate_threshold * 100:
            recommendations.append({
                "issue": "Low qualification rate",
                "current_value": f"{metrics['qualification_rate']:.1f}%",
                "threshold": f"{self.qualification_rate_threshold * 100:.1f}%",
                "severity": "medium",
                "recommendation": "Refine lead scoring criteria, adjust qualification thresholds, improve targeting",
                "expected_impact": "Increase qualified leads by 40-60%"
            })
            actions.append("REFINE_SCORING")

        # Check outreach success rate
        if metrics['outreach_success_rate'] < self.outreach_success_threshold * 100:
            recommendations.append({
                "issue": "Low outreach success rate",
                "current_value": f"{metrics['outreach_success_rate']:.1f}%",
                "threshold": f"{self.outreach_success_threshold * 100:.1f}%",
                "severity": "high",
                "recommendation": "Improve email templates, personalize outreach, A/B test subject lines, adjust timing",
                "expected_impact": "Increase response rate by 100-200%"
            })
            actions.append("IMPROVE_OUTREACH")

        # Check ROI
        if metrics['roi'] < 0:
            recommendations.append({
                "issue": "Negative ROI",
                "current_value": f"{metrics['roi']:.1f}%",
                "threshold": "0%",
                "severity": "critical",
                "recommendation": "PAUSE CAMPAIGN - Review entire strategy, costs are exceeding revenue",
                "expected_impact": "Stop losses immediately"
            })
            actions.append("PAUSE_CAMPAIGN")
        elif metrics['roi'] < 100:
            recommendations.append({
                "issue": "Low ROI",
                "current_value": f"{metrics['roi']:.1f}%",
                "threshold": "100%",
                "severity": "medium",
                "recommendation": "Optimize conversion funnel, improve closing process, increase pricing",
                "expected_impact": "Double revenue per lead"
            })
            actions.append("IMPROVE_CONVERSION")

        # High performers - scale up
        if metrics['roi'] > 300 and metrics['cost_per_lead'] < self.cost_per_lead_threshold:
            recommendations.append({
                "issue": "High performing campaign",
                "current_value": f"ROI: {metrics['roi']:.1f}%, CPL: ${metrics['cost_per_lead']:.2f}",
                "threshold": "N/A",
                "severity": "opportunity",
                "recommendation": "SCALE UP - Increase prospect count, expand to similar locations, replicate strategy",
                "expected_impact": "Multiply profits 2-3x"
            })
            actions.append("SCALE_UP")

        # Generate optimization report
        report = {
            "campaign_id": campaign_id,
            "campaign_name": metrics['campaign_name'],
            "analysis_date": safe_datetime_now().isoformat(),
            "current_performance": {
                "cost_per_lead": f"${metrics['cost_per_lead']:.2f}",
                "qualification_rate": f"{metrics['qualification_rate']:.1f}%",
                "outreach_success_rate": f"{metrics['outreach_success_rate']:.1f}%",
                "roi": f"{metrics['roi']:.1f}%"
            },
            "recommendations": recommendations,
            "suggested_actions": actions,
            "priority": "CRITICAL" if "PAUSE_CAMPAIGN" in actions else "HIGH" if len(recommendations) > 2 else "MEDIUM" if len(recommendations) > 0 else "LOW"
        }

        # Auto-execute critical actions
        if "PAUSE_CAMPAIGN" in actions:
            self.pause_campaign(campaign_id)
            report['auto_action_taken'] = "Campaign automatically paused due to negative ROI"

        return report

    def optimize_all_campaigns(self) -> Dict[str, Any]:
        """Run optimization analysis on all active DDS campaigns"""

        agents = self.memory.get_all_agents(department="sales")
        dds_campaigns = [a for a in agents if a['type'] == 'dds_campaign' and a['status'] == 'active']

        optimization_results = []

        for agent in dds_campaigns:
            result = self.optimize_campaign(agent['id'])
            optimization_results.append(result)

        # Summary
        critical_campaigns = [r for r in optimization_results if r['priority'] == 'CRITICAL']
        high_priority = [r for r in optimization_results if r['priority'] == 'HIGH']

        return {
            "total_campaigns_analyzed": len(dds_campaigns),
            "critical_issues": len(critical_campaigns),
            "high_priority_issues": len(high_priority),
            "campaigns_needing_attention": critical_campaigns + high_priority,
            "all_results": optimization_results,
            "generated_at": safe_datetime_now().isoformat()
        }

    # ==================== REPORTING ====================

    def generate_campaign_report(self, campaign_id: str, report_type: str = 'full') -> Dict[str, Any]:
        """
        Generate comprehensive campaign report

        Report types:
        - 'full': Complete performance report
        - 'costs': Cost breakdown only
        - 'leads': Lead metrics only
        - 'outreach': Outreach performance only
        """

        status = self.get_campaign_status(campaign_id)

        if 'error' in status.get('status', ''):
            return status

        if report_type == 'costs':
            return self._generate_cost_report(campaign_id, status)
        elif report_type == 'leads':
            return self._generate_lead_report(campaign_id, status)
        elif report_type == 'outreach':
            return self._generate_outreach_report(campaign_id, status)
        else:
            return self._generate_full_report(campaign_id, status)

    # ==================== HELPER METHODS ====================

    def _estimate_campaign_costs(self, prospect_count: int, vertical: str) -> Dict[str, float]:
        """Estimate costs for a DDS campaign"""

        # Google Maps scraping (Outscraper)
        scraping_cost = (prospect_count / 100) * 0.50  # $0.50 per 100 searches

        # Website analysis (Anthropic Claude)
        # ~500 tokens per analysis
        website_analysis_tokens = prospect_count * 500
        website_analysis_cost = (website_analysis_tokens / 1_000_000) * MODELS['haiku']['input_cost']

        # Lead scoring (Anthropic Claude)
        scoring_tokens = prospect_count * 300
        scoring_cost = (scoring_tokens / 1_000_000) * MODELS['haiku']['input_cost']

        # Email finding (Hunter.io)
        email_finding_cost = (prospect_count / 100) * 10.00  # ~$10 per 100 emails

        # Outreach emails (SendGrid/SMTP)
        # Assuming 3 emails per prospect (initial + 2 follow-ups)
        outreach_cost = (prospect_count * 3 * 0.001)  # $0.001 per email

        total = scraping_cost + website_analysis_cost + scoring_cost + email_finding_cost + outreach_cost

        return {
            "scraping": round(scraping_cost, 2),
            "website_analysis": round(website_analysis_cost, 2),
            "lead_scoring": round(scoring_cost, 2),
            "email_finding": round(email_finding_cost, 2),
            "outreach": round(outreach_cost, 2),
            "total": round(total, 2),
            "anthropic_tokens": website_analysis_tokens + scoring_tokens,
            "cost_per_prospect": round(total / prospect_count, 2)
        }

    def _get_dds_database_stats(self, campaign_id: str) -> Dict[str, Any]:
        """Get additional stats from DDS database if available"""

        if not self.dds_db_path:
            return {"available": False}

        try:
            conn = sqlite3.connect(self.dds_db_path)
            cursor = conn.cursor()

            # Check if campaigns table exists
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='campaigns'")
            if not cursor.fetchone():
                conn.close()
                return {"available": False}

            # Get campaign stats
            cursor.execute("""
                SELECT total_prospects, emails_sent, emails_opened,
                       emails_clicked, emails_replied
                FROM campaigns
                WHERE campaign_name LIKE ?
            """, (f"%{campaign_id}%",))

            row = cursor.fetchone()
            conn.close()

            if row:
                return {
                    "available": True,
                    "total_prospects": row[0],
                    "emails_sent": row[1],
                    "emails_opened": row[2],
                    "emails_clicked": row[3],
                    "emails_replied": row[4]
                }

            return {"available": False}

        except Exception as e:
            logger.error(f"Error reading DDS database: {e}")
            return {"available": False, "error": str(e)}

    def _generate_cost_report(self, campaign_id: str, status: Dict) -> Dict[str, Any]:
        """Generate cost-focused report"""
        metrics = status['metrics']

        return {
            "report_type": "costs",
            "campaign_id": campaign_id,
            "campaign_name": status['campaign_name'],
            "total_cost": metrics['total_cost'],
            "cost_per_lead": metrics['cost_per_lead'],
            "cost_per_qualified_lead": metrics['cost_per_qualified_lead'],
            "budget_used": f"{(metrics['total_cost'] / status['config']['budget']) * 100:.1f}%",
            "cost_breakdown": {
                "prospecting": "View detailed logs",
                "scoring": "View detailed logs",
                "outreach": "View detailed logs"
            },
            "cost_efficiency": status['performance']['cost_efficiency']
        }

    def _generate_lead_report(self, campaign_id: str, status: Dict) -> Dict[str, Any]:
        """Generate lead-focused report"""
        metrics = status['metrics']

        return {
            "report_type": "leads",
            "campaign_id": campaign_id,
            "campaign_name": status['campaign_name'],
            "leads_generated": metrics['leads_generated'],
            "leads_qualified": metrics['leads_qualified'],
            "qualification_rate": f"{metrics['qualification_rate']:.1f}%",
            "quality_assessment": status['performance']['qualification_quality'],
            "cost_per_lead": f"${metrics['cost_per_lead']:.2f}",
            "cost_per_qualified_lead": f"${metrics['cost_per_qualified_lead']:.2f}"
        }

    def _generate_outreach_report(self, campaign_id: str, status: Dict) -> Dict[str, Any]:
        """Generate outreach-focused report"""
        metrics = status['metrics']

        return {
            "report_type": "outreach",
            "campaign_id": campaign_id,
            "campaign_name": status['campaign_name'],
            "emails_sent": metrics['emails_sent'],
            "emails_opened": metrics['emails_opened'],
            "emails_replied": metrics['emails_replied'],
            "open_rate": f"{metrics['open_rate']:.1f}%",
            "reply_rate": f"{metrics['reply_rate']:.1f}%",
            "effectiveness": status['performance']['outreach_effectiveness']
        }

    def _generate_full_report(self, campaign_id: str, status: Dict) -> Dict[str, Any]:
        """Generate comprehensive report"""
        return {
            "report_type": "full",
            "campaign_id": campaign_id,
            "campaign_name": status['campaign_name'],
            "status": status['status'],
            "deployed_at": status['deployed_at'],
            "config": status['config'],
            "performance": {
                "leads": {
                    "generated": status['metrics']['leads_generated'],
                    "qualified": status['metrics']['leads_qualified'],
                    "qualification_rate": f"{status['metrics']['qualification_rate']:.1f}%"
                },
                "outreach": {
                    "emails_sent": status['metrics']['emails_sent'],
                    "open_rate": f"{status['metrics']['open_rate']:.1f}%",
                    "reply_rate": f"{status['metrics']['reply_rate']:.1f}%"
                },
                "financial": {
                    "total_cost": f"${status['metrics']['total_cost']:.2f}",
                    "revenue": f"${status['metrics']['revenue_generated']:.2f}",
                    "roi": f"{status['metrics']['roi']:.1f}%",
                    "cost_per_lead": f"${status['metrics']['cost_per_lead']:.2f}"
                }
            },
            "performance_ratings": status['performance'],
            "generated_at": safe_datetime_now().isoformat()
        }


# Singleton
_dds_instance = None

def get_dds() -> DDSIntegration:
    """Get or create DDS integration instance"""
    global _dds_instance
    if _dds_instance is None:
        _dds_instance = DDSIntegration()
    return _dds_instance
