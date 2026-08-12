from langchain_huggingface import ChatHuggingFace, HuggingFaceEndpoint
from dotenv import load_dotenv
from langchain_core.prompts import PromptTemplate
import os
from langchain_core.output_parsers import JsonOutputParser

load_dotenv()

llm = HuggingFaceEndpoint(
    repo_id="meta-llama/Llama-3.1-8B-Instruct",
    task="text-generation",
    huggingfacehub_api_token=os.getenv("HUGGINGFACEHUB_ACCESS_TOKEN")
)

model = ChatHuggingFace(llm=llm)


# Creating templates means the prompt can be dynamic
parser=JsonOutputParser()
template1 = PromptTemplate(
    template="give me the name,age and the city of the fictional person.\n {format_instruction}",
    input_varibales=[],
    partial_variables={'format_instruction':parser.get_format_instructions()}

)
prompt=template1.format()
result=model.invoke(prompt)
final_result=parser.parse(result.content)
print(final_result)