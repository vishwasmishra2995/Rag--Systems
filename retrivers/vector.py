from langchain_chroma import Chroma  # Updated import
from embedding.embed import get_embeddings

def get_vector_retriever(scope_id: str):
    db = Chroma(
        persist_directory="./chroma_db",
        embedding_function=get_embeddings()
    )

    return db.as_retriever(
        search_kwargs={
            "k": 5,
            "filter": {"scope_id": scope_id}
        }
    )