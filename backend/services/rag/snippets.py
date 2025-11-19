# services/rag_snippets.py
from typing import List, Dict, Any, Tuple

MAX_SNIPPET_CHARS = 1400  # still useful as a single place to cap snippet length

def _trim(s: str) -> str:
    s = (s or "").strip()
    return s if len(s) <= MAX_SNIPPET_CHARS else s[:MAX_SNIPPET_CHARS] + "…"

def _pack(packed: List[Dict[str, Any]]) -> str:
    lines = ["[RAG_SNIPPETS_BEGIN]"]
    for p in packed:
        lines.append(
            "{chunk_id:\"%s\", category:\"%s\", client_id:%s, title:\"%s\", "
            "similarity:%.4f, url:%s, content:\"%s\"}" % (
                p.get("chunk_id", ""),
                p.get("category", "") or "",
                ("null" if not p.get("client_id") else f"\"{p['client_id']}\""),
                (p.get("title") or "").replace('"', "'"),
                float(p.get("similarity", 0.0)),
                ("null" if not p.get("url") else f"\"{p['url']}\""),
                (p.get("content") or "").replace('"', "'"),
            )
        )
    lines.append("[RAG_SNIPPETS_END]")
    return "\n".join(lines)

def pack_snippets_with_meta(
    results: List[Dict[str, Any]],
    *,
    min_similarity: float,
    final_count: int
) -> Tuple[str, Dict[str, int]]:
    """Filter by floor, dedup by (document_id, chunk_index), trim, cap, then pack."""
    input_count = len(results)
    seen = set()
    after_floor = [r for r in results if float(r.get("similarity", 0.0)) >= min_similarity]
    kept_after_floor = len(after_floor)

    dedup_list: List[Dict[str, Any]] = []
    for r in after_floor:
        key = (r.get("document_id"), r.get("chunk_index"))
        if key in seen:
            continue
        seen.add(key)
        dedup_list.append(r)
    dedup_kept = len(dedup_list)

    included = []
    for r in dedup_list[:final_count]:
        included.append({
            "chunk_id": r.get("chunk_id") or "",
            "category": r.get("category") or "",
            "client_id": r.get("client_id"),
            "title": r.get("document_title") or r.get("doc_title") or "",
            "similarity": float(r.get("similarity", 0.0)),
            "url": r.get("source_url"),
            "content": _trim(r.get("content", "")),
        })

    block = _pack(included)
    meta = {
        "input_count": input_count,
        "kept_after_floor": kept_after_floor,
        "dedup_kept": dedup_kept,
        "included_count": len(included),
        "floor_used": int(round(min_similarity * 100)),
    }
    return block, meta
