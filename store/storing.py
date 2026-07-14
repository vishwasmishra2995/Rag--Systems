from langchain_chroma import Chroma
from embedding.embed import get_embeddings

def store_chunks(chunks):
    db = Chroma.from_documents(
        documents=chunks,
        embedding=get_embeddings(),
        persist_directory="./chroma_db"
    )
    return db