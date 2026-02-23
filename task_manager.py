"""
Task management module.

Handles CRUD operations for tasks with SQLite database persistence.
Uses database.py for all storage operations.
Each task has an auto-incrementing ID, name, and completion status.

Note: This module maintains backward compatibility by checking for
legacy JSON storage and migrating if needed.
"""

from typing import List, Dict, Any, Optional
from database import (
    init_db,
    db_add_task,
    db_list_tasks,
    db_complete_task,
    db_delete_task,
    db_get_task,
    db_clear_completed_tasks
)

# Ensure database is initialized on module load
init_db()


def _migrate_from_json():
    """
    Migrate tasks from legacy JSON storage to SQLite.
    
    This function checks for the old storage.json file and
    migrates any existing tasks to the SQLite database.
    """
    import json
    from pathlib import Path
    
    json_file = Path(__file__).parent / "storage.json"
    if not json_file.exists():
        return
    
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            tasks = json.load(f)
        
        if tasks:
            # Migrate each task
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump([], f)  # Clear JSON file after migration
            
            for task in tasks:
                name = task.get('name', '')
                completed = task.get('completed', False)
                
                if name:
                    result = db_add_task(name)
                    if result and completed:
                        db_complete_task(result['id'])
    except (json.JSONDecodeError, IOError):
        pass  # Ignore migration errors


# Run migration on module load (one-time)
_migrate_from_json()


def load_tasks() -> List[Dict[str, Any]]:
    """
    Load tasks from the database.
    
    Returns:
        List of task dictionaries. Each task has:
        - id: integer task identifier
        - name: string task description
        - completed: boolean completion status
    """
    return db_list_tasks()


def save_tasks(tasks: List[Dict[str, Any]]) -> bool:
    """
    Save tasks - kept for API compatibility.
    
    Note: With SQLite, individual operations persist immediately.
    This function is kept for backward compatibility but is a no-op.
    
    Args:
        tasks: List of task dictionaries (ignored).
        
    Returns:
        True (always successful).
    """
    return True


def add_task(task_name: str) -> Optional[Dict[str, Any]]:
    """
    Add a new task to the task list.
    
    Args:
        task_name: The name/description of the task to add.
        
    Returns:
        The created task dictionary if successful, None otherwise.
    """
    return db_add_task(task_name)


def list_tasks() -> List[Dict[str, Any]]:
    """
    Get all tasks.
    
    Returns:
        List of all task dictionaries.
    """
    return db_list_tasks()


def complete_task(task_id: int) -> Optional[Dict[str, Any]]:
    """
    Mark a task as completed by its ID.
    
    Args:
        task_id: The integer ID of the task to complete.
        
    Returns:
        The updated task dictionary if successful, None if task not found.
    """
    return db_complete_task(task_id)


def delete_task(task_id: int) -> bool:
    """
    Delete a task by its ID.
    
    Args:
        task_id: The integer ID of the task to delete.
        
    Returns:
        True if task was deleted, False if not found.
    """
    return db_delete_task(task_id)


def get_task_by_id(task_id: int) -> Optional[Dict[str, Any]]:
    """
    Get a specific task by its ID.
    
    Args:
        task_id: The integer ID of the task to retrieve.
        
    Returns:
        The task dictionary if found, None otherwise.
    """
    return db_get_task(task_id)


def clear_completed() -> int:
    """
    Remove all completed tasks.
    
    Returns:
        Number of tasks removed.
    """
    return db_clear_completed_tasks()


def format_tasks_for_display(tasks: List[Dict[str, Any]]) -> str:
    """
    Format tasks list for human-readable display.
    
    Args:
        tasks: List of task dictionaries.
        
    Returns:
        Formatted string representation of tasks.
    """
    if not tasks:
        return "No tasks found."
    
    lines = []
    for task in tasks:
        status = "✓" if task.get('completed', False) else "○"
        task_id = task.get('id', '?')
        name = task.get('name', 'Unknown')
        lines.append(f"[{task_id}] {status} {name}")
    
    return "\n".join(lines)
