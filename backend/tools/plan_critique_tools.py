"""
Plan critique phase tools for the Story Editor agent.

These tools are used during Phase 2 (PLAN_CRITIQUE) to review and refine
the planning materials created in Phase 1.
"""

import os
from typing import Dict, Any, Optional
from datetime import datetime

from backend.tools.base_tool import BaseTool
from backend.tools.project import get_active_project_folder
from backend.state_manager import NovelState, save_state, update_phase, require_approval
from backend.config import Phase


class LoadPlanMaterialsTool(BaseTool):
    """Tool for loading all planning documents for review."""

    @property
    def name(self) -> str:
        return "load_plan_materials"

    @property
    def description(self) -> str:
        return """Loads all planning materials (summary, characters, structure, outline) for review. \
Use this at the start of the plan critique phase to read all planning documents."""

    @property
    def parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {},
            "required": []
        }

    def execute(self, state: Optional[NovelState] = None) -> Dict[str, Any]:
        """
        Loads all planning materials.

        Args:
            state: Optional novel state to update

        Returns:
            Tool result dictionary with all planning content
        """
        project_folder = get_active_project_folder()
        if not project_folder:
            return {
                "success": False,
                "message": "Error: No active project folder."
            }

        files_to_load = {
            'summary': 'planning/summary.md',
            'characters': 'planning/characters.md',
            'structure': 'planning/structure.md',
            'outline': 'planning/outline.md'
        }

        loaded_content = {}
        missing_files = []

        for key, rel_path in files_to_load.items():
            file_path = os.path.join(project_folder, rel_path)
            if os.path.exists(file_path):
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        loaded_content[key] = f.read()
                except Exception as e:
                    loaded_content[key] = f"Error reading file: {str(e)}"
            else:
                missing_files.append(rel_path)

        if missing_files:
            return {
                "success": False,
                "message": f"Missing planning files: {', '.join(missing_files)}",
                "missing_files": missing_files
            }

        # Format content for agent review
        formatted_content = f"""PLANNING MATERIALS LOADED FOR REVIEW:

{'='*80}
STORY SUMMARY
{'='*80}
{loaded_content['summary']}

{'='*80}
DRAMATIS PERSONAE (CHARACTERS)
{'='*80}
{loaded_content['characters']}

{'='*80}
STORY STRUCTURE
{'='*80}
{loaded_content['structure']}

{'='*80}
PLOT OUTLINE
{'='*80}
{loaded_content['outline']}

{'='*80}
END OF PLANNING MATERIALS
{'='*80}
"""

        return {
            "success": True,
            "message": "Successfully loaded all planning materials for review.",
            "content": formatted_content,
            "files_loaded": list(files_to_load.values())
        }


class CritiquePlanTool(BaseTool):
    """Tool for providing critique feedback on the plan."""

    @property
    def name(self) -> str:
        return "critique_plan"

    @property
    def description(self) -> str:
        return """Provides comprehensive critique of the planning materials. Document any issues, \
plot holes, inconsistencies, weak motivations, or areas for improvement. This critique will be saved for reference."""

    @property
    def parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "critique_text": {
                    "type": "string",
                    "description": "Comprehensive critique identifying issues and suggesting improvements"
                }
            },
            "required": ["critique_text"]
        }

    def execute(
        self,
        critique_text: str,
        state: Optional[NovelState] = None
    ) -> Dict[str, Any]:
        """
        Saves critique feedback.

        Args:
            critique_text: Critique feedback text
            state: Optional novel state to update

        Returns:
            Tool result dictionary
        """
        project_folder = get_active_project_folder()
        if not project_folder:
            return {
                "success": False,
                "message": "Error: No active project folder."
            }

        # Determine critique version number
        version = 1
        if state:
            version = state.plan_critique_iterations + 1
            state.plan_critique_iterations = version

        # Save critique
        critique_dir = os.path.join(project_folder, "planning", "critiques")
        os.makedirs(critique_dir, exist_ok=True)

        file_path = os.path.join(critique_dir, f"plan_critique_v{version}.md")

        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(f"# Plan Critique - Version {version}\n\n")
                f.write(f"**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                f.write(f"---\n\n")
                f.write(critique_text)
                f.write("\n")

            if state:
                save_state(state)

            return {
                "success": True,
                "message": f"Critique saved as plan_critique_v{version}.md",
                "file_path": file_path,
                "version": version,
                "next_step": "Now use revision tools (revise_summary, revise_characters, etc.) to make changes, or use approve_plan if no changes needed"
            }

        except Exception as e:
            return {
                "success": False,
                "message": f"Error saving critique: {str(e)}"
            }


class ReviseSummaryTool(BaseTool):
    """Tool for revising the story summary."""

    @property
    def name(self) -> str:
        return "revise_summary"

    @property
    def description(self) -> str:
        return """Revises the story summary based on critique feedback. Overwrites the existing summary with improvements."""

    @property
    def parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "new_summary": {
                    "type": "string",
                    "description": "The revised story summary text"
                }
            },
            "required": ["new_summary"]
        }

    def execute(
        self,
        new_summary: str,
        state: Optional[NovelState] = None
    ) -> Dict[str, Any]:
        """
        Revises the summary file.

        Args:
            new_summary: Revised summary text
            state: Optional novel state to update

        Returns:
            Tool result dictionary
        """
        project_folder = get_active_project_folder()
        if not project_folder:
            return {
                "success": False,
                "message": "Error: No active project folder."
            }

        file_path = os.path.join(project_folder, "planning", "summary.md")

        try:
            # Read existing to preserve title
            title_line = ""
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as f:
                    first_line = f.readline()
                    if first_line.startswith('#'):
                        title_line = first_line

            # Write revised version
            with open(file_path, 'w', encoding='utf-8') as f:
                if title_line:
                    f.write(title_line)
                else:
                    f.write("# Story Summary\n\n")
                f.write(f"## Story Summary (Revised)\n\n")
                f.write(new_summary)
                f.write("\n")

            return {
                "success": True,
                "message": "Successfully revised story summary.",
                "file_path": file_path
            }

        except Exception as e:
            return {
                "success": False,
                "message": f"Error revising summary: {str(e)}"
            }


class ReviseCharactersTool(BaseTool):
    """Tool for revising character profiles."""

    @property
    def name(self) -> str:
        return "revise_characters"

    @property
    def description(self) -> str:
        return """Revises the character profiles based on critique feedback. Overwrites the existing characters file with improvements."""

    @property
    def parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "character_updates": {
                    "type": "string",
                    "description": "The revised character profiles text"
                }
            },
            "required": ["character_updates"]
        }

    def execute(
        self,
        character_updates: str,
        state: Optional[NovelState] = None
    ) -> Dict[str, Any]:
        """
        Revises the characters file.

        Args:
            character_updates: Revised character profiles
            state: Optional novel state to update

        Returns:
            Tool result dictionary
        """
        project_folder = get_active_project_folder()
        if not project_folder:
            return {
                "success": False,
                "message": "Error: No active project folder."
            }

        file_path = os.path.join(project_folder, "planning", "characters.md")

        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(f"# Dramatis Personae (Revised)\n\n")
                f.write(character_updates)
                f.write("\n")

            return {
                "success": True,
                "message": "Successfully revised character profiles.",
                "file_path": file_path
            }

        except Exception as e:
            return {
                "success": False,
                "message": f"Error revising characters: {str(e)}"
            }


class ReviseStructureTool(BaseTool):
    """Tool for revising story structure."""

    @property
    def name(self) -> str:
        return "revise_structure"

    @property
    def description(self) -> str:
        return """Revises the story structure based on critique feedback. Overwrites the existing structure file with improvements."""

    @property
    def parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "structure_updates": {
                    "type": "string",
                    "description": "The revised story structure text"
                }
            },
            "required": ["structure_updates"]
        }

    def execute(
        self,
        structure_updates: str,
        state: Optional[NovelState] = None
    ) -> Dict[str, Any]:
        """
        Revises the structure file.

        Args:
            structure_updates: Revised structure text
            state: Optional novel state to update

        Returns:
            Tool result dictionary
        """
        project_folder = get_active_project_folder()
        if not project_folder:
            return {
                "success": False,
                "message": "Error: No active project folder."
            }

        file_path = os.path.join(project_folder, "planning", "structure.md")

        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(f"# Story Structure (Revised)\n\n")
                f.write(structure_updates)
                f.write("\n")

            # Update chapter count if changed
            import re
            chapter_match = re.search(r'(\d+)\s+chapters?', structure_updates, re.IGNORECASE)
            if chapter_match and state:
                state.total_chapters = int(chapter_match.group(1))
                save_state(state)

            return {
                "success": True,
                "message": "Successfully revised story structure.",
                "file_path": file_path
            }

        except Exception as e:
            return {
                "success": False,
                "message": f"Error revising structure: {str(e)}"
            }


class ReviseOutlineTool(BaseTool):
    """Tool for revising plot outline."""

    @property
    def name(self) -> str:
        return "revise_outline"

    @property
    def description(self) -> str:
        return """Revises the plot outline based on critique feedback. Overwrites the existing outline file with improvements."""

    @property
    def parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "outline_updates": {
                    "type": "string",
                    "description": "The revised plot outline text"
                }
            },
            "required": ["outline_updates"]
        }

    def execute(
        self,
        outline_updates: str,
        state: Optional[NovelState] = None
    ) -> Dict[str, Any]:
        """
        Revises the outline file.

        Args:
            outline_updates: Revised outline text
            state: Optional novel state to update

        Returns:
            Tool result dictionary
        """
        project_folder = get_active_project_folder()
        if not project_folder:
            return {
                "success": False,
                "message": "Error: No active project folder."
            }

        file_path = os.path.join(project_folder, "planning", "outline.md")

        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(f"# Plot Outline (Revised)\n\n")
                f.write(outline_updates)
                f.write("\n")

            return {
                "success": True,
                "message": "Successfully revised plot outline.",
                "file_path": file_path
            }

        except Exception as e:
            return {
                "success": False,
                "message": f"Error revising outline: {str(e)}"
            }


class ApprovePlanTool(BaseTool):
    """Tool for approving the plan and transitioning to writing phase."""

    @property
    def name(self) -> str:
        return "approve_plan"

    @property
    def description(self) -> str:
        return """Approves the plan and transitions to the writing phase. Call this when all planning \
materials are reviewed and meet quality standards. This ends the plan critique phase."""

    @property
    def parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "approval_notes": {
                    "type": "string",
                    "description": "Notes about the approval and why the plan is ready for writing"
                }
            },
            "required": ["approval_notes"]
        }

    def execute(
        self,
        approval_notes: str,
        state: Optional[NovelState] = None
    ) -> Dict[str, Any]:
        """
        Approves the plan and transitions phases.

        Args:
            approval_notes: Notes about the approval
            state: Optional novel state to update

        Returns:
            Tool result dictionary with transition information
        """
        project_folder = get_active_project_folder()
        if not project_folder:
            return {
                "success": False,
                "message": "Error: No active project folder."
            }

        # Save approval notes
        approval_file = os.path.join(project_folder, "planning", "plan_approval.md")

        try:
            with open(approval_file, 'w', encoding='utf-8') as f:
                f.write(f"# Plan Approval\n\n")
                f.write(f"**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                f.write(f"**Status:** APPROVED\n\n")
                f.write(f"---\n\n")
                f.write(approval_notes)
                f.write("\n")

            # Update state
            if state:
                state.plan_approved = True
                update_phase(state, Phase.WRITING)
                save_state(state)

            return {
                "success": True,
                "message": "Plan approved! Transitioning to writing phase.",
                "file_path": approval_file,
                "transition": {
                    "to_phase": "WRITING",
                    "data": {
                        "approval_notes": approval_notes,
                        "critique_iterations": state.plan_critique_iterations if state else 0
                    }
                },
                "next_phase": "The Creative Writer will now begin writing chapters based on the approved plan."
            }

        except Exception as e:
            return {
                "success": False,
                "message": f"Error approving plan: {str(e)}"
            }


# Registry of all plan critique tools
def get_plan_critique_tools():
    """Get all plan critique phase tools."""
    return [
        LoadPlanMaterialsTool(),
        CritiquePlanTool(),
        ReviseSummaryTool(),
        ReviseCharactersTool(),
        ReviseStructureTool(),
        ReviseOutlineTool(),
        ApprovePlanTool()
    ]
