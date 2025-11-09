"""
REST API routes for the Kimi Multi-Agent Novel Writing System.

This module defines all HTTP endpoints for project management, configuration,
and control.
"""

import os
from typing import List, Optional
from fastapi import APIRouter, HTTPException, status
from datetime import datetime

from backend.api.schemas import (
    CreateProjectRequest, UpdateConfigRequest, ApprovalDecisionRequest,
    CustomWritingSampleRequest, ProjectResponse, ProjectListResponse,
    StateResponse, FileListResponse, FileContentResponse,
    WritingSampleResponse, WritingSamplesListResponse,
    SystemPromptResponse, SystemPromptsListResponse,
    ApprovalStatusResponse, ProgressResponse,
    ErrorResponse, SuccessResponse
)
from backend.config import (
    NovelConfig, get_default_config, load_config_from_file,
    save_config_to_file, get_config_path, generate_project_id,
    sanitize_project_name, WritingSampleConfig, CheckpointConfig, AgentConfig
)
from backend.state_manager import (
    NovelState, create_new_state, load_state, save_state,
    get_state_path, get_progress_percentage, approve_checkpoint,
    reject_checkpoint, pause_generation, resume_generation
)
from backend.writing_samples import (
    list_available_samples, get_writing_sample, save_custom_sample
)
from backend.system_prompts import (
    PLANNING_AGENT_BASE_PROMPT, PLAN_CRITIC_AGENT_BASE_PROMPT,
    WRITING_AGENT_BASE_PROMPT, WRITE_CRITIC_AGENT_BASE_PROMPT
)
from backend.utils.file_helpers import list_project_files, read_file

router = APIRouter()


# ============================================================================
# Configuration Endpoints
# ============================================================================

@router.post("/config", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_project(request: CreateProjectRequest):
    """Create a new novel project with configuration."""
    try:
        # Generate project ID and sanitize name
        project_id = generate_project_id()
        sanitized_name = sanitize_project_name(request.project_name)

        # Get API key from environment
        api_key = os.getenv("MOONSHOT_API_KEY")
        if not api_key:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="MOONSHOT_API_KEY not configured"
            )

        # Create config
        config = get_default_config(sanitized_name, request.theme, api_key)
        config.project_id = project_id
        config.novel_length = request.novel_length
        config.genre = request.genre

        # Set writing sample
        if request.writing_sample_id or request.custom_writing_sample:
            config.writing_sample.enabled = True
            if request.custom_writing_sample:
                config.writing_sample.sample_id = 'custom'
                config.writing_sample.custom_text = request.custom_writing_sample
            else:
                config.writing_sample.sample_id = request.writing_sample_id

        # Set agent config
        config.agent.max_plan_critique_iterations = request.max_plan_critique_iterations
        config.agent.max_write_critique_iterations = request.max_write_critique_iterations

        # Set checkpoint config
        config.checkpoints.require_plan_approval = request.require_plan_approval
        config.checkpoints.require_chapter_approval = request.require_chapter_approval

        # Create state
        state = create_new_state(project_id)

        # Ensure output directory exists
        os.makedirs(f"output/{project_id}", exist_ok=True)

        # Save config and state
        save_config_to_file(config, get_config_path(project_id))
        save_state(state)

        return ProjectResponse(
            project_id=project_id,
            project_name=sanitized_name,
            theme=request.theme,
            novel_length=request.novel_length.value,
            genre=request.genre,
            phase=state.phase.value,
            created_at=state.created_at,
            last_updated=state.last_updated,
            progress_percentage=get_progress_percentage(state)
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating project: {str(e)}"
        )


@router.get("/config/{project_id}")
async def get_config(project_id: str):
    """Get project configuration."""
    try:
        config_path = get_config_path(project_id)
        config = load_config_from_file(config_path)
        return config.model_dump(mode='json')
    except FileNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project {project_id} not found"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error loading config: {str(e)}"
        )


@router.put("/config/{project_id}")
async def update_config(project_id: str, request: UpdateConfigRequest):
    """Update project configuration."""
    try:
        config_path = get_config_path(project_id)
        config = load_config_from_file(config_path)

        # Update fields
        if request.novel_length:
            config.novel_length = request.novel_length
        if request.genre:
            config.genre = request.genre
        if request.writing_sample_id is not None:
            config.writing_sample.sample_id = request.writing_sample_id
            config.writing_sample.enabled = bool(request.writing_sample_id)
        if request.custom_writing_sample:
            config.writing_sample.sample_id = 'custom'
            config.writing_sample.custom_text = request.custom_writing_sample
            config.writing_sample.enabled = True
        if request.max_plan_critique_iterations:
            config.agent.max_plan_critique_iterations = request.max_plan_critique_iterations
        if request.max_write_critique_iterations:
            config.agent.max_write_critique_iterations = request.max_write_critique_iterations

        save_config_to_file(config, config_path)

        return SuccessResponse(
            success=True,
            message="Configuration updated successfully"
        )

    except FileNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project {project_id} not found"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating config: {str(e)}"
        )


@router.get("/config/defaults")
async def get_default_configuration():
    """Get default configuration template."""
    api_key = os.getenv("MOONSHOT_API_KEY", "")
    config = get_default_config("example_project", "example theme", api_key)
    return config.model_dump(mode='json')


# ============================================================================
# Project Management Endpoints
# ============================================================================

@router.get("/projects", response_model=ProjectListResponse)
async def list_projects():
    """List all projects."""
    try:
        output_dir = "output"
        if not os.path.exists(output_dir):
            return ProjectListResponse(projects=[], total_count=0)

        projects = []
        for project_id in os.listdir(output_dir):
            project_path = os.path.join(output_dir, project_id)
            if os.path.isdir(project_path):
                try:
                    # Load config and state
                    config = load_config_from_file(get_config_path(project_id))
                    state = load_state(project_id)

                    projects.append(ProjectResponse(
                        project_id=project_id,
                        project_name=config.project_name,
                        theme=config.theme,
                        novel_length=config.novel_length.value,
                        genre=config.genre,
                        phase=state.phase.value,
                        created_at=state.created_at,
                        last_updated=state.last_updated,
                        progress_percentage=get_progress_percentage(state)
                    ))
                except:
                    # Skip projects with missing/corrupt files
                    continue

        # Sort by last_updated descending
        projects.sort(key=lambda x: x.last_updated, reverse=True)

        return ProjectListResponse(
            projects=projects,
            total_count=len(projects)
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error listing projects: {str(e)}"
        )


@router.get("/projects/{project_id}", response_model=ProjectResponse)
async def get_project(project_id: str):
    """Get project details."""
    try:
        config = load_config_from_file(get_config_path(project_id))
        state = load_state(project_id)

        return ProjectResponse(
            project_id=project_id,
            project_name=config.project_name,
            theme=config.theme,
            novel_length=config.novel_length.value,
            genre=config.genre,
            phase=state.phase.value,
            created_at=state.created_at,
            last_updated=state.last_updated,
            progress_percentage=get_progress_percentage(state)
        )

    except FileNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project {project_id} not found"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error loading project: {str(e)}"
        )


@router.delete("/projects/{project_id}")
async def delete_project(project_id: str):
    """Delete a project."""
    try:
        project_path = f"output/{project_id}"
        if not os.path.exists(project_path):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Project {project_id} not found"
            )

        # Delete project directory
        import shutil
        shutil.rmtree(project_path)

        return SuccessResponse(
            success=True,
            message=f"Project {project_id} deleted successfully"
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting project: {str(e)}"
        )


# ============================================================================
# Execution Control Endpoints
# ============================================================================

@router.post("/projects/{project_id}/start")
async def start_generation(project_id: str):
    """Start novel generation (handled by agent_loop in background)."""
    # This endpoint will trigger the agent loop to start
    # Implementation will be in agent_loop.py
    return SuccessResponse(
        success=True,
        message=f"Generation started for project {project_id}",
        data={"project_id": project_id}
    )


@router.post("/projects/{project_id}/pause")
async def pause_project(project_id: str):
    """Pause novel generation."""
    try:
        state = load_state(project_id)
        pause_generation(state)
        save_state(state)

        return SuccessResponse(
            success=True,
            message="Generation paused"
        )

    except FileNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project {project_id} not found"
        )


@router.post("/projects/{project_id}/resume")
async def resume_project(project_id: str):
    """Resume novel generation."""
    try:
        state = load_state(project_id)
        resume_generation(state)
        save_state(state)

        return SuccessResponse(
            success=True,
            message="Generation resumed"
        )

    except FileNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project {project_id} not found"
        )


# ============================================================================
# Approval Endpoints
# ============================================================================

@router.get("/projects/{project_id}/pending-approval", response_model=ApprovalStatusResponse)
async def get_pending_approval(project_id: str):
    """Get pending approval status."""
    try:
        state = load_state(project_id)

        if state.pending_approval:
            return ApprovalStatusResponse(
                has_pending_approval=True,
                approval_type=state.pending_approval.type,
                approval_data=state.pending_approval.data,
                requested_at=state.pending_approval.requested_at
            )
        else:
            return ApprovalStatusResponse(has_pending_approval=False)

    except FileNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project {project_id} not found"
        )


@router.post("/projects/{project_id}/approve")
async def approve_pending(project_id: str, request: ApprovalDecisionRequest):
    """Approve or reject a checkpoint."""
    try:
        state = load_state(project_id)

        if not state.pending_approval:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No pending approval"
            )

        if request.approved:
            approve_checkpoint(state, request.notes)
            message = "Checkpoint approved"
        else:
            reject_checkpoint(state, request.notes or "Rejected by user")
            message = "Checkpoint rejected"

        save_state(state)

        return SuccessResponse(
            success=True,
            message=message
        )

    except FileNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project {project_id} not found"
        )


# ============================================================================
# File Access Endpoints
# ============================================================================

@router.get("/projects/{project_id}/files", response_model=FileListResponse)
async def list_files(project_id: str):
    """List all files in project."""
    try:
        files = list_project_files(project_id)
        return FileListResponse(
            files=files,
            total_count=len(files)
        )
    except:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project {project_id} not found"
        )


@router.get("/projects/{project_id}/files/{file_path:path}", response_model=FileContentResponse)
async def get_file(project_id: str, file_path: str):
    """Get file content."""
    try:
        full_path = f"output/{project_id}/{file_path}"
        content = read_file(full_path)
        size = len(content.encode('utf-8'))

        return FileContentResponse(
            file_path=file_path,
            content=content,
            size=size
        )
    except FileNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"File not found: {file_path}"
        )


# ============================================================================
# Writing Sample Endpoints
# ============================================================================

@router.get("/writing-samples", response_model=WritingSamplesListResponse)
async def get_writing_samples():
    """List available writing samples."""
    samples = list_available_samples()
    sample_responses = [
        WritingSampleResponse(**sample)
        for sample in samples
    ]

    return WritingSamplesListResponse(
        samples=sample_responses,
        total_count=len(sample_responses)
    )


@router.get("/writing-samples/{sample_id}")
async def get_sample(sample_id: str):
    """Get writing sample content."""
    sample_text = get_writing_sample(sample_id)
    if not sample_text:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Writing sample {sample_id} not found"
        )

    return {"sample_id": sample_id, "content": sample_text}


@router.post("/writing-samples/custom")
async def create_custom_sample(request: CustomWritingSampleRequest):
    """Upload custom writing sample."""
    try:
        sample_id = save_custom_sample(
            f"custom_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            request.name,
            request.sample_text,
            request.description or ""
        )

        return SuccessResponse(
            success=True,
            message="Custom sample saved",
            data={"sample_id": sample_id}
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error saving sample: {str(e)}"
        )


# ============================================================================
# System Prompt Endpoints
# ============================================================================

@router.get("/system-prompts", response_model=SystemPromptsListResponse)
async def get_system_prompts():
    """Get all default system prompts."""
    prompts = {
        "planning": PLANNING_AGENT_BASE_PROMPT,
        "plan_critic": PLAN_CRITIC_AGENT_BASE_PROMPT,
        "writing": WRITING_AGENT_BASE_PROMPT,
        "write_critic": WRITE_CRITIC_AGENT_BASE_PROMPT
    }

    return SystemPromptsListResponse(prompts=prompts)


@router.get("/system-prompts/{agent_type}", response_model=SystemPromptResponse)
async def get_system_prompt(agent_type: str):
    """Get system prompt for specific agent."""
    prompts = {
        "planning": PLANNING_AGENT_BASE_PROMPT,
        "plan_critic": PLAN_CRITIC_AGENT_BASE_PROMPT,
        "writing": WRITING_AGENT_BASE_PROMPT,
        "write_critic": WRITE_CRITIC_AGENT_BASE_PROMPT
    }

    if agent_type not in prompts:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Agent type {agent_type} not found"
        )

    return SystemPromptResponse(
        agent_type=agent_type,
        prompt=prompts[agent_type],
        is_custom=False
    )


# ============================================================================
# Status Endpoints
# ============================================================================

@router.get("/projects/{project_id}/status", response_model=StateResponse)
async def get_status(project_id: str):
    """Get current project state."""
    try:
        state = load_state(project_id)

        return StateResponse(
            project_id=project_id,
            phase=state.phase.value,
            plan_approved=state.plan_approved,
            total_chapters=state.total_chapters,
            current_chapter=state.current_chapter,
            chapters_completed=state.chapters_completed,
            chapters_approved=state.chapters_approved,
            paused=state.paused,
            created_at=state.created_at,
            last_updated=state.last_updated,
            progress_percentage=get_progress_percentage(state)
        )

    except FileNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project {project_id} not found"
        )


@router.get("/projects/{project_id}/progress", response_model=ProgressResponse)
async def get_progress(project_id: str):
    """Get progress information."""
    try:
        state = load_state(project_id)

        return ProgressResponse(
            project_id=project_id,
            phase=state.phase.value,
            progress_percentage=get_progress_percentage(state),
            current_chapter=state.current_chapter,
            total_chapters=state.total_chapters,
            chapters_completed=len(state.chapters_completed),
            estimated_completion=state.estimated_completion
        )

    except FileNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project {project_id} not found"
        )
