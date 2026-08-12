from langchain_huggingface import ChatHuggingFace, HuggingFaceEndpoint
from dotenv import load_dotenv
from langchain_core.prompts import PromptTemplate
import os
from langchain_core.output_parsers import StrOutputParser

load_dotenv()

llm = HuggingFaceEndpoint(
    repo_id="meta-llama/Llama-3.1-8B-Instruct",
    task="text-generation",
    huggingfacehub_api_token=os.getenv("HUGGINGFACEHUB_ACCESS_TOKEN")
)

model = ChatHuggingFace(llm=llm)


# Creating templates means the prompt can be dynamic

template1 = PromptTemplate(
    template="Write a detailed report on {topic}.",
    input_variables=['topic']
)

template2 = PromptTemplate(
    template="Write a 5 line summary on the following text.\n{text}",
    input_variables=['text']
)


prompt1 = template1.invoke({
    'topic': 'black hole'
})

result = model.invoke(prompt1)

prompt2 = template2.invoke({
    'text': result.content
})

result1 = model.invoke(prompt2)

print(result1.content)