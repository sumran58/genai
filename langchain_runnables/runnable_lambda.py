from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from dotenv import load_dotenv
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnableSequence,RunnableParallel,RunnablePassthrough,RunnableLambda


load_dotenv()
model=ChatGroq(model='llama-3.3-70b-versatile')

# def word_counter(text):
#     return len(text.split())
# runnable_word_counter=RunnableLambda(word_counter)
# print(runnable_word_counter.invoke('hi my name is simrfan'))


prompt1=PromptTemplate(
    template='give me the a joke on {topic}',
    input_variables=['topic']
)

parser=StrOutputParser()

joke_gen_chain=RunnableSequence(prompt1,model,parser)

parallel_chain=RunnableParallel(
    {
        'joke':RunnablePassthrough(),
        'word_count':RunnableLambda(lambda x : len(x.split()))
    }
)
chain=RunnableSequence(joke_gen_chain,parallel_chain)
result=chain.invoke({'topic':'AI'})
print(result)