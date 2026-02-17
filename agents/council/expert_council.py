"""
NovaOS V2 R&D Expert Council
Token-efficient advisory board with 4 expert avatars
"""

import anthropic
from typing import Dict, List, Any
from datetime import datetime

from core.memory import get_memory
from config.settings import (
    ANTHROPIC_API_KEY, MODELS, DEFAULT_MODELS,
    COUNCIL_AVATAR_BUDGET, COUNCIL_AVATARS, MCP_CONFIG
)


class ExpertAvatar:
    """Base class for expert avatar"""

    def __init__(self, name: str, config: Dict):
        self.name = name
        self.config = config
        self.token_budget = COUNCIL_AVATAR_BUDGET
        self.client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
        self.model = DEFAULT_MODELS["council"]
        self.memory = get_memory()

    def analyze(self, question: str, context: str = "") -> Dict[str, Any]:
        """Analyze a question from this avatar's perspective"""

        system_prompt = f"""You are the {self.name} avatar in the NovaOS R&D Expert Council.

Your perspective: {self.config['perspective']}
Your key question: {self.config['key_question']}
Your focus: {self.config['focus']}

Analyze the question through YOUR unique lens. Be:
- BRIEF: Maximum 3-4 sentences
- SPECIFIC: Concrete insights, not generic advice
- CONTRARIAN: Challenge assumptions if needed
- ACTIONABLE: Focus on what to do

Do not say "I think" or "In my opinion" - just provide your analysis directly."""

        user_prompt = f"""Question: {question}

{context if context else ''}

Provide your {self.name}-style analysis."""

        try:
            response = self.client.messages.create(
                model=MODELS[self.model]["id"],
                max_tokens=self.token_budget,
                system=system_prompt,
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
                operation=f"council_{self.name.lower()}_analysis",
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                cost=total_cost,
                agent_id=f"council_{self.name.lower()}",
                agent_name=f"{self.name} Avatar",
                department="research"
            )

            return {
                "analysis": response.content[0].text,
                "tokens_used": input_tokens + output_tokens,
                "cost": total_cost
            }

        except Exception as e:
            return {
                "analysis": f"Error: {str(e)}",
                "tokens_used": 0,
                "cost": 0.0
            }


class ThielAvatar(ExpertAvatar):
    """Peter Thiel avatar - Contrarian monopoly thinking"""

    def __init__(self):
        super().__init__("Thiel", COUNCIL_AVATARS["thiel"])


class MuskAvatar(ExpertAvatar):
    """Elon Musk avatar - First principles speed"""

    def __init__(self):
        super().__init__("Musk", COUNCIL_AVATARS["musk"])


class GrahamAvatar(ExpertAvatar):
    """Paul Graham avatar - Startup fundamentals"""

    def __init__(self):
        super().__init__("Graham", COUNCIL_AVATARS["graham"])


class TalebAvatar(ExpertAvatar):
    """Nassim Taleb avatar - Risk and antifragility"""

    def __init__(self):
        super().__init__("Taleb", COUNCIL_AVATARS["taleb"])


class ExpertCouncil:
    """R&D Expert Council - All 4 avatars"""

    def __init__(self):
        self.avatars = {
            "thiel": ThielAvatar(),
            "musk": MuskAvatar(),
            "graham": GrahamAvatar(),
            "taleb": TalebAvatar()
        }
        self.memory = get_memory()
        self.client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

    def analyze(self, question: str, sequential: bool = True) -> Dict[str, Any]:
        """
        Run full council analysis

        Args:
            question: The question to analyze
            sequential: If True, avatars debate in sequence (more token efficient)
                       If False, all analyze in parallel
        """

        print(f"🔮 Convening R&D Expert Council...")
        print(f"   Question: {question}\n")

        analyses = {}
        total_tokens = 0
        total_cost = 0.0

        if sequential:
            # Sequential debate - each avatar sees previous analyses
            context = ""

            for avatar_name, avatar in self.avatars.items():
                print(f"   Consulting {avatar.name} avatar...")

                result = avatar.analyze(question, context)
                analyses[avatar_name] = result['analysis']
                total_tokens += result['tokens_used']
                total_cost += result['cost']

                # Add to context for next avatar
                context += f"\n{avatar.name}'s view: {result['analysis']}\n"

        else:
            # Parallel analysis - all avatars analyze independently
            for avatar_name, avatar in self.avatars.items():
                print(f"   Consulting {avatar.name} avatar...")

                result = avatar.analyze(question)
                analyses[avatar_name] = result['analysis']
                total_tokens += result['tokens_used']
                total_cost += result['cost']

        # Synthesize consensus
        print("   Synthesizing consensus...")
        consensus_result = self._synthesize_consensus(question, analyses)
        total_tokens += consensus_result['tokens_used']
        total_cost += consensus_result['cost']

        # Extract action items and dissents
        action_items = self._extract_action_items(consensus_result['consensus'])
        dissents = self._identify_dissents(analyses)

        # Log to memory
        session_id = self.memory.log_council_session(
            question=question,
            analyses=analyses,
            consensus=consensus_result['consensus'],
            action_items=action_items,
            dissents=dissents,
            tokens_used=total_tokens,
            cost=total_cost
        )

        # Save to MCP if enabled
        if MCP_CONFIG["enabled"] and MCP_CONFIG["auto_save_council_sessions"]:
            try:
                from mcp__novaos_memory__save_memory import save_memory

                content = f"""# R&D Expert Council Session

**Question:** {question}

## Thiel (Contrarian/Monopoly)
{analyses['thiel']}

## Musk (First Principles/Speed)
{analyses['musk']}

## Graham (Fundamentals/PMF)
{analyses['graham']}

## Taleb (Risk/Antifragility)
{analyses['taleb']}

## Consensus
{consensus_result['consensus']}

## Action Items
{chr(10).join(f"- {item}" for item in action_items)}

---
*Tokens: {total_tokens} | Cost: ${total_cost:.4f}*
"""

                save_memory(
                    doc_id=f"council-session-{session_id}",
                    content=content,
                    tags=["council", "r&d", "analysis"]
                )
            except:
                pass  # MCP not available

        print(f"✓ Council session complete\n")

        return {
            "question": question,
            "analyses": analyses,
            "consensus": consensus_result['consensus'],
            "action_items": action_items,
            "dissents": dissents,
            "tokens_used": total_tokens,
            "cost": total_cost,
            "session_id": session_id
        }

    def _synthesize_consensus(self, question: str, analyses: Dict[str, str]) -> Dict[str, Any]:
        """Synthesize consensus from all avatar analyses"""

        system_prompt = """You are synthesizing expert opinions from 4 perspectives: Thiel (contrarian/monopoly), Musk (first principles/speed), Graham (fundamentals/PMF), and Taleb (risk/antifragility).

Your task:
1. Identify common themes and agreements
2. Note key disagreements or tensions
3. Provide a balanced recommendation
4. List 2-3 specific action items

Be BRIEF (4-5 sentences max) and ACTIONABLE."""

        user_prompt = f"""Question: {question}

EXPERT ANALYSES:

Thiel: {analyses['thiel']}

Musk: {analyses['musk']}

Graham: {analyses['graham']}

Taleb: {analyses['taleb']}

Synthesize the consensus and provide action items."""

        try:
            response = self.client.messages.create(
                model=MODELS[DEFAULT_MODELS["council"]]["id"],
                max_tokens=500,  # Short consensus
                system=system_prompt,
                messages=[{"role": "user", "content": user_prompt}]
            )

            input_tokens = response.usage.input_tokens
            output_tokens = response.usage.output_tokens

            input_cost = (input_tokens / 1_000_000) * MODELS[DEFAULT_MODELS["council"]]["input_cost"]
            output_cost = (output_tokens / 1_000_000) * MODELS[DEFAULT_MODELS["council"]]["output_cost"]
            total_cost = input_cost + output_cost

            self.memory.log_api_cost(
                model=MODELS[DEFAULT_MODELS["council"]]["id"],
                operation="council_consensus",
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                cost=total_cost,
                agent_id="council_synthesis",
                agent_name="Council Synthesis",
                department="research"
            )

            return {
                "consensus": response.content[0].text,
                "tokens_used": input_tokens + output_tokens,
                "cost": total_cost
            }

        except Exception as e:
            return {
                "consensus": f"Error synthesizing: {str(e)}",
                "tokens_used": 0,
                "cost": 0.0
            }

    def _extract_action_items(self, consensus: str) -> List[str]:
        """Extract action items from consensus"""
        # Simple extraction - look for numbered items or bullet points
        items = []
        lines = consensus.split('\n')

        for line in lines:
            line = line.strip()
            # Look for numbered items (1., 2., etc.) or bullet points (-, *, •)
            if line and (line[0].isdigit() or line[0] in ['-', '*', '•']):
                # Clean up
                item = line.lstrip('0123456789.-*• ').strip()
                if item:
                    items.append(item)

        # If no clear action items found, return generic
        if not items:
            items = ["Review full analysis and decide on implementation approach"]

        return items[:5]  # Max 5 action items

    def _identify_dissents(self, analyses: Dict[str, str]) -> List[str]:
        """Identify key disagreements or concerns"""
        # Look for negative keywords or warnings
        warning_keywords = [
            'risk', 'danger', 'concern', 'problem', 'avoid', 'don\'t',
            'warning', 'caution', 'however', 'but', 'unlikely'
        ]

        dissents = []

        for avatar_name, analysis in analyses.items():
            analysis_lower = analysis.lower()

            # Check if this analysis contains warnings
            if any(keyword in analysis_lower for keyword in warning_keywords):
                # Extract the cautionary part (simplified)
                sentences = analysis.split('.')
                for sentence in sentences:
                    if any(keyword in sentence.lower() for keyword in warning_keywords):
                        dissents.append(f"{avatar_name.title()}: {sentence.strip()}")
                        break

        return dissents[:3]  # Max 3 dissents


# Singleton instance
_council_instance = None

def get_council() -> ExpertCouncil:
    """Get or create council instance"""
    global _council_instance
    if _council_instance is None:
        _council_instance = ExpertCouncil()
    return _council_instance
