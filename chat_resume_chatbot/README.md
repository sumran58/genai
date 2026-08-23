# LangGraph Resume Chat - Hybrid Version

A conversational AI chatbot that combines **in-memory efficiency** with **multi-thread conversation support**. This version allows you to maintain multiple independent conversations within a single session using Groq's fast LLM API.

## ✨ Features

- 💬 **Interactive Chat Interface** - Clean Streamlit UI with real-time messaging
- 🔄 **Multiple Conversations** - Manage multiple independent threads simultaneously
- 📜 **Resume Conversations** - Load and continue previous conversations from sidebar
- ⚡ **Streaming Responses** - Real-time message streaming for better UX
- 🪶 **Lightweight In-Memory** - No database overhead, all state in RAM
- 🆔 **UUID-based Sessions** - Unique identifiers for each conversation thread
- 🧠 **LangGraph State Management** - Graph-based workflow with checkpointing
- 📊 **Multi-Thread Checkpointing** - InMemory checkpoints for each thread

## 🎯 Perfect For

✅ Development and prototyping  
✅ Demo applications  
✅ Single-session multi-conversation workflows  
✅ Learning advanced Streamlit patterns  
✅ Testing conversation management  
✅ Temporary chatbot sessions  
✅ Low-overhead production deployments  

## ⚠️ When NOT to Use

❌ Need permanent conversation storage  
❌ Users expecting data to persist across browser refreshes  
❌ Multi-day/multi-week conversations  
❌ Conversation analytics/auditing  
❌ Very high memory conversations  

## 🏗️ Architecture

### Components

**Frontend (resume_chat_frontend.py)**
- Streamlit-based multi-conversation interface
- Sidebar with conversation management
- UUID-based thread ID generation
- Session state for current conversation
- Real-time streaming with `st.write_stream()`
- "New Chat" button for quick conversation creation
- Conversation history loading and resumption

**Backend (langgraph_backend.py)**
- LangGraph state graph orchestration
- ChatGroq LLM integration
- InMemorySaver checkpointing for multi-thread state
- Message state management with `add_messages`
- No database dependency

### State Management

```
┌──────────────────────────────────┐
│  Streamlit Session State         │
│                                  │
│  - message_history (current)     │
│  - thread_id (active)            │
│  - chat_thread (all threads)     │
└────────────┬─────────────────────┘
             │
             ▼
┌──────────────────────────────────┐
│  LangGraph Backend               │
│                                  │
│  - ChatState (typed dict)        │
│  - InMemorySaver checkpoints     │
│  - Multiple thread support       │
│  - add_messages reducer          │
└────────────┬─────────────────────┘
             │
             ▼
┌──────────────────────────────────┐
│  RAM (Checkpoints)               │
│                                  │
│  thread-1 → [msg1, msg2, ...]   │
│  thread-2 → [msg3, msg4, ...]   │
│  thread-N → [...]               │
└──────────────────────────────────┘
```

## 📋 Prerequisites

- Python 3.9+
- Groq API key
- ~256MB RAM (depends on conversation size)

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
   pip install -r requirements_resume.txt
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example_resume .env
   ```
   
   Edit `.env` and add your Groq API key:
   ```env
   GROQ_API_KEY=your_groq_api_key_here
   ```

## ⚡ Quick Start

1. **Start the application**
   ```bash
   streamlit run resume_chat_frontend.py
   ```

2. **Open your browser**
   - Navigate to `http://localhost:8501`

3. **Start chatting**
   - Type a message and press Enter
   - Use "New Chat" to start a new conversation thread
   - Click previous conversations in sidebar to resume them
   - All conversations exist only for this session

## ⚙️ Configuration

### Environment Variables
- `GROQ_API_KEY` - Your Groq API key (required)

### LLM Model
Update the model in `langgraph_backend.py`:
```python
llm = ChatGroq(model="openai/gpt-oss-120b")
```

### Conversation Limit (Optional)
Add to frontend to limit stored threads:
```python
MAX_CONVERSATIONS = 10

if len(st.session_state['chat_thread']) > MAX_CONVERSATIONS:
    st.session_state['chat_thread'].pop(0)
```

## 📁 File Descriptions

### `resume_chat_frontend.py`
**Purpose**: Multi-conversation chat interface with session-based persistence

**Key Functions**:
- `generate_thread_id()` - Creates unique UUID for conversations
- `add_thread()` - Adds thread to conversation list
- `load_conversations()` - Retrieves conversation from in-memory checkpoint
- `reset_chat()` - Creates new conversation thread
- Sidebar management with conversation switching
- Real-time streaming with `st.write_stream()`

**Key Features**:
- Session state initialization with 3 variables
- Sidebar "New Chat" button
- Conversation history in reverse chronological order
- Click any conversation to load/resume
- Stream mode for progressive message display

### `langgraph_backend.py`
**Purpose**: Backend conversation engine with in-memory checkpointing

**Key Components**:
- `ChatState` - TypedDict with messages list
- `chat_node()` - Invokes ChatGroq LLM
- `InMemorySaver` - In-memory checkpoint storage
- State graph: START → chat_node → END
- Compiled graph with checkpoint support

## 🔄 Message Flow

```
User Input (Streamlit)
        ↓
HumanMessage created with thread_id config
        ↓
chatbot.stream() invoked in streaming mode
        ↓
ChatGroq LLM processes message
        ↓
Response chunks streamed via st.write_stream()
        ↓
Message saved to session_state
        ↓
InMemorySaver checkpoints to RAM
        ↓
Next message loaded from same thread checkpoint
```

## 💾 Session State Variables

| Variable | Type | Purpose | Persistence |
|----------|------|---------|-------------|
| `message_history` | List[Dict] | Current thread messages | Session only |
| `thread_id` | String (UUID) | Active conversation ID | Session only |
| `chat_thread` | List[String] | All conversation IDs | Session only |

**Persistence Level**: All data kept in RAM during session, cleared on browser refresh or app restart.

## 🔀 Conversation Switching

### How It Works
1. All conversations stored in RAM via InMemorySaver
2. Click conversation in sidebar to load it
3. `load_conversations()` retrieves from checkpoint
4. Messages displayed and ready for continuation
5. New messages added to current thread's checkpoint

### Example Flow
```
Thread-1: "Hello" → "Hi there"
Thread-2: "What's AI?" → "Artificial Intelligence..."

User clicks Thread-1 in sidebar:
- thread_id switches to Thread-1
- message_history loads Thread-1's messages
- New input continues Thread-1's conversation
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

See `requirements_resume.txt` for pinned versions.

## 🆚 Comparison with Other Versions

| Feature | In-Memory | Resume Chat | Database |
|---------|-----------|-------------|----------|
| Single Conversation | ✅ | ✅ | ✅ |
| Multiple Conversations | ❌ | ✅ | ✅ |
| Conversation Resumption | ❌ | ✅ | ✅ |
| Persistent Storage | ❌ | ❌ | ✅ |
| Session-Only Data | ✅ | ✅ | ❌ |
| In-Memory Checkpoints | ✅ | ✅ | ❌ |
| Streaming Support | ❌ | ✅ | ✅ |
| Sidebar Navigation | ❌ | ✅ | ✅ |
| Database Overhead | ❌ | ❌ | ✅ |
| Memory Usage | Low | Medium | Medium-High |

## 🎬 Usage Scenarios

### Scenario 1: Quick Testing
```
1. Start app
2. Have conversation in Thread-1
3. Click "New Chat" for Thread-2
4. Test different prompts in Thread-2
5. Switch between threads to compare responses
6. Refresh page → all data cleared
```

### Scenario 2: Demo Presentation
```
1. Pre-create conversations (setup before demo)
2. Show Thread-1 with example
3. Switch to Thread-2 for alternate approach
4. "New Chat" for live demo questions
5. All context available in sidebar
```

### Scenario 3: Development Workflow
```
1. Debug Thread-1 conversation
2. Create Thread-2 to test fixes
3. Compare outputs in sidebar
4. Iterate until satisfied
5. Data lost on refresh (expected)
```

## ⚡ Performance Characteristics

| Metric | Value | Notes |
|--------|-------|-------|
| Startup Time | ~2 seconds | Fast, no DB init |
| Response Time | ~2-5 seconds | LLM dependent |
| Thread Creation | Instant | UUID generation |
| Thread Switching | <100ms | In-memory lookup |
| Memory per Thread | ~10-50KB | Message dependent |
| Max Threads (RAM) | ~100-1000 | System dependent |

## 🔧 Advanced Usage

### Add Thread Limit
```python
MAX_THREADS = 20

def add_thread(thread_id):
    if thread_id not in st.session_state['chat_thread']:
        st.session_state['chat_thread'].append(thread_id)
        if len(st.session_state['chat_thread']) > MAX_THREADS:
            oldest = st.session_state['chat_thread'].pop(0)
            # Note: checkpoint for oldest still in RAM
```

### Add System Message
```python
from langchain_core.messages import SystemMessage

def chat_node(state: ChatState):
    system_msg = SystemMessage(
        content="You are a helpful assistant..."
    )
    messages = [system_msg] + state['messages']
    response = llm.invoke(messages)
    return {"messages": [response]}
```

### Export Conversation
```python
import json

def export_thread(thread_id):
    messages = load_conversations(thread_id)
    exported = [{
        'role': 'user' if isinstance(m, HumanMessage) else 'assistant',
        'content': m.content
    } for m in messages]
    return json.dumps(exported, indent=2)
```

## 🐛 Troubleshooting

### "Thread not found in checkpoint"
**Cause**: Switching threads before first message saved
**Solution**: Send at least one message before switching threads

### Memory usage growing
**Cause**: Many large conversations in RAM
**Solution**: 
- Restart app to clear memory
- Limit number of concurrent threads
- Export and archive large conversations

### Conversations disappear on refresh
**Cause**: In-memory storage cleared on page refresh
**Solution**: This is expected behavior. For persistence, use database version.

### GROQ_API_KEY not found
- Verify `.env` file exists
- Check API key format (no quotes)
- Restart app after changing .env

## 🚀 Production Deployment

### Small Scale (Demo/Testing)
✅ Works great with this version
- Lightweight setup
- No database needed
- Easy to deploy

### Medium Scale (10-100 users)
⚠️ Consider factors:
- RAM usage per user (~100-500MB)
- Session timeout handling
- User authentication
- Error handling

### Large Scale (100+ users)
❌ Not recommended
- Switch to database version
- Use PostgreSQL for checkpoints
- Implement proper session management

## 🔄 Upgrading to Database Version

To add persistence:

1. Keep this frontend, switch backend:
   ```python
   # Change from langgraph_backend.py to langgraph_database_backend.py
   from langgraph_database_backend import chatbot, retrieve_all_threads
   ```

2. Add database initialization on startup:
   ```python
   if 'chat_thread' not in st.session_state:
       st.session_state['chat_thread'] = retrieve_all_threads()
   ```

3. Install database dependencies:
   ```bash
   pip install -r requirements_database.txt
   ```

## 📊 Monitoring

### Check Memory Usage
```python
import psutil
import os

process = psutil.Process(os.getpid())
memory_info = process.memory_info()
print(f"Memory: {memory_info.rss / 1024 / 1024:.2f} MB")
```

### Log Thread Activity
```python
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def add_thread(thread_id):
    if thread_id not in st.session_state['chat_thread']:
        logger.info(f"New thread created: {thread_id}")
        st.session_state['chat_thread'].append(thread_id)
```

## 🎯 Future Enhancements

- [ ] Thread naming/descriptions
- [ ] Conversation search
- [ ] Export conversations to file
- [ ] Conversation sharing
- [ ] Custom system prompts per thread
- [ ] Conversation analytics
- [ ] Session persistence (localStorage)
- [ ] Thread archival
- [ ] Conversation merging
- [ ] Message editing

## 📄 License

[Add your license here - e.g., MIT, Apache 2.0, etc.]

## 🤝 Contributing

Contributions are welcome! Please submit a Pull Request.

## 📞 Support

For issues:
- Check existing GitHub issues
- Create a new issue with:
  - Error message and stack trace
  - Steps to reproduce
  - Python version
  - Which version you're using (Resume Chat, Database, etc.)

---

**Built with** 🚀
- [Streamlit](https://streamlit.io/)
- [LangGraph](https://langchain-ai.github.io/langgraph/)
- [LangChain](https://www.langchain.com/)
- [Groq](https://console.groq.com/)

## Quick Links

- 📖 [Full Documentation](README_RESUME.md)
- 🆚 [Compare Versions](COMPARISON.md)
- 📁 [Project Structure](PROJECT_STRUCTURE.md)
- 🚀 [In-Memory Version](README.md)
- 🗄️ [Database Version](README_DATABASE.md)
