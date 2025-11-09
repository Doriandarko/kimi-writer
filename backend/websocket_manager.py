"""
WebSocket manager for real-time updates to the frontend.

This module handles WebSocket connections and broadcasting updates during
novel generation.
"""

import json
import asyncio
from typing import Dict, Set, Any, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class WebSocketManager:
    """
    Manages WebSocket connections and broadcasts updates to connected clients.

    Supports multiple clients per project for collaborative viewing.
    """

    def __init__(self):
        """Initialize the WebSocket manager."""
        # {project_id: set of WebSocket connections}
        self.connections: Dict[str, Set] = {}
        self.lock = asyncio.Lock()

    async def connect(self, project_id: str, websocket):
        """
        Register a new WebSocket connection for a project.

        Args:
            project_id: Project ID
            websocket: WebSocket connection
        """
        async with self.lock:
            if project_id not in self.connections:
                self.connections[project_id] = set()

            self.connections[project_id].add(websocket)

            logger.info(f"WebSocket connected for project {project_id}. Total connections: {len(self.connections[project_id])}")

            # Send confirmation
            await self._send_to_websocket(websocket, {
                "type": "connected",
                "project_id": project_id,
                "timestamp": datetime.now().isoformat()
            })

    async def disconnect(self, project_id: str, websocket):
        """
        Unregister a WebSocket connection.

        Args:
            project_id: Project ID
            websocket: WebSocket connection
        """
        async with self.lock:
            if project_id in self.connections:
                self.connections[project_id].discard(websocket)

                # Clean up empty project entries
                if not self.connections[project_id]:
                    del self.connections[project_id]

                logger.info(f"WebSocket disconnected for project {project_id}")

    async def broadcast(self, project_id: str, message: Dict[str, Any]):
        """
        Broadcast a message to all connected clients for a project.

        Args:
            project_id: Project ID
            message: Message dictionary to broadcast
        """
        if project_id not in self.connections:
            return

        # Add timestamp if not present
        if "timestamp" not in message:
            message["timestamp"] = datetime.now().isoformat()

        # Get connections (copy to avoid modification during iteration)
        connections = self.connections[project_id].copy()

        # Send to all connections
        for websocket in connections:
            try:
                await self._send_to_websocket(websocket, message)
            except Exception as e:
                logger.error(f"Error sending to websocket: {e}")
                # Remove failed connection
                await self.disconnect(project_id, websocket)

    async def _send_to_websocket(self, websocket, message: Dict[str, Any]):
        """
        Send a message to a specific websocket.

        Args:
            websocket: WebSocket connection
            message: Message to send
        """
        await websocket.send_text(json.dumps(message))

    # Convenience methods for common message types

    async def send_phase_change(
        self,
        project_id: str,
        from_phase: str,
        to_phase: str
    ):
        """
        Notify clients of phase transition.

        Args:
            project_id: Project ID
            from_phase: Previous phase
            to_phase: New phase
        """
        await self.broadcast(project_id, {
            "type": "phase_change",
            "from_phase": from_phase,
            "to_phase": to_phase
        })

    async def send_agent_thinking(
        self,
        project_id: str,
        reasoning: str
    ):
        """
        Send agent reasoning/thinking content.

        Args:
            project_id: Project ID
            reasoning: Reasoning content
        """
        await self.broadcast(project_id, {
            "type": "agent_thinking",
            "content": reasoning
        })

    async def send_stream_chunk(
        self,
        project_id: str,
        content: str,
        is_reasoning: bool = False
    ):
        """
        Send streaming content chunk.

        Args:
            project_id: Project ID
            content: Content chunk
            is_reasoning: Whether this is reasoning content
        """
        await self.broadcast(project_id, {
            "type": "stream_chunk",
            "content": content,
            "is_reasoning": is_reasoning
        })

    async def send_tool_call(
        self,
        project_id: str,
        tool_name: str,
        arguments: Dict[str, Any]
    ):
        """
        Notify clients of tool execution.

        Args:
            project_id: Project ID
            tool_name: Name of tool being called
            arguments: Tool arguments
        """
        await self.broadcast(project_id, {
            "type": "tool_call",
            "tool_name": tool_name,
            "arguments": arguments
        })

    async def send_tool_result(
        self,
        project_id: str,
        tool_name: str,
        result: Dict[str, Any]
    ):
        """
        Send tool execution result.

        Args:
            project_id: Project ID
            tool_name: Name of tool
            result: Tool result
        """
        await self.broadcast(project_id, {
            "type": "tool_result",
            "tool_name": tool_name,
            "result": result
        })

    async def send_token_update(
        self,
        project_id: str,
        token_count: int,
        token_limit: int
    ):
        """
        Send token usage update.

        Args:
            project_id: Project ID
            token_count: Current token count
            token_limit: Maximum token limit
        """
        await self.broadcast(project_id, {
            "type": "token_update",
            "token_count": token_count,
            "token_limit": token_limit,
            "percentage": (token_count / token_limit * 100) if token_limit > 0 else 0
        })

    async def request_approval(
        self,
        project_id: str,
        approval_type: str,
        data: Dict[str, Any]
    ):
        """
        Request user approval for checkpoint.

        Args:
            project_id: Project ID
            approval_type: Type of approval needed
            data: Additional data for approval
        """
        await self.broadcast(project_id, {
            "type": "approval_required",
            "approval_type": approval_type,
            "data": data
        })

    async def send_progress(
        self,
        project_id: str,
        percentage: float,
        message: str,
        details: Optional[Dict[str, Any]] = None
    ):
        """
        Send progress update.

        Args:
            project_id: Project ID
            percentage: Progress percentage (0-100)
            message: Progress message
            details: Optional additional details
        """
        await self.broadcast(project_id, {
            "type": "progress",
            "percentage": percentage,
            "message": message,
            "details": details or {}
        })

    async def send_error(
        self,
        project_id: str,
        error_message: str,
        error_type: Optional[str] = None
    ):
        """
        Send error notification.

        Args:
            project_id: Project ID
            error_message: Error message
            error_type: Optional error type/category
        """
        await self.broadcast(project_id, {
            "type": "error",
            "message": error_message,
            "error_type": error_type
        })

    async def send_completion(
        self,
        project_id: str,
        stats: Dict[str, Any]
    ):
        """
        Send novel completion notification.

        Args:
            project_id: Project ID
            stats: Generation statistics
        """
        await self.broadcast(project_id, {
            "type": "complete",
            "stats": stats
        })

    def get_connection_count(self, project_id: str) -> int:
        """
        Get number of active connections for a project.

        Args:
            project_id: Project ID

        Returns:
            Connection count
        """
        return len(self.connections.get(project_id, set()))

    def has_connections(self, project_id: str) -> bool:
        """
        Check if project has any active connections.

        Args:
            project_id: Project ID

        Returns:
            True if connections exist
        """
        return project_id in self.connections and len(self.connections[project_id]) > 0


# Global instance
_ws_manager: Optional[WebSocketManager] = None


def get_ws_manager() -> WebSocketManager:
    """
    Get the global WebSocket manager instance.

    Returns:
        WebSocketManager instance
    """
    global _ws_manager
    if _ws_manager is None:
        _ws_manager = WebSocketManager()
    return _ws_manager
