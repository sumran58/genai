from langchain_huggingface import ChatHuggingFace,HuggingFaceEndpoint
#huggingfaceendpoint ham tab use karte jab ham uski access token use karte rather than downloading it loaclly on machine 
from dotenv import load_dotenv

load_dotenv()
llm=HuggingFaceEndpoint(
    repo_id="TinyLlama/TinyLlama-1.1B-Chat-v1.0", #konsa model from hugging face 
    task='text-generation' #konsa task ham perfrom kara rahe hai 
)

model=ChatHuggingFace(llm=llm)
result=model.invoke("what is the capital of india")
print(result.content)