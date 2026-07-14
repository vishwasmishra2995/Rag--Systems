from langchain_community.document_loaders import CSVLoader

def load_csv(path: str):
    loader = CSVLoader(file_path=path)
    docs = loader.load()
    return docs