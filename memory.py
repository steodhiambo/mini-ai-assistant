"""
Conversation memory management module.

Handles loading, saving, and managing conversation history.
Limits history to last 10 messages to reduce token usage.
"""

import json
from pathlib import Path
from typing import List, Dict, Any

# Path to the history JSON file
HISTORY_FILE = Path(__file__).parent / "history.json"

# Maximum number of messages to keep in history
MAX_MESSAGES = 10


def load_history() -> List[Dict[str, str]]:
    """
    Load conversation history from JSON file.
    
    Returns:
        List of message dictionaries with 'role' and 'content' keys.
        Returns empty list if file doesn't exist or is invalid.
    """
    if not HISTORY_FILE.exists():
        return []
    
    try:
        with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
            history = json.load(f)
            # Validate structure
            if isinstance(history, list):
                return history
            return []
    except (json.JSONDecodeError, IOError):
        # Return empty list if file is corrupted or unreadable
        return []


def save_history(history: List[Dict[str, str]]) -> bool:
    """
    Save conversation history to JSON file.
    
    Args:
        history: List of message dictionaries to save.
        
    Returns:
        True if save was successful, False otherwise.
    """
    try:
        with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
            json.dump(history, f, indent=2, ensure_ascii=False)
        return True
    except IOError as e:
        print(f"Error saving history: {e}")
        return False


def append_message(role: str, content: str) -> List[Dict[str, str]]:
    """
    Append a new message to conversation history and enforce message limit.
    
    Args:
        role: The role of the message sender ('user' or 'model').
        content: The message content.
        
    Returns:
        Updated history list after appending and trimming.
    """
    history = load_history()
    
    # Add new message
    history.append({
        "role": role,
        "content": content
    })
    
    # Enforce message limit - keep only the last MAX_MESSAGES
    # This ensures we don't exceed token limits while maintaining context
    if len(history) > MAX_MESSAGES:
        history = history[-MAX_MESSAGES:]
    
    save_history(history)
    return history


def clear_history() -> bool:
    """
    Clear all conversation history.
    
    Returns:
        True if clear was successful, False otherwise.
    """
    try:
        with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
            json.dump([], f, indent=2)
        return True
    except IOError as e:
        print(f"Error clearing history: {e}")
        return False


def get_history() -> List[Dict[str, str]]:
    """
    Get current conversation history without modification.
    
    Returns:
        Current list of messages in history.
    """
    return load_history()
