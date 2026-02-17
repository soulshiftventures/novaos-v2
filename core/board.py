"""
NovaOS V2 Board Agents
Strategic C-Suite AI Agents
"""

import anthropic
from typing import Dict, List, Optional, Any
from datetime import datetime
import json

from core.memory import get_memory
from config.settings import (
    ANTHROPIC_API_KEY, MODELS, DEFAULT_MODELS,
    BOARD_AGENT_BUDGETS, MCP_CONFIG
)


class BoardAgent:
    """Base class for board-level strategic agents"""

    def __init__(self, role: str, token_budget: int, model: str = None):
        self.role = role
        self.token_budget = token_budget
        self.model = model or DEFAULT_MODELS["board_agents"]
        self.client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
        self.memory = get_memory()
        self.agent_id = f"board_{role.lower()}"

        # Register agent
        self.memory.register_agent(
            agent_id=self.agent_id,
            name=f"{role} Agent",
            agent_type="board",
            department="board",
            token_budget=token_budget
        )

    def _call_claude(self, system: str, user_prompt: str, max_tokens: int = None) -> Dict[str, Any]:
        """Make Claude API call with cost tracking"""
        if max_tokens is None:
            max_tokens = min(self.token_budget, MODELS[self.model]["max_tokens"])

        try:
            response = self.client.messages.create(
                model=MODELS[self.model]["id"],
                max_tokens=max_tokens,
                system=system,
                messages=[{"role": "user", "content": user_prompt}]
            )

            # Extract usage
            input_tokens = response.usage.input_tokens
            output_tokens = response.usage.output_tokens

            # Calculate cost
            input_cost = (input_tokens / 1_000_000) * MODELS[self.model]["input_cost"]
            output_cost = (output_tokens / 1_000_000) * MODELS[self.model]["output_cost"]
            total_cost = input_cost + output_cost

            # Log cost
            self.memory.log_api_cost(
                model=MODELS[self.model]["id"],
                operation=f"{self.role}_analysis",
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                cost=total_cost,
                agent_id=self.agent_id,
                agent_name=f"{self.role} Agent",
                department="board"
            )

            return {
                "content": response.content[0].text,
                "tokens_used": input_tokens + output_tokens,
                "cost": total_cost
            }

        except Exception as e:
            print(f"Error calling Claude: {e}")
            return {
                "content": f"Error: {str(e)}",
                "tokens_used": 0,
                "cost": 0.0
            }

    def get_context(self) -> str:
        """Get relevant context from memory"""
        # Get recent decisions
        recent_decisions = self.memory.get_recent_decisions(limit=5)

        # Get system metrics
        total_revenue = self.memory.get_total_revenue()
        total_costs = self.memory.get_total_costs()
        roi_data = self.memory.get_roi_by_department()

        context = f"""
CURRENT SYSTEM STATE:
- Total Revenue: ${total_revenue:.2f}
- Total AI Costs: ${total_costs:.2f}
- Net Profit: ${total_revenue - total_costs:.2f}
- ROI: {((total_revenue - total_costs) / total_costs * 100) if total_costs > 0 else 0:.1f}%

RECENT DECISIONS:
"""
        for dec in recent_decisions[:3]:
            context += f"- [{dec['agent']}] {dec['question']}: {dec['decision']}\n"

        context += f"\nDEPARTMENT ROI:\n"
        for dept, data in roi_data.items():
            context += f"- {dept}: Revenue ${data['revenue']:.2f}, Cost ${data['cost']:.2f}, ROI {data['roi']:.1f}%\n"

        return context


class CEOAgent(BoardAgent):
    """CEO Agent - Strategic Decision Maker"""

    def __init__(self):
        super().__init__("CEO", BOARD_AGENT_BUDGETS["ceo"])

    def make_decision(self, opportunity: str, context: Dict = None) -> Dict[str, Any]:
        """Make GO/NO-GO decision on opportunity"""

        # Query learning system for similar past decisions
        try:
            from core.learning import get_decision_context
            learning_context = get_decision_context(opportunity, "opportunity_evaluation")
        except Exception as e:
            print(f"[CEO] Warning: Could not query learning system: {e}")
            learning_context = "No historical context available."

        system_prompt = """You are the CEO of NovaOS, an AI business orchestration platform.

Your role is to make strategic GO/NO-GO decisions on opportunities.

Analyze opportunities through these lenses:
1. Market timing - Is this the right time?
2. Competitive advantage - Do we have a unique edge?
3. Resource allocation - Can we afford this now?
4. Strategic fit - Does this align with our path to $200K/month?
5. Risk/reward - What's the upside vs downside?

CRITICAL: Review similar past decisions and learn from their outcomes. Don't repeat mistakes.

Your decisions must be:
- CLEAR: GO or NO-GO (no maybes)
- BRIEF: 2-3 sentences of reasoning
- STRATEGIC: Focus on 10X aggressive growth
- COST-CONSCIOUS: Consider AI spend efficiency
- INFORMED: Learn from past similar situations

Format your response as:
DECISION: [GO/NO-GO]
REASONING: [Your analysis]
PRIORITY: [HIGH/MEDIUM/LOW]
NEXT_STEPS: [Specific actions if GO]"""

        user_prompt = f"""
OPPORTUNITY: {opportunity}

{learning_context}

{self.get_context()}

ADDITIONAL CONTEXT:
{json.dumps(context, indent=2) if context else 'None'}

Make your decision."""

        result = self._call_claude(system_prompt, user_prompt)

        # Parse decision
        decision_text = result["content"]
        decision = "GO" if "DECISION: GO" in decision_text else "NO-GO"

        # Log decision
        decision_id = self.memory.log_decision(
            agent="CEO",
            decision_type="opportunity_evaluation",
            question=opportunity,
            decision=decision,
            reasoning=decision_text,
            tokens_used=result["tokens_used"],
            cost=result["cost"]
        )

        # Save to MCP if enabled
        if MCP_CONFIG["enabled"] and MCP_CONFIG["auto_save_decisions"]:
            try:
                from mcp__novaos_memory__save_memory import save_memory
                save_memory(
                    doc_id=f"ceo-decision-{decision_id}",
                    content=f"# CEO Decision\n\n**Opportunity:** {opportunity}\n\n**Decision:** {decision}\n\n**Analysis:**\n{decision_text}",
                    tags=["ceo", "decision", "board"]
                )
            except:
                pass  # MCP not available

        return {
            "decision": decision,
            "reasoning": decision_text,
            "tokens_used": result["tokens_used"],
            "cost": result["cost"],
            "decision_id": decision_id
        }


class CFOAgent(BoardAgent):
    """CFO Agent - Financial Manager & Cost Optimizer"""

    def __init__(self):
        super().__init__("CFO", BOARD_AGENT_BUDGETS["cfo"])

    def analyze_finances(self, period: str = "month") -> Dict[str, Any]:
        """Analyze financial health and AI cost efficiency"""

        from config.financial_targets import get_current_target, is_on_track, calculate_roi
        from datetime import datetime

        # Get current financial data
        total_revenue = self.memory.get_total_revenue()
        total_costs = self.memory.get_total_costs()
        cost_breakdown = self.memory.get_cost_breakdown(period)
        roi_by_dept = self.memory.get_roi_by_department()

        # Get targets
        targets = get_current_target()
        month = datetime.now().month
        day = datetime.now().day
        tracking = is_on_track(total_revenue, month, day)

        # Query learning system for patterns
        try:
            from core.learning import get_learning
            learning = get_learning()
            patterns = learning.get_patterns("agents")
            learning_insights = f"\nHISTORICAL PATTERNS:\n"

            if patterns.get('agent_patterns', {}).get('roi_by_department'):
                learning_insights += "\nHistorical ROI by Department:\n"
                for dept in patterns['agent_patterns']['roi_by_department'][:5]:
                    learning_insights += f"  {dept['department']}: {dept['avg_roi']:.1f}% avg ROI\n"

            if patterns.get('agent_patterns', {}).get('efficiency_by_type'):
                learning_insights += "\nAgent Efficiency Patterns:\n"
                for item in patterns['agent_patterns']['efficiency_by_type'][:3]:
                    roi = ((item['avg_revenue'] - item['avg_cost']) / item['avg_cost'] * 100) if item['avg_cost'] > 0 else 0
                    learning_insights += f"  {item['type']}: {roi:.1f}% avg ROI\n"
        except Exception as e:
            print(f"[CFO] Warning: Could not query learning system: {e}")
            learning_insights = ""

        system_prompt = """You are the CFO of NovaOS, responsible for financial health and AI cost optimization.

Your priorities:
1. Keep AI costs under 5% of revenue (CRITICAL)
2. Track ROI for every department and agent
3. Identify cost optimization opportunities
4. Ensure we hit aggressive revenue targets ($200K/month by year 1)
5. Alert on financial risks

CRITICAL: Review historical patterns to identify what strategies work and which ones drain money.

Analyze the financial data and provide:
- Health assessment (HEALTHY/WARNING/CRITICAL)
- Key insights (2-3 bullets)
- Cost optimization recommendations
- Revenue acceleration ideas
- Specific action items

Be ruthlessly focused on efficiency and growth."""

        user_prompt = f"""
FINANCIAL DATA ({period}):

Revenue: ${total_revenue:.2f}
AI Costs: ${total_costs:.2f}
AI Cost %: {(total_costs / total_revenue * 100) if total_revenue > 0 else 0:.1f}%
Net Profit: ${total_revenue - total_costs:.2f}
ROI: {calculate_roi(total_revenue, total_costs):.1f}%

TARGET TRACKING:
Monthly Target: ${targets['revenue_target']:,.0f}
Current: ${total_revenue:.2f}
Status: {tracking['status'].upper()}
% of Target: {(total_revenue / targets['revenue_target'] * 100) if targets['revenue_target'] > 0 else 0:.1f}%

COST BREAKDOWN:
{json.dumps(cost_breakdown, indent=2)}

DEPARTMENT ROI:
{json.dumps(roi_by_dept, indent=2)}

{learning_insights}

Provide your financial analysis and recommendations."""

        result = self._call_claude(system_prompt, user_prompt)

        # Log analysis
        self.memory.log_decision(
            agent="CFO",
            decision_type="financial_analysis",
            question=f"Financial health check - {period}",
            decision=result["content"],
            tokens_used=result["tokens_used"],
            cost=result["cost"]
        )

        return {
            "analysis": result["content"],
            "metrics": {
                "revenue": total_revenue,
                "costs": total_costs,
                "ai_cost_percent": (total_costs / total_revenue * 100) if total_revenue > 0 else 0,
                "roi": calculate_roi(total_revenue, total_costs),
                "on_track": tracking['on_track']
            },
            "tokens_used": result["tokens_used"],
            "cost": result["cost"]
        }


class CMOAgent(BoardAgent):
    """CMO Agent - Market Opportunity Scanner"""

    def __init__(self):
        super().__init__("CMO", BOARD_AGENT_BUDGETS["cmo"])

    def scan_opportunity(self, source: str, data: str) -> Dict[str, Any]:
        """Analyze potential opportunity from market signals"""

        system_prompt = """You are the CMO of NovaOS, responsible for identifying and evaluating market opportunities.

Your focus:
1. Identify emerging trends FAST
2. Assess market timing and size
3. Evaluate competitive landscape
4. Estimate revenue potential
5. Recommend action

For each opportunity, provide:
- VERDICT: [PURSUE/MONITOR/PASS]
- MARKET SIZE: [Estimated $ potential]
- TIMING: [NOW/SOON/LATER]
- COMPETITION: [Low/Medium/High]
- CONFIDENCE: [1-10]
- REASONING: [2-3 sentences]

Be aggressive but realistic. Focus on opportunities that can hit our 10X targets."""

        user_prompt = f"""
SOURCE: {source}

DATA/SIGNAL:
{data}

{self.get_context()}

Analyze this opportunity."""

        result = self._call_claude(system_prompt, user_prompt)

        # Parse opportunity
        content = result["content"]

        # Log opportunity if PURSUE or MONITOR
        if "PURSUE" in content or "MONITOR" in content:
            opp_id = self.memory.log_opportunity(
                title=f"Opportunity from {source}",
                description=data[:500],
                source=source,
                status="identified" if "PURSUE" in content else "monitoring",
                potential_revenue=None,  # TODO: Parse from content
                confidence_score=None  # TODO: Parse from content
            )

            return {
                "verdict": "PURSUE" if "PURSUE" in content else "MONITOR",
                "analysis": content,
                "opportunity_id": opp_id,
                "tokens_used": result["tokens_used"],
                "cost": result["cost"]
            }

        return {
            "verdict": "PASS",
            "analysis": content,
            "tokens_used": result["tokens_used"],
            "cost": result["cost"]
        }


class CTOAgent(BoardAgent):
    """CTO Agent - Technical Feasibility & Optimization"""

    def __init__(self):
        super().__init__("CTO", BOARD_AGENT_BUDGETS["cto"])

    def evaluate_technical_feasibility(self, project: str, requirements: str) -> Dict[str, Any]:
        """Evaluate technical feasibility of a project"""

        system_prompt = """You are the CTO of NovaOS, responsible for technical feasibility and system optimization.

Your focus:
1. Assess technical feasibility
2. Estimate implementation complexity
3. Identify technical risks
4. Recommend architecture
5. Optimize for AI cost efficiency

Provide:
- FEASIBILITY: [HIGH/MEDIUM/LOW]
- COMPLEXITY: [Simple/Moderate/Complex]
- TIME ESTIMATE: [Days/Weeks]
- RISKS: [Key technical risks]
- ARCHITECTURE: [High-level approach]
- AI EFFICIENCY: [Token optimization strategy]

Be practical and focused on rapid execution."""

        user_prompt = f"""
PROJECT: {project}

REQUIREMENTS:
{requirements}

{self.get_context()}

Evaluate technical feasibility."""

        result = self._call_claude(system_prompt, user_prompt)

        self.memory.log_decision(
            agent="CTO",
            decision_type="technical_evaluation",
            question=project,
            decision=result["content"],
            tokens_used=result["tokens_used"],
            cost=result["cost"]
        )

        return {
            "evaluation": result["content"],
            "tokens_used": result["tokens_used"],
            "cost": result["cost"]
        }


class COOAgent(BoardAgent):
    """COO Agent - Operations & System Health"""

    def __init__(self):
        super().__init__("COO", BOARD_AGENT_BUDGETS["coo"])

    def system_health_check(self) -> Dict[str, Any]:
        """Perform system health check"""

        # Get operational metrics
        agents = self.memory.get_all_agents(status="active")
        total_agents = len(agents)

        # Calculate agent performance
        high_roi_agents = sum(1 for a in agents if a.get('roi', 0) > 3.0)
        negative_roi_agents = sum(1 for a in agents if a.get('roi', 0) < 0)

        # Get costs
        total_costs = self.memory.get_total_costs()
        cost_breakdown = self.memory.get_cost_breakdown('today')

        system_prompt = """You are the COO of NovaOS, responsible for operational efficiency and system health.

Your focus:
1. Monitor agent performance
2. Identify operational bottlenecks
3. Ensure system reliability
4. Optimize resource allocation
5. Recommend operational improvements

Provide:
- HEALTH STATUS: [EXCELLENT/GOOD/FAIR/POOR]
- KEY METRICS: [Summary]
- ISSUES: [Problems identified]
- RECOMMENDATIONS: [Action items]

Be concise and action-oriented."""

        user_prompt = f"""
SYSTEM STATE:

Active Agents: {total_agents}
High ROI Agents (>300%): {high_roi_agents}
Negative ROI Agents: {negative_roi_agents}

Today's AI Spend: ${total_costs:.2f}
Cost Breakdown: {json.dumps(cost_breakdown, indent=2)}

{self.get_context()}

Perform health check."""

        result = self._call_claude(system_prompt, user_prompt, max_tokens=500)  # Short check

        return {
            "status": result["content"],
            "metrics": {
                "active_agents": total_agents,
                "high_roi_agents": high_roi_agents,
                "negative_roi_agents": negative_roi_agents,
                "today_cost": total_costs
            },
            "tokens_used": result["tokens_used"],
            "cost": result["cost"]
        }


# === BOARD FACTORY ===

class Board:
    """NovaOS Board - All C-suite agents"""

    def __init__(self):
        self.ceo = CEOAgent()
        self.cfo = CFOAgent()
        self.cmo = CMOAgent()
        self.cto = CTOAgent()
        self.coo = COOAgent()

    def get_status(self) -> Dict[str, Any]:
        """Get complete board status"""

        # Run quick checks
        coo_health = self.coo.system_health_check()
        cfo_analysis = self.cfo.analyze_finances("today")

        return {
            "timestamp": datetime.now().isoformat(),
            "operational_health": coo_health,
            "financial_health": cfo_analysis,
            "board_active": True
        }


def get_board() -> Board:
    """Get or create board instance"""
    global _board_instance
    try:
        return _board_instance
    except NameError:
        _board_instance = Board()
        return _board_instance
