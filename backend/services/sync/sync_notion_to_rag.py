# File: backend/services/sync_notion_to_rag.py
import os
import hashlib
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional, Tuple

from dotenv import load_dotenv
from notion_client import Client as NotionClient
from openai import OpenAI
from supabase_client import supabase
from services.notion.client_sync import _get_all_blocks  # your existing helper
from services.notion.client_sync import refresh_clients_from_notion


load_dotenv()

# ── ENV ────────────────────────────────────────────────────────────────────────
NOTION_TOKEN = os.getenv("NOTION_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Map your Notion DBs → categories you want to store
NOTION_DATABASE_IDS: Dict[str, Optional[str]] = {
    "meeting_notes": os.getenv("NOTION_MEETING_NOTES_DB_ID"),
    "sops":          os.getenv("NOTION_SOPS_DB_ID"),
    "clients":       os.getenv("NOTION_CLIENTS_DB_ID"),
}

# Optional toggle: include titles in embedding input (default: True)
INCLUDE_TITLE_IN_EMBED = os.getenv("INCLUDE_TITLE_IN_EMBED", "true").lower() in ("1", "true", "yes")

# Name of the relation property on Meeting Notes that links to a Client page in Notion
MEETING_NOTE_CLIENT_RELATION_NAME = os.getenv("MEETING_NOTE_CLIENT_RELATION_NAME", "Clients")

if not NOTION_TOKEN:
    raise RuntimeError("Missing NOTION_TOKEN in .env")
if not OPENAI_API_KEY:
    raise RuntimeError("Missing OPENAI_API_KEY in .env")

notion = NotionClient(auth=NOTION_TOKEN)
openai_client = OpenAI(api_key=OPENAI_API_KEY)

# ── CHUNKING / EMBEDDINGS ─────────────────────────────────────────────────────
MAX_CHARS = 2000     # target chunk size
OVERLAP   = 300      # overlapping stride
EMBEDDING_MODEL = "text-embedding-3-small"  # 1536 dims; matches vector(1536)


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _sha256(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def _norm_ts(ts: Optional[str]) -> Optional[str]:
    """Normalize ISO timestamps so 'Z' and '+00:00' compare equal at second precision."""
    if not ts:
        return None
    ts = ts.replace("Z", "+00:00")
    try:
        dt = datetime.fromisoformat(ts)
    except ValueError:
        return ts
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    else:
        dt = dt.astimezone(timezone.utc)
    return dt.replace(microsecond=0).isoformat()


def get_title_from_props(props: Dict[str, Any]) -> str:
    """Find a Notion 'title' property regardless of its display name."""
    for _, val in props.items():
        if isinstance(val, dict) and val.get("type") == "title":
            arr = val.get("title", [])
            if arr:
                return "".join(t.get("plain_text", "") for t in arr).strip()
    return "Untitled"


def get_rich_text_prop(props: Dict[str, Any], name: str) -> str:
    """Return plain text from a Notion rich_text property by name."""
    p = props.get(name)
    if isinstance(p, dict) and p.get("type") == "rich_text":
        arr = p.get("rich_text") or []
        return "".join(t.get("plain_text", "") for t in arr).strip()
    return ""


def chunk_text(text: str) -> List[str]:
    """Split long text into overlapping character chunks."""
    chunks: List[str] = []
    n = len(text)
    if n == 0:
        return chunks
    start = 0
    while start < n:
        end = min(start + MAX_CHARS, n)
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        if end == n:
            break
        start = max(0, end - OVERLAP)
    return chunks


def extract_full_page_text(page_id: str) -> str:
    """
    Concatenate visible rich_text from all blocks in a page.
    TIP (later): If you add a 'Summary' property in Notion, you can prefer it here.
    """
    blocks = _get_all_blocks(page_id)
    parts: List[str] = []
    for block in blocks:
        btype = block.get("type")
        data  = block.get(btype, {}) or {}
        rich  = data.get("rich_text")
        if isinstance(rich, list):
            txt = "".join(rt.get("plain_text", "") for rt in rich).strip()
            if txt:
                parts.append(txt)
    return "\n".join(parts).strip()


def embed_text(text: str) -> List[float]:
    """Return an embedding vector; return [] on failure (we'll still insert row)."""
    try:
        resp = openai_client.embeddings.create(model=EMBEDDING_MODEL, input=text)
        return resp.data[0].embedding
    except Exception as e:
        print(f"⚠️ Embedding error: {e}")
        return []


# ── CLIENT LINKING (Notion relation → Supabase UUID) ──────────────────────────
def build_client_cache() -> Dict[str, str]:
    """
    Load all Supabase clients into a dict:
      { notion_page_id (str) : client_id (uuid str) }
    """
    rows = (
        supabase.table("clients")
        .select("id, notion_page_id")
        .execute()
    ).data or []
    cache: Dict[str, str] = {}
    for r in rows:
        npid = (r.get("notion_page_id") or "").strip()
        cid  = (r.get("id") or "").strip()
        if npid and cid:
            cache[npid] = cid
    print(f"🗂️ Loaded {len(cache)} clients into cache")
    return cache


def resolve_client_id_from_note(props: Dict[str, Any], client_cache: Dict[str, str]) -> Optional[str]:
    """
    From a meeting note page's properties, read the relation property (e.g. 'Clients'),
    take the first related Notion page id, and map it to Supabase clients.id via cache.
    """
    rel = props.get(MEETING_NOTE_CLIENT_RELATION_NAME)
    if not isinstance(rel, dict) or rel.get("type") != "relation":
        return None

    rel_items = rel.get("relation") or []
    if not rel_items:
        return None

    # Take first related client page (adjust if you expect multiple)
    related_page_id = rel_items[0].get("id")
    if not related_page_id:
        return None

    cid = client_cache.get(related_page_id)
    if not cid:
        print(f"⚠️ No matching client in Supabase for Notion client page {related_page_id}")
    return cid


# ── DB HELPERS ────────────────────────────────────────────────────────────────
def _doc_by_notion_page_id(page_id: str) -> Optional[Dict[str, Any]]:
    res = (
        supabase.table("knowledge_documents")
        .select("id, checksum, last_edited_at")
        .eq("notion_page_id", page_id)
        .execute()
    )
    return res.data[0] if res.data else None


def _delete_chunks_for_document(document_id: str) -> None:
    supabase.table("knowledge_chunks").delete().eq("document_id", document_id).execute()


def _insert_chunks(
    document_id: str,
    chunks: List[str],
    title: str,
    client_id: Optional[str],
    category: str,
    tags: Optional[List[str]],
) -> int:
    rows: List[Dict[str, Any]] = []
    for idx, ch in enumerate(chunks):
        content_to_embed = f"{title}\n\n{ch}".strip() if INCLUDE_TITLE_IN_EMBED else ch
        rows.append(
            {
                "document_id": document_id,
                "chunk_index": idx,
                "content": ch,                             # human-readable content (no title)
                "tokens": None,
                "embedding": embed_text(content_to_embed), # vector(1536)
                "client_id": client_id,
                "category": category,
                "tags": tags or [],
            }
        )
    if rows:
        supabase.table("knowledge_chunks").insert(rows).execute()
    return len(rows)


# ── SUPABASE UPSERT ───────────────────────────────────────────────────────────
def upsert_document_and_chunks(
    *,
    notion_page_id: str,
    title: str,
    raw_text: str,
    category: str,
    last_edited_at: str,
    client_id: Optional[str] = None,
    source_url: Optional[str] = None,
    tags: Optional[List[str]] = None,
) -> Tuple[str, str]:
    """
    Upsert a knowledge_documents row keyed by notion_page_id.
    If unchanged (checksum match), skip re-chunk/insert.
    Else: (re)write document, delete old chunks and insert new chunks with embeddings.

    Returns (document_id, action) where action in {"added","updated","skipped"}.
    """
    existing = _doc_by_notion_page_id(notion_page_id)

    # Compute checksum using title + raw_text so title changes re-trigger embedding
    title_plus_text = f"{title}\n\n{raw_text}".strip()
    new_checksum = _sha256(title_plus_text)

    if existing and existing.get("checksum") == new_checksum:
        # fast path: unchanged
        print(f"✅ Skipping unchanged (checksum): {title}")
        return existing["id"], "skipped"

    doc_payload = {
        "source":          "notion",
        "source_id":       notion_page_id,
        "source_url":      source_url,
        "title":           title,
        "raw_text":        raw_text,
        "summary":         None,
        "client_id":       client_id,
        "category":        category,
        "tags":            tags or [],
        "notion_page_id":  notion_page_id,
        "last_edited_at":  last_edited_at,
        "last_synced_at":  _utc_now_iso(),
        "checksum":        new_checksum,
    }

    up = (
        supabase.table("knowledge_documents")
        .upsert(doc_payload, on_conflict="notion_page_id")
        .execute()
    )
    if not up.data:
        raise RuntimeError("Upsert failed: no data returned for knowledge_documents")
    document_id = up.data[0]["id"]

    # Overwrite chunks (content changed or it's new)
    _delete_chunks_for_document(document_id)

    chunks = chunk_text(raw_text)
    if not chunks:
        print(f"⚠️ No textual content for: {title}")
        return document_id, ("updated" if existing else "added")

    n = _insert_chunks(document_id, chunks, title, client_id, category, tags)
    print(f"✅ Synced '{title}' → {n} chunks")
    return document_id, ("updated" if existing else "added")


# ── NOTION SYNC ───────────────────────────────────────────────────────────────
def sync_notion_database(db_id: str, category: str, client_cache: Dict[str, str]) -> Tuple[set, Dict[str, int]]:
    """
    Iterate all pages in a Notion DB, pull text, and upsert in Supabase.
    Returns (seen_ids, stats) where stats has added/updated/skipped counts.
    """
    print(f"\n📚 Syncing category '{category}' (INCLUDE_TITLE_IN_EMBED={INCLUDE_TITLE_IN_EMBED})...")
    start_cursor = None
    total = 0
    seen_ids: set = set()
    stats = {"added": 0, "updated": 0, "skipped": 0}

    while True:
        args = {"database_id": db_id, "page_size": 50}
        if start_cursor:
            args["start_cursor"] = start_cursor

        res = notion.databases.query(**args)
        results = res.get("results", [])

        for page in results:
            if page.get("object") != "page":
                continue

            page_id = page["id"]
            seen_ids.add(page_id)

            props   = page.get("properties", {}) or {}
            title   = get_title_from_props(props)
            last_edited_time = page.get("last_edited_time") or _utc_now_iso()
            source_url = page.get("url")

            # Link meeting_notes to a Supabase client when possible
            client_id = None
            if category == "meeting_notes":
                client_id = resolve_client_id_from_note(props, client_cache)

            tags = None  # or pull from multi_select

            # Build raw text differently for clients vs others:
            # Clients: Description column + page body
            if category == "clients":
                desc_text = get_rich_text_prop(props, "Description")
                page_text = extract_full_page_text(page_id)
                parts: List[str] = []
                if desc_text:
                    parts.append(desc_text)
                if page_text:
                    parts.append(page_text)
                text = "\n\n".join(parts).strip()
            else:
                text = extract_full_page_text(page_id)

            if not text:
                stats["skipped"] += 1
                continue

            # Cheap pre-check to avoid heavy work when unchanged
            existing = _doc_by_notion_page_id(page_id)
            title_plus_text = f"{title}\n\n{text}".strip()
            new_checksum = _sha256(title_plus_text)
            if existing and existing.get("checksum") == new_checksum:
                print(f"✅ Skipping unchanged (checksum): {title}")
                stats["skipped"] += 1
                total += 1
                continue

            _, action = upsert_document_and_chunks(
                notion_page_id=page_id,
                title=title,
                raw_text=text,
                category=category,
                last_edited_at=last_edited_time,
                client_id=client_id,        # set for meeting_notes, None for others
                source_url=source_url,
                tags=tags,
            )
            stats[action] += 1
            total += 1

        if not res.get("has_more"):
            break
        start_cursor = res.get("next_cursor")

    print(f"🏁 Done: {category} → processed {total} pages (added={stats['added']}, updated={stats['updated']}, skipped={stats['skipped']})")
    return seen_ids, stats


# ── PRUNE ORPHANS ─────────────────────────────────────────────────────────────
def prune_orphan_documents(category: str, seen_notion_ids: set) -> int:
    """
    Delete knowledge_documents (and their chunks) for this category that no longer
    exist in the current Notion DB run (i.e., notion_page_id NOT IN seen_notion_ids).
    Returns number of documents deleted.
    """
    docs = (
        supabase.table("knowledge_documents")
        .select("id, notion_page_id")
        .eq("category", category)
        .eq("source", "notion")
        .execute()
        .data or []
    )

    to_delete_ids = [d["id"] for d in docs if d.get("notion_page_id") not in seen_notion_ids]
    if not to_delete_ids:
        print("🧹 No orphans to prune.")
        return 0

    # Delete chunks first (unless you have FK cascade)
    supabase.table("knowledge_chunks").delete().in_("document_id", to_delete_ids).execute()
    # Then delete documents
    supabase.table("knowledge_documents").delete().in_("id", to_delete_ids).execute()
    print(f"🧹 Pruned {len(to_delete_ids)} orphan documents in category '{category}'.")
    return len(to_delete_ids)


# ── RUN ALL ───────────────────────────────────────────────────────────────────
def run_full_sync():
    """
    Full sync:
      1) Sync clients table from Notion → Supabase (including website).
      2) Build client cache (Notion page id → Supabase client UUID).
      3) Sync each configured Notion DB into knowledge_documents / knowledge_chunks.
    """
    # 1) Sync clients first
    print("=== Sync: clients (Notion → Supabase) ===")
    try:
        client_summary = refresh_clients_from_notion()
        print(
            f"✅ Clients sync: "
            f"added={client_summary['added']}, "
            f"updated={client_summary['updated']}, "
            f"inactivated={client_summary['inactivated']}"
        )
    except Exception as e:
        print(f"❌ Error syncing clients: {e}")
        # You can choose to return early here if clients are critical
        # return

    # 2) Build the client cache once (Notion client page id → Supabase client UUID)
    print("\n=== Sync: knowledge (Notion DBs → RAG) ===")
    client_cache = build_client_cache()

    # 3) Sync each Notion database configured in NOTION_DATABASE_IDS
    for category, db_id in NOTION_DATABASE_IDS.items():
        if not db_id:
            print(f"⚠️ Skipping '{category}': NOTION_*_DB_ID not set")
            continue
        try:
            seen, stats = sync_notion_database(
                db_id,
                category,
                client_cache=client_cache,
            )
            deleted = prune_orphan_documents(category, seen)
            print(
                f"✅ Sync summary for '{category}': "
                f"added={stats['added']}, updated={stats['updated']}, "
                f"skipped={stats['skipped']}, deleted={deleted}"
            )
        except Exception as e:
            print(f"❌ Error syncing '{category}': {e}")


if __name__ == "__main__":
    run_full_sync()

