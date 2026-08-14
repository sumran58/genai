from langchain_community.document_loaders import WebBaseLoader
url='https://www.apple.com/in-edu/shop/buy-mac?afid=p240%7Cgo~cmp-11180744360~adg-180400898871~ad-816969290845_kwd-335670223~dev-c~ext-~prd-~mca-~nt-search&cid=aos-in-kwgo-txt-mac-mac--'
loader=WebBaseLoader(url)

docs=loader.load()
print(docs[0].page_content)