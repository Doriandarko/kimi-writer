"""
Base agent class for the Kimi Multi-Agent Novel Writing System.

This module provides the abstract base class that all phase-specific agents
inherit from.
"""

import json
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional

from backend.config import NovelConfig
from backend.state_manager import NovelState
from backend.tools.base_tool import BaseTool, ToolRegistry


class BaseAgent(ABC):
    """
    Abstract base class for all agents in the novel writing system.

    Each phase-specific agent inherits from this class and implements:
    - get_system_prompt(): Returns the agent's system prompt
    - get_tools(): Returns the tools available to this agent
    """

    def __init__(
        self,
        config: NovelConfig,
        state: NovelState,
        ws_manager=None
    ):
        """
        Initialize the agent.

        Args:
            config: Novel configuration
            state: Current novel state
            ws_manager: Optional WebSocket manager for real-time updates
        """
        self.config = config
        self.state = state
        self.ws_manager = ws_manager
        self.message_history: List[Dict[str, Any]] = []
        self.tool_registry = ToolRegistry()

        # Initialize tools
        self._register_tools()

    def _register_tools(self):
        """Register tools in the tool registry."""
        tools = self.get_tools()
        for tool in tools:
            self.tool_registry.register(tool)

    @abstractmethod
    def get_system_prompt(self) -> str:
        """
        Get the system prompt for this agent.

        Returns:
            System prompt string

        Raises:
            NotImplementedError: Must be implemented by subclass
        """
        raise NotImplementedError("Subclasses must implement get_system_prompt")

    @abstractmethod
    def get_tools(self) -> List[BaseTool]:
        """
        Get the list of tools available to this agent.

        Returns:
            List of BaseTool instances

        Raises:
            NotImplementedError: Must be implemented by subclass
        """
        raise NotImplementedError("Subclasses must implement get_tools")

    def get_tool_definitions(self) -> List[Dict[str, Any]]:
        """
        Get tool definitions in OpenAI format.

        Returns:
            List of tool definitions
        """
        return self.tool_registry.get_openai_tools()

    def get_tool_function(self, tool_name: str) -> BaseTool:
        """
        Get a tool by name.

        Args:
            tool_name: Name of the tool

        Returns:
            BaseTool instance

        Raises:
            KeyError: If tool not found
        """
        return self.tool_registry.get(tool_name)

    def execute_tool(self, tool_name: str, **kwargs) -> Dict[str, Any]:
        """
        Execute a tool by name.

        Args:
            tool_name: Name of the tool
            **kwargs: Tool arguments

        Returns:
            Tool execution result
        """
        # Add state to kwargs if not present
        if 'state' not in kwargs:
            kwargs['state'] = self.state

        return self.tool_registry.execute(tool_name, **kwargs)

    def add_system_message(self, content: str):
        """
        Add system message to history.

        Args:
            content: Message content
        """
        self.message_history.append({
            "role": "system",
            "content": content
        })

    def add_user_message(self, content: str):
        """
        Add user message to history.

        Args:
            content: Message content
        """
        self.message_history.append({
            "role": "user",
            "content": content
        })

    def add_assistant_message(
        self,
        content: Optional[str] = None,
        tool_calls: Optional[List] = None,
        reasoning: Optional[str] = None
    ):
        """
        Add assistant message to history.

        Args:
            content: Message content
            tool_calls: Tool calls made
            reasoning: Reasoning content (if supported by model)
        """
        message = {"role": "assistant"}

        if content:
            message["content"] = content

        if tool_calls:
            message["tool_calls"] = tool_calls

        if reasoning:
            message["reasoning_content"] = reasoning

        self.message_history.append(message)

    def add_tool_results(self, results: List[Dict[str, Any]], tool_calls: List):
        """
        Add tool results to message history.

        Args:
            results: List of tool execution results
            tool_calls: Corresponding tool calls
        """
        for tool_call, result in zip(tool_calls, results):
            self.message_history.append({
                "role": "tool",
                "content": json.dumps(result),
                "tool_call_id": tool_call.id,
                "name": tool_call.function.name
            })

    def load_project_files(self, *file_paths) -> Dict[str, str]:
        """
        Helper to load planning/writing files from project.

        Args:
            *file_paths: Relative paths to files in project

        Returns:
            Dictionary mapping file paths to contents
        """
        from backend.tools.project import get_active_project_folder
        import os

        project_folder = get_active_project_folder()
        if not project_folder:
            return {}

        files = {}
        for rel_path in file_paths:
            full_path = os.path.join(project_folder, rel_path)
            if os.path.exists(full_path):
                try:
                    with open(full_path, 'r', encoding='utf-8') as f:
                        files[rel_path] = f.read()
                except Exception as e:
                    files[rel_path] = f"Error reading file: {str(e)}"

        return files

    def get_message_count(self) -> int:
        """
        Get the number of messages in history.

        Returns:
            Message count
        """
        return len(self.message_history)

    def clear_message_history(self):
        """Clear the message history (use with caution)."""
        self.message_history = []

    def initialize_conversation(self, user_prompt: Optional[str] = None):
        """
        Initialize the conversation with system prompt and optional user prompt.

        Args:
            user_prompt: Optional initial user prompt
        """
        # Add system message
        system_prompt = self.get_system_prompt()
        self.add_system_message(system_prompt)

        # Add user prompt if provided
        if user_prompt:
            self.add_user_message(user_prompt)

    def send_ws_update(self, message_type: str, data: Dict[str, Any]):
        """
        Send WebSocket update if ws_manager is available.

        Args:
            message_type: Type of message
            data: Message data
        """
        if self.ws_manager:
            # This will be implemented in websocket_manager.py
            pass

    def __repr__(self) -> str:
        """String representation of agent."""
        return f"{self.__class__.__name__}(phase={self.state.phase}, messages={len(self.message_history)})"
