# Mini Personal AI Assistant

A lightweight, production-quality AI assistant powered  powered by Google Gemini that manages tasks, answers questions, and maintains conversational memory using official function calling.

## Features

- **Task Management**: Add, list, and complete tasks using natural language
- **General Knowledge Q&A**: Ask questions and get conversational answers
- **Smart Intent Routing**: Gemini automatically decides whether to call a function or respond with text
- **Conversational Memory**: Maintains context across the conversation
- **SQLite Database**: Robust local storage for tasks and history
- **Modern Web UI**: Beautiful, responsive interface with dark theme and blue accents

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Set your API key
echo "GEMINI_API_KEY=your-key" > .env

# Run the web application
python main.py

# Open browser to http://localhost:5000
```

## Architecture

```
mini-ai-assistant/
│
├── main.py              # Web application entry point
├── web_ui.py            # Flask web server and API endpoints
├── gemini_client.py     # Gemini API wrapper with function calling
├── task_manager.py      # Task CRUD operations
├── memory.py            # Conversation history management
├── database.py          # SQLite database operations
├── assistant.db         # SQLite database file (auto-created)
├── requirements.txt     # Python dependencies
├── templates/           # HTML templates for web UI
│   ├── index.html       # Chat interface
│   ├── tasks.html       # Task management dashboard
│   └── stats.html       # Statistics page
└── README.md            # This file
```

### Module Responsibilities

| Module | Purpose |
|--------|---------|
| `main.py` | Application entry point, initializes database and web server |
| `web_ui.py` | Flask server, REST API, web routes |
| `gemini_client.py` | API configuration, function declarations, message routing |
| `task_manager.py` | Task persistence, CRUD operations |
| `memory.py` | History loading/saving, message limit enforcement |
| `database.py` | SQLite connection, migrations, queries |

### System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Web UI (Flask)                          │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  │
│  │   Chat      │  │   Tasks     │  │      Stats          │  │
│  │  Interface  │  │  Dashboard  │  │     Dashboard       │  │
│  └─────────────┘  └─────────────┘  └─────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                            │
            ┌───────────────▼────────────────┐
            │     REST API Endpoints         │
            │  /api/chat, /api/tasks, etc.   │
            └───────────────┬────────────────┘
                            │
            ┌───────────────▼──────────────┐
            │    Gemini Client Layer       │
            │   (gemini_client.py)         │
            │  - Function Calling          │
            │  - Intent Detection          │
            └───────────────┬──────────────┘
                            │
            ┌───────────────▼──────────────┐
            │     Business Logic           │
            │  - task_manager.py           │
            │  - memory.py                 │
            └───────────────┬──────────────┘
                            │
            ┌───────────────▼──────────────┐
            │    SQLite Database           │
            │  - assistant.db              │
            │  - tasks table               │
            │  - conversation_history      │
            └──────────────────────────────┘
```

## Setup Instructions

### Prerequisites

- Python 3.8 or higher
- Google Gemini API key

### Installation

1. **Clone or navigate to the project directory:**
   ```bash
   git clone https://github.com/steodhiambo/mini-ai-assistant.git
   cd mini-ai-assistant
   ```

2. **Create a virtual environment (recommended):**
   ```bash
   python3 -m venv venv
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

5. **Run the application:**
   ```bash
   python main.py
   ```

6. **Open your browser:**
   - Local: http://localhost:5000
   - Network: http://YOUR_IP:5000

## Usage

### Web Interface

The application provides three main pages:

#### 1. Chat (Home)
- Conversational interface with the AI
- Type naturally: "Add buy groceries to my tasks"
- Ask questions: "What is machine learning?"
- Suggestion chips for quick actions

#### 2. Tasks Dashboard
- View all tasks with status indicators
- Add new tasks with the + button
- Click checkbox to complete tasks
- Delete tasks individually or clear all completed

#### 3. Statistics
- View task completion metrics (total, pending, completed)
- Track conversation history count
- Visual progress bar showing completion rate
- Clear chat history option

### Example Interactions

| User Input | AI Response |
|------------|-------------|
| "Add buy groceries to my tasks" | Adds task and confirms |
| "Show me my tasks" | Lists all pending tasks |
| "Complete task 1" | Marks task as done |
| "What is Python?" | Answers the question |
| "Explain AI" | Provides explanation |

### API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Chat interface |
| `/tasks` | GET | Task dashboard |
| `/stats` | GET | Statistics page |
| `/api/chat` | POST | Send chat message |
| `/api/tasks` | GET | Get all tasks |
| `/api/tasks` | POST | Add new task |
| `/api/tasks/<id>/complete` | POST | Complete task |
| `/api/tasks/<id>` | DELETE | Delete task |
| `/api/history` | GET | Get chat history |
| `/api/history` | DELETE | Clear history |
| `/api/stats` | GET | Get statistics |

## Assumptions

1. **API Key**: The user has a valid Google Gemini API key.

2. **Internet Connection**: Required for Gemini API communication.

3. **File Permissions**: Write access for `assistant.db` in the project directory.

4. **Python Version**: Python 3.8+ with pip.

5. **Single User**: Designed for personal/single-user usage.

## Database Schema

### tasks table
| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key, auto-increment |
| name | TEXT | Task description |
| completed | INTEGER | 0 = pending, 1 = completed |
| created_at | TIMESTAMP | Creation timestamp |
| completed_at | TIMESTAMP | Completion timestamp |

### conversation_history table
| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key, auto-increment |
| role | TEXT | 'user' or 'model' |
| content | TEXT | Message content |
| created_at | TIMESTAMP | Message timestamp |

## Future Improvements

- [ ] Task due dates and reminders
- [ ] Task categories/tags
- [ ] Search functionality
- [ ] Task priorities
- [ ] Export/import data
- [ ] Multiple user profiles
- [ ] Voice input support
- [ ] Calendar integration
- [ ] Email notifications
- [ ] Dark/light theme toggle
- [ ] Custom AI prompts

## Troubleshooting

### API Key Error
```
Warning: GEMINI_API_KEY not set.
```
**Solution**: Set your API key in `.env` or export it.

### Port Already in Use
```
Address already in use
```
**Solution**: Edit `web_ui.py` and change the default port from 5000 to another value.

### Database Errors
```
no such table: tasks
```
**Solution**: Delete `assistant.db` and restart - tables will be recreated.

### Rate Limiting
If you encounter rate limiting, wait a minute or check your API quota at [Google AI Studio](https://makersuite.google.com/).

## License

This project is provided as-is for educational and personal use.

## Getting a Gemini API Key

1. Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy the key to your `.env` file

## Tech Stack

- **Backend**: Python 3, Flask
- **AI**: Google Gemini API (google-genai SDK)
- **Database**: SQLite3
- **Frontend**: HTML5, CSS3, Vanilla JavaScript
- **Styling**: Custom CSS with dark theme and blue accents
