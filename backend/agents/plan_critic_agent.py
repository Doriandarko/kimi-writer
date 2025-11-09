"""
Plan Critic Agent (Story Editor) for Phase 2.

This agent reviews and critiques the planning materials, identifying issues
and requesting revisions or approving the plan for writing.
"""

from typing import List

from backend.agents.base_agent import BaseAgent
from backend.tools.base_tool import BaseTool
from backend.tools.plan_critique_tools import get_plan_critique_tools
from backend.system_prompts import get_custom_prompt_or_default
from backend.config import NovelConfig
from backend.state_manager import NovelState


class PlanCriticAgent(BaseAgent):
    """
    Story Editor agent for the plan critique phase.

    Responsibilities:
    - Review all planning materials
    - Identify plot holes and inconsistencies
    - Check character motivations and relationships
    - Verify structural soundness
    - Request revisions or approve plan
    """

    def get_system_prompt(self) -> str:
        """
        Get the plan critic agent's system prompt.

        Returns:
            System prompt for plan critique phase
        """
        return get_custom_prompt_or_default('plan_critic', self.config)

    def get_tools(self) -> List[BaseTool]:
        """
        Get tools available to the plan critic agent.

        Returns:
            List of plan critique tools
        """
        return get_plan_critique_tools()

    def get_initial_prompt(self) -> str:
        """
        Get the initial prompt to start the plan critique process.

        Returns:
            Initial user prompt
        """
        max_iterations = self.config.agent.max_plan_critique_iterations

        return f"""The planning phase is complete. Please review all planning materials and provide critique.

Your workflow:
1. Load all planning materials using load_plan_materials
2. Carefully review the summary, characters, structure, and outline
3. Use critique_plan to document any issues found
4. If issues exist, use the revision tools (revise_summary, revise_characters, etc.) to make improvements
5. You can iterate up to {max_iterations} times
6. When the plan is solid, use approve_plan to move forward

Focus on:
- Plot consistency and logic
- Character motivations and development
- Structural soundness
- Pacing and tension
- Theme integration
- Overall narrative quality

Be thorough but constructive. The goal is to ensure a strong foundation for writing."""
