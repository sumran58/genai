from langchain_groq import ChatGroq
from dotenv import load_dotenv

load_dotenv()

model=ChatGroq(model='llama-3.3-70b-versatile',temperature=0)
#temperature is just the parameter that decides the randomness  from  the model and it varies between 0 to 3 the higer the value the more brainstorming the reposne from the model 
result=model.invoke("crate a poen on name simran ")
print(result.content)