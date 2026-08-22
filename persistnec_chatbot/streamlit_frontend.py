import streamlit as st
from langgraph_backend import chatbot
from langchain_core.messages import HumanMessage

config={'configurable':{'thread_id':'thread-1'}}

#every time we press enter the content in the message history gets efreshed so we ahve session_state in streamlit which is dictionary which dont gets reset unless we manually press  refreshbutton from browser 

if 'message_history' not in st.session_state:
    st.session_state['message_history']=[]



for message in st.session_state['message_history']:
    with st.chat_message(message['role']):
        st.text(message['content'])

user_input=st.chat_input('Type here')

if user_input:
    st.session_state['message_history'].append({'role':'user','content':user_input})
    with st.chat_message('user'):#brackets me jo 'user ' hai wo rek role assign kiye hai ham jisse wo icon ayega side me 
        st.text(user_input)


    response=chatbot.invoke({'messages':[HumanMessage(content=user_input)]},config=config)
    ai_message=response['messages'][-1].content
    
    st.session_state['message_history'].append({'role':'assistant','content':ai_message})
    with st.chat_message('assistant'):#brackets me jo 'user ' hai wo rek role assign kiye hai ham jisse wo icon ayega side me 
        st.text(ai_message)