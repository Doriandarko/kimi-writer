"""
WebSocket endpoint handlers for real-time updates.

This module handles WebSocket connections for streaming novel generation
progress to the frontend.
"""

from fastapi import WebSocket, WebSocketDisconnect
import logging

from backend.websocket_manager import get_ws_manager

logger = logging.getLogger(__name__)


async def websocket_endpoint(websocket: WebSocket, project_id: str):
    """
    WebSocket endpoint for real-time project updates.

    Args:
        websocket: WebSocket connection
        project_id: Project ID to subscribe to
    """
    ws_manager = get_ws_manager()

    # Accept connection
    await websocket.accept()

    # Register connection
    await ws_manager.connect(project_id, websocket)

    try:
        # Keep connection alive and listen for client messages
        while True:
            # Receive messages from client (e.g., ping/pong, manual requests)
            data = await websocket.receive_text()

            # Handle client messages if needed
            # For now, we just echo back to confirm receipt
            if data == "ping":
                await websocket.send_json({"type": "pong"})

    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected for project {project_id}")
    except Exception as e:
        logger.error(f"WebSocket error for project {project_id}: {e}")
    finally:
        # Unregister connection
        await ws_manager.disconnect(project_id, websocket)
