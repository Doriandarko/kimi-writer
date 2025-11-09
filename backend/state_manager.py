"""
State management for the Kimi Multi-Agent Novel Writing System.

This module handles tracking of novel generation progress across all phases,
including planning, critiquing, writing, and approvals.
"""

import json
import os
from datetime import datetime
from typing import Optional, Dict, List, Any
from pydantic import BaseModel, Field

from backend.config import Phase


class ApprovalRequest(BaseModel):
    """Pending approval request."""
    type: str  # "plan", "plan_critique", "chapter", "chapter_critique"
    data: Dict[str, Any]  # Additional data for the approval
    requested_at: datetime = Field(default_factory=datetime.now)


class DeviationLogEntry(BaseModel):
    """Log entry for plan deviations."""
    chapter_number: Optional[int] = None
    deviation_type: str  # "plot", "character", "structure"
    description: str
    timestamp: datetime = Field(default_factory=datetime.now)


class ErrorLogEntry(BaseModel):
    """Log entry for errors encountered."""
    error_type: str
    error_message: str
    phase: str
    timestamp: datetime = Field(default_factory=datetime.now)


class NovelState(BaseModel):
    """
    Comprehensive state tracking for novel generation.

    This tracks progress through all phases, handles approvals,
    and maintains metadata about the generation process.
    """
    # Core identification
    project_id: str
    phase: Phase = Phase.PLANNING

    # Planning phase tracking
    plan_approved: bool = False
    plan_critique_iterations: int = 0
    plan_files_created: Dict[str, bool] = Field(default_factory=dict)  # {filename: exists}

    # Writing phase tracking
    total_chapters: int = 0  # Determined during planning
    current_chapter: int = 0  # Currently being worked on
    chapters_completed: List[int] = Field(default_factory=list)
    chapters_approved: List[int] = Field(default_factory=list)
    chapter_critique_iterations: Dict[int, int] = Field(default_factory=dict)  # {chapter_num: count}

    # Approval system
    pending_approval: Optional[ApprovalRequest] = None
    approval_history: List[Dict[str, Any]] = Field(default_factory=list)

    # Progress tracking
    created_at: datetime = Field(default_factory=datetime.now)
    last_updated: datetime = Field(default_factory=datetime.now)
    estimated_completion: Optional[datetime] = None
    paused: bool = False
    paused_at: Optional[datetime] = None

    # Logs and metadata
    deviations_log: List[DeviationLogEntry] = Field(default_factory=list)
    error_log: List[ErrorLogEntry] = Field(default_factory=list)
    generation_stats: Dict[str, Any] = Field(default_factory=dict)

    # Agent iteration tracking
    current_agent_iterations: int = 0  # Iterations in current phase
    total_iterations: int = 0  # Total iterations across all phases


def get_state_path(project_id: str) -> str:
    """
    Get path to state file for a project.

    Args:
        project_id: Project ID

    Returns:
        Path to state file
    """
    return f"output/{project_id}/.novel_state.json"


def load_state(project_id: str) -> NovelState:
    """
    Load state from file.

    Args:
        project_id: Project ID

    Returns:
        NovelState instance

    Raises:
        FileNotFoundError: If state file doesn't exist
        ValueError: If state file is corrupted
    """
    state_path = get_state_path(project_id)

    if not os.path.exists(state_path):
        raise FileNotFoundError(f"State file not found: {state_path}")

    try:
        with open(state_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return NovelState(**data)
    except json.JSONDecodeError as e:
        raise ValueError(f"Corrupted state file for project {project_id}: {e}")
    except Exception as e:
        raise ValueError(f"Error loading state: {e}")


def save_state(state: NovelState) -> None:
    """
    Save state to file.

    Args:
        state: NovelState instance
    """
    # Update timestamp
    state.last_updated = datetime.now()

    # Get state path
    state_path = get_state_path(state.project_id)

    # Ensure parent directory exists
    os.makedirs(os.path.dirname(state_path), exist_ok=True)

    # Write state with backup
    _write_state_with_backup(state, state_path)


def _write_state_with_backup(state: NovelState, path: str) -> None:
    """
    Write state file with backup to prevent corruption.

    Args:
        state: NovelState instance
        path: Path to state file
    """
    # Create backup if file exists
    if os.path.exists(path):
        backup_path = f"{path}.backup"
        try:
            with open(path, 'r') as f_src, open(backup_path, 'w') as f_dst:
                f_dst.write(f_src.read())
        except Exception:
            pass  # Backup is best-effort

    # Write new state
    try:
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(
                state.model_dump(mode='json'),
                f,
                indent=2,
                ensure_ascii=False
            )
    except Exception as e:
        # Attempt to restore from backup
        backup_path = f"{path}.backup"
        if os.path.exists(backup_path):
            with open(backup_path, 'r') as f_src, open(path, 'w') as f_dst:
                f_dst.write(f_src.read())
        raise e


def create_new_state(project_id: str) -> NovelState:
    """
    Create new state for a project.

    Args:
        project_id: Project ID

    Returns:
        New NovelState instance
    """
    return NovelState(project_id=project_id)


def update_phase(state: NovelState, new_phase: Phase) -> NovelState:
    """
    Update current phase and reset phase-specific tracking.

    Args:
        state: Current state
        new_phase: New phase to transition to

    Returns:
        Updated state
    """
    old_phase = state.phase
    state.phase = new_phase
    state.current_agent_iterations = 0

    # Log phase transition in generation stats
    if 'phase_transitions' not in state.generation_stats:
        state.generation_stats['phase_transitions'] = []

    state.generation_stats['phase_transitions'].append({
        'from': old_phase,
        'to': new_phase,
        'timestamp': datetime.now().isoformat()
    })

    return state


def require_approval(
    state: NovelState,
    approval_type: str,
    data: Dict[str, Any]
) -> NovelState:
    """
    Set pending approval request.

    Args:
        state: Current state
        approval_type: Type of approval needed
        data: Additional data for approval

    Returns:
        Updated state
    """
    state.pending_approval = ApprovalRequest(
        type=approval_type,
        data=data
    )
    return state


def approve_checkpoint(
    state: NovelState,
    approval_notes: Optional[str] = None
) -> NovelState:
    """
    Approve current checkpoint.

    Args:
        state: Current state
        approval_notes: Optional notes about approval

    Returns:
        Updated state
    """
    if not state.pending_approval:
        raise ValueError("No pending approval")

    # Log approval
    state.approval_history.append({
        'type': state.pending_approval.type,
        'approved': True,
        'notes': approval_notes,
        'timestamp': datetime.now().isoformat()
    })

    # Update phase-specific flags
    approval_type = state.pending_approval.type
    if approval_type == 'plan':
        state.plan_approved = True
    elif approval_type.startswith('chapter_'):
        chapter_num = state.pending_approval.data.get('chapter_number')
        if chapter_num and chapter_num not in state.chapters_approved:
            state.chapters_approved.append(chapter_num)

    # Clear pending approval
    state.pending_approval = None

    return state


def reject_checkpoint(
    state: NovelState,
    rejection_notes: str
) -> NovelState:
    """
    Reject current checkpoint (requires revision).

    Args:
        state: Current state
        rejection_notes: Notes about why rejected

    Returns:
        Updated state
    """
    if not state.pending_approval:
        raise ValueError("No pending approval")

    # Log rejection
    state.approval_history.append({
        'type': state.pending_approval.type,
        'approved': False,
        'notes': rejection_notes,
        'timestamp': datetime.now().isoformat()
    })

    # Clear pending approval (agent will handle revision)
    state.pending_approval = None

    return state


def increment_chapter(state: NovelState) -> NovelState:
    """
    Move to next chapter.

    Args:
        state: Current state

    Returns:
        Updated state
    """
    if state.current_chapter not in state.chapters_completed:
        state.chapters_completed.append(state.current_chapter)

    state.current_chapter += 1

    # Initialize critique iteration counter for new chapter
    if state.current_chapter not in state.chapter_critique_iterations:
        state.chapter_critique_iterations[state.current_chapter] = 0

    return state


def get_progress_percentage(state: NovelState) -> float:
    """
    Calculate overall progress percentage.

    Args:
        state: Current state

    Returns:
        Progress percentage (0-100)
    """
    if state.phase == Phase.COMPLETE:
        return 100.0

    # Weight phases
    phase_weights = {
        Phase.PLANNING: 10,
        Phase.PLAN_CRITIQUE: 10,
        Phase.WRITING: 70,
        Phase.WRITE_CRITIQUE: 10
    }

    # Base progress from completed phases
    completed_weight = 0
    if state.phase != Phase.PLANNING:
        completed_weight += phase_weights[Phase.PLANNING]
    if state.phase not in [Phase.PLANNING, Phase.PLAN_CRITIQUE]:
        completed_weight += phase_weights[Phase.PLAN_CRITIQUE]

    # Add progress within current phase
    current_phase_progress = 0
    if state.phase == Phase.WRITING or state.phase == Phase.WRITE_CRITIQUE:
        if state.total_chapters > 0:
            chapter_progress = len(state.chapters_completed) / state.total_chapters
            writing_weight = phase_weights[Phase.WRITING] + phase_weights[Phase.WRITE_CRITIQUE]
            current_phase_progress = chapter_progress * writing_weight
    elif state.phase == Phase.PLAN_CRITIQUE:
        # Estimate progress within critique phase (up to 50% after first iteration)
        current_phase_progress = min(
            phase_weights[Phase.PLAN_CRITIQUE] * 0.5,
            phase_weights[Phase.PLAN_CRITIQUE]
        )

    total_progress = completed_weight + current_phase_progress
    return min(100.0, total_progress)


def add_deviation(
    state: NovelState,
    deviation_type: str,
    description: str,
    chapter_number: Optional[int] = None
) -> NovelState:
    """
    Log a deviation from the plan.

    Args:
        state: Current state
        deviation_type: Type of deviation
        description: Description of deviation
        chapter_number: Chapter where deviation occurred

    Returns:
        Updated state
    """
    entry = DeviationLogEntry(
        chapter_number=chapter_number,
        deviation_type=deviation_type,
        description=description
    )
    state.deviations_log.append(entry)
    return state


def add_error(
    state: NovelState,
    error_type: str,
    error_message: str
) -> NovelState:
    """
    Log an error.

    Args:
        state: Current state
        error_type: Type of error
        error_message: Error message

    Returns:
        Updated state
    """
    entry = ErrorLogEntry(
        error_type=error_type,
        error_message=error_message,
        phase=state.phase.value
    )
    state.error_log.append(entry)
    return state


def is_complete(state: NovelState) -> bool:
    """
    Check if novel generation is complete.

    Args:
        state: Current state

    Returns:
        True if complete
    """
    return state.phase == Phase.COMPLETE


def pause_generation(state: NovelState) -> NovelState:
    """
    Pause generation.

    Args:
        state: Current state

    Returns:
        Updated state
    """
    state.paused = True
    state.paused_at = datetime.now()
    return state


def resume_generation(state: NovelState) -> NovelState:
    """
    Resume generation.

    Args:
        state: Current state

    Returns:
        Updated state
    """
    state.paused = False
    state.paused_at = None
    return state
