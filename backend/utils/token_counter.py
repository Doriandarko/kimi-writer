"""
Token counting utilities for the Kimi Multi-Agent Novel Writing System.

This module provides token estimation using the Moonshot AI API.
"""

import httpx
from typing import List, Dict, Any


def estimate_token_count(
    base_url: str,
    api_key: str,
    model: str,
    messages: List[Dict]
) -> int:
    """
    Estimate the token count for the given messages using the Moonshot API.

    Note: Token estimation uses api.moonshot.ai (not .cn)

    Args:
        base_url: The base URL for the API (will be converted to .ai for token endpoint)
        api_key: The API key for authentication
        model: The model name
        messages: List of message dictionaries

    Returns:
        Total token count

    Raises:
        httpx.HTTPStatusError: If API request fails
    """
    # Convert messages to serializable format (remove non-serializable objects)
    serializable_messages = []
    for msg in messages:
        if hasattr(msg, 'model_dump'):
            # OpenAI SDK message object
            msg_dict = msg.model_dump()
        elif isinstance(msg, dict):
            msg_dict = msg.copy()
        else:
            msg_dict = {"role": "assistant", "content": str(msg)}

        # Clean up the message to only include serializable fields
        clean_msg = {}
        if 'role' in msg_dict:
            clean_msg['role'] = msg_dict['role']
        if 'content' in msg_dict and msg_dict['content']:
            clean_msg['content'] = msg_dict['content']
        if 'name' in msg_dict:
            clean_msg['name'] = msg_dict['name']
        if 'tool_calls' in msg_dict and msg_dict['tool_calls']:
            clean_msg['tool_calls'] = msg_dict['tool_calls']
        if 'tool_call_id' in msg_dict:
            clean_msg['tool_call_id'] = msg_dict['tool_call_id']

        serializable_messages.append(clean_msg)

    # Both token estimation and chat use api.moonshot.ai
    token_base_url = base_url

    # Make the API call
    with httpx.Client(
        base_url=token_base_url,
        headers={"Authorization": f"Bearer {api_key}"},
        timeout=30.0
    ) as client:
        response = client.post(
            "/tokenizers/estimate-token-count",
            json={
                "model": model,
                "messages": serializable_messages
            }
        )
        response.raise_for_status()
        data = response.json()
        return data.get("data", {}).get("total_tokens", 0)


async def estimate_token_count_async(
    base_url: str,
    api_key: str,
    model: str,
    messages: List[Dict]
) -> int:
    """
    Async version of token estimation.

    Args:
        base_url: The base URL for the API
        api_key: The API key for authentication
        model: The model name
        messages: List of message dictionaries

    Returns:
        Total token count

    Raises:
        httpx.HTTPStatusError: If API request fails
    """
    # Convert messages to serializable format
    serializable_messages = []
    for msg in messages:
        if hasattr(msg, 'model_dump'):
            msg_dict = msg.model_dump()
        elif isinstance(msg, dict):
            msg_dict = msg.copy()
        else:
            msg_dict = {"role": "assistant", "content": str(msg)}

        clean_msg = {}
        if 'role' in msg_dict:
            clean_msg['role'] = msg_dict['role']
        if 'content' in msg_dict and msg_dict['content']:
            clean_msg['content'] = msg_dict['content']
        if 'name' in msg_dict:
            clean_msg['name'] = msg_dict['name']
        if 'tool_calls' in msg_dict and msg_dict['tool_calls']:
            clean_msg['tool_calls'] = msg_dict['tool_calls']
        if 'tool_call_id' in msg_dict:
            clean_msg['tool_call_id'] = msg_dict['tool_call_id']

        serializable_messages.append(clean_msg)

    token_base_url = base_url

    async with httpx.AsyncClient(
        base_url=token_base_url,
        headers={"Authorization": f"Bearer {api_key}"},
        timeout=30.0
    ) as client:
        response = await client.post(
            "/tokenizers/estimate-token-count",
            json={
                "model": model,
                "messages": serializable_messages
            }
        )
        response.raise_for_status()
        data = response.json()
        return data.get("data", {}).get("total_tokens", 0)


def should_compress(
    token_count: int,
    token_limit: int,
    compression_threshold: int
) -> bool:
    """
    Determine if context should be compressed based on token count.

    Args:
        token_count: Current token count
        token_limit: Maximum token limit
        compression_threshold: Threshold at which to start compression

    Returns:
        True if compression is needed
    """
    return token_count >= compression_threshold
