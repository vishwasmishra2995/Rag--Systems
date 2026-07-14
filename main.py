import os
import json
from datetime import datetime, timezone
from pathlib import Path
import hashlib
from dotenv import load_dotenv
load_dotenv()

from fastapi.responses import StreamingResponse
from fastapi import FastAPI,Depends,UploadFile, Form, HTTPException
from auth.dependencies import get_scope_id
from auth.jwtutils import create_scope_token
#from rewrite.queryrewrite import rewrite
from simpleai import simple_chain
from langsmith import traceable


BASE_DIR = Path(__file__).resolve().parent
MODEL_DIR = BASE_DIR / "models"
TEMP_DIR = BASE_DIR / "temp"
EVAL_DATA_DIR = BASE_DIR / "evaluation_data"

os.environ.setdefault("HF_HOME", str(MODEL_DIR))
TEMP_DIR.mkdir(exist_ok=True)
EVAL_DATA_DIR.mkdir(exist_ok=True)
from inject import inject
from evaluation.store import InteractionStore

app = FastAPI( 
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
    )

interaction_store = InteractionStore(EVAL_DATA_DIR)

# In-memory chat history per scope_id (last 5 turns)
chat_histories: dict[str, list[dict]] = {}


def _persist_interaction(scope_id: str, question: str, answer: str, contexts: list[str]):
    interaction_store.save_interaction(
        {
            "scope_id": scope_id,
            "question": question,
            "answer": answer,
            "contexts": contexts,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
    )

@app.get("/")
def root():
    return {"status": "RAG Backend is running"}


@app.post("/login")
def login(username: str):
    scope_id = hashlib.sha256(username.lower().encode()).hexdigest()

    token = create_scope_token(scope_id)

    return {"token": token}

@app.post("/inject/file")
@traceable(name="injectfile")
async def inject_file(
    file: UploadFile,
    scope_id: str = Depends(get_scope_id)
):
    filename = file.filename.lower()
    if filename.endswith('.pdf'):
        source_type = 'pdf'
    elif filename.endswith('.csv'):
        source_type = 'csv'
    elif filename.endswith('.docx'):
        source_type = 'docx'
    elif filename.endswith('.txt'):
        source_type = 'txt'
    else:
        return {"error": f"Unsupported file type. Supported:  .pdf, .csv, .docx, .txt"}

    # Use absolute path
    path = TEMP_DIR / file.filename
    try:
        with open(path, "wb") as f:
            f.write(await file.read())

        inject(source_type, str(path), scope_id)
        return {"status": "Done loading"}
    except Exception as e:
        return {"error": f"Failed to process file: {str(e)}"}
    finally:
        if path.exists():
            path.unlink()

from rag import rag_chain
from retrivers.hybrid import hybrid_retrieve_top1
from retrivers.bm25 import bm25_retriever
from retrivers.vector import get_vector_retriever

@app.post("/ask")
@traceable(name="ask")
async def ask(
    question: str,
    scope_id: str = Depends(get_scope_id)
):
    query_rewriting = question #rewrite require higher ""rewrite(question)"" compuation
    vector_retriever = get_vector_retriever(scope_id)
    top_doc = hybrid_retrieve_top1(query_rewriting, bm25_retriever, vector_retriever, scope_id)
    print(top_doc)

    # caht history 
    history = chat_histories.get(scope_id, [])
    history_str = "\n".join(f"User: {h['q']}\nAssistant: {h['a']}" for h in history[-5:]) if history else "(none)"

    def _save_turn(answer_text):
        chat_histories.setdefault(scope_id, []).append({"q": query_rewriting, "a": answer_text})
        if len(chat_histories[scope_id]) > 5:
            chat_histories[scope_id] = chat_histories[scope_id][-5:]

    if not top_doc or len(top_doc.page_content.strip()) < 10:
        async def generate_simple():
            full = []
            for chunk in simple_chain.stream({"question": query_rewriting, "chat_history": history_str}):
                full.append(chunk)
                yield chunk
            answer = "".join(full)
            _save_turn(answer)
            _persist_interaction(scope_id, query_rewriting, answer, [])
        return StreamingResponse(generate_simple(), media_type="text/plain")

    context_text = top_doc.page_content
    async def generate_rag():
        full = []
        for chunk in rag_chain.stream({"context": context_text, "question": query_rewriting, "chat_history": history_str}):
            full.append(chunk)
            yield chunk
        answer = "".join(full)
        _save_turn(answer)
        _persist_interaction(scope_id, query_rewriting, answer, [context_text])
    return StreamingResponse(generate_rag(), media_type="text/plain")


@app.get("/evaluation/run")
@traceable(name="run_evaluation")
def run_evaluation(scope_id: str | None = None):
    from evaluation.pipeline import run_ragas_evaluation

    records = interaction_store.load_interactions()
    if not records:
        raise HTTPException(status_code=404, detail="No  data available for evaluation")

    run_dir = interaction_store.create_run_dir(scope_id=None)
    summary = run_ragas_evaluation(records, run_dir)
    summary["run_dir"] = str(run_dir)
    summary["scope_id"] = "all"
    with open(run_dir / "summary.json", "w", encoding="utf-8") as handle:
        json.dump(summary, handle, ensure_ascii=False, indent=2)
    return summary

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=7860
    )


