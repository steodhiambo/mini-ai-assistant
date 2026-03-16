import os
import sys
from dotenv import load_dotenv

# Import local modules
from database import init_db
from gemini_client import configure_api, get_model_info
from web_ui import run_server
from config import Config
from logger import logger


def main():
    """Entry point for the web application."""
    # Load environment variables from .env
    load_dotenv()
    
    logger.info("Starting Mini AI Assistant")
    logger.info(f"Environment: {Config.get_environment()}")
    
    # Initialize database
    try:
        init_db()
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        sys.exit(1)
    
    # Configure API
    if not configure_api():
        logger.warning("GEMINI_API_KEY not set.")
        logger.warning("AI features will not work until you set your API key.")
        logger.warning("Create a .env file with: GEMINI_API_KEY=your-key")
    else:
        # Show model info
        model_info = get_model_info()
        if model_info.get('configured'):
            logger.info(f"AI Model: {model_info['model_name']}")
            logger.info(f"Max Tokens: {model_info.get('max_tokens', 'N/A')}")
            logger.info(f"Temperature: {model_info.get('temperature', 'N/A')}")
    
    # Start web server
    try:
        run_server()
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Server error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
