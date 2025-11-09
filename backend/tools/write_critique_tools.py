"""
Write critique phase tools for the Chapter Editor agent.

These tools are used during Phase 4 (WRITE_CRITIQUE) to review and critique
individual chapters, ensuring quality before moving forward.
"""

import os
from typing import Dict, Any, Optional
from datetime import datetime

from backend.tools.base_tool import BaseTool
from backend.tools.project import get_active_project_folder
from backend.state_manager import NovelState, save_state, update_phase, increment_chapter
from backend.config import Phase


class LoadChapterForReviewTool(BaseTool):
    """Tool for loading a chapter for review."""

    @property
    def name(self) -> str:
        return "load_chapter_for_review"

    @property
    def description(self) -> str:
        return """Loads the specified chapter for review. Use this to read the chapter content \
before providing critique."""

    @property
    def parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "chapter_number": {
                    "type": "integer",
                    "description": "The chapter number to review (1-indexed)"
                }
            },
            "required": ["chapter_number"]
        }

    def execute(
        self,
        chapter_number: int,
        state: Optional[NovelState] = None
    ) -> Dict[str, Any]:
        """
        Loads a chapter for review.

        Args:
            chapter_number: Chapter number to load
            state: Optional novel state to update

        Returns:
            Tool result dictionary with chapter content
        """
        project_folder = get_active_project_folder()
        if not project_folder:
            return {
                "success": False,
                "message": "Error: No active project folder."
            }

        filename = f"chapter_{chapter_number:02d}.md"
        file_path = os.path.join(project_folder, "manuscript", filename)

        if not os.path.exists(file_path):
            return {
                "success": False,
                "message": f"Chapter {chapter_number} not found."
            }

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            word_count = len(content.split())

            formatted_content = f"""CHAPTER {chapter_number} FOR REVIEW:

{'='*80}
{content}
{'='*80}

Word Count: {word_count}
"""

            return {
                "success": True,
                "message": f"Loaded Chapter {chapter_number} for review ({word_count} words).",
                "content": formatted_content,
                "chapter_number": chapter_number,
                "word_count": word_count
            }

        except Exception as e:
            return {
                "success": False,
                "message": f"Error loading chapter: {str(e)}"
            }


class LoadContextForCritiqueTool(BaseTool):
    """Tool for loading relevant context for chapter critique."""

    @property
    def name(self) -> str:
        return "load_context_for_critique"

    @property
    def description(self) -> str:
        return """Loads relevant context for critiquing a chapter, including the plan, outline, \
and previous chapters for continuity checking."""

    @property
    def parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "chapter_number": {
                    "type": "integer",
                    "description": "The chapter number being critiqued"
                }
            },
            "required": ["chapter_number"]
        }

    def execute(
        self,
        chapter_number: int,
        state: Optional[NovelState] = None
    ) -> Dict[str, Any]:
        """
        Loads context for critique.

        Args:
            chapter_number: Chapter number being critiqued
            state: Optional novel state to update

        Returns:
            Tool result dictionary with context
        """
        project_folder = get_active_project_folder()
        if not project_folder:
            return {
                "success": False,
                "message": "Error: No active project folder."
            }

        context_parts = []

        # Load outline
        outline_path = os.path.join(project_folder, "planning", "outline.md")
        if os.path.exists(outline_path):
            try:
                with open(outline_path, 'r', encoding='utf-8') as f:
                    outline = f.read()
                    context_parts.append(f"PLOT OUTLINE:\n{'='*80}\n{outline}")
            except:
                pass

        # Load character profiles
        chars_path = os.path.join(project_folder, "planning", "characters.md")
        if os.path.exists(chars_path):
            try:
                with open(chars_path, 'r', encoding='utf-8') as f:
                    chars = f.read()
                    context_parts.append(f"\nCHARACTER PROFILES:\n{'='*80}\n{chars}")
            except:
                pass

        # Load previous chapter if exists
        if chapter_number > 1:
            prev_filename = f"chapter_{chapter_number-1:02d}.md"
            prev_path = os.path.join(project_folder, "manuscript", prev_filename)
            if os.path.exists(prev_path):
                try:
                    with open(prev_path, 'r', encoding='utf-8') as f:
                        prev_chapter = f.read()
                        context_parts.append(f"\nPREVIOUS CHAPTER (Chapter {chapter_number-1}):\n{'='*80}\n{prev_chapter}")
                except:
                    pass

        formatted_content = f"""CONTEXT FOR CRITIQUING CHAPTER {chapter_number}:

{'='*80}
{''.join(context_parts)}
{'='*80}
"""

        return {
            "success": True,
            "message": f"Loaded context for critiquing Chapter {chapter_number}.",
            "content": formatted_content
        }


class CritiqueChapterTool(BaseTool):
    """Tool for providing critique feedback on a chapter."""

    @property
    def name(self) -> str:
        return "critique_chapter"

    @property
    def description(self) -> str:
        return """Provides detailed critique of a chapter. Document issues with plot consistency, \
character behavior, prose quality, pacing, or adherence to the plan. This critique will be saved."""

    @property
    def parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "chapter_number": {
                    "type": "integer",
                    "description": "The chapter number being critiqued"
                },
                "critique_text": {
                    "type": "string",
                    "description": "Detailed critique feedback"
                }
            },
            "required": ["chapter_number", "critique_text"]
        }

    def execute(
        self,
        chapter_number: int,
        critique_text: str,
        state: Optional[NovelState] = None
    ) -> Dict[str, Any]:
        """
        Saves chapter critique.

        Args:
            chapter_number: Chapter number
            critique_text: Critique feedback
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

        # Determine critique version
        version = 1
        if state and chapter_number in state.chapter_critique_iterations:
            version = state.chapter_critique_iterations[chapter_number] + 1
            state.chapter_critique_iterations[chapter_number] = version
        elif state:
            state.chapter_critique_iterations[chapter_number] = 1

        # Save critique
        critique_dir = os.path.join(project_folder, "critiques")
        os.makedirs(critique_dir, exist_ok=True)

        filename = f"chapter_{chapter_number:02d}_critique_v{version}.md"
        file_path = os.path.join(critique_dir, filename)

        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(f"# Chapter {chapter_number} Critique - Version {version}\n\n")
                f.write(f"**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                f.write(f"---\n\n")
                f.write(critique_text)
                f.write("\n")

            if state:
                save_state(state)

            return {
                "success": True,
                "message": f"Critique saved for Chapter {chapter_number} (version {version}).",
                "file_path": file_path,
                "version": version,
                "chapter_number": chapter_number,
                "next_step": "Use approve_chapter to accept it or request_revision to send back for improvements"
            }

        except Exception as e:
            return {
                "success": False,
                "message": f"Error saving critique: {str(e)}"
            }


class ApproveChapterTool(BaseTool):
    """Tool for approving a chapter and moving to next chapter or completion."""

    @property
    def name(self) -> str:
        return "approve_chapter"

    @property
    def description(self) -> str:
        return """Approves a chapter, marking it as complete. If there are more chapters to write, \
transitions back to writing phase for the next chapter. If this is the last chapter, completes the novel."""

    @property
    def parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "chapter_number": {
                    "type": "integer",
                    "description": "The chapter number being approved"
                },
                "approval_notes": {
                    "type": "string",
                    "description": "Notes about why the chapter is approved"
                }
            },
            "required": ["chapter_number", "approval_notes"]
        }

    def execute(
        self,
        chapter_number: int,
        approval_notes: str,
        state: Optional[NovelState] = None
    ) -> Dict[str, Any]:
        """
        Approves a chapter.

        Args:
            chapter_number: Chapter number
            approval_notes: Approval notes
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
        approval_dir = os.path.join(project_folder, "critiques")
        os.makedirs(approval_dir, exist_ok=True)

        filename = f"chapter_{chapter_number:02d}_approval.md"
        file_path = os.path.join(approval_dir, filename)

        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(f"# Chapter {chapter_number} Approval\n\n")
                f.write(f"**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                f.write(f"**Status:** APPROVED\n\n")
                f.write(f"---\n\n")
                f.write(approval_notes)
                f.write("\n")

            # Update state
            is_complete = False
            next_phase_msg = ""

            if state:
                # Mark chapter as completed and approved
                if chapter_number not in state.chapters_completed:
                    state.chapters_completed.append(chapter_number)
                if chapter_number not in state.chapters_approved:
                    state.chapters_approved.append(chapter_number)

                # Check if novel is complete
                if len(state.chapters_approved) >= state.total_chapters:
                    update_phase(state, Phase.COMPLETE)
                    is_complete = True
                    next_phase_msg = "All chapters complete! Novel generation finished."
                else:
                    # Move to next chapter
                    increment_chapter(state)
                    update_phase(state, Phase.WRITING)
                    next_phase_msg = f"Chapter {chapter_number} approved. Moving to Chapter {state.current_chapter}."

                save_state(state)

            return {
                "success": True,
                "message": f"Chapter {chapter_number} approved!",
                "file_path": file_path,
                "is_complete": is_complete,
                "transition": {
                    "to_phase": "COMPLETE" if is_complete else "WRITING",
                    "data": {
                        "chapter_number": chapter_number,
                        "approval_notes": approval_notes
                    }
                },
                "next_phase": next_phase_msg
            }

        except Exception as e:
            return {
                "success": False,
                "message": f"Error approving chapter: {str(e)}"
            }


class RequestRevisionTool(BaseTool):
    """Tool for requesting revisions to a chapter."""

    @property
    def name(self) -> str:
        return "request_revision"

    @property
    def description(self) -> str:
        return """Requests revisions to a chapter. Sends the chapter back to the writing phase \
with specific revision notes. The writer will revise and resubmit the chapter."""

    @property
    def parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "chapter_number": {
                    "type": "integer",
                    "description": "The chapter number requiring revision"
                },
                "revision_notes": {
                    "type": "string",
                    "description": "Specific notes about what needs to be revised"
                }
            },
            "required": ["chapter_number", "revision_notes"]
        }

    def execute(
        self,
        chapter_number: int,
        revision_notes: str,
        state: Optional[NovelState] = None
    ) -> Dict[str, Any]:
        """
        Requests chapter revision.

        Args:
            chapter_number: Chapter number
            revision_notes: Revision requirements
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

        # Check iteration limit
        if state:
            max_iterations = 2  # Default, should come from config
            current_iterations = state.chapter_critique_iterations.get(chapter_number, 0)

            if current_iterations >= max_iterations:
                return {
                    "success": False,
                    "message": f"Maximum critique iterations ({max_iterations}) reached for Chapter {chapter_number}. Auto-approving to prevent infinite loop.",
                    "auto_approve": True
                }

        # Save revision request
        revision_dir = os.path.join(project_folder, "critiques")
        os.makedirs(revision_dir, exist_ok=True)

        version = state.chapter_critique_iterations.get(chapter_number, 0) if state else 0
        filename = f"chapter_{chapter_number:02d}_revision_request_v{version}.md"
        file_path = os.path.join(revision_dir, filename)

        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(f"# Chapter {chapter_number} Revision Request - Version {version}\n\n")
                f.write(f"**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                f.write(f"**Status:** REVISION REQUESTED\n\n")
                f.write(f"---\n\n")
                f.write(revision_notes)
                f.write("\n")

            # Update state - transition back to writing
            if state:
                update_phase(state, Phase.WRITING)
                save_state(state)

            return {
                "success": True,
                "message": f"Revision requested for Chapter {chapter_number}. Transitioning back to writing phase.",
                "file_path": file_path,
                "transition": {
                    "to_phase": "WRITING",
                    "data": {
                        "chapter_number": chapter_number,
                        "revision_notes": revision_notes,
                        "iteration": version
                    }
                },
                "next_phase": f"The Creative Writer will now revise Chapter {chapter_number} based on feedback."
            }

        except Exception as e:
            return {
                "success": False,
                "message": f"Error requesting revision: {str(e)}"
            }


# Registry of all write critique tools
def get_write_critique_tools():
    """Get all write critique phase tools."""
    return [
        LoadChapterForReviewTool(),
        LoadContextForCritiqueTool(),
        CritiqueChapterTool(),
        ApproveChapterTool(),
        RequestRevisionTool()
    ]
