"""
Planning phase tools for the Story Architect agent.

These tools are used during Phase 1 (PLANNING) to create comprehensive
story blueprints including summary, characters, structure, and outline.
"""

import os
from typing import Dict, Any, Optional

from backend.tools.base_tool import BaseTool
from backend.tools.project import get_active_project_folder
from backend.state_manager import NovelState, save_state, update_phase
from backend.config import Phase


class CreateStorySummaryTool(BaseTool):
    """Tool for creating the high-level story summary."""

    @property
    def name(self) -> str:
        return "create_story_summary"

    @property
    def description(self) -> str:
        return """Creates the high-level story summary file. This should include the core concept, \
main themes, central conflict, and narrative arc. This is the foundational planning document."""

    @property
    def parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "project_name": {
                    "type": "string",
                    "description": "The title/name of the novel project"
                },
                "summary_text": {
                    "type": "string",
                    "description": "The complete story summary including concept, themes, conflict, and arc"
                }
            },
            "required": ["project_name", "summary_text"]
        }

    def execute(
        self,
        project_name: str,
        summary_text: str,
        state: Optional[NovelState] = None
    ) -> Dict[str, Any]:
        """
        Creates the story summary file.

        Args:
            project_name: The title/name of the novel
            summary_text: The complete summary text
            state: Optional novel state to update

        Returns:
            Tool result dictionary
        """
        project_folder = get_active_project_folder()
        if not project_folder:
            return {
                "success": False,
                "message": "Error: No active project folder. Create project first."
            }

        # Create file in planning directory
        file_path = os.path.join(project_folder, "planning", "summary.md")
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(f"# {project_name}\n\n")
                f.write(f"## Story Summary\n\n")
                f.write(summary_text)
                f.write("\n")

            # Update state
            if state:
                state.plan_files_created['planning/summary.md'] = True
                save_state(state)

            return {
                "success": True,
                "message": f"Successfully created story summary in planning/summary.md",
                "file_path": file_path,
                "next_step": "Now create the dramatis personae (character profiles) using create_dramatis_personae"
            }

        except Exception as e:
            return {
                "success": False,
                "message": f"Error creating summary: {str(e)}"
            }


class CreateDramatisPersonaeTool(BaseTool):
    """Tool for creating character profiles."""

    @property
    def name(self) -> str:
        return "create_dramatis_personae"

    @property
    def description(self) -> str:
        return """Creates the character profiles file (dramatis personae). Include all major and \
significant minor characters with their backgrounds, motivations, relationships, and character arcs."""

    @property
    def parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "characters_data": {
                    "type": "string",
                    "description": "Complete character profiles in markdown format with all major and significant minor characters"
                }
            },
            "required": ["characters_data"]
        }

    def execute(
        self,
        characters_data: str,
        state: Optional[NovelState] = None
    ) -> Dict[str, Any]:
        """
        Creates the characters file.

        Args:
            characters_data: Character profiles in markdown format
            state: Optional novel state to update

        Returns:
            Tool result dictionary
        """
        project_folder = get_active_project_folder()
        if not project_folder:
            return {
                "success": False,
                "message": "Error: No active project folder. Create project first."
            }

        file_path = os.path.join(project_folder, "planning", "characters.md")
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(f"# Dramatis Personae\n\n")
                f.write(characters_data)
                f.write("\n")

            # Update state
            if state:
                state.plan_files_created['planning/characters.md'] = True
                save_state(state)

            return {
                "success": True,
                "message": f"Successfully created character profiles in planning/characters.md",
                "file_path": file_path,
                "next_step": "Now create the story structure using create_story_structure"
            }

        except Exception as e:
            return {
                "success": False,
                "message": f"Error creating characters: {str(e)}"
            }


class CreateStoryStructureTool(BaseTool):
    """Tool for defining narrative structure."""

    @property
    def name(self) -> str:
        return "create_story_structure"

    @property
    def description(self) -> str:
        return """Creates the story structure file. Define POV (point of view), narrative timeline, \
chapter count, pacing strategy, and structural elements (acts, parts, etc.)."""

    @property
    def parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "structure_data": {
                    "type": "string",
                    "description": "Complete structure information including POV, timeline, chapter count, and pacing"
                }
            },
            "required": ["structure_data"]
        }

    def execute(
        self,
        structure_data: str,
        state: Optional[NovelState] = None
    ) -> Dict[str, Any]:
        """
        Creates the story structure file.

        Args:
            structure_data: Structure information in markdown format
            state: Optional novel state to update

        Returns:
            Tool result dictionary
        """
        project_folder = get_active_project_folder()
        if not project_folder:
            return {
                "success": False,
                "message": "Error: No active project folder. Create project first."
            }

        file_path = os.path.join(project_folder, "planning", "structure.md")
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(f"# Story Structure\n\n")
                f.write(structure_data)
                f.write("\n")

            # Extract chapter count if mentioned (for state tracking)
            # Simple heuristic: look for "X chapters" pattern
            import re
            chapter_match = re.search(r'(\d+)\s+chapters?', structure_data, re.IGNORECASE)
            if chapter_match and state:
                state.total_chapters = int(chapter_match.group(1))

            # Update state
            if state:
                state.plan_files_created['planning/structure.md'] = True
                save_state(state)

            return {
                "success": True,
                "message": f"Successfully created story structure in planning/structure.md",
                "file_path": file_path,
                "next_step": "Now create the detailed plot outline using create_plot_outline"
            }

        except Exception as e:
            return {
                "success": False,
                "message": f"Error creating structure: {str(e)}"
            }


class CreatePlotOutlineTool(BaseTool):
    """Tool for creating chapter-by-chapter plot outline."""

    @property
    def name(self) -> str:
        return "create_plot_outline"

    @property
    def description(self) -> str:
        return """Creates the detailed plot outline file. Break down the story chapter by chapter \
with key events, character moments, plot developments, and how each chapter advances the narrative."""

    @property
    def parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "outline_data": {
                    "type": "string",
                    "description": "Complete chapter-by-chapter plot outline in markdown format"
                }
            },
            "required": ["outline_data"]
        }

    def execute(
        self,
        outline_data: str,
        state: Optional[NovelState] = None
    ) -> Dict[str, Any]:
        """
        Creates the plot outline file.

        Args:
            outline_data: Plot outline in markdown format
            state: Optional novel state to update

        Returns:
            Tool result dictionary
        """
        project_folder = get_active_project_folder()
        if not project_folder:
            return {
                "success": False,
                "message": "Error: No active project folder. Create project first."
            }

        file_path = os.path.join(project_folder, "planning", "outline.md")
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(f"# Plot Outline\n\n")
                f.write(outline_data)
                f.write("\n")

            # Update state
            if state:
                state.plan_files_created['planning/outline.md'] = True
                save_state(state)

            return {
                "success": True,
                "message": f"Successfully created plot outline in planning/outline.md",
                "file_path": file_path,
                "next_step": "Now finalize the plan using finalize_plan to complete the planning phase"
            }

        except Exception as e:
            return {
                "success": False,
                "message": f"Error creating outline: {str(e)}"
            }


class FinalizePlanTool(BaseTool):
    """Tool for finalizing the planning phase."""

    @property
    def name(self) -> str:
        return "finalize_plan"

    @property
    def description(self) -> str:
        return """Finalizes the planning phase. Call this after creating all planning documents \
(summary, characters, structure, outline). This transitions the project to the plan critique phase."""

    @property
    def parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "notes": {
                    "type": "string",
                    "description": "Optional notes about the completed plan"
                }
            },
            "required": []
        }

    def execute(
        self,
        notes: str = "",
        state: Optional[NovelState] = None
    ) -> Dict[str, Any]:
        """
        Finalizes the planning phase.

        Args:
            notes: Optional notes about the plan
            state: Optional novel state to update

        Returns:
            Tool result dictionary with transition information
        """
        project_folder = get_active_project_folder()
        if not project_folder:
            return {
                "success": False,
                "message": "Error: No active project folder. Create project first."
            }

        # Verify all required planning files exist
        required_files = [
            'planning/summary.md',
            'planning/characters.md',
            'planning/structure.md',
            'planning/outline.md'
        ]

        missing_files = []
        for file in required_files:
            file_path = os.path.join(project_folder, file)
            if not os.path.exists(file_path):
                missing_files.append(file)

        if missing_files:
            return {
                "success": False,
                "message": f"Cannot finalize plan. Missing required files: {', '.join(missing_files)}",
                "missing_files": missing_files
            }

        # Update state and transition to plan critique phase
        if state:
            state.plan_files_created['_finalized'] = True
            update_phase(state, Phase.PLAN_CRITIQUE)
            save_state(state)

        return {
            "success": True,
            "message": "Planning phase complete! All planning documents created. Transitioning to plan critique phase.",
            "transition": {
                "to_phase": "PLAN_CRITIQUE",
                "data": {
                    "notes": notes,
                    "files_created": required_files
                }
            },
            "next_phase": "The Story Editor will now review and critique the plan."
        }


# Registry of all planning tools
def get_planning_tools():
    """Get all planning phase tools."""
    return [
        CreateStorySummaryTool(),
        CreateDramatisPersonaeTool(),
        CreateStoryStructureTool(),
        CreatePlotOutlineTool(),
        FinalizePlanTool()
    ]
