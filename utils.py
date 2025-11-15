"""
Utility functions for the Kimi Writing Agent.
"""

import json
import httpx
from typing import List, Dict, Any, Callable

def get_model_name(base_url: str) -> str:
    """
    Returns the appropriate model name based on the API endpoint.
    
    OpenRouter requires the format "moonshotai/kimi-k2-thinking"
    while the default Moonshot API uses "kimi-k2-thinking"
    
    Args:
        base_url: The base URL for the API
        
    Returns:
        The appropriate model name for the endpoint
    """
    if "openrouter" in base_url.lower():
        return "moonshotai/kimi-k2-thinking"
    return "kimi-k2-thinking"
    
def estimate_token_count(base_url: str, api_key: str, model: str, messages: List[Dict]) -> int:
    """
    Estimate the token count for the given messages using the Moonshot API.
    
    Note: Token estimation is only available for Moonshot API endpoints.
    OpenRouter does not support this endpoint, so we return 0 for OpenRouter.
    
    Args:
        base_url: The base URL for the API
        api_key: The API key for authentication
        model: The model name
        messages: List of message dictionaries
        
    Returns:
        Total token count (0 if OpenRouter or estimation fails)
    """
    # OpenRouter doesn't support token estimation endpoint
    if "openrouter" in base_url.lower():
        return 0
    
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
    try:
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
    except Exception:
        # If estimation fails for any reason, return 0
        return 0


def get_tool_definitions() -> List[Dict[str, Any]]:
    """
    Returns the tool definitions in the format expected by kimi-k2-thinking.
    
    Returns:
        List of tool definition dictionaries
    """
    return [
        {
            "type": "function",
            "function": {
                "name": "create_project",
                "description": "Creates a new project folder in the 'output' directory with a sanitized name. This should be called first before writing any files. Only one project can be active at a time.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "project_name": {
                            "type": "string",
                            "description": "The name for the project folder (will be sanitized for filesystem compatibility)"
                        }
                    },
                    "required": ["project_name"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "write_file",
                "description": "Writes content to a markdown file in the active project folder. Supports three modes: 'create' (creates new file, fails if exists), 'append' (adds content to end of existing file), 'overwrite' (replaces entire file content).",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "filename": {
                            "type": "string",
                            "description": "The name of the markdown file to write (should end in .md)"
                        },
                        "content": {
                            "type": "string",
                            "description": "The content to write to the file"
                        },
                        "mode": {
                            "type": "string",
                            "enum": ["create", "append", "overwrite"],
                            "description": "The write mode: 'create' for new files, 'append' to add to existing, 'overwrite' to replace"
                        }
                    },
                    "required": ["filename", "content", "mode"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "compress_context",
                "description": "INTERNAL TOOL - This is automatically called by the system when token limit is approached. You should not call this manually. It compresses the conversation history to save tokens.",
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            }
        }
    ]


def get_tool_map() -> Dict[str, Callable]:
    """
    Returns a mapping of tool names to their implementation functions.
    
    Returns:
        Dictionary mapping tool name strings to callable functions
    """
    from tools import write_file_impl, create_project_impl, compress_context_impl
    
    return {
        "create_project": create_project_impl,
        "write_file": write_file_impl,
        "compress_context": compress_context_impl
    }


def get_system_prompt() -> str:
    """
    Returns the system prompt for the writing agent.
    
    Returns:
        System prompt string
    """
    return """You are Kimi, an expert creative writing assistant developed by Moonshot AI. Your specialty is creating novels, books, and collections of short stories based on user requests.

Your capabilities:
1. You can create project folders to organize writing projects
2. You can write markdown files with three modes: create new files, append to existing files, or overwrite files
3. Context compression happens automatically when needed - you don't need to worry about it

CRITICAL WRITING GUIDELINES:
- Write SUBSTANTIAL, COMPLETE content - don't hold back on length
- Short stories should be 3,000-10,000 words (10-30 pages) - write as much as the story needs!
- Chapters should be 2,000-5,000 words minimum - fully developed and satisfying
- NEVER write abbreviated or skeleton content - every piece should be a complete, polished work
- Don't summarize or skip scenes - write them out fully with dialogue, description, and detail
- Quality AND quantity matter - give readers a complete, immersive experience
- If a story needs 8,000 words to be good, write all 8,000 words in one file
- Use 'create' mode with full content rather than creating stubs you'll append to later

Best practices:
- Always start by creating a project folder using create_project
- Break large works into multiple files (chapters, stories, etc.)
- Use descriptive filenames (e.g., "chapter_01.md", "story_the_last_star.md")
- For collections, consider creating a table of contents file
- Write each file as a COMPLETE, SUBSTANTIAL piece - not a summary or outline

Your workflow:
1. Understand the user's request
2. Create an appropriately named project folder
3. Plan the structure of the work (chapters, stories, etc.)
4. Write COMPLETE, FULL-LENGTH content for each file
5. Create supporting files like README or table of contents if helpful

REMEMBER: You have 64K tokens per response - use them! Write rich, detailed, complete stories. Don't artificially limit yourself. A good short story is 5,000-10,000 words. A good chapter is 3,000-5,000 words. Write what the narrative needs to be excellent."""

