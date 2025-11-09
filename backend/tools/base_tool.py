"""
Base tool class for the Kimi Multi-Agent Novel Writing System.

This module provides a base class for all tools with OpenAI function calling
format conversion.
"""

from typing import Dict, Any, Callable
from abc import ABC, abstractmethod


class BaseTool(ABC):
    """
    Base class for all tools.

    Subclasses must implement:
    - name: Tool name
    - description: Tool description
    - parameters: OpenAI function parameters schema
    - execute: Tool execution logic
    """

    def __init__(self):
        """Initialize the tool."""
        self._validate_tool()

    def _validate_tool(self):
        """Validate that required attributes are set."""
        required_attrs = ['name', 'description', 'parameters']
        for attr in required_attrs:
            if not hasattr(self, attr):
                raise ValueError(f"Tool must define '{attr}' attribute")

    @property
    @abstractmethod
    def name(self) -> str:
        """Tool name."""
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        """Tool description."""
        pass

    @property
    @abstractmethod
    def parameters(self) -> Dict[str, Any]:
        """OpenAI function parameters schema."""
        pass

    @abstractmethod
    def execute(self, **kwargs) -> Dict[str, Any]:
        """
        Execute the tool.

        Args:
            **kwargs: Tool arguments

        Returns:
            Tool result dictionary
        """
        pass

    def as_openai_tool(self) -> Dict[str, Any]:
        """
        Convert to OpenAI function calling format.

        Returns:
            Tool definition in OpenAI format
        """
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.parameters
            }
        }

    def __call__(self, **kwargs) -> Dict[str, Any]:
        """
        Allow calling tool as a function.

        Args:
            **kwargs: Tool arguments

        Returns:
            Tool result
        """
        return self.execute(**kwargs)


class ToolRegistry:
    """Registry for managing tools."""

    def __init__(self):
        """Initialize the registry."""
        self._tools: Dict[str, BaseTool] = {}

    def register(self, tool: BaseTool):
        """
        Register a tool.

        Args:
            tool: Tool instance
        """
        self._tools[tool.name] = tool

    def get(self, name: str) -> BaseTool:
        """
        Get tool by name.

        Args:
            name: Tool name

        Returns:
            Tool instance

        Raises:
            KeyError: If tool not found
        """
        if name not in self._tools:
            raise KeyError(f"Tool not found: {name}")
        return self._tools[name]

    def get_all(self) -> Dict[str, BaseTool]:
        """
        Get all registered tools.

        Returns:
            Dictionary of tool name to tool instance
        """
        return self._tools.copy()

    def get_openai_tools(self) -> list:
        """
        Get all tools in OpenAI format.

        Returns:
            List of tool definitions
        """
        return [tool.as_openai_tool() for tool in self._tools.values()]

    def execute(self, name: str, **kwargs) -> Dict[str, Any]:
        """
        Execute a tool by name.

        Args:
            name: Tool name
            **kwargs: Tool arguments

        Returns:
            Tool result
        """
        tool = self.get(name)
        return tool.execute(**kwargs)
