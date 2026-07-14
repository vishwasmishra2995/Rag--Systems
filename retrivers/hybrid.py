def hybrid_retrieve(query, bm25_retriever, vector_retriever, scope_id=None, k_each=5):
    """Hybrid retrieval using Reciprocal Rank Fusion (RRF).

    RRF is language-agnostic - it fuses results based on rank positions,
    not word overlap, so it works identically for all languages.
    """

    bm25_docs = bm25_retriever.invoke(query)[:k_each]
    vector_docs = vector_retriever.invoke(query)[:k_each]


    if scope_id:
        bm25_docs = [d for d in bm25_docs if d.metadata.get("scope_id") == scope_id]
        vector_docs = [d for d in vector_docs if d.metadata.get("scope_id") == scope_id]

   
    RRF_K = 60  
    scores = {}
    doc_map = {}

    for rank, doc in enumerate(bm25_docs):
        key = doc.page_content.strip()
        scores[key] = scores.get(key, 0) + 1 / (RRF_K + rank + 1)
        doc_map[key] = doc

    for rank, doc in enumerate(vector_docs):
        key = doc.page_content.strip()
        scores[key] = scores.get(key, 0) + 1 / (RRF_K + rank + 1)
        doc_map[key] = doc

    if not scores:
        return []

    ranked_keys = sorted(scores, key=scores.get, reverse=True)
    return [doc_map[key] for key in ranked_keys]


def hybrid_retrieve_top1(query, bm25_retriever, vector_retriever, scope_id=None, k_each=5):
    ranked_docs = hybrid_retrieve(query, bm25_retriever, vector_retriever, scope_id, k_each)
    return ranked_docs[0] if ranked_docs else None
