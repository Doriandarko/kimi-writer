"""
File writing tool for creating and managing markdown files.

Migrated from tools/writer.py with updates for multi-agent architecture.
"""

import os
from typing import Literal, Dict, Any, Optional

from backend.tools.base_tool import BaseTool
from backend.tools.project import get_active_project_folder
from backend.state_manager import NovelState, save_state


class WriteFileTool(BaseTool):
    """Tool for writing files in the project directory."""

    @property
    def name(self) -> str:
        return "write_file"

    @property
    def description(self) -> str:
        return """Writes content to a markdown file in the active project folder. \
Supports three modes: 'create' (creates new file, fails if exists), 'append' (adds content to end of existing file), \
'overwrite' (replaces entire file content)."""

    @property
    def parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "filename": {
                    "type": "string",
                    "description": "The name of the markdown file to write (should end in .md)"
                },
                "content": {
                    "type": "string",
                    "description": "The content to write to the file"
                },
                "mode": {
                    "type": "string",
                    "enum": ["create", "append", "overwrite"],
                    "description": "The write mode: 'create' for new files, 'append' to add to existing, 'overwrite' to replace"
                }
            },
            "required": ["filename", "content", "mode"]
        }

    def execute(
        self,
        filename: str,
        content: str,
        mode: Literal["create", "append", "overwrite"],
        state: Optional[NovelState] = None
    ) -> Dict[str, Any]:
        """
        Writes content to a markdown file.

        Args:
            filename: The name of the file to write
            content: The content to write
            mode: The write mode - 'create', 'append', or 'overwrite'
            state: Optional novel state to update

        Returns:
            Tool result dictionary
        """
        # Check if project folder is initialized
        project_folder = get_active_project_folder()
        if not project_folder:
            return {
                "success": False,
                "message": "Error: No active project folder. Please create a project first using create_project."
            }

        # Ensure filename ends with .md
        if not filename.endswith('.md'):
            filename = filename + '.md'

        # Create full file path
        file_path = os.path.join(project_folder, filename)

        try:
            if mode == "create":
                # Create mode: fail if file exists
                if os.path.exists(file_path):
                    return {
                        "success": False,
                        "message": f"Error: File '{filename}' already exists. Use 'append' or 'overwrite' mode to modify it."
                    }

                # Ensure parent directory exists
                os.makedirs(os.path.dirname(file_path), exist_ok=True)

                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)

                result = {
                    "success": True,
                    "message": f"Successfully created file '{filename}' with {len(content)} characters.",
                    "file_path": file_path,
                    "filename": filename,
                    "operation": "create"
                }

            elif mode == "append":
                # Append mode: add to end of file
                with open(file_path, 'a', encoding='utf-8') as f:
                    f.write(content)

                result = {
                    "success": True,
                    "message": f"Successfully appended {len(content)} characters to '{filename}'.",
                    "file_path": file_path,
                    "filename": filename,
                    "operation": "append"
                }

            elif mode == "overwrite":
                # Overwrite mode: replace entire file
                os.makedirs(os.path.dirname(file_path), exist_ok=True)

                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)

                result = {
                    "success": True,
                    "message": f"Successfully overwrote '{filename}' with {len(content)} characters.",
                    "file_path": file_path,
                    "filename": filename,
                    "operation": "overwrite"
                }

            else:
                return {
                    "success": False,
                    "message": f"Error: Invalid mode '{mode}'. Use 'create', 'append', or 'overwrite'."
                }

            # Update state if provided
            if state and mode == "create":
                # Track created files in state
                relative_path = os.path.relpath(file_path, project_folder)
                if hasattr(state, 'plan_files_created') and isinstance(state.plan_files_created, dict):
                    state.plan_files_created[relative_path] = True
                    save_state(state)

            return result

        except Exception as e:
            return {
                "success": False,
                "message": f"Error writing file '{filename}': {str(e)}"
            }


# For backward compatibility
def write_file_impl(filename: str, content: str, mode: Literal["create", "append", "overwrite"]) -> str:
    """
    Legacy implementation for backward compatibility.

    Args:
        filename: The name of the file to write
        content: The content to write
        mode: The write mode

    Returns:
        Success message or error message
    """
    tool = WriteFileTool()
    result = tool.execute(filename, content, mode)
    return result["message"]
