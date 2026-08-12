from langchain_huggingface import ChatHuggingFace, HuggingFaceEndpoint
from dotenv import load_dotenv
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StructuredOutputParser, ResponseSchema
import os

load_dotenv()

# Hugging Face model
llm = HuggingFaceEndpoint(
    repo_id="meta-llama/Llama-3.1-8B-Instruct",
    task="text-generation",
    huggingfacehub_api_token=os.getenv("HUGGINGFACEHUB_ACCESS_TOKEN")
)

model = ChatHuggingFace(llm=llm)


# Define the structure we want from the LLM
response_schemas = [
    ResponseSchema(
        name="summary",
        description="A short summary of the topic"
    ),
    ResponseSchema(
        name="facts",
        description="Important facts about the topic"
    ),
    ResponseSchema(
        name="analogy",
        description="A simple analogy to explain the topic"
    )
]


# Create the structured output parser
parser = StructuredOutputParser.from_response_schemas(response_schemas)


# Get formatting instructions from the parser
format_instructions = parser.get_format_instructions()


# Create prompt
template = PromptTemplate(
    template="""
Write a detailed report on {topic}.

Give the answer in the exact format requested below.

{format_instructions}
""",
    input_variables=["topic"],
    partial_variables={
        "format_instructions": format_instructions
    }
)


# Create chain
chain = template | model | parser


# Invoke chain
result = chain.invoke({
    "topic": "black hole"
})

print(result)