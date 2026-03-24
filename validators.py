"""
Input validation and sanitization utilities.

Provides security functions for validating and sanitizing user input.
"""

import html
import re
from typing import Optional, Any, Dict


def sanitize_html(text: str) -> str:
    """
    Sanitize text to prevent XSS attacks.
    
    Args:
        text: Raw user input text.
        
    Returns:
        HTML-escaped text safe for display.
    """
    if not text:
        return ""
    return html.escape(str(text))


def validate_task_name(task_name: str) -> tuple[bool, Optional[str]]:
    """
    Validate task name input.
    
    Args:
        task_name: Task name to validate.
        
    Returns:
        Tuple of (is_valid, error_message).
    """
    if not task_name or not task_name.strip():
        return False, "Task name cannot be empty"
    
    if len(task_name) > 500:
        return False, "Task name too long (max 500 characters)"
    
    # Check for suspicious patterns
    suspicious_patterns = [
        r'<script',
        r'javascript:',
        r'onerror=',
        r'onclick=',
    ]
    
    for pattern in suspicious_patterns:
        if re.search(pattern, task_name, re.IGNORECASE):
            return False, "Task name contains invalid characters"
    
    return True, None


def validate_message(message: str) -> tuple[bool, Optional[str]]:
    """
    Validate chat message input.
    
    Args:
        message: Message to validate.
        
    Returns:
        Tuple of (is_valid, error_message).
    """
    if not message or not message.strip():
        return False, "Message cannot be empty"
    
    if len(message) > 5000:
        return False, "Message too long (max 5000 characters)"
    
    return True, None


def validate_task_id(task_id: Any) -> tuple[bool, Optional[str]]:
    """
    Validate task ID.
    
    Args:
        task_id: Task ID to validate.
        
    Returns:
        Tuple of (is_valid, error_message).
    """
    try:
        task_id_int = int(task_id)
        if task_id_int < 1:
            return False, "Task ID must be positive"
        return True, None
    except (ValueError, TypeError):
        return False, "Invalid task ID format"


def sanitize_api_response(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Sanitize API response data to prevent XSS.
    
    Args:
        data: Response dictionary.
        
    Returns:
        Sanitized response dictionary.
    """
    if not isinstance(data, dict):
        return data
    
    sanitized = {}
    for key, value in data.items():
        if isinstance(value, str):
            sanitized[key] = sanitize_html(value)
        elif isinstance(value, dict):
            sanitized[key] = sanitize_api_response(value)
        elif isinstance(value, list):
            sanitized[key] = [
                sanitize_api_response(item) if isinstance(item, dict) else sanitize_html(str(item)) if isinstance(item, str) else item
                for item in value
            ]
        else:
            sanitized[key] = value
    
    return sanitized
