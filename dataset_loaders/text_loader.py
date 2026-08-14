from langchain_community.document_loaders import TextLoader
from langchain_groq import ChatGroq
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from dotenv import load_dotenv
load_dotenv()
model=ChatGroq(model='llama-3.3-70b-versatile')
loader=TextLoader('cricket.txt',encoding='utf-8')

prompt=PromptTemplate(
    template="write a summary for the following poem - \n {poem}",
    input_variables=['poem']
)
parser=StrOutputParser()
docs=loader.load()
print(docs[0])
chain=prompt | model | parser
print(chain.invoke({'poem':docs[0].page_content}))
