from langchain_groq import ChatGroq
from dotenv import load_dotenv
from typing import TypedDict
load_dotenv()

model=ChatGroq(model='llama-3.3-70b-versatile')

class Review(TypedDict):
    summary:str
    sentiment:str

structured_model=model.with_structured_output(Review)

result=structured_model.invoke(""" the hardware is great but the software feel bloated and there are so many pre installed apps that i cant remove""")

print(result)
#niw here we hve not specify anywahere that give us the sentiment and all because whn we use typeddict and give it a structure and use the with_structured_output behind the scene a system prompt is generated 

#if we dont want our llm to get confused we can also make use of Annotated

# from typing import Annotated
# class Review(TypedDict):
#     summary:Annotated[str,"generate the summary from the review"]