from langchain_huggingface import HuggingFaceEmbeddings
_embeddings = None

"""
def get_embeddings():
    global _embeddings
    if _embeddings is None:
        _embeddings = HuggingFaceEmbeddings(
            model_name="BAAI/bge-m3",
            encode_kwargs={"normalize_embeddings": True}
        )
    return _embeddings

"""

def get_embeddings():
    global _embeddings
    if _embeddings is None:
        _embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2",
            encode_kwargs={"normalize_embeddings": True}
        )
    return _embeddings