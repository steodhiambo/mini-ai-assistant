#!/usr/bin/env python3
"""
Mini Personal AI Assistant - Main CLI Application

A lightweight AI assistant powered by Google Gemini that:
- Manages tasks using natural language
- Answers general knowledge questions
- Automatically routes user intent using Gemini function calling
- Maintains conversational memory

Usage:
    python main.py

Environment:
    Set GEMINI_API_KEY environment variable or create a .env file:
    GEMINI_API_KEY=your-api-key-here
"""

import os
import sys
from typing import Optional

# Import local modules
from memory import append_message, get_history, clear_history
from task_manager import (
    add_task,
    list_tasks,
    complete_task,
    format_tasks_for_display,
    get_task_by_id
)
from gemini_client import (
    configure_api,
    send_message,
    create_function_response,
    get_model_info,
    GeminiResponse,
    FunctionCallResult
)


# CLI Configuration
PROMPT = "You: "
AI_PREFIX = "Assistant: "
WELCOME_MESSAGE = """
╔═══════════════════════════════════════════════════════════╗
║           Mini Personal AI Assistant                      ║
║           Powered by Google Gemini                        ║
╚═══════════════════════════════════════════════════════════╝

I can help you manage tasks and answer questions!

Commands:
  • Just ask me anything or tell me to add/complete tasks
  • Type 'tasks' to see your task list
  • Type 'clear' to clear conversation history
  • Type 'quit' or 'exit' to end the session
  • Press Ctrl+C to exit anytime

"""


def execute_function_call(func_call: FunctionCallResult) -> str:
    """
    Execute a function call from Gemini and return the result.
    
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


def handle_direct_command(user_input: str) -> Optional[str]:
    """
    Handle direct CLI commands before sending to Gemini.
    
    Args:
        user_input: Raw user input string.
        
    Returns:
        Response string if command handled, None otherwise.
    """
    cmd = user_input.strip().lower()
    
    if cmd in ("quit", "exit"):
        print("\nGoodbye! 👋")
        sys.exit(0)
        
    elif cmd == "clear":
        clear_history()
        return "Conversation history cleared."
        
    elif cmd == "tasks":
        tasks = list_tasks()
        return format_tasks_for_display(tasks)
    
    return None


def process_ai_response(response: GeminiResponse) -> str:
    """
    Process Gemini's response, handling both text and function calls.
    
    If Gemini returns a function call:
    1. Execute the function locally
    2. Send result back to Gemini for natural language response
    3. Return Gemini's final response
    
    If Gemini returns text:
    1. Return the text directly
    
    Args:
        response: GeminiResponse from the API.
        
    Returns:
        Final response string to display to user.
    """
    if response.is_function_call and response.function_call:
        # Execute the function
        func_result = execute_function_call(response.function_call)
        
        # Send function result back to Gemini for natural language response
        func_response_msg = create_function_response(
            response.function_call.name,
            func_result
        )
        
        # Get Gemini's natural language response based on function result
        history = get_history()
        follow_up = send_message(
            f"Function executed. Result: {func_result}",
            history
        )
        
        if follow_up.text:
            return follow_up.text
        return func_result
        
    elif response.text:
        return response.text
    
    return "I'm not sure how to respond to that."


def run_cli():
    """
    Main CLI loop for the AI assistant.
    
    Runs an infinite loop that:
    1. Gets user input
    2. Sends to Gemini (with conversation history)
    3. Handles function calls or displays text responses
    4. Maintains conversation memory
    """
    # Print welcome message
    print(WELCOME_MESSAGE)
    
    # Configure API
    if not configure_api():
        print("Error: GEMINI_API_KEY environment variable not set.")
        print("Please set your API key and try again.")
        print("\nExample:")
        print("  export GEMINI_API_KEY='your-api-key-here'")
        print("  python main.py")
        sys.exit(1)
    
    # Show model info
    model_info = get_model_info()
    print(f"Using model: {model_info['model_name']}")
    print("-" * 50)
    
    # Main conversation loop
    while True:
        try:
            # Get user input
            user_input = input(PROMPT).strip()
            
            # Skip empty input
            if not user_input:
                continue
            
            # Check for direct commands
            cmd_response = handle_direct_command(user_input)
            if cmd_response:
                print(f"\n{AI_PREFIX}{cmd_response}\n")
                continue
            
            # Save user message to history
            append_message("user", user_input)
            
            # Get conversation history for context
            history = get_history()
            
            # Send to Gemini
            response = send_message(user_input, history)
            
            # Process and display response
            ai_response = process_ai_response(response)
            print(f"\n{AI_PREFIX}{ai_response}\n")
            
            # Save AI response to history
            append_message("model", ai_response)
            
        except KeyboardInterrupt:
            # Handle Ctrl+C gracefully
            print("\n\nInterrupted. Goodbye! 👋")
            break
            
        except EOFError:
            # Handle end of input
            print("\nGoodbye! 👋")
            break
            
        except Exception as e:
            # Handle unexpected errors
            print(f"\n{AI_PREFIX}Sorry, I encountered an error: {str(e)}\n")


def main():
    """Entry point for the application."""
    run_cli()


if __name__ == "__main__":
    main()
