from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from dotenv import load_dotenv
from langchain_core.output_parsers import StrOutputParser

load_dotenv()
model=ChatGroq(model='llama-3.3-70b-versatile')

prompt=PromptTemplate(
    template='give me the 5 line summary on {topic}',
    input_variables=['topic']
)

parser=StrOutputParser()

chain= prompt | model | parser
result=chain.invoke({'topic':'cricket'})
print(result)

chain.get_graph().print_ascii()