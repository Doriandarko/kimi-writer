"""
Configuration management for the Kimi Multi-Agent Novel Writing System.

This module provides Pydantic models for all configuration needs:
- NovelConfig: Main configuration for novel generation
- AgentConfig: Agent-specific settings (prompts, iterations)
- WritingSampleConfig: Writing sample selection
- CheckpointConfig: Approval checkpoint settings
- APIConfig: Moonshot AI API credentials and settings
"""

import json
import os
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field, field_validator


class NovelLength(str, Enum):
    """Enum for novel length options."""
    SHORT_STORY = "short_story"  # 3,000-10,000 words (1-5 chapters)
    NOVELLA = "novella"  # 20,000-50,000 words (5-15 chapters)
    NOVEL = "novel"  # 50,000-110,000 words (15-30 chapters)
    LONG_NOVEL = "long_novel"  # 110,000-200,000 words (30-50 chapters)
    AI_DECIDE = "ai_decide"  # Let AI determine based on story needs


class Phase(str, Enum):
    """Enum for workflow phases."""
    PLANNING = "PLANNING"
    PLAN_CRITIQUE = "PLAN_CRITIQUE"
    WRITING = "WRITING"
    WRITE_CRITIQUE = "WRITE_CRITIQUE"
    COMPLETE = "COMPLETE"


class WritingSampleConfig(BaseModel):
    """Configuration for writing sample selection."""
    sample_id: Optional[str] = None  # Preset sample ID or 'custom'
    custom_text: Optional[str] = None  # Custom sample text if sample_id is 'custom'
    enabled: bool = False  # Whether to use writing sample

    @field_validator('custom_text')
    @classmethod
    def validate_custom_text(cls, v, info):
        """Validate custom text length."""
        if v and len(v) < 100:
            raise ValueError("Custom writing sample must be at least 100 characters")
        return v


class CheckpointConfig(BaseModel):
    """Configuration for approval checkpoints."""
    require_plan_approval: bool = True  # Approval after planning phase
    require_plan_critique_approval: bool = False  # Approval after each plan critique
    require_chapter_approval: bool = False  # Approval after each chapter
    require_chapter_critique_approval: bool = False  # Approval after each critique


class AgentConfig(BaseModel):
    """Configuration for agent behavior."""
    max_plan_critique_iterations: int = Field(default=2, ge=1, le=10)
    max_write_critique_iterations: int = Field(default=2, ge=1, le=10)

    # System prompt overrides (None = use defaults)
    planning_prompt_override: Optional[str] = None
    plan_critic_prompt_override: Optional[str] = None
    writing_prompt_override: Optional[str] = None
    write_critic_prompt_override: Optional[str] = None


class APIConfig(BaseModel):
    """Configuration for Moonshot AI API."""
    api_key: str
    base_url: str = "https://api.moonshot.ai/v1"
    model_name: str = "kimi-k2-thinking"
    token_limit: int = 200000
    compression_threshold: int = 180000  # Start compression at 90% of limit
    max_iterations: int = 300  # Safety limit for infinite loops


class NovelConfig(BaseModel):
    """Main configuration for novel generation."""
    # Project identification
    project_id: str
    project_name: str

    # Novel parameters
    novel_length: NovelLength = NovelLength.NOVEL
    theme: str = ""  # User's initial prompt/theme
    genre: Optional[str] = None

    # Sub-configurations
    writing_sample: WritingSampleConfig = Field(default_factory=WritingSampleConfig)
    checkpoints: CheckpointConfig = Field(default_factory=CheckpointConfig)
    agent: AgentConfig = Field(default_factory=AgentConfig)
    api: APIConfig

    # Metadata
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)


def generate_project_id() -> str:
    """Generate a unique project ID based on timestamp."""
    return f"novel_{datetime.now().strftime('%Y%m%d_%H%M%S')}"


def sanitize_project_name(name: str) -> str:
    """Sanitize project name for filesystem compatibility."""
    # Replace spaces and special characters
    sanitized = "".join(c if c.isalnum() or c in (' ', '-', '_') else '_' for c in name)
    # Replace multiple spaces/underscores with single underscore
    sanitized = '_'.join(sanitized.split())
    # Lowercase and limit length
    sanitized = sanitized.lower()[:50]
    return sanitized


def load_config_from_file(path: str) -> NovelConfig:
    """
    Load configuration from a JSON file.

    Args:
        path: Path to config file

    Returns:
        NovelConfig instance

    Raises:
        FileNotFoundError: If config file doesn't exist
        ValueError: If config file is invalid
    """
    if not os.path.exists(path):
        raise FileNotFoundError(f"Config file not found: {path}")

    try:
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return NovelConfig(**data)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in config file: {e}")
    except Exception as e:
        raise ValueError(f"Error loading config: {e}")


def save_config_to_file(config: NovelConfig, path: str) -> None:
    """
    Save configuration to a JSON file.

    Args:
        config: NovelConfig instance
        path: Path to save config file
    """
    # Update timestamp
    config.updated_at = datetime.now()

    # Ensure parent directory exists
    os.makedirs(os.path.dirname(path), exist_ok=True)

    # Write config
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(
            config.model_dump(mode='json'),
            f,
            indent=2,
            ensure_ascii=False
        )


def validate_config(config: NovelConfig) -> bool:
    """
    Validate configuration.

    Args:
        config: NovelConfig instance

    Returns:
        True if valid

    Raises:
        ValueError: If configuration is invalid
    """
    # Validate API key
    if not config.api.api_key:
        raise ValueError("API key is required")

    # Validate project name
    if not config.project_name:
        raise ValueError("Project name is required")

    # Validate writing sample
    if config.writing_sample.enabled:
        if not config.writing_sample.sample_id:
            raise ValueError("Writing sample ID required when enabled")
        if config.writing_sample.sample_id == 'custom' and not config.writing_sample.custom_text:
            raise ValueError("Custom text required when sample_id is 'custom'")

    return True


def get_default_config(
    project_name: str,
    theme: str,
    api_key: str
) -> NovelConfig:
    """
    Get default configuration with minimal user input.

    Args:
        project_name: Name for the project
        theme: User's theme/prompt
        api_key: Moonshot API key

    Returns:
        NovelConfig with default settings
    """
    project_id = generate_project_id()
    sanitized_name = sanitize_project_name(project_name)

    return NovelConfig(
        project_id=project_id,
        project_name=sanitized_name,
        theme=theme,
        api=APIConfig(api_key=api_key)
    )


def get_config_path(project_id: str) -> str:
    """
    Get path to config file for a project.

    Args:
        project_id: Project ID

    Returns:
        Path to config file
    """
    return f"output/{project_id}/.novel_config.json"


def load_or_create_config(
    project_id: Optional[str] = None,
    project_name: Optional[str] = None,
    theme: Optional[str] = None,
    api_key: Optional[str] = None
) -> NovelConfig:
    """
    Load existing config or create new one.

    Args:
        project_id: Existing project ID (if loading)
        project_name: New project name (if creating)
        theme: Theme/prompt (if creating)
        api_key: API key (if creating)

    Returns:
        NovelConfig instance
    """
    if project_id:
        # Load existing
        config_path = get_config_path(project_id)
        return load_config_from_file(config_path)
    else:
        # Create new
        if not all([project_name, theme, api_key]):
            raise ValueError("project_name, theme, and api_key required for new project")
        return get_default_config(project_name, theme, api_key)
