# services/tools/rag_search_tool.py
"""
RAG search tool callable by the LLM.

- Validates category (sops | meeting_notes | clients | website | GLOBAL fallback)
- Injects primary client name for meeting_notes if not present
- Scopes website queries to the current conversation's client
- Supports "normal" vs "website_full" modes (for broader website pulls)
- Calls your internal rag_search (no HTTP) and packs results with rag.snippets
- Returns a compact JSON payload + prints an audit line
- If the user asks what happened/what we promised: prefer meeting_notes (when available). If none support the claim, say so briefly and base guidance on SOPs/playbooks.
"""

from __future__ import annotations
import json
import os
import re
from typing import Any, Dict, List, Optional, Tuple

# Late imports to avoid circular FastAPI imports on module load
from services.rag.core import RagQuery, rag_search
from services.rag.snippets import pack_snippets_with_meta

# -----------------------------
# Config knobs (easy to tweak)
# -----------------------------
TOOL_NAME = "rag_search_tool"

# Default search behavior (model can override `top_k` and `min_similarity` in args if you let it)
DEFAULT_TOP_K = int(os.getenv("RAG_TOOL_TOPK", "12"))
DEFAULT_MIN_SIM = float(os.getenv("RAG_TOOL_MIN_SIM", "0.35"))  # 0..1
DEFAULT_FINAL_SNIPPETS = int(os.getenv("RAG_TOOL_FINAL_SNIPPETS", "6"))  # 5–7 works well

# "Full website" mode: used when the model explicitly wants a broad view of the site
WEBSITE_FULL_TOP_K = int(os.getenv("RAG_WEBSITE_FULL_TOPK", "48"))
WEBSITE_FULL_FINAL_SNIPPETS = int(os.getenv("RAG_WEBSITE_FULL_FINAL_SNIPPETS", "18"))

# Allowed explicit categories; GLOBAL is handled via None
ALLOWED_CATEGORIES = {"sops", "meeting_notes", "clients", "website", "upload"}

# -----------------------------


def get_tool_definition() -> Dict[str, Any]:
    """OpenAI tool schema."""
    return {
        "type": "function",
        "function": {
            "name": TOOL_NAME,
            "description": (
                "Search the knowledge base for relevant snippets. "
                "The knowledge base also includes website content for the primary client of this conversation. "
                "You can use this tool to query website infomration about the current client. "
                "Choose a category if you know which corpus to search. "
                "For cross-cutting topics, set category to GLOBAL (or leave blank) to search everything. "
                "When category is 'website', this tool only searches website content for the primary client "
                "associated with the current conversation. "
                "Use 'website_full' mode when you need a broad understanding of the client's entire website "
                "rather than a narrow answer."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Semantic search query."
                    },
                    "category": {
                        "type": "string",
                        "description": (
                            "One of: sops, meeting_notes, clients, website, upload, GLOBAL "
                            "(GLOBAL = all categories). "
                            "For website, you only get content for the current conversation's client. "
                            "Use 'upload' when you specifically want to search files uploaded in "
                            "this conversation."
                        ),
                    },
                    "top_k": {
                        "type": "integer",
                        "description": (
                            f"How many candidates to retrieve (default {DEFAULT_TOP_K}). "
                            "Typically you do not need to override this; instead use 'mode' "
                            "to ask for a broader website view."
                        ),
                    },
                    "min_similarity": {
                        "type": "number",
                        "description": (
                            f"Similarity floor 0..1 (default {DEFAULT_MIN_SIM}). "
                            "Higher values = stricter relevance."
                        ),
                    },
                    "mode": {
                        "type": "string",
                        "description": (
                            "How broadly to search. "
                            "'normal' (default) = standard context window. "
                            "'website_full' = for category 'website', retrieve many more chunks to "
                            "understand most of the client's website content."
                        ),
                    },
                },
                "required": ["query"],
            },
        },
    }


def _inject_client_name_if_needed(
    query: str,
    category: Optional[str],
    primary_client_name: Optional[str],
) -> Tuple[str, bool]:
    """
    If category == meeting_notes and client name isn't in query, inject it.
    Returns (final_query, injected_flag).
    """
    if category != "meeting_notes" or not primary_client_name:
        return query, False

    if re.search(re.escape(primary_client_name), query, flags=re.IGNORECASE):
        return query, False

    return f"{primary_client_name} {query}".strip(), True


def run(raw_args: str, *, tool_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Execute the RAG tool. Returns a dict containing:
      - "json": a JSON string that will be sent back to the LLM as the tool result
      - "meta": a dict with counts/best_similarity/titles for server-side auditing
      - "effective_args": the final args we executed (after defaults and client injection)
    """
    tool_context = tool_context or {}
    try:
        args = json.loads(raw_args) if isinstance(raw_args, str) else dict(raw_args or {})
    except Exception:
        args = {}

    query = (args.get("query") or "").strip()
    category = (args.get("category") or "").strip().lower()
    mode = (args.get("mode") or "normal").strip().lower()
    top_k = DEFAULT_TOP_K
    min_sim = DEFAULT_MIN_SIM

    primary_client_name = tool_context.get("primary_client_name")
    primary_client_id = tool_context.get("primary_client_id")
    conversation_id = tool_context.get("conversation_id")

    planned_category = category or "GLOBAL"
    effective_category = category if category in ALLOWED_CATEGORIES else None  # GLOBAL = None

    # Decide client scoping:
    # - For website category, we always scope to the primary client id for this conversation.
    # - For other categories (sops, meeting_notes, clients, GLOBAL), we allow cross-client search.
    if effective_category == "website" and primary_client_id:
        client_filter = primary_client_id
    else:
        client_filter = None

    # Decide how many snippets to keep based on mode and category
    if mode == "website_full" and effective_category == "website":
        # Broad website overview: more candidates, more final snippets
        top_k_effective = WEBSITE_FULL_TOP_K
        final_snippets = WEBSITE_FULL_FINAL_SNIPPETS
        mode_used = "website_full"
    else:
        top_k_effective = top_k
        final_snippets = DEFAULT_FINAL_SNIPPETS
        mode_used = "normal"

    # Client-name injection for meeting_notes
    query_effective, injected = _inject_client_name_if_needed(
        query, category, primary_client_name
    )

    # Pre-call audit
    print(
        "🔎 RAG(tool): "
        f"planned={planned_category} | effective={effective_category or 'GLOBAL'} | "
        f"mode={mode_used} | client_filter={client_filter or 'ALL'} | "
        f"q={query_effective!r} | top_k={top_k_effective} | floor={int(min_sim * 100)}% | "
        f"augmented_with_client={injected}"
    )

    # Call your internal rag_search() (no HTTP)
    rpc = rag_search(
        RagQuery(
            query=query_effective,
            top_k=top_k_effective,
            category=effective_category,
            client_id=client_filter,  # <- only non-None for website category
            min_similarity=0.0,       # we apply the floor in our packer
            conversation_id=conversation_id,
        )
    )

    # Normalize rows → dict
    rows = [r.dict() if hasattr(r, "dict") else r for r in rpc.results]

    # Apply floor, dedup, cap to final N, and pack block for the model
    block, meta = pack_snippets_with_meta(
        rows,
        min_similarity=min_sim,
        final_count=final_snippets,
    )

    # Derive extra audit fields
    titles: List[str] = []
    for r in rows[:5]:
        t = r.get("document_title") or r.get("doc_title") or ""
        if t:
            titles.append(t)

    best_sim = 0.0
    if rows:
        kept = meta.get("kept_after_floor", 0)
        if kept > 0:
            best_sim = float(
                max(
                    r.get("similarity", 0.0)
                    for r in rows
                    if float(r.get("similarity", 0.0)) >= min_sim
                )
            )

    # Server log, one line
    print(
        "🔎 RAG(tool): "
        f"planned={planned_category} | effective={effective_category or 'GLOBAL'} | "
        f"mode={mode_used} | client_filter={client_filter or 'ALL'} | "
        f"q={query_effective!r} | top_k={top_k_effective} | floor={int(min_sim * 100)}% | "
        f"total={len(rows)} | kept={meta.get('kept_after_floor')} | "
        f"best_sim={best_sim:.4f} | titles={', '.join(titles[:3]) or '-'}"
    )

    # What the model gets back as the tool result
    result_to_model = {
        "ok": True,
        "category": effective_category or "GLOBAL",
        "query": query_effective,
        "mode": mode_used,
        "client_scoped": bool(client_filter),
        "snippets_block": block,            # [RAG_SNIPPETS_BEGIN]…[END]
        "kept": meta.get("kept_after_floor"),
        "included": meta.get("included_count"),
        "best_similarity": round(best_sim, 4),
        "titles": titles[:5],
    }

    return {
        "json": json.dumps(result_to_model, ensure_ascii=False),
        "meta": {
            "planned_category": planned_category,
            "effective_category": effective_category or "GLOBAL",
            "mode": mode_used,
            "client_scoped": bool(client_filter),
            "query": query_effective,
            "top_k": top_k_effective,
            "floor": min_sim,
            "total": len(rows),
            "kept": meta.get("kept_after_floor"),
            "included": meta.get("included_count"),
            "best_similarity": best_sim,
            "titles": titles[:5],
        },
        "effective_args": {
            "query": query_effective,
            "category": effective_category or "GLOBAL",
            "mode": mode_used,
            "top_k": top_k_effective,
            "min_similarity": min_sim,
            "conversation_id": conversation_id,
        },
    }
