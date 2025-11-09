"""
Planning Agent (Story Architect) for Phase 1.

This agent is responsible for creating comprehensive story blueprints including
summary, characters, structure, and detailed chapter outlines.
"""

from typing import List

from backend.agents.base_agent import BaseAgent
from backend.tools.base_tool import BaseTool
from backend.tools.planning_tools import get_planning_tools
from backend.tools.project import CreateProjectTool
from backend.system_prompts import get_custom_prompt_or_default
from backend.config import NovelConfig
from backend.state_manager import NovelState


class PlanningAgent(BaseAgent):
    """
    Story Architect agent for the planning phase.

    Responsibilities:
    - Create high-level story summary
    - Develop character profiles
    - Define narrative structure
    - Create detailed chapter-by-chapter outline
    """

    def get_system_prompt(self) -> str:
        """
        Get the planning agent's system prompt.

        Returns:
            System prompt for planning phase
        """
        return get_custom_prompt_or_default('planning', self.config)

    def get_tools(self) -> List[BaseTool]:
        """
        Get tools available to the planning agent.

        Returns:
            List of planning tools
        """
        tools = []

        # Add project creation tool (in case not already created)
        tools.append(CreateProjectTool())

        # Add all planning-specific tools
        tools.extend(get_planning_tools())

        return tools

    def get_initial_prompt(self) -> str:
        """
        Get the initial prompt to start the planning process.

        Returns:
            Initial user prompt
        """
        return f"""Please create a comprehensive plan for a novel based on the following theme/concept:

"{self.config.theme}"

Target length: {self.config.novel_length.value.replace('_', ' ').title()}
{f"Genre: {self.config.genre}" if self.config.genre else ""}

Follow the planning workflow:
1. Create the project folder
2. Create a story summary (concept, themes, conflict, arc)
3. Create dramatis personae (character profiles)
4. Create story structure (POV, timeline, chapter count, pacing)
5. Create a detailed plot outline (chapter-by-chapter breakdown)
6. Finalize the plan

Take your time to think deeply about the narrative structure, character arcs, and thematic elements. Create a solid foundation for writing."""
