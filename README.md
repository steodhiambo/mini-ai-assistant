# Mini Personal AI Assistant

A lightweight, production-quality AI assistant powered by Google Gemini that manages tasks, answers questions, and maintains conversational memory using official function calling.

## Features

- **Task Management**: Add, list, and complete tasks using natural language
- **General Knowledge Q&A**: Ask questions and get conversational answers
- **Smart Intent Routing**: Gemini automatically decides whether to call a function or respond with text
- **Conversational Memory**: Maintains context across the conversation (last 10 messages)
- **Local Persistence**: Tasks and history stored in JSON files
- **Clean CLI Interface**: Simple, intuitive command-line interaction

## Architecture

```
mini-ai-assistant/
│
├── main.py           # CLI entry point and main loop
├── gemini_client.py  # Gemini API wrapper with function calling
├── task_manager.py   # Task CRUD operations
├── memory.py         # Conversation history management
├── storage.json      # Persistent task storage
├── history.json      # Persistent conversation history
├── requirements.txt  # Python dependencies
└── README.md         # This file
```

### Module Responsibilities

| Module | Purpose |
|--------|---------|
| `main.py` | CLI loop, user input handling, response processing |
| `gemini_client.py` | API configuration, function declarations, message routing |
| `task_manager.py` | Task persistence, CRUD operations |
| `memory.py` | History loading/saving, message limit enforcement |

### Function Calling Flow

```
User Input → Gemini API → Function Call? → Execute → Response to Gemini → Final Response
                              ↓
                          Text Response → Display
```

## Setup Instructions

### Prerequisites

- Python 3.8 or higher
- Google Gemini API key

### Installation

1. **Clone or navigate to the project directory:**
   ```bash
   cd mini-ai-assistant
   ```

2. **Create a virtual environment (recommended):**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/macOS
   # or
   venv\Scripts\activate     # Windows
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set your Gemini API key:**

   **Option A - Using .env file (recommended):**
   ```bash
   cp .env.example .env
   # Edit .env and add your API key
   ```

   **Option B - Using environment variable:**
   ```bash
   export GEMINI_API_KEY='your-api-key-here'
   ```

5. **Run the assistant:**
   ```bash
   python main.py
   ```

## Example Usage

### Starting the Assistant

```bash
$ export GEMINI_API_KEY='your-api-key-here'
$ python main.py

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

Using model: gemini-1.5-flash
--------------------------------------------------
```

### Task Management

```
You: Add a task to buy groceries

Assistant: I've added "buy groceries" to your task list with ID 1. Is there anything else you'd like me to help you with?

You: Add another task - call the dentist tomorrow

Assistant: I've added "call the dentist tomorrow" to your task list with ID 2.

You: Show me my tasks

Assistant: [1] ○ buy groceries
[2] ○ call the dentist tomorrow

You: Complete task 1

Assistant: Task 1 "buy groceries" has been marked as completed.

You: tasks

Assistant: [1] ✓ buy groceries
[2] ○ call the dentist tomorrow
```

### General Questions

```
You: What's the capital of France?

Assistant: The capital of France is Paris. It's the country's largest city and a major European hub for art, fashion, culture, and business.

You: Can you explain quantum computing in simple terms?

Assistant: Quantum computing is a type of computing that uses quantum mechanics principles...
```

### CLI Commands

```
You: tasks      # Show all tasks
You: clear      # Clear conversation history
You: quit       # Exit the assistant
```

## Assumptions

1. **API Key**: The user has a valid Google Gemini API key and sets it via the `GEMINI_API_KEY` environment variable.

2. **Internet Connection**: The assistant requires an active internet connection to communicate with the Gemini API.

3. **File Permissions**: The application has read/write permissions for `storage.json` and `history.json` in the project directory.

4. **Python Version**: Python 3.8+ is available with pip for package installation.

5. **Token Limits**: History is limited to 10 messages to stay within token limits and reduce API costs.

## Future Improvements

- [ ] **Task Editing**: Add ability to modify existing tasks
- [ ] **Task Deletion**: Add ability to delete tasks (beyond completion)
- [ ] **Due Dates**: Support for task deadlines and reminders
- [ ] **Task Categories**: Organize tasks by project or category
- [ ] **Search**: Search tasks by keyword
- [ ] **Export/Import**: Backup and restore tasks
- [ ] **Multiple Users**: Support for multiple user profiles
- [ ] **Voice Input**: Speech-to-text integration
- [ ] **GUI Option**: Optional graphical interface
- [ ] **More Functions**: Calendar integration, email, weather, etc.
- [ ] **Streaming Responses**: Real-time response streaming
- [ ] **Custom Prompts**: User-configurable system prompts

## Troubleshooting

### API Key Error
```
Error: GEMINI_API_KEY environment variable not set.
```
**Solution**: Set your API key: `export GEMINI_API_KEY='your-key'`

### Import Error
```
ModuleNotFoundError: No module named 'google.generativeai'
```
**Solution**: Install dependencies: `pip install -r requirements.txt`

### Rate Limiting
If you encounter rate limiting, the Gemini API may have usage quotas. Check your API dashboard.

## License

This project is provided as-is for educational and personal use.

## Getting a Gemini API Key

1. Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy the key and set it as `GEMINI_API_KEY` environment variable
