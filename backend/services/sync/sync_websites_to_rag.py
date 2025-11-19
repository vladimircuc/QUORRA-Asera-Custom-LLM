import os
import hashlib
from datetime import datetime, timezone
from typing import List, Dict, Any, Set, Tuple
from collections import deque
from urllib.parse import urlparse, urljoin, urldefrag

import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from openai import OpenAI

from supabase_client import supabase

# -----------------------------------------------------------------------------
# ENV + CONFIG
# -----------------------------------------------------------------------------
load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise RuntimeError("OPENAI_API_KEY is not set in .env")

# Crawling knobs (from .env, with your defaults)
MAX_DEPTH = int(os.getenv("WEBSITE_MAX_DEPTH", "2"))
MAX_PAGES = int(os.getenv("WEBSITE_MAX_PAGES", "25"))

# Embeddings
EMBED_MODEL = "text-embedding-3-small"
_oai = OpenAI(api_key=OPENAI_API_KEY)

# Chunking
MAX_CHARS_PER_CHUNK = 2000  # rough ~500 tokens

# Simple blacklist for junk URLs
BLACKLIST_SUBSTRINGS = (
    "/login",
    "/cart",
    "/checkout",
    "/wp-admin",
    "/account",
    "/privacy",
    "/terms",
    "/cookies",
)


# -----------------------------------------------------------------------------
# Logging helper
# -----------------------------------------------------------------------------
def log(msg: str) -> None:
    print(msg, flush=True)


# -----------------------------------------------------------------------------
# HTML parsing helpers
# -----------------------------------------------------------------------------
def extract_title_and_text(html: str) -> Tuple[str, str]:
    """
    Extract a page title and main-ish text from HTML using BeautifulSoup.
    Not perfect, but good enough for v1.
    """
    soup = BeautifulSoup(html, "html.parser")

    # Remove obviously-noisy tags
    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()

    # Try to focus on <main>, then fall back to body
    main = soup.find("main") or soup.body or soup

    # Title: <title> or first <h1>
    title = ""
    if soup.title and soup.title.string:
        title = soup.title.string.strip()
    else:
        h1 = soup.find("h1")
        if h1:
            title = h1.get_text(strip=True)

    # Collect text from headings, paragraphs, list items, etc.
    texts: List[str] = []
    for tag in main.find_all(["h1", "h2", "h3", "p", "li"]):
        text = tag.get_text(" ", strip=True)
        if text:
            texts.append(text)

    full_text = "\n".join(texts)
    return title, full_text.strip()


# -----------------------------------------------------------------------------
# Crawling helpers
# -----------------------------------------------------------------------------
def is_same_site(root: str, candidate: str) -> bool:
    """Return True if candidate URL is on the same domain & scheme as root."""
    p_root = urlparse(root)
    p_cand = urlparse(candidate)
    if not p_cand.scheme.startswith("http"):
        return False
    return p_root.scheme == p_cand.scheme and p_root.netloc == p_cand.netloc


def is_blacklisted(path: str) -> bool:
    path_lower = path.lower()
    return any(bad in path_lower for bad in BLACKLIST_SUBSTRINGS)


def normalize_url(base: str, href: str) -> str:
    """Convert relative href to absolute, strip fragments."""
    abs_url = urljoin(base, href)
    abs_url, _frag = urldefrag(abs_url)
    return abs_url


def crawl_site(root_url: str, max_depth: int, max_pages: int) -> List[Dict[str, str]]:
    """
    BFS crawl starting from root_url, limited by depth and page count.
    Returns a list of {url, title, text}.
    """
    log(f"  🌐 Starting crawl at {root_url} (depth <= {max_depth}, pages <= {max_pages})")

    visited: Set[str] = set()
    results: List[Dict[str, str]] = []
    queue: deque[Tuple[str, int]] = deque()
    queue.append((root_url, 0))

    root_parsed = urlparse(root_url)

    session = requests.Session()
    session.headers.update({
        "User-Agent": "QUORRA-WebsiteSync/1.0 (+https://asera.ai)"
    })

    while queue and len(results) < max_pages:
        url, depth = queue.popleft()

        if url in visited:
            continue
        if depth > max_depth:
            continue

        visited.add(url)
        log(f"    🔎 [depth={depth}] Fetching: {url}")

        try:
            resp = session.get(url, timeout=10)
        except Exception as e:
            log(f"    ⚠️  Error fetching {url}: {e}")
            continue

        if resp.status_code >= 400:
            log(f"    ⚠️  Skipping {url}: HTTP {resp.status_code}")
            continue

        content_type = resp.headers.get("Content-Type", "")
        if "text/html" not in content_type:
            log(f"    ⚠️  Skipping {url}: non-HTML content ({content_type})")
            continue

        title, text = extract_title_and_text(resp.text)

        # Skip tiny/empty pages
        if len(text) < 300:
            log(f"    ⚠️  Skipping {url}: too little text ({len(text)} chars)")
        else:
            results.append({
                "url": url,
                "title": title or url,
                "text": text,
            })
            log(f"    ✅ Parsed page: '{title or url}' ({len(text)} chars)")

        # Discover new links if we still have crawling budget
        if depth < max_depth and len(results) < max_pages:
            soup = BeautifulSoup(resp.text, "html.parser")
            for a in soup.find_all("a", href=True):
                href = a["href"]
                # Ignore javascript/mailto/etc.
                if href.startswith("#") or href.startswith("mailto:") or href.startswith("tel:"):
                    continue
                abs_url = normalize_url(url, href)
                parsed = urlparse(abs_url)
                if not is_same_site(root_url, abs_url):
                    continue
                if is_blacklisted(parsed.path):
                    continue
                if abs_url not in visited:
                    queue.append((abs_url, depth + 1))

    log(f"  📄 Crawl finished: {len(results)} pages kept.")
    return results


# -----------------------------------------------------------------------------
# Chunking + embeddings
# -----------------------------------------------------------------------------
def split_into_chunks(text: str, max_chars: int = MAX_CHARS_PER_CHUNK) -> List[str]:
    """
    Simple paragraph-based chunking: group paragraphs until char budget is hit.
    """
    paragraphs = [p.strip() for p in text.split("\n") if p.strip()]
    chunks: List[str] = []
    current = ""

    for p in paragraphs:
        if not current:
            current = p
        elif len(current) + len(p) + 1 <= max_chars:
            current = current + "\n" + p
        else:
            chunks.append(current)
            current = p

    if current:
        chunks.append(current)

    return chunks


def embed_texts(texts: List[str]) -> List[List[float]]:
    """
    Batch-embed a list of texts with OpenAI.
    """
    if not texts:
        return []

    resp = _oai.embeddings.create(
        model=EMBED_MODEL,
        input=texts,
    )
    return [item.embedding for item in resp.data]


# -----------------------------------------------------------------------------
# Supabase upsert helpers
# -----------------------------------------------------------------------------
def upsert_page_for_client(
    client_id: str,
    page: Dict[str, str],
    now: datetime,
) -> None:
    """
    Upsert one website page into knowledge_documents + knowledge_chunks.
    """
    url = page["url"]
    title = page["title"]
    text = page["text"]
    checksum = hashlib.sha256(text.encode("utf-8")).hexdigest()

    # Fetch existing doc for this client + URL + category='website'
    existing_docs = (
        supabase.table("knowledge_documents")
        .select("id, checksum")
        .eq("client_id", client_id)
        .eq("category", "website")
        .eq("source_url", url)
        .execute()
        .data
    )

    doc_id = None
    status = ""

    if existing_docs:
        doc = existing_docs[0]
        doc_id = doc["id"]
        old_checksum = doc.get("checksum")

        if old_checksum == checksum:
            status = "unchanged"
            log(f"    ▫️  Doc unchanged, keeping chunks: {url}")
        else:
            status = "updated"
            log(f"    ✏️  Updating existing website doc: {url}")
            supabase.table("knowledge_documents").update({
                "title": title,
                "raw_text": text,
                "checksum": checksum,
                "updated_at": now.isoformat(),
                "last_synced_at": now.isoformat(),
            }).eq("id", doc_id).execute()
    else:
        status = "new"
        log(f"    ➕ Inserting new website doc: {url}")
        insert_resp = supabase.table("knowledge_documents").insert({
            "source": "manual",              # keep within CHECK
            "source_id": None,
            "source_url": url,
            "title": title,
            "raw_text": text,
            "summary": None,
            "client_id": client_id,
            "category": "website",
            "tags": ["website"],
            "notion_page_id": None,
            "last_edited_at": now.isoformat(),
            "last_synced_at": now.isoformat(),
            "checksum": checksum,
        }).execute()
        if not insert_resp.data:
            log("    ❌ Failed to insert knowledge_document")
            return
        doc_id = insert_resp.data[0]["id"]

    # If unchanged, we can skip re-chunking to save tokens (optional).
    # For v1, we'll re-chunk only on new/updated:
    if status in ("new", "updated"):
        # Delete existing chunks for this doc
        supabase.table("knowledge_chunks").delete().eq("document_id", doc_id).execute()

        chunks = split_into_chunks(text)
        embeddings = embed_texts(chunks)
        rows = []
        for idx, (chunk_text, emb) in enumerate(zip(chunks, embeddings)):
            rows.append({
                "document_id": doc_id,
                "chunk_index": idx,
                "content": chunk_text,
                "tokens": len(chunk_text.split()),
                "embedding": emb,
                "client_id": client_id,
                "category": "website",
                "tags": ["website"],
            })

        if rows:
            supabase.table("knowledge_chunks").insert(rows).execute()
            log(f"    🧩 Stored {len(rows)} chunks for doc: {url}")
        else:
            log(f"    ⚠️ No chunks produced for doc: {url}")


# -----------------------------------------------------------------------------
# Cleanup: remove website docs/chunks for invalid clients
# -----------------------------------------------------------------------------
def cleanup_orphan_website_docs() -> None:
    """
    Delete website documents + chunks for:
      - clients that no longer exist, OR
      - clients that exist but no longer have a website or are inactive.
    """
    log("=== Cleanup: website docs for invalid/missing clients ===")

    # All clients with their website + status
    clients_res = (
        supabase.table("clients")
        .select("id, website, status")
        .execute()
    )
    clients = clients_res.data or []
    client_index: Dict[str, Dict[str, Any]] = {c["id"]: c for c in clients}

    # All website documents
    docs_res = (
        supabase.table("knowledge_documents")
        .select("id, client_id, source_url")
        .eq("category", "website")
        .execute()
    )
    docs = docs_res.data or []

    delete_doc_ids: List[str] = []

    for doc in docs:
        cid = doc.get("client_id")
        if not cid or cid not in client_index:
            # client missing entirely
            delete_doc_ids.append(doc["id"])
            continue

        c = client_index[cid]
        website = c.get("website")
        status = (c.get("status") or "").lower()

        if not website or status == "inactive":
            delete_doc_ids.append(doc["id"])

    if not delete_doc_ids:
        log("  ✅ No orphan website docs to delete.")
        return

    log(f"  🗑  Deleting {len(delete_doc_ids)} website docs (and their chunks).")

    # Delete chunks first (FK)
    for doc_id in delete_doc_ids:
        supabase.table("knowledge_chunks").delete().eq("document_id", doc_id).execute()
        supabase.table("knowledge_documents").delete().eq("id", doc_id).execute()

    log("  ✅ Cleanup finished.")


# -----------------------------------------------------------------------------
# Main sync driver
# -----------------------------------------------------------------------------
def sync_websites_to_rag() -> None:
    """
    Main entrypoint:
      - Fetch clients with websites
      - Crawl their sites
      - Upsert website pages into knowledge_documents + knowledge_chunks
      - Cleanup invalid website docs
    """
    log("=== Website → RAG sync started ===")
    log(f"Config: MAX_DEPTH={MAX_DEPTH}, MAX_PAGES={MAX_PAGES}")

    # Fetch all clients and filter in Python for clarity
    res = (
        supabase.table("clients")
        .select("id, name, website, status")
        .execute()
    )
    clients = res.data or []

    valid_clients = [
        c for c in clients
        if c.get("website") and (c.get("status") or "").lower() != "inactive"
    ]

    if not valid_clients:
        log("⚠️ No active clients with website set. Nothing to do.")
        return

    log(f"Found {len(valid_clients)} active clients with websites.")

    now = datetime.now(timezone.utc)

    for client in valid_clients:
        client_id = client["id"]
        name = client.get("name") or client_id
        website = client.get("website")

        log("\n" + "=" * 70)
        log(f"🏢 Client: {name} ({client_id})")
        log(f"🌍 Website: {website}")

        try:
            pages = crawl_site(website, max_depth=MAX_DEPTH, max_pages=MAX_PAGES)
        except Exception as e:
            log(f"❌ Error crawling {website}: {e}")
            continue

        if not pages:
            log("  ⚠️ No pages extracted for this website.")
            continue

        log(f"  📚 Upserting {len(pages)} page(s) into RAG…")

        for page in pages:
            try:
                upsert_page_for_client(client_id, page, now)
            except Exception as e:
                log(f"    ❌ Error upserting page {page['url']}: {e}")

    # Cleanup orphan docs
    log("\n" + "=" * 70)
    cleanup_orphan_website_docs()

    log("\n=== Website → RAG sync completed ===")


if __name__ == "__main__":
    sync_websites_to_rag()
