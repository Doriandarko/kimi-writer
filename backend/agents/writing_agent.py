"""
Writing Agent (Creative Writer) for Phase 3.

This agent writes complete, polished chapters based on the approved plan,
maintaining consistent voice and following the outline.
"""

from typing import List, Optional

from backend.agents.base_agent import BaseAgent
from backend.tools.base_tool import BaseTool
from backend.tools.writing_tools import get_writing_tools
from backend.system_prompts import get_custom_prompt_or_default
from backend.config import NovelConfig
from backend.state_manager import NovelState
from backend.writing_samples import get_writing_sample


class WritingAgent(BaseAgent):
    """
    Creative Writer agent for the writing phase.

    Responsibilities:
    - Write complete, substantial chapters
    - Follow the approved plan and outline
    - Maintain consistent voice and style
    - Ensure continuity with previous chapters
    - Create engaging, polished prose
    """

    def get_system_prompt(self) -> str:
        """
        Get the writing agent's system prompt with optional writing sample.

        Returns:
            System prompt for writing phase
        """
        # Get current chapter number
        chapter_num = self.state.current_chapter if self.state.current_chapter > 0 else 1

        # Get writing sample if configured
        writing_sample_text = None
        if self.config.writing_sample.enabled and self.config.writing_sample.sample_id:
            if self.config.writing_sample.sample_id == 'custom':
                writing_sample_text = self.config.writing_sample.custom_text
            else:
                writing_sample_text = get_writing_sample(self.config.writing_sample.sample_id)

        return get_custom_prompt_or_default(
            'writing',
            self.config,
            chapter_num=chapter_num,
            writing_sample=writing_sample_text
        )

    def get_tools(self) -> List[BaseTool]:
        """
        Get tools available to the writing agent.

        Returns:
            List of writing tools
        """
        return get_writing_tools()

    def get_initial_prompt(self, chapter_number: Optional[int] = None) -> str:
        """
        Get the initial prompt to start writing a chapter.

        Args:
            chapter_number: Specific chapter to write (or uses state.current_chapter)

        Returns:
            Initial user prompt
        """
        if chapter_number is None:
            chapter_number = self.state.current_chapter if self.state.current_chapter > 0 else 1

        # Check if this is a revision
        is_revision = False
        if chapter_number in self.state.chapter_critique_iterations:
            is_revision = self.state.chapter_critique_iterations[chapter_number] > 0

        revision_note = ""
        if is_revision:
            # Look for revision request file
            from backend.tools.project import get_active_project_folder
            import os

            project_folder = get_active_project_folder()
            if project_folder:
                version = self.state.chapter_critique_iterations[chapter_number]
                revision_file = os.path.join(
                    project_folder,
                    "critiques",
                    f"chapter_{chapter_number:02d}_revision_request_v{version-1}.md"
                )
                if os.path.exists(revision_file):
                    try:
                        with open(revision_file, 'r', encoding='utf-8') as f:
                            revision_content = f.read()
                            revision_note = f"\n\nREVISION REQUESTED - Please address the following feedback:\n{revision_content}\n"
                    except:
                        pass

        return f"""{'REVISION: ' if is_revision else ''}Please write Chapter {chapter_number} of the novel.
{revision_note}
Your workflow:
1. Use load_approved_plan to refresh your memory of the story blueprint
2. Use get_chapter_context to get the specific outline for Chapter {chapter_number}
3. Use review_previous_writing if you need to check earlier chapters for continuity
4. Write a complete, polished chapter (2,500-5,000+ words)
5. Use write_chapter to save your work
6. Use finalize_chapter to submit it for critique

Remember:
- Follow the approved plan and outline
- Maintain consistent voice and style throughout
- Show, don't tell - use vivid scenes and dialogue
- Every chapter should advance plot, develop characters, or explore themes
- Write complete, publication-quality prose
- Don't hold back on length - tell the story fully

Focus on creating an engaging, immersive reading experience."""
