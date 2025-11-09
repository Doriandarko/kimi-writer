"""
Project folder management tool.

Migrated from tools/project.py with updates for multi-agent architecture.
"""

import os
import re
from typing import Optional, Dict, Any

from backend.tools.base_tool import BaseTool
from backend.state_manager import NovelState, save_state


# Global variable to track the active project folder
_active_project_folder: Optional[str] = None


def sanitize_folder_name(name: str) -> str:
    """
    Sanitizes a folder name for filesystem compatibility.

    Args:
        name: The proposed folder name

    Returns:
        Sanitized folder name
    """
    # Replace spaces with underscores
    name = name.strip().replace(' ', '_')
    # Remove any characters that aren't alphanumeric, underscore, or hyphen
    name = re.sub(r'[^\w\-]', '', name)
    # Remove leading/trailing hyphens or underscores
    name = name.strip('-_')
    # Ensure it's not empty
    if not name:
        name = "untitled_project"
    return name


def get_active_project_folder() -> Optional[str]:
    """
    Returns the currently active project folder path.

    Returns:
        Path to active project folder or None if not set
    """
    return _active_project_folder


def set_active_project_folder(folder_path: str) -> None:
    """
    Sets the active project folder.

    Args:
        folder_path: Path to the project folder
    """
    global _active_project_folder
    _active_project_folder = folder_path


class CreateProjectTool(BaseTool):
    """Tool for creating project folders."""

    @property
    def name(self) -> str:
        return "create_project"

    @property
    def description(self) -> str:
        return """Creates a new project folder in the 'output' directory with a sanitized name. \
This should be called first before writing any files. Only one project can be active at a time."""

    @property
    def parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "project_name": {
                    "type": "string",
                    "description": "The name for the project folder (will be sanitized for filesystem compatibility)"
                }
            },
            "required": ["project_name"]
        }

    def execute(self, project_name: str, state: Optional[NovelState] = None) -> Dict[str, Any]:
        """
        Creates a new project folder.

        Args:
            project_name: The desired project name
            state: Optional novel state to update

        Returns:
            Tool result dictionary
        """
        global _active_project_folder

        # Sanitize the folder name
        sanitized_name = sanitize_folder_name(project_name)

        # Get the backend directory
        backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        root_dir = os.path.dirname(backend_dir)

        # Create output directory if it doesn't exist
        output_dir = os.path.join(root_dir, "output")
        if not os.path.exists(output_dir):
            try:
                os.makedirs(output_dir, exist_ok=True)
            except Exception as e:
                return {
                    "success": False,
                    "message": f"Error creating output directory: {str(e)}"
                }

        # Create the full path inside output directory
        project_path = os.path.join(output_dir, sanitized_name)

        # Check if folder already exists
        if os.path.exists(project_path):
            # Use existing folder and set it as active
            _active_project_folder = project_path
            return {
                "success": True,
                "message": f"Project folder already exists at '{project_path}'. Set as active project folder.",
                "project_path": project_path,
                "project_name": sanitized_name
            }

        # Create the folder
        try:
            os.makedirs(project_path, exist_ok=True)
            _active_project_folder = project_path

            # Create subdirectories for organization
            subdirs = ['planning', 'manuscript', 'critiques']
            for subdir in subdirs:
                os.makedirs(os.path.join(project_path, subdir), exist_ok=True)

            return {
                "success": True,
                "message": f"Successfully created project folder at '{project_path}'. This is now the active project folder.",
                "project_path": project_path,
                "project_name": sanitized_name
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Error creating project folder: {str(e)}"
            }


# For backward compatibility
def create_project_impl(project_name: str) -> str:
    """
    Legacy implementation for backward compatibility.

    Args:
        project_name: The desired project name

    Returns:
        Success message with folder path or error message
    """
    tool = CreateProjectTool()
    result = tool.execute(project_name)
    return result["message"]
