from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from dotenv import load_dotenv
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableParallel,RunnableBranch,RunnableLambda
from langchain_core.output_parsers import PydanticOutputParser
from pydantic import BaseModel,Field
from typing import Literal

load_dotenv()
model=ChatGroq(model='llama-3.3-70b-versatile')

parser=StrOutputParser()

class Feedback(BaseModel):
        sentiment:Literal['Positive','Negative']=Field(description='give the sentiment of the feedback')
parser2=PydanticOutputParser(pydantic_object=Feedback)

prompt1=PromptTemplate(
    template='classify the feedback text into positive or negative \n {feedback} \n {format_instruction}',
    input_variables=['feedback'],
    partial_variables={'format_instruction':parser2.get_format_instructions()}
)

classifier_chain = prompt1 | model | parser2

prompt2=PromptTemplate(
        template='Write an appropriate reponse to this negative feedback \n {feedback}',
        input_variables=['feedback']
)

prompt3=PromptTemplate(
        template='Write an appropriate reponse to this positive feedback \n {feedback}',
        input_variables=['feedback']
)
branch_chain=RunnableBranch(
        (lambda x :x.sentiment=='Positive' , prompt3 | model | parser),
        (lambda x :x.sentiment=='Negative', prompt2 | model | parser),
        #yahape ek default chain bhi deni padti so vo  ek chain nhi  hoti hai to usko hamko runnablelambda me convert karna padt ahia 
        RunnableLambda(lambda x: "could not find the sentiment")
)
chain=classifier_chain | branch_chain
print(chain.invoke({'feedback':'it was a terrible experience'}))