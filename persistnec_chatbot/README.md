# LangGraph Chatbot with Streamlit Frontend

A conversational AI chatbot built with **LangGraph** backend and **Streamlit** frontend. This application uses Groq's LLM API for fast, efficient inference with persistent conversation memory.

## Features

- 💬 **Interactive Chat Interface** - Clean, user-friendly chat UI built with Streamlit
- 🧠 **Stateful Conversations** - Maintains conversation history across sessions using Streamlit's `session_state`
- 📊 **LangGraph Backend** - Structured workflow management with graph-based state handling
- 💾 **Checkpoint System** - In-memory checkpointing for multi-turn conversation tracking
- 🔄 **Thread-based Sessions** - Support for managing multiple conversation threads

## Architecture

### Components

**Frontend (streamlit_frontend.py)**
- Streamlit-based chat interface
- Session state management for message history
- Real-time message display with role-based styling (user/assistant icons)
- User input handling via `st.chat_input()`

**Backend (langgraph_backend.py)**
- LangGraph state graph for workflow orchestration
- ChatGroq integration for LLM inference
- Message state management using `TypedDict` and `Annotated`
- In-memory checkpointer for conversation persistence

## Prerequisites

- Python 3.9+
- Groq API key

## Installation

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

## Quick Start

1. **Start the application**
   ```bash
   streamlit run streamlit_frontend.py
   ```

2. **Open your browser**
   - Navigate to `http://localhost:8501`

3. **Start chatting**
   - Type your message in the input field and press Enter
   - The chatbot will respond using the Groq LLM

## Configuration

### Environment Variables
- `GROQ_API_KEY` - Your Groq API key (required)

### Thread Configuration
The default thread ID is set to `'thread-1'` in the frontend. Modify the `config` dictionary in `streamlit_frontend.py` to use different thread IDs for separate conversation threads:

```python
config = {'configurable': {'thread_id': 'thread-1'}}
```

### LLM Model
Update the model in `langgraph_backend.py`:
```python
llm = ChatGroq(model="openai/gpt-oss-120b")
```

## File Descriptions

### `streamlit_frontend.py`
- **Purpose**: User-facing chat interface
- **Key Features**:
  - Initializes message history in `st.session_state` on first load
  - Renders previous messages from session state
  - Accepts user input and sends to backend
  - Displays bot responses with proper formatting

### `langgraph_backend.py`
- **Purpose**: Backend conversation engine
- **Key Components**:
  - `ChatState`: TypedDict defining conversation state schema
  - `chat_node`: Function that processes messages through the LLM
  - State graph setup with START → chat_node → END flow
  - Compiled graph with checkpoint support

## Message Flow

```
User Input (Streamlit)
        ↓
HumanMessage created
        ↓
chatbot.invoke() called with config (thread_id)
        ↓
LangGraph routes to chat_node
        ↓
ChatGroq LLM generates response
        ↓
Response returned to frontend
        ↓
Added to session_state & displayed
```

## Session State Management

The application uses Streamlit's `session_state` to persist the message history. This ensures:
- Messages are not lost on page refresh (unless browser cache is cleared)
- Conversation context is maintained across interactions
- Multiple sessions can run independently

**Note**: Session state is stored client-side. For production with user authentication, consider implementing server-side session storage.

## Dependencies

```
streamlit
langgraph
langchain
langchain-core
langchain-groq
python-dotenv
```

See `requirements.txt` for pinned versions.

## Future Enhancements

- [ ] Database integration for persistent conversation storage
- [ ] Multi-user support with authentication
- [ ] Conversation history export (JSON, PDF)
- [ ] Custom system prompts
- [ ] Token usage tracking and cost calculation
- [ ] Conversation analytics
- [ ] Support for multiple LLM providers
- [ ] Streaming responses for faster perceived performance

## Troubleshooting

### "GROQ_API_KEY not found"
- Ensure `.env` file exists in the root directory
- Verify the API key is correctly set
- Check that `python-dotenv` is installed

### Messages not persisting
- Clear browser cache/cookies
- Check Streamlit version compatibility
- Ensure `session_state` is properly initialized

### Backend connection issues
- Verify `langgraph_backend.py` is in the same directory or in Python path
- Check network connectivity for Groq API calls
- Verify Groq API key validity

## License

[Add your license here - e.g., MIT, Apache 2.0, etc.]

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Support

For issues and questions:
- Check existing GitHub issues
- Create a new issue with detailed description
- Include error messages and reproduction steps

---

**Built with** 🚀
- [Streamlit](https://streamlit.io/)
- [LangGraph](https://langchain-ai.github.io/langgraph/)
- [LangChain](https://www.langchain.com/)
- [Groq](https://console.groq.com/)
