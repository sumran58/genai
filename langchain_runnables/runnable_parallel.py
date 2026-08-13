from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from dotenv import load_dotenv
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnableSequence,RunnableParallel

load_dotenv()

model=ChatGroq(model='llama-3.3-70b-versatile')

prompt1=PromptTemplate(
    template='generate a tweet about the  {topic}',
    input_variables=['topic']
)

prompt2=PromptTemplate(
    template='generate a linkedin post about   {topic}',
    input_variables=['topic']
)


parser=StrOutputParser()

chain=RunnableParallel(
    {
        'tweet':RunnableSequence(prompt1,model,parser),
        'linkedin':RunnableSequence(prompt2,model,parser)
    }
)
print(chain.invoke({'topic':'cricket'}))