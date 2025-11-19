"""
Live web fetch tool callable by the LLM.

- Given an explicit URL, fetch the page over HTTP.
- Strip HTML → clean text, truncate to a safe length.
- Return {ok, url, title, content, error} as JSON for the model.
- Designed to be used *after* internal RAG, when fresh page info is needed.
"""

from __future__ import annotations
import json
import os
from typing import Any, Dict, Optional
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup

TOOL_NAME = "web_fetch_tool"

# Config knobs (override via .env if you want)
DEFAULT_MAX_CHARS = int(os.getenv("WEB_FETCH_MAX_CHARS", "6000"))
REQUEST_TIMEOUT = float(os.getenv("WEB_FETCH_TIMEOUT", "5.0"))  # seconds
USER_AGENT = os.getenv(
    "WEB_FETCH_USER_AGENT",
    "QUORRA-WebFetch/1.0 (+https://example.com)"
)


def get_tool_definition() -> Dict[str, Any]:
    """OpenAI tool schema."""
    return {
        "type": "function",
        "function": {
            "name": TOOL_NAME,
            "description": (
                "Fetch the contents of a specific web page when you have an explicit URL. "
                "Use this only when you need the latest information from that page. "
                "Prefer internal knowledge (RAG) when it's sufficient. "
                "Do NOT invent or guess URLs. Only use URLs that the user explicitly mentioned "
                "in their latest message (for example, a link they pasted or a domain they wrote)."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "url": {
                        "type": "string",
                        "description": (
                            "The full URL of the web page to fetch. "
                            "Must start with http:// or https://."
                        ),
                    },
                    "max_chars": {
                        "type": "integer",
                        "description": (
                            f"Optional maximum number of characters of cleaned text to return "
                            f"(default {DEFAULT_MAX_CHARS})."
                        ),
                    },
                },
                "required": ["url"],
            },
        },
    }


def _normalize_url(url: str) -> str:
    """Ensure URL has a scheme; default to https:// if missing."""
    url = (url or "").strip()
    if not url:
        return url

    if url.startswith("http://") or url.startswith("https://"):
        return url

    # If there is no scheme at all, assume https
    if "://" not in url:
        return "https://" + url

    return url


def _extract_text_from_html(html: str) -> tuple[str, str]:
    """
    Extract (title, text) from HTML.
    - Drop script/style/noscript.
    - Prefer <body> but fall back to full document.
    - Normalize whitespace and blank lines.
    """
    soup = BeautifulSoup(html or "", "html.parser")

    # Kill obvious non-content
    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()

    # Title
    title = ""
    if soup.title and soup.title.string:
        title = soup.title.string.strip()

    # Main text (body if present)
    node = soup.body or soup
    raw_text = node.get_text(separator="\n")

    # Normalize whitespace
    lines = [line.strip() for line in (raw_text or "").splitlines()]
    lines = [ln for ln in lines if ln]  # drop empty
    text = "\n".join(lines)

    return title, text


def run(raw_args: str, *, tool_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Execute the web fetch tool.

    Returns a dict:
      - "json": JSON string sent back to the LLM
      - "meta": server-side logging info (url, status, length, ok, error)
      - "effective_args": the final args we executed
    """
    tool_context = tool_context or {}

    # Parse arguments
    try:
        args = json.loads(raw_args) if isinstance(raw_args, str) else dict(raw_args or {})
    except Exception:
        args = {}

    url_raw = (args.get("url") or "").strip()
    max_chars = int(args.get("max_chars") or DEFAULT_MAX_CHARS)

    url = _normalize_url(url_raw)
    effective_args = {"url": url, "max_chars": max_chars}

    # Early validation
    if not url:
        err = "No URL provided."
        print(f"🌐 WEB(tool) error: {err}")
        result_to_model = {
            "ok": False,
            "url": url_raw,
            "title": "",
            "content": "",
            "error": err,
        }
        return {
            "json": json.dumps(result_to_model, ensure_ascii=False),
            "meta": {"ok": False, "error": err, **effective_args},
            "effective_args": effective_args,
        }

    if not (url.startswith("http://") or url.startswith("https://")):
        err = f"Invalid URL scheme for '{url_raw}'."
        print(f"🌐 WEB(tool) error: {err}")
        result_to_model = {
            "ok": False,
            "url": url_raw,
            "title": "",
            "content": "",
            "error": err,
        }
        return {
            "json": json.dumps(result_to_model, ensure_ascii=False),
            "meta": {"ok": False, "error": err, **effective_args},
            "effective_args": effective_args,
        }

    # Fetch + parse
    try:
        print(f"🌐 WEB(tool): fetching {url} (timeout={REQUEST_TIMEOUT}s)")
        resp = requests.get(
            url,
            timeout=REQUEST_TIMEOUT,
            headers={"User-Agent": USER_AGENT},
        )
        status = resp.status_code

        if not (200 <= status < 300):
            err = f"Non-2xx status code: {status}"
            print(f"🌐 WEB(tool) error: {err}")
            result_to_model = {
                "ok": False,
                "url": url,
                "title": "",
                "content": "",
                "error": err,
            }
            return {
                "json": json.dumps(result_to_model, ensure_ascii=False),
                "meta": {
                    "ok": False,
                    "error": err,
                    "status_code": status,
                    "content_length": len(resp.content or b""),
                    **effective_args,
                },
                "effective_args": effective_args,
            }

        html = resp.text or ""
        title, text = _extract_text_from_html(html)
        original_len = len(text)

        if original_len > max_chars:
            text = text[:max_chars] + "…"

        print(
            f"🌐 WEB(tool): fetched {url} | status={status} | "
            f"chars={original_len} -> returned={len(text)}"
        )

        result_to_model = {
            "ok": True,
            "url": url,
            "title": title,
            "content": text,
            "error": None,
        }

        meta = {
            "ok": True,
            "status_code": status,
            "content_length": len(resp.content or b""),
            "text_length_original": original_len,
            "text_length_returned": len(text),
            **effective_args,
        }

        return {
            "json": json.dumps(result_to_model, ensure_ascii=False),
            "meta": meta,
            "effective_args": effective_args,
        }

    except Exception as e:
        err = f"Exception while fetching URL: {e}"
        print(f"🌐 WEB(tool) exception: {err}")
        result_to_model = {
            "ok": False,
            "url": url,
            "title": "",
            "content": "",
            "error": err,
        }
        return {
            "json": json.dumps(result_to_model, ensure_ascii=False),
            "meta": {"ok": False, "error": err, **effective_args},
            "effective_args": effective_args,
        }
