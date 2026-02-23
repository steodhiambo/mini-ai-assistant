#!/usr/bin/env python3
"""
Mini Personal AI Assistant - Web Application

A lightweight AI assistant powered by Google Gemini that:
- Manages tasks using natural language
- Answers general knowledge questions
- Automatically routes user intent using Gemini function calling
- Maintains conversational memory
- Provides a modern web interface

Usage:
    python main.py

Environment:
    Set GEMINI_API_KEY environment variable or create a .env file:
    GEMINI_API_KEY=your-api-key-here
"""

import os
import sys
from dotenv import load_dotenv

# Import local modules
from database import init_db
from gemini_client import configure_api, get_model_info
from web_ui import run_server


def main():
    """Entry point for the web application."""
    # Load environment variables from .env
    load_dotenv()
    
    # Initialize database
    init_db()
    
    # Configure API
    if not configure_api():
        print("⚠️  Warning: GEMINI_API_KEY not set.")
        print("   AI features will not work until you set your API key.")
        print("   Create a .env file with: GEMINI_API_KEY=your-key")
        print()
    
    # Show model info
    model_info = get_model_info()
    if model_info.get('configured'):
        print(f"✓ AI Model: {model_info['model_name']}")
        print()
    
    # Start web server
    run_server(host='0.0.0.0', port=5000, debug=False)


if __name__ == "__main__":
    main()
