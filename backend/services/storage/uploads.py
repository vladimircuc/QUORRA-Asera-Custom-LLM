# backend/services/storage/uploads.py

from __future__ import annotations

import os
import re
import io
from datetime import datetime, timezone
from typing import Tuple

from supabase_client import supabase

# Reuse the SAME chunking + embedding logic as Notion sync
from services.sync.sync_notion_to_rag import (
    chunk_text,
    _insert_chunks,   # private, but it's okay to import
    _sha256,
    _utc_now_iso,
)

# Optional PDF / DOCX parsers
try:
    from pypdf import PdfReader
except ImportError:
    PdfReader = None  # we'll handle gracefully
try:
    import docx  # from python-docx
except ImportError:
    docx = None

UPLOADS_BUCKET = os.getenv("UPLOADS_BUCKET", "uploads")


def _safe_filename(name: str) -> str:
    name = name.strip().replace(" ", "_")
    return re.sub(r"[^A-Za-z0-9._-]", "_", name)


def _extract_text_from_bytes(filename: str, data: bytes) -> str:
    """
    Extract text from uploaded file bytes.

    Supported for now:
      - .txt, .md, .csv, .log  → UTF-8 decode
      - .pdf                   → via pypdf (if installed)
      - .docx                  → via python-docx (if installed)

    Everything else returns "" for now (you can add OCR/Image later).
    """
    lower = (filename or "").lower()

    # 1) Plain text-ish
    if lower.endswith((".txt", ".md", ".csv", ".log")):
        try:
            return data.decode("utf-8", errors="ignore")
        except Exception:
            return ""

    # 2) PDF
    if lower.endswith(".pdf"):
        if not PdfReader:
            print("⚠️ PdfReader (pypdf) not installed; cannot parse PDF.")
            return ""
        try:
            reader = PdfReader(io.BytesIO(data))
            parts = []
            for page in reader.pages:
                txt = page.extract_text() or ""
                if txt.strip():
                    parts.append(txt)
            return "\n\n".join(parts).strip()
        except Exception as e:
            print(f"⚠️ PDF extract error for {filename}: {e}")
            return ""

    # 3) DOCX (modern Word)
    if lower.endswith(".docx"):
        if not docx:
            print("⚠️ python-docx (docx) not installed; cannot parse DOCX.")
            return ""
        try:
            document = docx.Document(io.BytesIO(data))
            parts = []
            for para in document.paragraphs:
                txt = para.text or ""
                if txt.strip():
                    parts.append(txt)
            return "\n".join(parts).strip()
        except Exception as e:
            print(f"⚠️ DOCX extract error for {filename}: {e}")
            return ""

    # 4) Old .doc (not really supported here)
    if lower.endswith(".doc"):
        # You could integrate textract / antiword / unoconv later if you need this.
        print(f"⚠️ .doc format not supported yet for {filename}.")
        return ""

    # 5) Everything else (images, etc.) → empty for now
    return ""


def upload_conversation_file(
    *,
    client_id: str,
    conversation_id: str,
    original_filename: str,
    mime_type: str,
    file_bytes: bytes,
) -> Tuple[str, str]:
    """
    Uploads a file to Supabase Storage AND creates a knowledge_documents row
    AND immediately chunks/embeds it using the SAME logic as Notion sync
    (chunk_text + _insert_chunks).

    Returns: (document_id, storage_path)
    """
    now = datetime.now(timezone.utc)
    timestamp = now.strftime("%Y%m%d-%H%M%S")
    safe_name = _safe_filename(original_filename or "upload.bin")

    storage_path = f"{conversation_id}/{timestamp}_{safe_name}"

    # 1) Upload file to Supabase Storage
    res = supabase.storage.from_(UPLOADS_BUCKET).upload(
        path=storage_path,
        file=file_bytes,
        file_options={"content-type": mime_type},
    )
    if isinstance(res, dict) and res.get("error"):
        raise RuntimeError(f"Failed to upload file to storage: {res['error']}")

    # 2) Extract raw text from the file bytes for RAG
    raw_text = _extract_text_from_bytes(original_filename, file_bytes)

    # 3) Create knowledge_documents row
    title = original_filename or "Uploaded file"
    title_plus_text = f"{title}\n\n{raw_text}".strip()
    checksum = _sha256(title_plus_text) if raw_text else None
    tags = ["upload", mime_type]

    doc_payload = {
        "source": "upload",
        "source_id": original_filename,
        "source_url": storage_path,
        "title": title,
        "raw_text": raw_text,
        "summary": None,
        "client_id": client_id,
        "category": "upload",
        "tags": tags,
        "notion_page_id": None,
        "conversation_id": conversation_id,
        "last_edited_at": _utc_now_iso(),
        "last_synced_at": _utc_now_iso(),
        "checksum": checksum,
    }

    insert_res = supabase.table("knowledge_documents").insert(doc_payload).execute()
    if not insert_res.data:
        raise RuntimeError("Insert failed for knowledge_documents")
    doc_row = insert_res.data[0]
    document_id = doc_row["id"]

    # 4) If we got any text, chunk + embed using the SAME logic as Notion
    if raw_text:
        chunks = chunk_text(raw_text)
        if chunks:
            _insert_chunks(
                document_id=document_id,
                chunks=chunks,
                title=title,
                client_id=client_id,
                category="upload",
                tags=tags,
            )

    return document_id, storage_path
