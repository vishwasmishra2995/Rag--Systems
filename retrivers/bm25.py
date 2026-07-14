import re
from langchain_community.retrievers import BM25Retriever
from langchain_core.documents import Document
from langchain_chroma import Chroma
from embedding.embed import get_embeddings

def multilingual_tokenize(text: str) -> list:
    """Tokenize  bm25 all languages
    
"""
    text = text.lower()
    text = re.sub(r'([\u4e00-\u9fff\u3040-\u309f\u30a0-\u30ff\uac00-\ud7af])', r' \1 ', text)
    tokens = re.findall(r'\w+', text, re.UNICODE)
    return tokens

def _load_chunks_from_chroma():
    """Reload all documents from Chroma on startup so BM25 stays in sync."""
    try:
        db = Chroma(
            persist_directory="./chroma_db",
            embedding_function=get_embeddings()
        )
        data = db.get(include=["documents", "metadatas"])
        docs = []
        for content, meta in zip(data["documents"], data["metadatas"]):
            if content and content.strip():
                docs.append(Document(page_content=content, metadata=meta or {}))
        return docs
    except Exception:
        return []


all_chunks = _load_chunks_from_chroma()


dummy_doc = Document(page_content="dummy", metadata={"scope_id": "dummy"})
bm25_retriever = BM25Retriever.from_documents(
    all_chunks if all_chunks else [dummy_doc],
    preprocess_func=multilingual_tokenize
)
bm25_retriever.k = 5

def reinitialize_bm25():
    global bm25_retriever
    if all_chunks:
        bm25_retriever = BM25Retriever.from_documents(
            all_chunks,
            preprocess_func=multilingual_tokenize
        )
        bm25_retriever.k = 5

def bm25_search(query: str, scope_id: str):
    docs = bm25_retriever.invoke(query)
    return [
        d for d in docs
        if d.metadata.get("scope_id") == scope_id
    ]