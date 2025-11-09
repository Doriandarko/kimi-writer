"""
Agent loop for the Kimi Multi-Agent Novel Writing System.

This module orchestrates the four-phase novel generation workflow using
phase-specific agents.
"""

import json
import asyncio
import logging
from typing import Optional, List, Dict, Any
from openai import OpenAI
from datetime import datetime

from backend.config import NovelConfig, Phase, load_config_from_file, get_config_path
from backend.state_manager import (
    NovelState, load_state, save_state, update_phase,
    require_approval, is_complete, get_progress_percentage
)
from backend.agents.planning_agent import PlanningAgent
from backend.agents.plan_critic_agent import PlanCriticAgent
from backend.agents.writing_agent import WritingAgent
from backend.agents.write_critic_agent import WriteCriticAgent
from backend.tools.project import set_active_project_folder
from backend.utils.token_counter import estimate_token_count_async, should_compress
from backend.tools.compression import compress_context_impl
from backend.websocket_manager import get_ws_manager

logger = logging.getLogger(__name__)


class AgentLoop:
    """
    Main agent loop that orchestrates multi-agent novel generation.

    Manages phase transitions, tool execution, token tracking, and
    WebSocket updates.
    """

    def __init__(
        self,
        project_id: str,
        config: Optional[NovelConfig] = None,
        state: Optional[NovelState] = None
    ):
        """
        Initialize the agent loop.

        Args:
            project_id: Project ID
            config: Optional novel configuration (will load if not provided)
            state: Optional novel state (will load if not provided)
        """
        self.project_id = project_id

        # Load or use provided config/state
        if config is None:
            config_path = get_config_path(project_id)
            self.config = load_config_from_file(config_path)
        else:
            self.config = config

        if state is None:
            self.state = load_state(project_id)
        else:
            self.state = state

        # Initialize OpenAI client
        self.client = OpenAI(
            api_key=self.config.api.api_key,
            base_url=self.config.api.base_url
        )

        # WebSocket manager for real-time updates
        self.ws_manager = get_ws_manager()

        # Set active project folder for tools
        set_active_project_folder(f"output/{project_id}")

        # Current agent
        self.current_agent = None

        # Statistics
        self.start_time = datetime.now()

    async def run(self):
        """
        Main execution loop.

        Runs the multi-agent workflow until completion or max iterations.
        """
        logger.info(f"Starting agent loop for project {self.project_id}")

        try:
            while not is_complete(self.state) and self.state.total_iterations < self.config.api.max_iterations:
                # Check if paused
                if self.state.paused:
                    logger.info("Generation paused, waiting...")
                    await asyncio.sleep(5)
                    self.state = load_state(self.project_id)  # Reload state
                    continue

                # Check for pending approvals
                if self.state.pending_approval:
                    await self.ws_manager.request_approval(
                        self.project_id,
                        self.state.pending_approval.type,
                        self.state.pending_approval.data
                    )
                    logger.info(f"Waiting for approval: {self.state.pending_approval.type}")
                    await asyncio.sleep(5)
                    self.state = load_state(self.project_id)  # Reload state
                    continue

                # Get current agent
                agent = self.get_current_agent()

                # Initialize conversation if needed
                if agent.get_message_count() == 0:
                    initial_prompt = self.get_initial_prompt(agent)
                    agent.initialize_conversation(initial_prompt)

                # Run agent iteration
                await self.run_agent_iteration(agent)

                # Update state
                self.state.total_iterations += 1
                self.state.current_agent_iterations += 1
                save_state(self.state)

            # Send completion notification
            if is_complete(self.state):
                stats = self.get_generation_stats()
                await self.ws_manager.send_completion(self.project_id, stats)
                logger.info(f"Novel generation complete for project {self.project_id}")

        except Exception as e:
            logger.error(f"Error in agent loop: {e}", exc_info=True)
            await self.ws_manager.send_error(self.project_id, str(e), "agent_loop_error")
            raise

    def get_current_agent(self):
        """
        Get the agent for the current phase.

        Returns:
            Agent instance for current phase
        """
        agents = {
            Phase.PLANNING: PlanningAgent,
            Phase.PLAN_CRITIQUE: PlanCriticAgent,
            Phase.WRITING: WritingAgent,
            Phase.WRITE_CRITIQUE: WriteCriticAgent
        }

        agent_class = agents.get(self.state.phase)
        if not agent_class:
            raise ValueError(f"Unknown phase: {self.state.phase}")

        # Reuse agent if same phase, otherwise create new
        if (self.current_agent is None or
            self.current_agent.__class__ != agent_class):
            self.current_agent = agent_class(self.config, self.state, self.ws_manager)
            logger.info(f"Initialized {agent_class.__name__} for phase {self.state.phase}")

        return self.current_agent

    def get_initial_prompt(self, agent) -> str:
        """
        Get initial prompt for agent.

        Args:
            agent: Agent instance

        Returns:
            Initial prompt string
        """
        if hasattr(agent, 'get_initial_prompt'):
            return agent.get_initial_prompt()
        return None

    async def run_agent_iteration(self, agent):
        """
        Run a single agent iteration.

        Args:
            agent: Agent to run
        """
        # Estimate tokens
        token_count = await estimate_token_count_async(
            self.config.api.base_url,
            self.config.api.api_key,
            self.config.api.model_name,
            agent.message_history
        )

        logger.info(f"Token count: {token_count}/{self.config.api.token_limit}")

        # Send token update
        await self.ws_manager.send_token_update(
            self.project_id,
            token_count,
            self.config.api.token_limit
        )

        # Check if compression needed
        if should_compress(token_count, self.config.api.token_limit, self.config.api.compression_threshold):
            logger.info("Compressing context...")
            await self.compress_context(agent)

        # Call model with streaming
        try:
            stream = self.client.chat.completions.create(
                model=self.config.api.model_name,
                messages=agent.message_history,
                tools=agent.get_tool_definitions(),
                temperature=1.0,
                stream=True
            )

            # Process stream
            reasoning_content = ""
            content_text = ""
            tool_calls_data = []
            role = None

            for chunk in stream:
                if not chunk.choices:
                    continue

                delta = chunk.choices[0].delta

                if hasattr(delta, "role") and delta.role:
                    role = delta.role

                # Handle reasoning content
                if hasattr(delta, "reasoning_content") and delta.reasoning_content:
                    reasoning_content += delta.reasoning_content
                    await self.ws_manager.send_stream_chunk(
                        self.project_id,
                        delta.reasoning_content,
                        is_reasoning=True
                    )

                # Handle regular content
                if hasattr(delta, "content") and delta.content:
                    content_text += delta.content
                    await self.ws_manager.send_stream_chunk(
                        self.project_id,
                        delta.content,
                        is_reasoning=False
                    )

                # Handle tool calls
                if hasattr(delta, "tool_calls") and delta.tool_calls:
                    for tc_delta in delta.tool_calls:
                        while len(tool_calls_data) <= tc_delta.index:
                            tool_calls_data.append({
                                "id": None,
                                "type": "function",
                                "function": {"name": "", "arguments": ""}
                            })

                        tc = tool_calls_data[tc_delta.index]

                        if tc_delta.id:
                            tc["id"] = tc_delta.id
                        if hasattr(tc_delta, "function"):
                            if tc_delta.function.name:
                                tc["function"]["name"] = tc_delta.function.name
                            if tc_delta.function.arguments:
                                tc["function"]["arguments"] += tc_delta.function.arguments

            # Add assistant message to history
            agent.add_assistant_message(
                content=content_text if content_text else None,
                tool_calls=self.reconstruct_tool_calls(tool_calls_data) if tool_calls_data else None,
                reasoning=reasoning_content if reasoning_content else None
            )

            # Check if completed (no tool calls)
            if not tool_calls_data or not any(tc["id"] for tc in tool_calls_data):
                logger.info("Agent completed with no tool calls")
                return

            # Execute tools
            await self.execute_tools(agent, tool_calls_data)

        except Exception as e:
            logger.error(f"Error in agent iteration: {e}", exc_info=True)
            await self.ws_manager.send_error(self.project_id, str(e))
            raise

    def reconstruct_tool_calls(self, tool_calls_data: List[Dict]) -> List:
        """Reconstruct tool calls from streamed data."""
        tool_calls = []
        for tc in tool_calls_data:
            if tc["id"]:
                tool_call = type('ToolCall', (), {
                    'id': tc["id"],
                    'type': 'function',
                    'function': type('Function', (), {
                        'name': tc["function"]["name"],
                        'arguments': tc["function"]["arguments"]
                    })()
                })()
                tool_calls.append(tool_call)
        return tool_calls

    async def execute_tools(self, agent, tool_calls_data: List[Dict]):
        """
        Execute tool calls and add results to message history.

        Args:
            agent: Current agent
            tool_calls_data: List of tool call data
        """
        results = []

        for tc in tool_calls_data:
            if not tc["id"]:
                continue

            func_name = tc["function"]["name"]
            args_str = tc["function"]["arguments"]

            # Send tool call notification
            try:
                args = json.loads(args_str)
            except json.JSONDecodeError:
                args = {}

            await self.ws_manager.send_tool_call(
                self.project_id,
                func_name,
                args
            )

            # Execute tool
            try:
                result = agent.execute_tool(func_name, **args)
                results.append(result)

                # Send tool result
                await self.ws_manager.send_tool_result(
                    self.project_id,
                    func_name,
                    result
                )

                logger.info(f"Executed tool: {func_name}")

                # Check for phase transitions
                if result.get("transition"):
                    await self.handle_phase_transition(result["transition"])

            except Exception as e:
                error_result = {
                    "success": False,
                    "message": f"Error executing tool: {str(e)}"
                }
                results.append(error_result)
                logger.error(f"Tool execution error: {e}")

        # Add tool results to agent history
        tool_calls_reconstructed = self.reconstruct_tool_calls(tool_calls_data)
        agent.add_tool_results(results, tool_calls_reconstructed)

    async def handle_phase_transition(self, transition_data: Dict):
        """
        Handle phase transitions.

        Args:
            transition_data: Transition information
        """
        to_phase_str = transition_data.get("to_phase")
        data = transition_data.get("data", {})

        # Convert string to Phase enum
        try:
            to_phase = Phase(to_phase_str)
        except ValueError:
            logger.error(f"Invalid phase: {to_phase_str}")
            return

        from_phase = self.state.phase

        # Check if approval required
        checkpoint_key = f"require_{to_phase_str.lower()}_approval"
        if hasattr(self.config.checkpoints, checkpoint_key):
            requires_approval = getattr(self.config.checkpoints, checkpoint_key)
            if requires_approval:
                require_approval(self.state, to_phase_str.lower(), data)
                save_state(self.state)
                logger.info(f"Approval required for transition to {to_phase_str}")
                return

        # Perform transition
        update_phase(self.state, to_phase)
        save_state(self.state)

        # Notify via WebSocket
        await self.ws_manager.send_phase_change(
            self.project_id,
            from_phase.value,
            to_phase.value
        )

        logger.info(f"Phase transition: {from_phase} -> {to_phase}")

    async def compress_context(self, agent):
        """
        Compress agent message history.

        Args:
            agent: Current agent
        """
        result = compress_context_impl(
            messages=agent.message_history,
            client=self.client,
            model=self.config.api.model_name,
            keep_recent=10,
            state=self.state
        )

        if result.get("success") and result.get("compressed_messages"):
            agent.message_history = result["compressed_messages"]
            logger.info(f"Context compressed: {result.get('message')}")

    def get_generation_stats(self) -> Dict[str, Any]:
        """
        Get generation statistics.

        Returns:
            Statistics dictionary
        """
        elapsed = (datetime.now() - self.start_time).total_seconds()

        return {
            "project_id": self.project_id,
            "total_iterations": self.state.total_iterations,
            "time_elapsed_seconds": elapsed,
            "phases_completed": len(self.state.generation_stats.get("phase_transitions", [])),
            "chapters_written": len(self.state.chapters_completed),
            "chapters_approved": len(self.state.chapters_approved),
            "progress_percentage": get_progress_percentage(self.state)
        }


# Standalone run function for CLI or background execution
async def run_generation(project_id: str):
    """
    Run novel generation for a project.

    Args:
        project_id: Project ID to generate
    """
    loop = AgentLoop(project_id)
    await loop.run()
