from langchain_community.document_loaders import TextLoader

def loadtxt(path:str):
    loader = TextLoader(path , encoding="utf-8")
    docs = loader.load()
    return docs