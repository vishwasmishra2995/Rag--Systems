from langchain_community.document_loaders import Docx2txtLoader

def loaddocx(path : str):
    loader = Docx2txtLoader(path)
    docs = loader.load()
    return docs