from loader.pdf import load_pdf
from loader.csv import load_csv
from loader.web import load_web
from loader.docx import loaddocx
from loader.txt import loadtxt
from splitter.split import split_docs
from store.storing import store_chunks
from retrivers.bm25 import all_chunks, reinitialize_bm25

def inject(source_type: str, source: str, scope_id: str):
    if source_type == "pdf":
        docs = load_pdf(source)
    elif source_type == "csv":
        docs = load_csv(source)
    elif source_type == "web":
        docs = load_web(source)
    elif source_type == "docx":
        docs = loaddocx(source)
    elif source_type == "txt":
        docs = loadtxt(source)
    else:
        raise ValueError("unsupported type")
    chunks = split_docs(docs)

    for doc in chunks:
        doc.metadata["scope_id"] = scope_id
    store_chunks(chunks)
    all_chunks.extend(chunks)
    reinitialize_bm25()  