from langchain_text_splitters import RecursiveCharacterTextSplitter

text=""" Artificial intelligence is changing the way people work, learn, and solve problems. It allows computers to understand information, recognize patterns, generate content, and make predictions. Technologies such as machine learning, deep learning, and generative AI are now being used in healthcare, education, finance, transportation, and many other industries. AI can help businesses automate repetitive tasks, analyze large amounts of data, and provide faster and more personalized services.

However, artificial intelligence also comes with challenges and responsibilities. AI systems can sometimes produce incorrect information, reflect biases in their training data, or create privacy and security concerns. Therefore, people need to understand both the benefits and limitations of AI before using it. With responsible development, proper testing, and human supervision, AI can become a powerful tool that improves productivity and helps solve complex real-world problems."""
splitter=RecursiveCharacterTextSplitter(
    chunk_size=100,
    chunk_overlap=0,
    
)
result=splitter.split_text(text)
print(result)
print(len(result))