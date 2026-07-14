from langchain_community.document_loaders import WebBaseLoader
def load_web(url: str):
    loader = WebBaseLoader(url)
    docs = loader.load()
    return docs