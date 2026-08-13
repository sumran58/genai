from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from dotenv import load_dotenv
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableParallel

load_dotenv()
model=ChatGroq(model='llama-3.3-70b-versatile')

prompt1=PromptTemplate(
    template='generate short and simple note from the following text \n {text}',
    input_variables=['text']
)

prompt2=PromptTemplate(
    template='generate 5 short question answer on the following text  \n {text}',
    input_variables=['text']
)

prompt3=PromptTemplate(
    template='merge the provided notes and quiz into the single document   \n  notes->{notes} and quiz-> {quiz}',
    input_variables=['notes','quiz']
)

parser=StrOutputParser()

parallel_chain=RunnableParallel(
    {
        'notes':prompt1 | model | parser,
        'quiz': prompt2 | model | parser
    }
)
merge_chain=prompt3 | model | parser

chain= parallel_chain | merge_chain

text="""Artificial Intelligence (AI) is a branch of computer science that focuses on creating machines capable of performing tasks that normally require human intelligence.
AI systems can perform tasks such as understanding language, recognizing images, solving problems, and making decisions.
Machine Learning (ML) is a subset of AI in which computers learn patterns from data instead of being explicitly programmed for every task.
Deep Learning is a subset of ML that uses artificial neural networks with multiple layers to learn complex patterns from large amounts of data.
Generative AI is a type of AI that can create new content such as text, images, audio, video, and computer code.
Large Language Models (LLMs) are deep learning models trained on huge amounts of text to understand and generate human-like language.
Before text is processed by an LLM, it is usually divided into smaller units called tokens through a process called tokenization.
Each token is converted into a numerical representation that can be processed by the neural network.
Prompt engineering involves designing effective instructions or prompts to guide an AI model toward producing useful and accurate responses.
A prompt can be static, where the instructions remain the same, or dynamic, where information changes according to the user's input.
LangChain is a framework that helps developers build applications using language models and connect them with prompts, tools, memory, and other components.
A chain in LangChain connects multiple components so that the output of one component can become the input of another component.
Sequential chains execute multiple tasks one after another, while parallel chains allow independent tasks to be handled separately.
Output parsers can convert an LLM's raw response into a structured format that an application can easily process.
These technologies together allow developers to build applications such as chatbots, document summarizers, question-answering systems, and AI-powered assistants.
"""

result=chain.invoke({'text':text})
print(result)

chain.get_graph().print_ascii()