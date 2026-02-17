"""
NovaOS V2 Sandbox Evaluator
Integrates R&D Expert Council for deep project analysis
"""

from typing import Dict, Any
from datetime import datetime

from agents.council.expert_council import ExpertCouncil, get_council


class SandboxEvaluator:
    """
    Enhanced sandbox evaluator that uses R&D Expert Council

    Combines quantitative metrics with qualitative expert analysis:
    - Metrics: ROI, cost, revenue, agent performance
    - Expert Council: Strategic value, risk assessment, recommendations
    """

    def __init__(self):
        self.council = None  # Lazy load to avoid circular imports

    def _get_council(self):
        """Lazy load council"""
        if self.council is None:
            self.council = get_council()
        return self.council

    def evaluate_project(self, project, basic_evaluation: Dict) -> Dict[str, Any]:
        """
        Comprehensive project evaluation using R&D Council

        Args:
            project: SandboxProject instance
            basic_evaluation: Basic metrics evaluation from SandboxManager

        Returns:
            Enhanced evaluation with council analysis
        """

        metrics = basic_evaluation['metrics']

        # Build context for council
        context = self._build_evaluation_context(project, metrics)

        # Ask R&D Council for analysis
        question = f"""Should we promote this sandbox project to production?

PROJECT: {project.name}
DESCRIPTION: {project.description}

METRICS:
- ROI: {metrics['roi']:.1f}%
- Profit: ${metrics['profit']:.2f}
- Total Cost: ${metrics['total_cost']:.2f}
- Total Revenue: ${metrics['total_revenue']:.2f}
- Active Agents: {metrics['active_agents']}
- Total Agents: {metrics['total_agents']}

AGENTS:
{context['agents_summary']}

EVALUATION CRITERIA:
{self._format_criteria(basic_evaluation['criteria'])}

Is this worth promoting to production? What are the risks and opportunities?"""

        print("\n🔮 Consulting R&D Expert Council for evaluation...\n")

        # Get council analysis
        council_result = self._get_council().analyze(question, sequential=True)

        # Combine basic and council evaluation
        enhanced_evaluation = {
            **basic_evaluation,
            'council_analysis': {
                'analyses': council_result['analyses'],
                'consensus': council_result['consensus'],
                'action_items': council_result['action_items'],
                'dissents': council_result['dissents'],
                'tokens_used': council_result['tokens_used'],
                'cost': council_result['cost']
            },
            'evaluated_at': datetime.now().isoformat(),
            'evaluation_type': 'comprehensive'
        }

        # Update recommendation based on council input
        enhanced_evaluation['final_recommendation'] = self._synthesize_recommendation(
            basic_evaluation['recommendation'],
            council_result['consensus'],
            metrics
        )

        return enhanced_evaluation

    def _build_evaluation_context(self, project, metrics: Dict) -> Dict[str, str]:
        """Build context summary for council"""

        agents = project.list_agents()

        # Summarize agents
        if agents:
            agents_summary = []
            for agent in agents[:5]:  # Top 5 agents
                agents_summary.append(
                    f"  - {agent['name']} ({agent['type']}): "
                    f"ROI {agent.get('roi', 0):.1f}%, "
                    f"Status: {agent['status']}"
                )
            agents_text = "\n".join(agents_summary)
            if len(agents) > 5:
                agents_text += f"\n  ... and {len(agents) - 5} more agents"
        else:
            agents_text = "  No agents deployed"

        return {
            'agents_summary': agents_text
        }

    def _format_criteria(self, criteria: Dict) -> str:
        """Format criteria for display"""
        lines = []
        for name, info in criteria.items():
            status = "✓ PASS" if info['pass'] else "✗ FAIL"
            lines.append(f"  - {name}: {status} (value: {info['value']}, threshold: {info['threshold']})")
        return "\n".join(lines)

    def _synthesize_recommendation(self, basic_rec: str, council_consensus: str,
                                   metrics: Dict) -> Dict[str, Any]:
        """
        Synthesize final recommendation from basic and council analysis

        Args:
            basic_rec: Basic recommendation (STRONGLY_RECOMMEND, RECOMMEND, CONSIDER, NOT_READY)
            council_consensus: Council consensus text
            metrics: Project metrics

        Returns:
            Final recommendation with reasoning
        """

        # Extract sentiment from council consensus (simple keyword analysis)
        consensus_lower = council_consensus.lower()

        positive_signals = [
            'promote', 'ready', 'strong', 'excellent', 'recommend',
            'good', 'promising', 'potential', 'profitable'
        ]
        negative_signals = [
            'risky', 'not ready', 'concern', 'warning', 'avoid',
            'insufficient', 'weak', 'problematic'
        ]

        positive_count = sum(1 for signal in positive_signals if signal in consensus_lower)
        negative_count = sum(1 for signal in negative_signals if signal in consensus_lower)

        # Determine council sentiment
        if positive_count > negative_count:
            council_sentiment = 'POSITIVE'
        elif negative_count > positive_count:
            council_sentiment = 'NEGATIVE'
        else:
            council_sentiment = 'NEUTRAL'

        # Synthesize final recommendation
        if basic_rec in ['STRONGLY_RECOMMEND', 'RECOMMEND'] and council_sentiment == 'POSITIVE':
            final_rec = 'PROMOTE'
            confidence = 'HIGH'
            reason = "Both metrics and expert council agree: this project is ready for production"

        elif basic_rec in ['STRONGLY_RECOMMEND', 'RECOMMEND'] and council_sentiment == 'NEUTRAL':
            final_rec = 'PROMOTE_WITH_CAUTION'
            confidence = 'MEDIUM'
            reason = "Metrics look good, but expert council identified some considerations"

        elif basic_rec in ['STRONGLY_RECOMMEND', 'RECOMMEND'] and council_sentiment == 'NEGATIVE':
            final_rec = 'HOLD'
            confidence = 'MEDIUM'
            reason = "Metrics are positive, but expert council recommends caution or improvements first"

        elif basic_rec == 'CONSIDER' and council_sentiment == 'POSITIVE':
            final_rec = 'PROMOTE_WITH_CAUTION'
            confidence = 'MEDIUM'
            reason = "Metrics are mixed, but expert council sees strategic value"

        elif basic_rec == 'CONSIDER' and council_sentiment in ['NEUTRAL', 'NEGATIVE']:
            final_rec = 'HOLD'
            confidence = 'MEDIUM'
            reason = "Metrics are mixed and expert council recommends waiting"

        else:  # NOT_READY or negative signals
            final_rec = 'DO_NOT_PROMOTE'
            confidence = 'HIGH'
            reason = "Project not ready for production - needs improvement"

        return {
            'decision': final_rec,
            'confidence': confidence,
            'reason': reason,
            'basic_recommendation': basic_rec,
            'council_sentiment': council_sentiment,
            'metrics_summary': {
                'roi': metrics['roi'],
                'profit': metrics['profit'],
                'active_agents': metrics['active_agents']
            }
        }

    def quick_evaluate(self, project, basic_evaluation: Dict) -> Dict[str, Any]:
        """
        Quick evaluation without R&D Council (saves cost)

        Use this for preliminary checks before full evaluation
        """

        return {
            **basic_evaluation,
            'evaluated_at': datetime.now().isoformat(),
            'evaluation_type': 'quick',
            'final_recommendation': {
                'decision': basic_evaluation['recommendation'],
                'confidence': 'MEDIUM',
                'reason': 'Quick evaluation based on metrics only (no council analysis)',
                'basic_recommendation': basic_evaluation['recommendation'],
                'council_sentiment': 'NOT_CONSULTED',
                'metrics_summary': {
                    'roi': basic_evaluation['metrics']['roi'],
                    'profit': basic_evaluation['metrics']['profit'],
                    'active_agents': basic_evaluation['metrics']['active_agents']
                }
            }
        }


# Singleton instance
_evaluator_instance = None

def get_evaluator() -> SandboxEvaluator:
    """Get or create sandbox evaluator instance"""
    global _evaluator_instance
    if _evaluator_instance is None:
        _evaluator_instance = SandboxEvaluator()
    return _evaluator_instance
