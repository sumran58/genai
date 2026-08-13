from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from dotenv import load_dotenv
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnableSequence

load_dotenv()
model=ChatGroq(model='llama-3.3-70b-versatile')

prompt=PromptTemplate(
    template='give me the 5 line summary on {topic}',
    input_variables=['topic']
)
parser=StrOutputParser()

chain=RunnableSequence(prompt ,model, parser)
print(chain.invoke({'topic':'cricket'}))