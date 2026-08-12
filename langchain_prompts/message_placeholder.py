from langchain_core.prompts import ChatPromptTemplate,MessagesPlaceholder
from langchain_core.messages import HumanMessage
chat_template=ChatPromptTemplate([
    ('system','you are a helpful customer support agent'),
    MessagesPlaceholder(variable_name='chat_history'), #purane jitne bhi chats huele rahege wo yaha aa jayege 
    ('human','{query}')
])
chat_history=[]
with open('chat_history.txt') as f:
    chat_history.extend(f.readlines())
print(chat_history)

prompt=chat_template.invoke({'chat_history':chat_history,'query':HumanMessage(content="what is the difference between human and ai ")})
print(prompt)