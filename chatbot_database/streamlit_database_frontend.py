import streamlit as st
from langgraph_database_backend import chatbot,retrieve_all_threads
from langchain_core.messages import HumanMessage
import uuid


# =========================================================
# Generate new thread ID
# =========================================================

def generate_thread_id():
    return str(uuid.uuid4())


# =========================================================
# Add thread to conversation list
# =========================================================

def add_thread(thread_id):
    if thread_id not in st.session_state['chat_thread']:
        st.session_state['chat_thread'].append(thread_id)


# =========================================================
# Load messages of a conversation
# =========================================================

def load_conversations(thread_id):

    state = chatbot.get_state(
        config={
            'configurable': {
                'thread_id': thread_id
            }
        }
    )

    # If this thread has no saved state yet
    if not state.values:
        return []

    # Get messages from the state
    return state.values.get('messages', [])


# =========================================================
# Reset / create new chat
# =========================================================

def reset_chat():

    thread_id = generate_thread_id()

    st.session_state['thread_id'] = thread_id

    add_thread(thread_id)

    st.session_state['message_history'] = []

    st.rerun()


# =========================================================
# SESSION STATE INITIALIZATION
# =========================================================

if 'message_history' not in st.session_state:
    st.session_state['message_history'] = []


if 'thread_id' not in st.session_state:
    st.session_state['thread_id'] = generate_thread_id()


if 'chat_thread' not in st.session_state:
    st.session_state['chat_thread'] = retrieve_all_threads()


# Add current thread to conversation list
add_thread(st.session_state['thread_id'])


# =========================================================
# SIDEBAR
# =========================================================

st.sidebar.title('LangGraph Chatbot')


# New Chat button
if st.sidebar.button('New Chat'):
    reset_chat()


st.sidebar.header('My Conversations')


# Show all conversations
for thread_id in st.session_state['chat_thread'][::-1]:

    if st.sidebar.button(str(thread_id)):

        # Set selected thread
        st.session_state['thread_id'] = thread_id

        # Load messages from LangGraph
        messages = load_conversations(thread_id)

        temp_messages = []

        for msg in messages:

            if isinstance(msg, HumanMessage):
                role = 'user'
            else:
                role = 'assistant'

            temp_messages.append({
                'role': role,
                'content': msg.content
            })

        # Replace current displayed history
        st.session_state['message_history'] = temp_messages

        # Refresh UI
        st.rerun()


# =========================================================
# LANGGRAPH CONFIG
# =========================================================

config = {
    'configurable': {
        'thread_id': st.session_state['thread_id']
    }
}


# =========================================================
# DISPLAY PREVIOUS MESSAGES
# =========================================================

for message in st.session_state['message_history']:

    with st.chat_message(message['role']):
        st.text(message['content'])


# =========================================================
# USER INPUT
# =========================================================

user_input = st.chat_input('Type here')


if user_input:

    # -----------------------------------------------------
    # Display user message
    # -----------------------------------------------------

    st.session_state['message_history'].append({
        'role': 'user',
        'content': user_input
    })

    with st.chat_message('user'):
        st.text(user_input)


    # -----------------------------------------------------
    # Get AI response
    # -----------------------------------------------------

    with st.chat_message('assistant'):

        ai_message = st.write_stream(
            message_chunk.content
            for message_chunk, metadata in chatbot.stream(
                {
                    'messages': [
                        HumanMessage(content=user_input)
                    ]
                },
                config=config,
                stream_mode='messages'
            )
        )


    # -----------------------------------------------------
    # Save AI response
    # -----------------------------------------------------

    st.session_state['message_history'].append({
        'role': 'assistant',
        'content': ai_message
    })