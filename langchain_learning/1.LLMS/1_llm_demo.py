from langchain_groq import ChatGroq
from dotenv import load_dotenv

load_dotenv()
llm=ChatGroq(
    model='llama-3.3-70b-versatile'
)
#invoke is the function that contains the question and will hit the api and the model will process the question and give back the answer
result=llm.invoke("what is the capital of india")
print(result)