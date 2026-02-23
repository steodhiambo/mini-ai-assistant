"""
Database module for SQLite operations.

Provides a unified database interface for:
- Task storage and retrieval
- Conversation history management
- Database initialization and migrations
"""

import sqlite3
from pathlib import Path
from typing import List, Dict, Any, Optional
from contextlib import contextmanager

# Path to the SQLite database file
DB_FILE = Path(__file__).parent / "assistant.db"


@contextmanager
def get_connection():
    """
    Context manager for database connections.
    
    Yields:
        sqlite3.Connection object for database operations.
        
    Usage:
        with get_connection() as conn:
            cursor = conn.execute("SELECT * FROM tasks")
    """
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row  # Enable column access by name
    try:
        yield conn
    finally:
        conn.close()


def init_db():
    """
    Initialize the database with required tables.
    
    Creates:
    - tasks table: Stores task items with status
    - conversation_history table: Stores chat messages
    
    This function is idempotent - safe to call multiple times.
    """
    with get_connection() as conn:
        # Create tasks table
        conn.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                completed INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                completed_at TIMESTAMP
            )
        """)
        
        # Create conversation history table
        conn.execute("""
            CREATE TABLE IF NOT EXISTS conversation_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create index for faster history retrieval
        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_history_created 
            ON conversation_history(created_at DESC)
        """)
        
        conn.commit()


# ============== Task Operations ==============

def db_add_task(task_name: str) -> Optional[Dict[str, Any]]:
    """
    Add a new task to the database.
    
    Args:
        task_name: The name/description of the task.
        
    Returns:
        Dictionary with task details if successful, None otherwise.
    """
    if not task_name or not task_name.strip():
        return None
    
    with get_connection() as conn:
        cursor = conn.execute(
            "INSERT INTO tasks (name) VALUES (?)",
            (task_name.strip(),)
        )
        conn.commit()
        
        task_id = cursor.lastrowid
        return {
            "id": task_id,
            "name": task_name.strip(),
            "completed": False
        }


def db_list_tasks() -> List[Dict[str, Any]]:
    """
    Get all tasks from the database.
    
    Returns:
        List of task dictionaries ordered by creation date.
    """
    with get_connection() as conn:
        cursor = conn.execute(
            "SELECT id, name, completed FROM tasks ORDER BY created_at ASC"
        )
        rows = cursor.fetchall()
        
        return [
            {
                "id": row["id"],
                "name": row["name"],
                "completed": bool(row["completed"])
            }
            for row in rows
        ]


def db_complete_task(task_id: int) -> Optional[Dict[str, Any]]:
    """
    Mark a task as completed.

    Args:
        task_id: The ID of the task to complete.

    Returns:
        Updated task dictionary if found, None otherwise.
    """
    with get_connection() as conn:
        # Update the task
        conn.execute("""
            UPDATE tasks
            SET completed = 1, completed_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (task_id,))
        conn.commit()  # Commit the transaction

        # Fetch the updated task
        cursor = conn.execute(
            "SELECT id, name, completed FROM tasks WHERE id = ?",
            (task_id,)
        )
        row = cursor.fetchone()

        if row:
            return {
                "id": row["id"],
                "name": row["name"],
                "completed": bool(row["completed"])
            }
        return None


def db_delete_task(task_id: int) -> bool:
    """
    Delete a task from the database.
    
    Args:
        task_id: The ID of the task to delete.
        
    Returns:
        True if deleted, False if not found.
    """
    with get_connection() as conn:
        cursor = conn.execute(
            "DELETE FROM tasks WHERE id = ?",
            (task_id,)
        )
        conn.commit()
        return cursor.rowcount > 0


def db_get_task(task_id: int) -> Optional[Dict[str, Any]]:
    """
    Get a specific task by ID.
    
    Args:
        task_id: The task ID to retrieve.
        
    Returns:
        Task dictionary if found, None otherwise.
    """
    with get_connection() as conn:
        cursor = conn.execute(
            "SELECT id, name, completed FROM tasks WHERE id = ?",
            (task_id,)
        )
        row = cursor.fetchone()
        
        if row:
            return {
                "id": row["id"],
                "name": row["name"],
                "completed": bool(row["completed"])
            }
        return None


def db_clear_completed_tasks() -> int:
    """
    Remove all completed tasks from the database.
    
    Returns:
        Number of tasks deleted.
    """
    with get_connection() as conn:
        cursor = conn.execute("DELETE FROM tasks WHERE completed = 1")
        conn.commit()
        return cursor.rowcount


# ============== Conversation History Operations ==============

def db_append_message(role: str, content: str, limit: int = 10) -> List[Dict[str, str]]:
    """
    Append a message to conversation history and enforce limit.
    
    Args:
        role: The role ('user' or 'model').
        content: The message content.
        limit: Maximum number of messages to keep.
        
    Returns:
        List of recent messages after insertion.
    """
    with get_connection() as conn:
        # Insert new message
        conn.execute(
            "INSERT INTO conversation_history (role, content) VALUES (?, ?)",
            (role, content)
        )
        
        # Delete old messages beyond the limit
        conn.execute("""
            DELETE FROM conversation_history 
            WHERE id NOT IN (
                SELECT id FROM conversation_history 
                ORDER BY created_at DESC 
                LIMIT ?
            )
        """, (limit,))
        
        conn.commit()
        
        # Fetch recent messages
        return db_get_history(limit)


def db_get_history(limit: int = 10) -> List[Dict[str, str]]:
    """
    Get recent conversation history.
    
    Args:
        limit: Maximum number of messages to retrieve.
        
    Returns:
        List of message dictionaries with 'role' and 'content'.
    """
    with get_connection() as conn:
        cursor = conn.execute("""
            SELECT role, content FROM conversation_history 
            ORDER BY created_at DESC 
            LIMIT ?
        """, (limit,))
        
        rows = cursor.fetchall()
        # Reverse to get chronological order
        return [
            {"role": row["role"], "content": row["content"]}
            for row in reversed(rows)
        ]


def db_clear_history() -> bool:
    """
    Clear all conversation history.
    
    Returns:
        True if successful.
    """
    with get_connection() as conn:
        conn.execute("DELETE FROM conversation_history")
        conn.commit()
        return True


def db_get_stats() -> Dict[str, Any]:
    """
    Get database statistics.
    
    Returns:
        Dictionary with task and conversation stats.
    """
    with get_connection() as conn:
        # Task stats
        total = conn.execute("SELECT COUNT(*) FROM tasks").fetchone()[0]
        completed = conn.execute("SELECT COUNT(*) FROM tasks WHERE completed = 1").fetchone()[0]
        pending = total - completed
        
        # History stats
        messages = conn.execute("SELECT COUNT(*) FROM conversation_history").fetchone()[0]
        
        return {
            "total_tasks": total,
            "completed_tasks": completed,
            "pending_tasks": pending,
            "conversation_messages": messages
        }
