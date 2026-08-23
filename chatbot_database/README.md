# LangGraph Chatbot with SQLite Database Backend

A production-ready conversational AI chatbot built with **LangGraph**, **Streamlit**, and **SQLite**. This application features persistent conversation storage, multi-thread support, and real-time streaming responses using Groq's LLM API.

## ✨ Features

- 💬 **Interactive Chat Interface** - Clean, user-friendly chat UI with Streamlit
- 🗄️ **SQLite Persistence** - Conversations stored in SQLite database for durability
- 🔄 **Multi-Thread Support** - Manage multiple independent conversations simultaneously
- ⚡ **Streaming Responses** - Real-time message streaming for faster perceived performance
- 📜 **Conversation History** - Load and resume previous conversations from sidebar
- 🆔 **UUID-based Sessions** - Unique identifiers for each conversation thread
- 📊 **LangGraph Backend** - Advanced state management with graph-based workflow
- 💾 **Checkpoint System** - SQLite checkpointing for state persistence

## 🏗️ Architecture

### Components

**Frontend (streamlit_database_frontend.py)**
- Streamlit-based chat interface with sidebar navigation
- Conversation management (new chat, load previous conversations)
- Session state management for UI persistence
- Real-time message streaming with `st.write_stream()`
- UUID-based thread ID generation and management

**Backend (langgraph_database_backend.py)**
- LangGraph state graph for workflow orchestration
- SQLite-based checkpoint system for persistent state storage
- ChatGroq integration for LLM inference
- Message state management with `TypedDict` and `add_messages`
- Thread retrieval for conversation history

**Database**
- SQLite database (`chatbot_db`) for conversation storage
- Automatic checkpoint creation for each interaction
- Thread-ID based conversation isolation

## 📋 Prerequisites

- Python 3.9+
- Groq API key
- SQLite3 (included with Python)

## 🚀 Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd <project-directory>
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   ```
   
   Edit `.env` and add your Groq API key:
   ```env
   GROQ_API_KEY=your_groq_api_key_here
   ```

## ⚡ Quick Start

1. **Start the application**
   ```bash
   streamlit run streamlit_database_frontend.py
   ```

2. **Open your browser**
   - Navigate to `http://localhost:8501`

3. **Start chatting**
   - Type a message and press Enter
   - Watch responses stream in real-time
   - Click "New Chat" to start a fresh conversation
   - Access previous conversations from the sidebar

## ⚙️ Configuration

### Environment Variables
- `GROQ_API_KEY` - Your Groq API key (required)

### Database Configuration
The SQLite database is created automatically as `chatbot_db` in the project root:
```python
conn = sqlite3.connect(
    database="chatbot_db",
    check_same_thread=False
)
```

### LLM Model
Update the model in `langgraph_database_backend.py`:
```python
llm = ChatGroq(model="openai/gpt-oss-120b")
```

## 📁 File Descriptions

### `streamlit_database_frontend.py`
**Purpose**: Multi-conversation chat interface

**Key Functions**:
- `generate_thread_id()` - Creates unique UUID for new conversations
- `add_thread()` - Adds thread ID to conversation list
- `load_conversations()` - Retrieves conversation history from database
- `reset_chat()` - Initializes new conversation thread
- Sidebar management for conversation switching
- Real-time message streaming

**Key Features**:
- Sidebar with "New Chat" button
- List of all previous conversations
- Click to load any previous conversation
- Stream mode for progressive message display
- Session state preservation

### `langgraph_database_backend.py`
**Purpose**: Backend conversation engine with persistence

**Key Components**:
- `ChatState` - TypedDict defining conversation schema
- `chat_node()` - Processes messages through ChatGroq LLM
- `SqliteSaver` - SQLite-based checkpoint management
- `retrieve_all_threads()` - Gets all conversation thread IDs from database

**Database Schema**:
LangGraph's SqliteSaver automatically creates tables for:
- Checkpoints (conversation states)
- Checkpoint write values (message content)
- Checkpoint tuples (state snapshots)

## 🔄 Message Flow

```
User Input (Streamlit)
        ↓
New Thread ID created (if new chat)
        ↓
HumanMessage created with thread config
        ↓
chatbot.stream() invoked in streaming mode
        ↓
ChatGroq LLM generates response
        ↓
Chunks streamed to frontend with st.write_stream()
        ↓
Message saved to session_state & displayed
        ↓
LangGraph checkpoint saves to SQLite database
```

## 💾 Session State Management

The application uses three key session state variables:

| Variable | Purpose | Type |
|----------|---------|------|
| `message_history` | Current chat messages | List of dicts |
| `thread_id` | Current conversation ID | String (UUID) |
| `chat_thread` | All conversation IDs | List of strings |

These are loaded from the database on startup via `retrieve_all_threads()`.

## ⚡ Streaming vs. Invoke

This version uses **streaming mode** for better UX:

```python
# Streaming (real-time chunks)
chatbot.stream(
    {'messages': [HumanMessage(...)]},
    config=config,
    stream_mode='messages'
)

# vs. Invoke (wait for complete response)
chatbot.invoke(
    {'messages': [HumanMessage(...)]},
    config=config
)
```

Benefits of streaming:
- Faster perceived response time
- Better for longer responses
- More interactive experience
- Can be interrupted by user

## 🗄️ Database Operations

### View Conversation History
```python
from langgraph_database_backend import retrieve_all_threads

threads = retrieve_all_threads()
# Returns: ['uuid-1', 'uuid-2', ...]
```

### Access Specific Conversation
```python
config = {'configurable': {'thread_id': 'target-uuid'}}
state = chatbot.get_state(config)
messages = state.values.get('messages', [])
```

### Delete Conversations (if needed)
```bash
rm chatbot_db  # Delete entire database
# (will be recreated on next run)
```

## 📦 Dependencies

```
streamlit>=1.28.0
langgraph>=0.0.63
langchain>=0.1.9
langchain-core>=0.1.33
langchain-groq>=0.0.1
python-dotenv>=1.0.0
```

See `requirements.txt` for pinned versions.

## 🚀 Deployment Considerations

### Production Recommendations

1. **Database Backups**
   - Regularly backup `chatbot_db` file
   - Consider implementing periodic snapshots

2. **Scalability**
   - For high-traffic: Consider PostgreSQL + LangGraph's PostgresSaver
   - Implement connection pooling

3. **Security**
   - Use environment variables for API keys
   - Implement user authentication
   - Add rate limiting on API calls
   - Encrypt sensitive data in database

4. **Performance**
   - Monitor database file size
   - Archive old conversations periodically
   - Consider indexing thread_id in checkpoints

5. **Monitoring**
   - Log API errors and failures
   - Track conversation metrics
   - Monitor response latency

## 🔧 Advanced Usage

### Custom System Prompt
Modify the `chat_node` function to add a system prompt:

```python
def chat_node(state: ChatState):
    messages = state["messages"]
    
    # Add system message at the beginning
    system_messages = [
        SystemMessage(content="You are a helpful assistant...")
    ]
    
    response = llm.invoke(system_messages + messages)
    return {"messages": [response]}
```

### Multi-User Support
Add user authentication to session state:

```python
if 'user_id' not in st.session_state:
    st.session_state['user_id'] = st.sidebar.text_input("User ID")

thread_id = f"{user_id}_{uuid.uuid4()}"
```

### Export Conversations
Add conversation export functionality:

```python
def export_conversation(thread_id, format='json'):
    messages = load_conversations(thread_id)
    # Export logic here
```

## 🐛 Troubleshooting

### Database Lock Error
**Problem**: "database is locked"
```
Solution: 
- Ensure check_same_thread=False is set
- Close other connections to the database
- Restart the application
```

### Streaming Not Working
**Problem**: Messages appear all at once instead of streaming
```
Solution:
- Verify stream_mode='messages' is set
- Check Streamlit version (>=1.28.0)
- Ensure ChatGroq supports streaming
```

### Missing Conversations
**Problem**: Previous conversations not showing in sidebar
```
Solution:
- Check chatbot_db file exists
- Verify retrieve_all_threads() is called on startup
- Ensure thread_id is in configurable checkpoint config
```

### GROQ_API_KEY not found
- Verify `.env` file in root directory
- Check API key format (should not have quotes)
- Restart application after changing .env

## 📊 Monitoring

### Check Database Stats
```python
import sqlite3

conn = sqlite3.connect('chatbot_db')
cursor = conn.cursor()

# Get total conversations
cursor.execute("SELECT COUNT(DISTINCT thread_id) FROM checkpoint")
total_threads = cursor.fetchone()[0]

# Get database size
import os
db_size = os.path.getsize('chatbot_db') / (1024 * 1024)  # in MB
```

## 🔄 Migration from In-Memory Version

If upgrading from the in-memory version:

1. The new version is backward compatible
2. Database is created automatically on first run
3. No data migration needed (in-memory data not persisted)
4. All new conversations stored in SQLite

## 🎯 Future Enhancements

- [ ] PostgreSQL support for production deployments
- [ ] User authentication and multi-user support
- [ ] Conversation search functionality
- [ ] Export conversations (JSON, PDF, CSV)
- [ ] Custom system prompts per conversation
- [ ] Message editing and deletion
- [ ] Conversation sharing
- [ ] Analytics dashboard
- [ ] Token usage tracking
- [ ] Rate limiting per user
- [ ] Conversation tags/categories
- [ ] Full-text search across conversations

## 📄 License

[Add your license here - e.g., MIT, Apache 2.0, etc.]

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📞 Support

For issues and questions:
- Check existing GitHub issues
- Create a new issue with detailed description
- Include:
  - Error messages and stack traces
  - Steps to reproduce
  - Python and package versions
  - Database size (if applicable)

---

**Built with** 🚀
- [Streamlit](https://streamlit.io/)
- [LangGraph](https://langchain-ai.github.io/langgraph/)
- [LangChain](https://www.langchain.com/)
- [Groq](https://console.groq.com/)
- [SQLite](https://www.sqlite.org/)
