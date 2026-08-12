from langchain_google_genai import GoogleGenerativeAIEmbeddings
from dotenv import load_dotenv

load_dotenv()
embedding=GoogleGenerativeAIEmbeddings(model="gemini-embedding-001",dimensions=32)
result=embedding.embed_query("delhi is the capital of india")
print(str(result))