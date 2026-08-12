from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import SystemMessage,HumanMessage,AIMessage

template=ChatPromptTemplate([
    ('system','you are a helpful {domain} expert'),
    ('human','explain in simple termns what is {topic}')
])

prompt=template.invoke({'domain':'ai','topic':'langchain'})
print(prompt)