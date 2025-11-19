# backend/services/rag_core.py
from typing import Optional, List, Any, Dict
from pydantic import BaseModel
from supabase_client import supabase
from openai import OpenAI
import os

_oai = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
EMBED_MODEL = "text-embedding-3-small"  # 1536 dims

class RagQuery(BaseModel):
    query: str
    top_k: int = 5
    category: Optional[str] = None
    client_id: Optional[str] = None
    min_similarity: float = 0.0

class RagChunk(BaseModel):
    chunk_id: str
    document_id: str
    chunk_index: int
    document_title: str
    source_url: Optional[str] = None
    category: Optional[str] = None
    client_id: Optional[str] = None
    similarity: float
    content: str

class RagResult(BaseModel):
    query: str
    results: List[RagChunk]

def _embed(text: str) -> List[float]:
    resp = _oai.embeddings.create(model=EMBED_MODEL, input=text)
    return resp.data[0].embedding

def rag_search(body: RagQuery) -> RagResult:
    vec = _embed(body.query)
    rpc = supabase.rpc(
        "match_knowledge_chunks",
        {
            "query_embedding": vec,
            "match_count": body.top_k,
            "in_category": body.category,
            "in_client": body.client_id,
        },
    ).execute()

    rows: List[Dict[str, Any]] = rpc.data or []
    # Optional filter; tool usually sets 0.0 and filters later.
    rows = [r for r in rows if float(r["similarity"]) >= body.min_similarity]

    out = [
        RagChunk(
            chunk_id=r["chunk_id"],
            document_id=r["document_id"],
            chunk_index=r["chunk_index"],
            document_title=r["doc_title"],
            source_url=r.get("source_url"),
            category=r.get("category"),
            client_id=r.get("client_id"),
            similarity=float(r["similarity"]),
            content=r["content"],
        )
        for r in rows
    ]
    return RagResult(query=body.query, results=out)
