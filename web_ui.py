"""Web UI module for the Mini AI Assistant.

Provides a Flask-based web interface with:
- Chat interface for interacting with the AI
- Task management dashboard
- Real-time updates via JavaScript fetch
- Security features: XSS protection, rate limiting, input validation
"""

import os
import html
from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from dotenv import load_dotenv

from gemini_client import configure_api, send_message, get_model_info
from task_manager import add_task, list_tasks, complete_task, delete_task, format_tasks_for_display
from memory import append_message, get_history, clear_history
from database import init_db, db_get_stats
from config import Config
from validators import sanitize_html, validate_task_name, validate_message, validate_task_id, sanitize_api_response
from logger import logger

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = Config.SECRET_KEY

# Initialize rate limiter
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=[Config.RATE_LIMIT_DEFAULT] if Config.RATE_LIMIT_ENABLED else [],
    storage_uri="memory://"
)

# Ensure database and API are initialized
init_db()
configure_api()


# ============== Web Pages ==============

@app.route('/')
def index():
    """Render the main chat interface."""
    return render_template('index.html')


@app.route('/tasks')
def tasks_page():
    """Render the task management dashboard."""
    return render_template('tasks.html')


@app.route('/stats')
def stats_page():
    """Render the statistics dashboard."""
    return render_template('stats.html')


# ============== API Endpoints ==============

@app.route('/api/chat', methods=['POST'])
@limiter.limit("20 per minute")
def api_chat():
    """
    Handle chat messages from the web interface.
    
    Expects JSON: {"message": "user input"}
    Returns JSON: {"response": "AI response"}
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Invalid JSON"}), 400
        
        user_message = data.get('message', '').strip()
        
        # Validate input
        is_valid, error_msg = validate_message(user_message)
        if not is_valid:
            return jsonify({"error": error_msg}), 400
        
        # Sanitize input
        user_message = sanitize_html(user_message)
        
        logger.info(f"Received chat message: {user_message[:50]}...")
        
        # Save user message to history
        append_message("user", user_message)
        
        # Get conversation history
        history = get_history()
        
        # Send to Gemini
        response = send_message(user_message, history[:-1])  # Exclude current message
        
        # Process response
        ai_response = process_chat_response(response)
        
        # Sanitize response
        ai_response = sanitize_html(ai_response)
        
        # Save AI response to history
        append_message("model", ai_response)
        
        return jsonify({"response": ai_response})
    
    except Exception as e:
        logger.error(f"Error in chat endpoint: {e}")
        return jsonify({"error": "Internal server error"}), 500


def process_chat_response(response):
    """
    Process Gemini response, handling function calls.
    
    Args:
        response: GeminiResponse object.
        
    Returns:
        String response to display to user.
    """
    from gemini_client import FunctionCallResult, create_function_response
    
    if response.is_function_call and response.function_call:
        # Execute the function
        func_result = execute_function_call(response.function_call)
        
        # Get Gemini's natural language response
        history = get_history()
        follow_up = send_message(f"Function executed. Result: {func_result}", history)
        
        if follow_up.text:
            return follow_up.text
        return func_result
        
    elif response.text:
        return response.text
    
    return "I'm not sure how to respond to that."


def execute_function_call(func_call):
    """
    Execute a function call from Gemini.
    
    Args:
        func_call: FunctionCallResult with name and arguments.
        
    Returns:
        String result of the function execution.
    """
    func_name = func_call.name
    func_args = func_call.args
    
    try:
        if func_name == "add_task":
            task_name = func_args.get("task_name", "")
            result = add_task(task_name)
            if result:
                return f"Task added successfully with ID {result['id']}: {result['name']}"
            return "Failed to add task. Task name may be empty."
            
        elif func_name == "list_tasks":
            tasks = list_tasks()
            return format_tasks_for_display(tasks)
            
        elif func_name == "complete_task":
            task_id = func_args.get("task_id")
            if task_id is None:
                return "Error: No task_id provided."
            result = complete_task(task_id)
            if result:
                return f"Task completed: {result['name']}"
            return f"Task with ID {task_id} not found."
            
        else:
            return f"Unknown function: {func_name}"
            
    except Exception as e:
        return f"Error executing {func_name}: {str(e)}"


@app.route('/api/tasks', methods=['GET'])
def api_get_tasks():
    """Get all tasks as JSON."""
    try:
        tasks = list_tasks()
        # Sanitize task data
        sanitized_tasks = [sanitize_api_response(task) for task in tasks]
        return jsonify(sanitized_tasks)
    except Exception as e:
        logger.error(f"Error getting tasks: {e}")
        return jsonify({"error": "Failed to retrieve tasks"}), 500


@app.route('/api/tasks', methods=['POST'])
@limiter.limit("30 per minute")
def api_add_task_endpoint():
    """Add a new task."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Invalid JSON"}), 400
        
        task_name = data.get('name', '').strip()
        
        # Validate input
        is_valid, error_msg = validate_task_name(task_name)
        if not is_valid:
            return jsonify({"error": error_msg}), 400
        
        # Sanitize input
        task_name = sanitize_html(task_name)
        
        logger.info(f"Adding task: {task_name}")
        
        result = add_task(task_name)
        if result:
            return jsonify(sanitize_api_response(result)), 201
        return jsonify({"error": "Failed to add task"}), 500
    
    except Exception as e:
        logger.error(f"Error adding task: {e}")
        return jsonify({"error": "Internal server error"}), 500


@app.route('/api/tasks/<int:task_id>/complete', methods=['POST'])
def api_complete_task(task_id):
    """Mark a task as completed."""
    try:
        # Validate task ID
        is_valid, error_msg = validate_task_id(task_id)
        if not is_valid:
            return jsonify({"error": error_msg}), 400
        
        result = complete_task(task_id)
        if result:
            return jsonify(sanitize_api_response(result))
        return jsonify({"error": "Task not found"}), 404
    
    except Exception as e:
        logger.error(f"Error completing task {task_id}: {e}")
        return jsonify({"error": "Internal server error"}), 500


@app.route('/api/tasks/<int:task_id>/toggle', methods=['POST'])
def api_toggle_task(task_id):
    """Toggle task completion status (complete/uncomplete)."""
    from database import db_get_task, db_complete_task, get_connection
    
    # Get current task status
    task = db_get_task(task_id)
    if not task:
        return jsonify({"error": "Task not found"}), 404
    
    # Toggle the status
    with get_connection() as conn:
        new_status = 0 if task['completed'] else 1
        conn.execute("""
            UPDATE tasks
            SET completed = ?, completed_at = CASE WHEN ? = 1 THEN CURRENT_TIMESTAMP ELSE NULL END
            WHERE id = ?
        """, (new_status, new_status, task_id))
        conn.commit()
        
        # Fetch updated task
        cursor = conn.execute(
            "SELECT id, name, completed FROM tasks WHERE id = ?",
            (task_id,)
        )
        row = cursor.fetchone()
        
        if row:
            return jsonify({
                "id": row["id"],
                "name": row["name"],
                "completed": bool(row["completed"])
            })
    
    return jsonify({"error": "Failed to toggle task"}), 500


@app.route('/api/tasks/<int:task_id>', methods=['DELETE'])
def api_delete_task(task_id):
    """Delete a task."""
    try:
        # Validate task ID
        is_valid, error_msg = validate_task_id(task_id)
        if not is_valid:
            return jsonify({"error": error_msg}), 400
        
        if delete_task(task_id):
            return jsonify({"success": True})
        return jsonify({"error": "Task not found"}), 404
    
    except Exception as e:
        logger.error(f"Error deleting task {task_id}: {e}")
        return jsonify({"error": "Internal server error"}), 500


@app.route('/api/history', methods=['GET'])
def api_get_history():
    """Get conversation history."""
    history = get_history()
    return jsonify(history)


@app.route('/api/history', methods=['DELETE'])
def api_clear_history_endpoint():
    """Clear conversation history."""
    clear_history()
    return jsonify({"success": True})


@app.route('/api/stats', methods=['GET'])
def api_get_stats():
    """Get database statistics."""
    stats = db_get_stats()
    model_info = get_model_info()
    stats['model'] = model_info.get('model_name', 'Unknown')
    return jsonify(stats)


# ============== Run Server ==============

def run_server(host: str = None, port: int = None, debug: bool = None):
    """
    Run the Flask web server.
    
    Args:
        host: Host to bind to (default: from config).
        port: Port to listen on (default: from config).
        debug: Enable debug mode (default: from config).
    """
    host = host or Config.FLASK_HOST
    port = port or Config.FLASK_PORT
    debug = debug if debug is not None else Config.FLASK_DEBUG
    
    # Ensure API is configured
    if not configure_api():
        logger.warning("GEMINI_API_KEY not set. AI features will not work.")
    
    logger.info(f"Starting Mini AI Assistant Web UI")
    logger.info(f"Environment: {Config.get_environment()}")
    logger.info(f"Local:   http://localhost:{port}")
    
    if host != '127.0.0.1':
        logger.warning(f"Server exposed on all interfaces: {host}")
        logger.warning("This is not recommended for production without proper security")
        logger.info(f"Network: http://{get_local_ip()}:{port}")
    
    logger.info("Press Ctrl+C to stop the server")
    
    app.run(host=host, port=port, debug=debug)


def get_local_ip():
    """Get the local IP address for network access."""
    import socket
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.settimeout(2)  # Set timeout to prevent blocking
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.shutdown(socket.SHUT_RDWR)  # Proper socket shutdown
        s.close()
        return ip
    except Exception as e:
        logger.warning(f"Could not determine local IP: {e}")
        return "127.0.0.1"


if __name__ == '__main__':
    run_server(debug=True)
