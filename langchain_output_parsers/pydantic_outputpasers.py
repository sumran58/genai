from langchain_huggingface import ChatHuggingFace, HuggingFaceEndpoint
from dotenv import load_dotenv
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from pydantic import BaseModel,Field
import os
load_dotenv()

# Hugging Face model
llm = HuggingFaceEndpoint(
    repo_id="meta-llama/Llama-3.1-8B-Instruct",
    task="text-generation",
    huggingfacehub_api_token=os.getenv("HUGGINGFACEHUB_ACCESS_TOKEN")
)

model = ChatHuggingFace(llm=llm)

class Person(BaseModel):
    name:str=Field(description='name of the person')
    age:int=Field(ge=18,description="Age of the person")
    city:str=Field('Name of the city the person belongs to ')

parser=PydanticOutputParser(pydantic_object=Person)
template=PromptTemplate(
    template='generate the name,age and the city of the bollywood {place} person \n {format_instruction}',
    input_variables=['place'],
    partial_variables={'format_instruction':parser.get_format_instructions()}
)

prompt=template.invoke({'place':'Indian'})
result=model.invoke(prompt)
final_result=parser.parse(result.content)
print(final_result)

