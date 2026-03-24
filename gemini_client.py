"""Gemini API client module.

Handles interaction with Google's Gemini API including:
- API configuration via environment variable or .env file
- Function declarations for tool calling
- Message generation with function routing
- Response parsing for function calls vs text responses
- Resource limits and timeout controls

Uses the new google-genai package (successor to google-generativeai).
"""

import os
from pathlib import Path
from typing import Dict, Any, Optional, List
from dataclasses import dataclass

from dotenv import load_dotenv
from google import genai
from google.genai import types

from config import Config
from logger import logger

# Load environment variables from .env file if it exists
# This allows API key to be stored in .env instead of only environment
ENV_FILE = Path(__file__).parent / ".env"
load_dotenv(dotenv_path=ENV_FILE)


@dataclass
class FunctionCallResult:
    """Represents a function call detected in Gemini's response."""
    name: str
    args: Dict[str, Any]


@dataclass
class GeminiResponse:
    """Container for Gemini API response."""
    text: Optional[str] = None
    function_call: Optional[FunctionCallResult] = None
    is_function_call: bool = False


def _get_tools_config() -> List[types.Tool]:
    """
    Create the tool configuration for Gemini function calling.
    
    Returns:
        List of Tool objects with function declarations.
    """
    return [
        types.Tool(
            function_declarations=[
                types.FunctionDeclaration(
                    name="add_task",
                    description="Add a new task to the user's task list. Use this when the user wants to create or add a new task, todo, or reminder.",
                    parameters={
                        "type": "object",
                        "properties": {
                            "task_name": {
                                "type": "string",
                                "description": "The name or description of the task to add. Should be clear and actionable."
                            }
                        },
                        "required": ["task_name"]
                    }
                ),
                types.FunctionDeclaration(
                    name="list_tasks",
                    description="List all tasks in the user's task list. Use this when the user wants to see their tasks, todos, or what they need to do.",
                    parameters={
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                ),
                types.FunctionDeclaration(
                    name="complete_task",
                    description="Mark a task as completed. Use this when the user wants to finish, complete, or check off a specific task by its ID.",
                    parameters={
                        "type": "object",
                        "properties": {
                            "task_id": {
                                "type": "integer",
                                "description": "The numeric ID of the task to mark as completed."
                            }
                        },
                        "required": ["task_id"]
                    }
                )
            ]
        )
    ]


class GeminiClient:
    """Gemini API client wrapper with configuration management."""
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize the Gemini client."""
        self.api_key = api_key or Config.GEMINI_API_KEY
        self.client: Optional[genai.Client] = None
        self.model_name = Config.GEMINI_MODEL
        self.temperature = Config.GEMINI_TEMPERATURE
        self.max_tokens = Config.GEMINI_MAX_TOKENS
        self.timeout = Config.GEMINI_TIMEOUT
        
        if self.api_key:
            self._initialize_client()
    
    def _initialize_client(self) -> bool:
        """Initialize the Gemini API client."""
        try:
            self.client = genai.Client(api_key=self.api_key)
            logger.info(f"Gemini client initialized with model: {self.model_name}")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize Gemini client: {e}")
            return False
    
    def is_configured(self) -> bool:
        """Check if client is properly configured."""
        return self.client is not None


# Global client instance
_gemini_client: Optional[GeminiClient] = None


def configure_api(api_key: Optional[str] = None) -> bool:
    """
    Configure the Gemini API with the provided or environment key.
    
    Args:
        api_key: Optional API key. If not provided, uses config.
        
    Returns:
        True if configuration successful, False otherwise.
    """
    global _gemini_client
    _gemini_client = GeminiClient(api_key)
    return _gemini_client.is_configured()


def _convert_history_to_gemini_format(
    history: List[Dict[str, str]]
) -> List[types.Content]:
    """
    Convert internal history format to Gemini's expected format.
    
    Args:
        history: List of messages with 'role' and 'content' keys.
        
    Returns:
        List of Content objects for Gemini API.
    """
    contents = []
    for msg in history:
        role = msg.get('role', 'user')
        content = msg.get('content', '')
        
        # Gemini expects 'user' or 'model' roles
        if role == 'assistant':
            role = 'model'
        
        contents.append(
            types.Content(
                role=role,
                parts=[types.Part.from_text(text=content)]
            )
        )
    
    return contents


def send_message(
    message: str,
    history: Optional[List[Dict[str, str]]] = None
) -> GeminiResponse:
    """
    Send a message to Gemini and get a response.
    
    Handles both text responses and function calls automatically.
    Gemini will decide whether to call a function or respond with text.
    
    Args:
        message: The user's message to send.
        history: Optional conversation history for context.
        
    Returns:
        GeminiResponse containing either text or function call details.
    """
    global _gemini_client
    
    if _gemini_client is None or not _gemini_client.is_configured():
        logger.error("Gemini API not configured")
        return GeminiResponse(text="API not configured. Please set GEMINI_API_KEY.", is_function_call=False)
    
    try:
        # Prepare conversation history
        contents = []
        if history:
            contents = _convert_history_to_gemini_format(history)
        
        # Add current user message
        contents.append(
            types.Content(
                role="user",
                parts=[types.Part.from_text(text=message)]
            )
        )
        
        # Generate content with function calling enabled and resource limits
        logger.info(f"Sending message to Gemini (length: {len(message)} chars)")
        response = _gemini_client.client.models.generate_content(
            model=_gemini_client.model_name,
            contents=contents,
            config=types.GenerateContentConfig(
                temperature=_gemini_client.temperature,
                max_output_tokens=_gemini_client.max_tokens,
                tools=_get_tools_config(),
            )
        )
        
        # Check if response contains a function call
        if response.candidates and len(response.candidates) > 0:
            candidate = response.candidates[0]
            
            if candidate.content and candidate.content.parts:
                for part in candidate.content.parts:
                    # Check if this part is a function call
                    if part.function_call:
                        func_call = part.function_call
                        
                        # Extract function name and arguments
                        func_name = func_call.name
                        func_args = {}
                        
                        if func_call.args:
                            func_args = dict(func_call.args)
                        
                        if func_name:
                            return GeminiResponse(
                                function_call=FunctionCallResult(
                                    name=func_name,
                                    args=func_args
                                ),
                                is_function_call=True
                            )
        
        # If no function call, return text response
        text_response = ""
        if response.text:
            text_response = response.text.strip()
        
        return GeminiResponse(text=text_response, is_function_call=False)
        
    except Exception as e:
        # Handle API errors gracefully
        logger.error(f"Gemini API error: {str(e)}")
        error_msg = f"Error communicating with Gemini: {str(e)}"
        return GeminiResponse(text=error_msg, is_function_call=False)


def create_function_response(function_name: str, result: str) -> List[Dict[str, Any]]:
    """
    Create a function response message to send back to Gemini.
    
    This allows Gemini to see the result of a function execution and
    potentially generate a follow-up response.
    
    Args:
        function_name: Name of the function that was called.
        result: String result of the function execution.
        
    Returns:
        Message list formatted for Gemini to process function results.
    """
    return [
        {
            "role": "function",
            "function_name": function_name,
            "result": result
        }
    ]


def get_model_info() -> Dict[str, Any]:
    """
    Get information about the configured model.
    
    Returns:
        Dictionary with model name and configuration status.
    """
    global _gemini_client
    if _gemini_client:
        return {
            "model_name": _gemini_client.model_name,
            "configured": _gemini_client.is_configured(),
            "max_tokens": _gemini_client.max_tokens,
            "temperature": _gemini_client.temperature
        }
    return {
        "model_name": Config.GEMINI_MODEL,
        "configured": False
    }
