"""
File I/O utilities for the Kimi Multi-Agent Novel Writing System.

This module provides helper functions for reading and writing files
in the project structure.
"""

import os
from typing import Optional


def read_file(file_path: str) -> str:
    """
    Read file content.

    Args:
        file_path: Path to file

    Returns:
        File content

    Raises:
        FileNotFoundError: If file doesn't exist
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()


def write_file(file_path: str, content: str) -> None:
    """
    Write content to file.

    Args:
        file_path: Path to file
        content: Content to write
    """
    # Ensure parent directory exists
    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)


def append_to_file(file_path: str, content: str) -> None:
    """
    Append content to file.

    Args:
        file_path: Path to file
        content: Content to append
    """
    # Ensure parent directory exists
    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    with open(file_path, 'a', encoding='utf-8') as f:
        f.write(content)


def file_exists(file_path: str) -> bool:
    """
    Check if file exists.

    Args:
        file_path: Path to file

    Returns:
        True if file exists
    """
    return os.path.exists(file_path)


def get_project_root() -> str:
    """
    Get project root directory.

    Returns:
        Path to project root
    """
    # Assuming this file is in backend/utils/
    current_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.dirname(os.path.dirname(current_dir))


def get_output_dir() -> str:
    """
    Get output directory.

    Returns:
        Path to output directory
    """
    return os.path.join(get_project_root(), 'output')


def ensure_project_dir(project_id: str) -> str:
    """
    Ensure project directory exists.

    Args:
        project_id: Project ID

    Returns:
        Path to project directory
    """
    project_dir = os.path.join(get_output_dir(), project_id)
    os.makedirs(project_dir, exist_ok=True)
    return project_dir


def list_project_files(project_id: str) -> list:
    """
    List all files in a project.

    Args:
        project_id: Project ID

    Returns:
        List of file paths relative to project directory
    """
    project_dir = os.path.join(get_output_dir(), project_id)

    if not os.path.exists(project_dir):
        return []

    files = []
    for root, dirs, filenames in os.walk(project_dir):
        # Skip hidden files and directories
        dirs[:] = [d for d in dirs if not d.startswith('.')]
        for filename in filenames:
            if not filename.startswith('.'):
                full_path = os.path.join(root, filename)
                rel_path = os.path.relpath(full_path, project_dir)
                files.append(rel_path)

    return sorted(files)
