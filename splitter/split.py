from langchain_text_splitters import RecursiveCharacterTextSplitter

def split_docs(docs):

    text_length = sum(len(doc.page_content) for doc in docs)

    if text_length < 5000:
        chunk_size = 500
        chunk_overlap = 100
    elif text_length < 50000:
        chunk_size = 800
        chunk_overlap = 150
    else:
        chunk_size = 1200
        chunk_overlap = 200

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=[
        "\n\n",
        "\n",
        "。",   
        "। ",  
        "؟ ", 
        "？",  
        "！",  
        ". ",
        "? ",
        "! ",
        " ",
        ""     
    ]
    )
    return splitter.split_documents(docs)