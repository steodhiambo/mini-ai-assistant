"""
Task management module.

Handles CRUD operations for tasks with local JSON persistence.
Each task has an auto-incrementing ID, name, and completion status.
"""

import json
from pathlib import Path
from typing import List, Dict, Any, Optional

# Path to the tasks JSON file
TASKS_FILE = Path(__file__).parent / "storage.json"


def load_tasks() -> List[Dict[str, Any]]:
    """
    Load tasks from JSON file.
    
    Returns:
        List of task dictionaries. Each task has:
        - id: integer task identifier
        - name: string task description
        - completed: boolean completion status
        Returns empty list if file doesn't exist or is invalid.
    """
    if not TASKS_FILE.exists():
        return []
    
    try:
        with open(TASKS_FILE, 'r', encoding='utf-8') as f:
            tasks = json.load(f)
            # Validate structure
            if isinstance(tasks, list):
                return tasks
            return []
    except (json.JSONDecodeError, IOError):
        # Return empty list if file is corrupted or unreadable
        return []


def save_tasks(tasks: List[Dict[str, Any]]) -> bool:
    """
    Save tasks to JSON file.
    
    Args:
        tasks: List of task dictionaries to save.
        
    Returns:
        True if save was successful, False otherwise.
    """
    try:
        with open(TASKS_FILE, 'w', encoding='utf-8') as f:
            json.dump(tasks, f, indent=2, ensure_ascii=False)
        return True
    except IOError as e:
        print(f"Error saving tasks: {e}")
        return False


def _get_next_id(tasks: List[Dict[str, Any]]) -> int:
    """
    Generate the next available task ID.
    
    Args:
        tasks: Current list of tasks.
        
    Returns:
        Next available integer ID (max existing ID + 1, or 1 if empty).
    """
    if not tasks:
        return 1
    return max(task.get('id', 0) for task in tasks) + 1


def add_task(task_name: str) -> Optional[Dict[str, Any]]:
    """
    Add a new task to the task list.
    
    Args:
        task_name: The name/description of the task to add.
        
    Returns:
        The created task dictionary if successful, None otherwise.
    """
    if not task_name or not task_name.strip():
        return None
    
    tasks = load_tasks()
    
    new_task = {
        "id": _get_next_id(tasks),
        "name": task_name.strip(),
        "completed": False
    }
    
    tasks.append(new_task)
    
    if save_tasks(tasks):
        return new_task
    return None


def list_tasks() -> List[Dict[str, Any]]:
    """
    Get all tasks.
    
    Returns:
        List of all task dictionaries.
    """
    return load_tasks()


def complete_task(task_id: int) -> Optional[Dict[str, Any]]:
    """
    Mark a task as completed by its ID.
    
    Args:
        task_id: The integer ID of the task to complete.
        
    Returns:
        The updated task dictionary if successful, None if task not found.
    """
    tasks = load_tasks()
    
    for task in tasks:
        if task.get('id') == task_id:
            task['completed'] = True
            save_tasks(tasks)
            return task
    
    # Task not found
    return None


def delete_task(task_id: int) -> bool:
    """
    Delete a task by its ID.
    
    Args:
        task_id: The integer ID of the task to delete.
        
    Returns:
        True if task was deleted, False if not found.
    """
    tasks = load_tasks()
    
    original_length = len(tasks)
    tasks = [task for task in tasks if task.get('id') != task_id]
    
    if len(tasks) < original_length:
        return save_tasks(tasks)
    return False


def get_task_by_id(task_id: int) -> Optional[Dict[str, Any]]:
    """
    Get a specific task by its ID.
    
    Args:
        task_id: The integer ID of the task to retrieve.
        
    Returns:
        The task dictionary if found, None otherwise.
    """
    tasks = load_tasks()
    
    for task in tasks:
        if task.get('id') == task_id:
            return task
    return None


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
