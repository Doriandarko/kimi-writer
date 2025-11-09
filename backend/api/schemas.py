"""
Pydantic schemas for API requests and responses.

This module defines the data models used in the REST API.
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field

from backend.config import NovelLength, Phase


# Request Schemas

class CreateProjectRequest(BaseModel):
    """Request to create a new novel project."""
    project_name: str = Field(..., min_length=1, max_length=100)
    theme: str = Field(..., min_length=1)
    novel_length: NovelLength = NovelLength.NOVEL
    genre: Optional[str] = None
    writing_sample_id: Optional[str] = None
    custom_writing_sample: Optional[str] = None
    max_plan_critique_iterations: int = Field(default=2, ge=1, le=10)
    max_write_critique_iterations: int = Field(default=2, ge=1, le=10)
    require_plan_approval: bool = True
    require_chapter_approval: bool = False


class UpdateConfigRequest(BaseModel):
    """Request to update project configuration."""
    novel_length: Optional[NovelLength] = None
    genre: Optional[str] = None
    writing_sample_id: Optional[str] = None
    custom_writing_sample: Optional[str] = None
    max_plan_critique_iterations: Optional[int] = Field(None, ge=1, le=10)
    max_write_critique_iterations: Optional[int] = Field(None, ge=1, le=10)


class ApprovalDecisionRequest(BaseModel):
    """Request to approve or reject a checkpoint."""
    approved: bool
    notes: Optional[str] = None


class CustomWritingSampleRequest(BaseModel):
    """Request to save a custom writing sample."""
    name: str
    sample_text: str = Field(..., min_length=100)
    description: Optional[str] = None


# Response Schemas

class ProjectResponse(BaseModel):
    """Response containing project information."""
    project_id: str
    project_name: str
    theme: str
    novel_length: str
    genre: Optional[str]
    phase: str
    created_at: datetime
    last_updated: datetime
    progress_percentage: float


class ProjectListResponse(BaseModel):
    """Response containing list of projects."""
    projects: List[ProjectResponse]
    total_count: int


class StateResponse(BaseModel):
    """Response containing project state."""
    project_id: str
    phase: str
    plan_approved: bool
    total_chapters: int
    current_chapter: int
    chapters_completed: List[int]
    chapters_approved: List[int]
    paused: bool
    created_at: datetime
    last_updated: datetime
    progress_percentage: float


class FileListResponse(BaseModel):
    """Response containing list of project files."""
    files: List[str]
    total_count: int


class FileContentResponse(BaseModel):
    """Response containing file content."""
    file_path: str
    content: str
    size: int


class WritingSampleResponse(BaseModel):
    """Response containing writing sample information."""
    id: str
    name: str
    description: str
    source: Optional[str] = None


class WritingSamplesListResponse(BaseModel):
    """Response containing list of writing samples."""
    samples: List[WritingSampleResponse]
    total_count: int


class SystemPromptResponse(BaseModel):
    """Response containing system prompt."""
    agent_type: str
    prompt: str
    is_custom: bool


class SystemPromptsListResponse(BaseModel):
    """Response containing all system prompts."""
    prompts: Dict[str, str]


class ApprovalStatusResponse(BaseModel):
    """Response containing pending approval status."""
    has_pending_approval: bool
    approval_type: Optional[str] = None
    approval_data: Optional[Dict[str, Any]] = None
    requested_at: Optional[datetime] = None


class ProgressResponse(BaseModel):
    """Response containing progress information."""
    project_id: str
    phase: str
    progress_percentage: float
    current_chapter: int
    total_chapters: int
    chapters_completed: int
    estimated_completion: Optional[datetime] = None


class ErrorResponse(BaseModel):
    """Error response."""
    error: str
    detail: Optional[str] = None
    error_type: Optional[str] = None


class SuccessResponse(BaseModel):
    """Generic success response."""
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None


class GenerationStatsResponse(BaseModel):
    """Response containing generation statistics."""
    project_id: str
    total_iterations: int
    plan_critique_iterations: int
    average_chapter_critique_iterations: float
    total_words_written: int
    time_elapsed: float
    phase_transitions: List[Dict[str, Any]]
    compressions: int
