from langchain_text_splitters import CharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader

loader=PyPDFLoader('SUMRAN_HARCHIRKAR_CV_Dubai.pdf')

docs=loader.load()


splitter=CharacterTextSplitter(
    chunk_size=100,
    chunk_overlap=0, # means kuch words/chaarcters aise 2 chunks me same hoge so isse jo  senetnece abruptly cut horaha tha and semantic meaning loose ho raha tha wo nhi hoga yaha 
    separator=' '
)
result=splitter.split_documents(docs)
print(result[0].page_content)