"""
Writing phase tools for the Creative Writer agent.

These tools are used during Phase 3 (WRITING) to write complete chapters
based on the approved plan.
"""

import os
from typing import Dict, Any, Optional

from backend.tools.base_tool import BaseTool
from backend.tools.project import get_active_project_folder
from backend.state_manager import NovelState, save_state, update_phase
from backend.config import Phase


class LoadApprovedPlanTool(BaseTool):
    """Tool for loading the approved plan materials."""

    @property
    def name(self) -> str:
        return "load_approved_plan"

    @property
    def description(self) -> str:
        return """Loads the approved planning materials (summary, characters, structure, outline) \
to refresh your memory before writing. Use this at the start of writing or when you need to check the plan."""

    @property
    def parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {},
            "required": []
        }

    def execute(self, state: Optional[NovelState] = None) -> Dict[str, Any]:
        """
        Loads the approved plan.

        Args:
            state: Optional novel state to update

        Returns:
            Tool result dictionary with plan content
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
        for key, rel_path in files_to_load.items():
            file_path = os.path.join(project_folder, rel_path)
            if os.path.exists(file_path):
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        loaded_content[key] = f.read()
                except Exception as e:
                    loaded_content[key] = f"Error reading file: {str(e)}"

        formatted_content = f"""APPROVED PLAN - REFERENCE FOR WRITING:

{'='*80}
{loaded_content.get('summary', 'Summary not found')}

{'='*80}
{loaded_content.get('characters', 'Characters not found')}

{'='*80}
{loaded_content.get('structure', 'Structure not found')}

{'='*80}
{loaded_content.get('outline', 'Outline not found')}

{'='*80}
"""

        return {
            "success": True,
            "message": "Successfully loaded approved plan materials.",
            "content": formatted_content
        }


class GetChapterContextTool(BaseTool):
    """Tool for getting specific context for a chapter."""

    @property
    def name(self) -> str:
        return "get_chapter_context"

    @property
    def description(self) -> str:
        return """Gets the specific outline and context for a particular chapter. \
Use this to see what should happen in the chapter you're about to write."""

    @property
    def parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "chapter_number": {
                    "type": "integer",
                    "description": "The chapter number to get context for (1-indexed)"
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
        Gets chapter-specific context.

        Args:
            chapter_number: Chapter number (1-indexed)
            state: Optional novel state to update

        Returns:
            Tool result dictionary with chapter context
        """
        project_folder = get_active_project_folder()
        if not project_folder:
            return {
                "success": False,
                "message": "Error: No active project folder."
            }

        # Load outline
        outline_path = os.path.join(project_folder, "planning", "outline.md")
        if not os.path.exists(outline_path):
            return {
                "success": False,
                "message": "Outline file not found."
            }

        try:
            with open(outline_path, 'r', encoding='utf-8') as f:
                outline_content = f.read()

            # Update state
            if state:
                state.current_chapter = chapter_number
                if chapter_number not in state.chapter_critique_iterations:
                    state.chapter_critique_iterations[chapter_number] = 0
                save_state(state)

            return {
                "success": True,
                "message": f"Context loaded for Chapter {chapter_number}",
                "content": f"""CHAPTER {chapter_number} CONTEXT:

Full outline for reference:
{outline_content}

NOTE: Focus on the section for Chapter {chapter_number} when writing.
""",
                "chapter_number": chapter_number
            }

        except Exception as e:
            return {
                "success": False,
                "message": f"Error loading context: {str(e)}"
            }


class WriteChapterTool(BaseTool):
    """Tool for writing a complete chapter."""

    @property
    def name(self) -> str:
        return "write_chapter"

    @property
    def description(self) -> str:
        return """Writes a complete chapter to a file. The chapter should be substantial (2,500-5,000+ words), \
fully developed with scenes, dialogue, and description. Creates the file in the manuscript directory."""

    @property
    def parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "chapter_number": {
                    "type": "integer",
                    "description": "The chapter number (used for filename)"
                },
                "content": {
                    "type": "string",
                    "description": "The complete chapter content"
                }
            },
            "required": ["chapter_number", "content"]
        }

    def execute(
        self,
        chapter_number: int,
        content: str,
        state: Optional[NovelState] = None
    ) -> Dict[str, Any]:
        """
        Writes a chapter file.

        Args:
            chapter_number: Chapter number
            content: Chapter content
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

        # Format chapter filename
        filename = f"chapter_{chapter_number:02d}.md"
        file_path = os.path.join(project_folder, "manuscript", filename)
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(f"# Chapter {chapter_number}\n\n")
                f.write(content)
                f.write("\n")

            word_count = len(content.split())

            return {
                "success": True,
                "message": f"Successfully wrote Chapter {chapter_number} ({word_count} words) to manuscript/{filename}",
                "file_path": file_path,
                "filename": filename,
                "chapter_number": chapter_number,
                "word_count": word_count,
                "next_step": "Use finalize_chapter to submit this chapter for critique"
            }

        except Exception as e:
            return {
                "success": False,
                "message": f"Error writing chapter: {str(e)}"
            }


class ReviewPreviousWritingTool(BaseTool):
    """Tool for reviewing previously written chapters."""

    @property
    def name(self) -> str:
        return "review_previous_writing"

    @property
    def description(self) -> str:
        return """Loads and displays previously written chapters for continuity checking. \
Use this to maintain consistency in voice, plot, and character development."""

    @property
    def parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "chapter_range": {
                    "type": "string",
                    "description": "Chapter range to review (e.g., '1-3' or 'all' or '5')"
                }
            },
            "required": ["chapter_range"]
        }

    def execute(
        self,
        chapter_range: str,
        state: Optional[NovelState] = None
    ) -> Dict[str, Any]:
        """
        Reviews previous chapters.

        Args:
            chapter_range: Chapter range specification
            state: Optional novel state to update

        Returns:
            Tool result dictionary with previous chapters
        """
        project_folder = get_active_project_folder()
        if not project_folder:
            return {
                "success": False,
                "message": "Error: No active project folder."
            }

        manuscript_dir = os.path.join(project_folder, "manuscript")
        if not os.path.exists(manuscript_dir):
            return {
                "success": False,
                "message": "No manuscript directory found. No chapters written yet."
            }

        # Parse chapter range
        chapters_to_load = []
        if chapter_range.lower() == 'all':
            # Load all chapters
            for file in sorted(os.listdir(manuscript_dir)):
                if file.startswith('chapter_') and file.endswith('.md'):
                    chapters_to_load.append(file)
        elif '-' in chapter_range:
            # Range like "1-3"
            try:
                start, end = map(int, chapter_range.split('-'))
                for i in range(start, end + 1):
                    chapters_to_load.append(f"chapter_{i:02d}.md")
            except:
                return {
                    "success": False,
                    "message": f"Invalid chapter range format: {chapter_range}"
                }
        else:
            # Single chapter
            try:
                num = int(chapter_range)
                chapters_to_load.append(f"chapter_{num:02d}.md")
            except:
                return {
                    "success": False,
                    "message": f"Invalid chapter number: {chapter_range}"
                }

        # Load chapters
        loaded_chapters = []
        for filename in chapters_to_load:
            file_path = os.path.join(manuscript_dir, filename)
            if os.path.exists(file_path):
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        loaded_chapters.append(f"\n{'='*80}\n{filename}\n{'='*80}\n{content}")
                except Exception as e:
                    loaded_chapters.append(f"\nError loading {filename}: {str(e)}")

        if not loaded_chapters:
            return {
                "success": False,
                "message": f"No chapters found for range: {chapter_range}"
            }

        formatted_content = f"""PREVIOUS CHAPTERS FOR REVIEW:

{''.join(loaded_chapters)}

{'='*80}
END OF PREVIOUS CHAPTERS
{'='*80}
"""

        return {
            "success": True,
            "message": f"Loaded {len(loaded_chapters)} chapter(s) for review.",
            "content": formatted_content,
            "chapters_loaded": len(loaded_chapters)
        }


class FinalizeChapterTool(BaseTool):
    """Tool for finalizing a chapter and submitting for critique."""

    @property
    def name(self) -> str:
        return "finalize_chapter"

    @property
    def description(self) -> str:
        return """Finalizes a chapter and submits it for critique. Call this after writing a complete chapter. \
This transitions to the write critique phase for this specific chapter."""

    @property
    def parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "chapter_number": {
                    "type": "integer",
                    "description": "The chapter number being finalized"
                },
                "notes": {
                    "type": "string",
                    "description": "Optional notes about the chapter"
                }
            },
            "required": ["chapter_number"]
        }

    def execute(
        self,
        chapter_number: int,
        notes: str = "",
        state: Optional[NovelState] = None
    ) -> Dict[str, Any]:
        """
        Finalizes a chapter.

        Args:
            chapter_number: Chapter number
            notes: Optional notes
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

        # Verify chapter exists
        filename = f"chapter_{chapter_number:02d}.md"
        file_path = os.path.join(project_folder, "manuscript", filename)

        if not os.path.exists(file_path):
            return {
                "success": False,
                "message": f"Chapter {chapter_number} not found. Write the chapter first using write_chapter."
            }

        # Update state
        if state:
            update_phase(state, Phase.WRITE_CRITIQUE)
            state.current_chapter = chapter_number
            save_state(state)

        return {
            "success": True,
            "message": f"Chapter {chapter_number} finalized and submitted for critique.",
            "transition": {
                "to_phase": "WRITE_CRITIQUE",
                "data": {
                    "chapter_number": chapter_number,
                    "notes": notes
                }
            },
            "next_phase": f"The Chapter Editor will now review Chapter {chapter_number}."
        }


# Registry of all writing tools
def get_writing_tools():
    """Get all writing phase tools."""
    return [
        LoadApprovedPlanTool(),
        GetChapterContextTool(),
        WriteChapterTool(),
        ReviewPreviousWritingTool(),
        FinalizeChapterTool()
    ]
