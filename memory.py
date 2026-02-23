"""
Conversation memory management module.

Handles loading, saving, and managing conversation history using SQLite.
Uses database.py for all storage operations.
Limits history to last 10 messages to reduce token usage.

Note: This module maintains backward compatibility by checking for
legacy JSON storage and migrating if needed.
"""

from typing import List, Dict, Any
from database import (
    init_db,
    db_append_message,
    db_get_history,
    db_clear_history
)

# Maximum number of messages to keep in history
MAX_MESSAGES = 10

# Ensure database is initialized on module load
init_db()


def _migrate_from_json():
    """
    Migrate conversation history from legacy JSON storage to SQLite.
    
    This function checks for the old history.json file and
    migrates any existing messages to the SQLite database.
    """
    import json
    from pathlib import Path
    
    json_file = Path(__file__).parent / "history.json"
    if not json_file.exists():
        return
    
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            history = json.load(f)
        
        if history:
            # Migrate each message
            for msg in history:
                role = msg.get('role', 'user')
                content = msg.get('content', '')
                if role and content:
                    db_append_message(role, content, limit=100)
            
            # Clear JSON file after migration
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump([], f, indent=2)
    except (json.JSONDecodeError, IOError):
        pass  # Ignore migration errors


# Run migration on module load (one-time)
_migrate_from_json()


def load_history() -> List[Dict[str, str]]:
    """
    Load conversation history from the database.
    
    Returns:
        List of message dictionaries with 'role' and 'content' keys.
        Returns empty list if no history exists.
    """
    return db_get_history(MAX_MESSAGES)


def save_history(history: List[Dict[str, str]]) -> bool:
    """
    Save conversation history - kept for API compatibility.
    
    Note: With SQLite, messages are persisted immediately on append.
    This function is kept for backward compatibility but is a no-op.
    
    Args:
        history: List of message dictionaries (ignored).
        
    Returns:
        True (always successful).
    """
    return True


def append_message(role: str, content: str) -> List[Dict[str, str]]:
    """
    Append a new message to conversation history and enforce message limit.
    
    Args:
        role: The role of the message sender ('user' or 'model').
        content: The message content.
        
    Returns:
        Updated history list after appending and trimming.
    """
    return db_append_message(role, content, MAX_MESSAGES)


def clear_history() -> bool:
    """
    Clear all conversation history.
    
    Returns:
        True if clear was successful, False otherwise.
    """
    return db_clear_history()


def get_history() -> List[Dict[str, str]]:
    """
    Get current conversation history without modification.
    
    Returns:
        Current list of messages in history (last MAX_MESSAGES).
    """
    return db_get_history(MAX_MESSAGES)
