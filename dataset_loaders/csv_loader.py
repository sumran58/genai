from langchain_community.document_loaders import CSVLoader
loader=CSVLoader(file_path='diabetes (1).csv')

docs=loader.load()
print(docs[1])

#har row ke liye alag document banata ahi 