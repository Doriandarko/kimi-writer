"""
Command-line interface for the Kimi Novel Writing System.

This module provides a backward-compatible CLI for running novel generation
from the terminal, similar to the original kimi-writer.py.
"""

import os
import sys
import asyncio
import argparse
import logging
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv

from backend.config import (
    NovelConfig, NovelLength, WritingSampleConfig,
    CheckpointConfig, AgentConfig, APIConfig,
    generate_project_id, sanitize_project_name,
    save_config_to_file, get_config_path
)
from backend.state_manager import NovelState, save_state, load_state
from backend.agent_loop import AgentLoop
from backend.writing_samples import get_writing_sample, list_available_samples

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class CLIProgressMonitor:
    """
    Simple progress monitor for CLI mode.

    Prints updates to console instead of using WebSocket.
    """

    def __init__(self):
        self.current_phase = None
        self.iteration = 0

    async def send_phase_change(self, project_id: str, from_phase: str, to_phase: str):
        """Print phase transition."""
        print(f"\n{'=' * 60}")
        print(f"PHASE TRANSITION: {from_phase} -> {to_phase}")
        print(f"{'=' * 60}\n")
        self.current_phase = to_phase

    async def send_stream_chunk(self, project_id: str, content: str, is_reasoning: bool = False):
        """Print streaming content."""
        if is_reasoning:
            # Print reasoning in dim color if terminal supports it
            print(f"\033[2m{content}\033[0m", end='', flush=True)
        else:
            print(content, end='', flush=True)

    async def send_tool_call(self, project_id: str, tool_name: str, arguments: dict):
        """Print tool execution."""
        print(f"\n[TOOL] {tool_name}")
        if arguments:
            print(f"  Arguments: {arguments}")

    async def send_tool_result(self, project_id: str, tool_name: str, result: dict):
        """Print tool result."""
        if result.get("success"):
            print(f"  ✓ Success: {result.get('message', 'Done')}")
        else:
            print(f"  ✗ Error: {result.get('message', 'Unknown error')}")

    async def send_token_update(self, project_id: str, token_count: int, token_limit: int):
        """Print token usage."""
        percentage = (token_count / token_limit * 100) if token_limit > 0 else 0
        print(f"\n[TOKENS] {token_count:,} / {token_limit:,} ({percentage:.1f}%)")

    async def request_approval(self, project_id: str, approval_type: str, data: dict):
        """Request user approval via console input."""
        print(f"\n{'=' * 60}")
        print(f"APPROVAL REQUIRED: {approval_type}")
        print(f"{'=' * 60}")

        if approval_type == "plan":
            print("\nPlan materials have been created. Please review:")
            print(f"  - Summary: output/{project_id}/summary.txt")
            print(f"  - Characters: output/{project_id}/dramatis_personae.txt")
            print(f"  - Structure: output/{project_id}/story_structure.txt")
            print(f"  - Outline: output/{project_id}/plot_outline.txt")
        elif approval_type == "chapter":
            chapter_num = data.get("chapter_number", "?")
            print(f"\nChapter {chapter_num} has been written. Please review:")
            print(f"  - output/{project_id}/chapter_{chapter_num}.txt")

        while True:
            response = input("\nApprove? (y/n): ").strip().lower()
            if response in ['y', 'yes']:
                print("✓ Approved. Continuing...\n")
                # Update state to approve
                state = load_state(project_id)
                if state.pending_approval:
                    state.pending_approval = None
                    if approval_type == "plan":
                        state.plan_approved = True
                    elif approval_type == "chapter":
                        chapter_num = data.get("chapter_number")
                        if chapter_num and chapter_num not in state.chapters_approved:
                            state.chapters_approved.append(chapter_num)
                    save_state(state)
                break
            elif response in ['n', 'no']:
                print("✗ Rejected. Please modify the files and restart.")
                sys.exit(0)
            else:
                print("Invalid input. Please enter 'y' or 'n'.")

    async def send_progress(self, project_id: str, percentage: float, message: str, details: dict = None):
        """Print progress update."""
        print(f"\n[PROGRESS] {percentage:.1f}% - {message}")

    async def send_error(self, project_id: str, error_message: str, error_type: str = None):
        """Print error."""
        print(f"\n[ERROR] {error_message}")
        if error_type:
            print(f"  Type: {error_type}")

    async def send_completion(self, project_id: str, stats: dict):
        """Print completion message."""
        print(f"\n{'=' * 60}")
        print("NOVEL GENERATION COMPLETE!")
        print(f"{'=' * 60}")
        print(f"Project: {project_id}")
        print(f"Total iterations: {stats.get('total_iterations', 0)}")
        print(f"Time elapsed: {stats.get('time_elapsed_seconds', 0):.1f}s")
        print(f"Chapters written: {stats.get('chapters_written', 0)}")
        print(f"\nOutput directory: output/{project_id}/")
        print(f"{'=' * 60}\n")

    # Stub methods for compatibility
    async def connect(self, project_id: str, websocket): pass
    async def disconnect(self, project_id: str, websocket): pass
    async def broadcast(self, project_id: str, message: dict): pass
    async def send_agent_thinking(self, project_id: str, reasoning: str): pass


def create_config_from_args(args) -> tuple[NovelConfig, NovelState]:
    """
    Create configuration and initial state from CLI arguments.

    Args:
        args: Parsed command-line arguments

    Returns:
        Tuple of (NovelConfig, NovelState)
    """
    # Generate project ID
    project_id = generate_project_id()
    project_name = sanitize_project_name(args.name or args.theme)

    # Handle writing sample
    writing_sample_config = WritingSampleConfig()
    if args.writing_sample:
        sample_text = get_writing_sample(args.writing_sample)
        if sample_text:
            writing_sample_config.sample_id = args.writing_sample
            writing_sample_config.sample_text = sample_text
        else:
            logger.warning(f"Writing sample '{args.writing_sample}' not found. Proceeding without sample.")

    # Create config
    config = NovelConfig(
        project_id=project_id,
        project_name=project_name,
        novel_length=NovelLength(args.length),
        theme=args.theme,
        genre=args.genre,
        writing_sample=writing_sample_config,
        checkpoints=CheckpointConfig(
            require_plan_approval=args.require_plan_approval,
            require_chapter_approval=args.require_chapter_approval
        ),
        agent=AgentConfig(
            max_plan_critique_iterations=args.max_plan_critique,
            max_write_critique_iterations=args.max_write_critique
        ),
        api=APIConfig(
            api_key=os.getenv("MOONSHOT_API_KEY"),
            base_url=os.getenv("MOONSHOT_API_BASE_URL", "https://api.moonshot.cn/v1"),
            model_name=os.getenv("MOONSHOT_MODEL", "kimi-k2-thinking"),
            max_iterations=args.max_iterations,
            token_limit=args.token_limit,
            compression_threshold=args.compression_threshold
        )
    )

    # Save config
    config_path = get_config_path(project_id)
    save_config_to_file(config, config_path)
    logger.info(f"Configuration saved to {config_path}")

    # Create initial state
    state = NovelState(
        project_id=project_id,
        total_chapters=config.novel_length.num_chapters
    )
    save_state(state)
    logger.info(f"Initial state saved for project {project_id}")

    return config, state


async def run_cli(args):
    """
    Run novel generation in CLI mode.

    Args:
        args: Parsed command-line arguments
    """
    # Check for API key
    if not os.getenv("MOONSHOT_API_KEY"):
        logger.error("MOONSHOT_API_KEY not found in environment")
        print("\nError: MOONSHOT_API_KEY not set")
        print("Please set it in your .env file or environment variables")
        sys.exit(1)

    # List writing samples if requested
    if args.list_samples:
        samples = list_available_samples()
        print("\nAvailable writing samples:")
        if samples:
            for sample_id, info in samples.items():
                print(f"  - {sample_id}: {info.get('name', 'Unknown')}")
        else:
            print("  (No writing samples available. Add samples to backend/writing_samples.py)")
        print()
        return

    # Create configuration
    print(f"\nCreating new novel project...")
    print(f"Theme: {args.theme}")
    print(f"Length: {args.length}")
    if args.genre:
        print(f"Genre: {args.genre}")
    if args.writing_sample:
        print(f"Writing sample: {args.writing_sample}")
    print()

    config, state = create_config_from_args(args)

    print(f"Project ID: {config.project_id}")
    print(f"Output directory: output/{config.project_id}/")
    print()

    # Create CLI progress monitor
    cli_monitor = CLIProgressMonitor()

    # Create agent loop with CLI monitor instead of WebSocket manager
    loop = AgentLoop(
        project_id=config.project_id,
        config=config,
        state=state
    )
    loop.ws_manager = cli_monitor  # Replace WebSocket manager with CLI monitor

    # Run generation
    print("Starting novel generation...\n")
    print(f"{'=' * 60}\n")

    try:
        await loop.run()
    except KeyboardInterrupt:
        print("\n\nInterrupted by user. State has been saved.")
        print(f"To resume, use the web UI or implement resume functionality.")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Generation failed: {e}", exc_info=True)
        print(f"\nError: {e}")
        sys.exit(1)


def main():
    """Main entry point for CLI."""
    parser = argparse.ArgumentParser(
        description="Kimi Multi-Agent Novel Writing System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Create a sci-fi novel
  python -m backend.cli --theme "Space exploration in the 23rd century" --genre "science fiction"

  # Create a short story with writing sample
  python -m backend.cli --theme "A mysterious stranger" --length short_story --writing-sample hemingway

  # List available writing samples
  python -m backend.cli --list-samples

For more information, visit: https://github.com/yourusername/kimi-writer
        """
    )

    # Required arguments
    parser.add_argument(
        "--theme",
        type=str,
        help="Theme or premise for the novel (required unless --list-samples)"
    )

    # Optional arguments
    parser.add_argument(
        "--name",
        type=str,
        help="Project name (defaults to sanitized theme)"
    )

    parser.add_argument(
        "--length",
        type=str,
        choices=["flash_fiction", "short_story", "novelette", "novella", "novel"],
        default="novel",
        help="Novel length (default: novel)"
    )

    parser.add_argument(
        "--genre",
        type=str,
        help="Genre (optional, e.g., 'science fiction', 'mystery', 'romance')"
    )

    parser.add_argument(
        "--writing-sample",
        type=str,
        help="Writing sample ID to use for style guidance"
    )

    parser.add_argument(
        "--require-plan-approval",
        action="store_true",
        default=True,
        help="Require approval after planning phase (default: True)"
    )

    parser.add_argument(
        "--no-plan-approval",
        action="store_false",
        dest="require_plan_approval",
        help="Don't require approval after planning phase"
    )

    parser.add_argument(
        "--require-chapter-approval",
        action="store_true",
        default=False,
        help="Require approval after each chapter (default: False)"
    )

    parser.add_argument(
        "--max-plan-critique",
        type=int,
        default=2,
        help="Max plan critique iterations (default: 2)"
    )

    parser.add_argument(
        "--max-write-critique",
        type=int,
        default=2,
        help="Max write critique iterations per chapter (default: 2)"
    )

    parser.add_argument(
        "--max-iterations",
        type=int,
        default=300,
        help="Maximum total iterations (default: 300)"
    )

    parser.add_argument(
        "--token-limit",
        type=int,
        default=200000,
        help="Token limit for context (default: 200000)"
    )

    parser.add_argument(
        "--compression-threshold",
        type=int,
        default=180000,
        help="Token threshold for compression (default: 180000)"
    )

    parser.add_argument(
        "--list-samples",
        action="store_true",
        help="List available writing samples and exit"
    )

    args = parser.parse_args()

    # Validate arguments
    if not args.list_samples and not args.theme:
        parser.error("--theme is required (unless using --list-samples)")

    # Run async CLI
    try:
        asyncio.run(run_cli(args))
    except KeyboardInterrupt:
        print("\nExiting...")
        sys.exit(0)


if __name__ == "__main__":
    main()
