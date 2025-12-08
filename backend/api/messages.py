# backend/api/messages.py

from typing import List, Optional

from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from supabase_client import supabase
from uuid import uuid4
from datetime import datetime, timezone
from pydantic import BaseModel

from services.llm.gpt_tool_service import generate_gpt_reply_with_tools
from services.llm.summarization import maybe_update_summary, count_tokens
from services.llm.title_generator import generate_conversation_title
from services.storage.uploads import upload_conversation_file  

router = APIRouter()


# ------------------------------
# MODELS
# ------------------------------
class MessageCreate(BaseModel):
    conversation_id: str
    content: str
    role: str | None = "user"
    user_id: str | None = None


# ------------------------------
# ENDPOINTS
# ------------------------------
@router.post("/")
def create_message(data: MessageCreate):
    """
    Insert a user message, build client context, and generate a grounded reply.
    The model can optionally call tools (rag_search_tool) up to the configured budget.
    A detailed tool audit is printed server-side and returned in `debug.tool_audit`.
    """
    if not data.user_id:
        raise HTTPException(status_code=400, detail="user_id is required")
    user_id = data.user_id

    # 1) Persist the user's message FIRST so the conversation has it in history.
    user_msg = {
        "id": str(uuid4()),
        "conversation_id": data.conversation_id,
        "user_id": user_id,
        "role": "user",
        "content": {"text": data.content},
        "tokens": count_tokens(data.content),
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    supabase.table("messages").insert(user_msg).execute()

    # 1.1) If it’s the very first user message, generate a conversation title once.
    msg_count = (
        supabase.table("messages")
        .select("id", count="exact")
        .eq("conversation_id", data.conversation_id)
        .execute()
        .count
    )
    if msg_count == 1 and data.role == "user":
        try:
            title = generate_conversation_title(data.content)
            supabase.table("conversations").update({"title": title}).eq("id", data.conversation_id).execute()
            print(f"🧠 Auto-generated conversation title: {title}")
        except Exception as e:
            print(f"⚠️ Failed to generate title: {e}")

    # 2) Resolve the conversation’s primary client (we still allow cross-client refs in answers).
    convo_result = (
        supabase.table("conversations")
        .select("client_id")
        .eq("id", data.conversation_id)
        .execute()
    )
    if not convo_result.data:
        raise HTTPException(status_code=404, detail="Conversation not found")
    client_id = convo_result.data[0]["client_id"]

    # 2.5) Check how many uploaded documents this conversation has
    upload_docs_count = (
        supabase.table("knowledge_documents")
        .select("id", count="exact")
        .eq("source", "upload")
        .eq("conversation_id", data.conversation_id)
        .execute()
        .count
    )
    has_uploaded_docs = upload_docs_count > 0

    client_result = (
        supabase.table("clients")
        .select("*")
        .eq("id", client_id)
        .execute()
    )
    if not client_result.data:
        raise HTTPException(status_code=404, detail="Client not found")
    client = client_result.data[0]
    # 3) Build the client context (QUORRA is internal; cross-client comparisons are allowed).
    products_list = ", ".join(client.get("products") or [])
    client_context = f"""
You are QUORRA, an internal Asera assistant. You may reference and compare across ANY clients when it helps answer the question accurately.

- Name: {client.get('name')}
- Status: {client.get('status')}
- Account Manager: {client.get('account_manager')}
- Priority: {client.get('priority')}
- Contact Email: {client.get('contact_email')}
- Products: {products_list}
- Service End Date: {client.get('service_end_date')}
- Description: {client.get('description')}

# Retrieval & Grounding Rules
- For adaptation/comparison: you may bring in examples from other clients; clearly name those clients and cite the snippet IDs used.
- Do not invent numbers or commitments. Only quote metrics or promises that appear in retrieved snippets.
- For client websites, first try the internal 'website' category via rag_search_tool.
- For client websites queries:
  - Only use the web_fetch_tool if the user has pasted an URL in their latest message, in most cases use the rag_search_tool with the website category.
  - Only use web_fetch_tool if BOTH:
    (1) the user explicitly asks you to read or check a URL/website, and
    (2) the domain of that URL appears in the user's latest message.
  - Do not use web_fetch_tool just because you see a Website field in context.
- Do not guess or invent URLs.
""".strip()

    # 4) Pull the current running summary (if we’ve created one already).
    summary_result = (
        supabase.table("conversation_summary")
        .select("summary")
        .eq("conversation_id", data.conversation_id)
        .execute()
    )
    summary_text = summary_result.data[0]["summary"] if summary_result.data else None

    # 5) Fetch recent history (newest→oldest) and restore chronological order for the model.
    history_result = (
        supabase.table("messages")
        .select("role, content, created_at")
        .eq("conversation_id", data.conversation_id)
        .order("created_at", desc=True)
        .limit(10)
        .execute()
    )
    history = list(reversed(history_result.data))

    # 6) Assemble GPT input
    messages = [
        {
            "role": "system",
            "content": (
                "You are QUORRA, the Asera AI assistant. "
                "Be concise, smart, and aware of past messages. "
                "Do NOT print chunk IDs or any '(source: …)' text in your answers. "
                "If no snippet supports a claim, say so briefly. "
                "You may call tools (like rag_search_tool) if you truly need more context; "
                "otherwise answer directly. "
                "You may compare across clients using internal data (SOPs, client records, meeting notes). "
                "However, when using tools to query website content, you only have access to the website "
                "data for the primary client of this conversation. "
                "If the user asks for website details about a different client, explain that this chat is "
                "scoped to the current client and that they should start a separate conversation for that other client."
            ),
        },
        {"role": "system", "content": client_context},
        {
            "role": "system",
            "content": (
                f"This conversation currently has {upload_docs_count} uploaded file(s). "
                "If this number is 0, do not use the 'upload' category in rag_search_tool, "
                "because there is nothing to retrieve yet."
            ),
        },
    ]
    if summary_text:
        messages.append({"role": "system", "content": f"Summary of previous conversation:\n{summary_text}"})

    # Include the recent history (includes the user message we saved above).
    for m in history:
        messages.append({"role": m["role"], "content": m["content"]["text"]})

    # 7) Generate GPT reply (tool-capable)
    try:
        assistant_text, tool_audit = generate_gpt_reply_with_tools(
            messages,
            tool_context={
                "primary_client_name": client.get("name"),
                "primary_client_id": client_id,            
                "primary_client_website": client.get("website"),
                "last_user_message": data.content,  
                "conversation_id": data.conversation_id,
                "has_uploaded_docs": has_uploaded_docs,
            },
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"GPT/tool generation failed: {str(e)}")

    # 8) Persist the assistant reply
    assistant_msg = {
        "id": str(uuid4()),
        "conversation_id": data.conversation_id,
        "user_id": user_id,
        "role": "assistant",
        "content": {"text": assistant_text},
        "tokens": count_tokens(assistant_text),
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    supabase.table("messages").insert(assistant_msg).execute()

    # 9) Opportunistic summary maintenance (non-fatal if it fails)
    try:
        maybe_update_summary(data.conversation_id)
    except Exception as e:
        print(f"⚠️ Summary update failed: {e}")

    # 10) Return
    return {
        "status": "success",
        "message": {"role": "assistant", "content": assistant_text},
        "client": {"name": client.get("name")},
        "debug": {"tool_audit": tool_audit},
    }


@router.get("/{conversation_id}")
def get_messages(conversation_id: str):
    """Fetch all messages for a specific conversation."""
    result = (
        supabase.table("messages")
        .select("*")
        .eq("conversation_id", conversation_id)
        .order("created_at")  # ascending
        .execute()
    )

    if not result.data:
        return {"messages": []}

    return {"total": len(result.data), "messages": result.data}

@router.post("/with-files")
async def create_message_with_files(
    conversation_id: str = Form(...),
    content: str = Form(""),
    user_id: Optional[str] = Form(None),
    files: List[UploadFile] = File(default_factory=list),
):
    """
    Create a user message that may include one or more uploaded files.
    - Saves the message in `messages`
    - Uploads each file to Supabase Storage + creates `knowledge_documents`
      and chunks+embeds it using the SAME pipeline as Notion
    - Links message <-> documents in `message_documents`
    - Runs the normal GPT + tools pipeline to generate a reply
    """
    if not user_id:
        raise HTTPException(status_code=400, detail="user_id is required")
    
    now_iso = datetime.now(timezone.utc).isoformat()

    # 1) Insert the user's message (even if content is empty and it's "just files")
    message_id = str(uuid4())
    user_msg = {
        "id": message_id,
        "conversation_id": conversation_id,
        "user_id": user_id,
        "role": "user",
        "content": {"text": content},
        "tokens": count_tokens(content or ""),
        "created_at": now_iso,
    }
    supabase.table("messages").insert(user_msg).execute()

    # 2) Resolve client_id from conversation
    convo_result = (
        supabase.table("conversations")
        .select("client_id")
        .eq("id", conversation_id)
        .execute()
    )
    if not convo_result.data:
        raise HTTPException(status_code=404, detail="Conversation not found")
    client_id = convo_result.data[0]["client_id"]


    # 3) Upload each file and link it via message_documents
    attached_docs = []

    for upload in files:
        if not upload.filename:
            continue

        file_bytes = await upload.read()

        # Upload + create document + chunk+embed (Notion-style)
        doc_id, storage_path = upload_conversation_file(
            client_id=client_id,
            conversation_id=conversation_id,
            original_filename=upload.filename,
            mime_type=upload.content_type or "application/octet-stream",
            file_bytes=file_bytes,
        )

        # Link message <-> document
        supabase.table("message_documents").insert(
            {
                "message_id": message_id,
                "document_id": doc_id,
                "created_at": now_iso,
            }
        ).execute()

        attached_docs.append(
            {"document_id": doc_id, "filename": upload.filename, "path": storage_path}
        )

    # 3.5) Re-count uploaded docs *after* this upload, so the model sees fresh state
    upload_docs_count = (
        supabase.table("knowledge_documents")
        .select("id", count="exact")
        .eq("source", "upload")
        .eq("conversation_id", conversation_id)
        .execute()
        .count
    )
    has_uploaded_docs = upload_docs_count > 0
    
    # 4) Fetch client context (same as existing create_message)
    client_result = (
        supabase.table("clients")
        .select("*")
        .eq("id", client_id)
        .execute()
    )
    if not client_result.data:
        raise HTTPException(status_code=404, detail="Client not found")
    client = client_result.data[0]

    products_list = ", ".join(client.get("products") or [])
    client_context = f"""
You are QUORRA, an internal Asera assistant. You may reference and compare across ANY clients when it helps answer the question accurately.

- Name: {client.get('name')}
- Status: {client.get('status')}
- Account Manager: {client.get('account_manager')}
- Priority: {client.get('priority')}
- Contact Email: {client.get('contact_email')}
- Products: {products_list}
- Service End Date: {client.get('service_end_date')}
- Description: {client.get('description')}

# Retrieval & Grounding Rules
- For adaptation/comparison: you may bring in examples from other clients; clearly name those clients and cite the snippet IDs used.
- Do not invent numbers or commitments. Only quote metrics or promises that appear in retrieved snippets.
- For client websites, first try the internal 'website' category via rag_search_tool.
- For client websites queries:
  - Only use the web_fetch_tool if the user has pasted an URL in their latest message, in most cases use the rag_search_tool with the website category.
  - Only use web_fetch_tool if BOTH:
    (1) the user explicitly asks you to read or check a URL/website, and
    (2) the domain of that URL appears in the user's latest message.
  - Do not use web_fetch_tool just because you see a Website field in context.
- Do not guess or invent URLs.
""".strip()

    # 5) Pull summary (if any)
    summary_result = (
        supabase.table("conversation_summary")
        .select("summary")
        .eq("conversation_id", conversation_id)
        .execute()
    )
    summary_text = summary_result.data[0]["summary"] if summary_result.data else None

    # 6) Fetch recent history (includes this new message)
    history_result = (
        supabase.table("messages")
        .select("role, content, created_at")
        .eq("conversation_id", conversation_id)
        .order("created_at", desc=True)
        .limit(10)
        .execute()
    )
    history = list(reversed(history_result.data))

    # 7) Build messages for GPT
    messages = [
        {
            "role": "system",
            "content": (
                "You are QUORRA, the Asera AI assistant. "
                "Be concise, smart, and aware of past messages. "
                "Do NOT print chunk IDs or any '(source: …)' text in your answers. "
                "If no snippet supports a claim, say so briefly. "
                "You may call tools (like rag_search_tool) if you truly need more context; "
                "otherwise answer directly. "
                "You may compare across clients using internal data (SOPs, client records, meeting notes). "
                "However, when using tools to query website content, you only have access to the website "
                "data for the primary client of this conversation. "
                "If the user asks for website details about a different client, explain that this chat is "
                "scoped to the current client and that they should start a separate conversation for that other client."
            ),
        },
        {"role": "system", "content": client_context},
        {
            "role": "system",
            "content": (
                f"This conversation currently has {upload_docs_count} uploaded file(s). "
                "If this number is 0, do not use the 'upload' category in rag_search_tool."
            ),
        },
    ]
    if summary_text:
        messages.append(
            {
                "role": "system",
                "content": f"Summary of previous conversation:\n{summary_text}",
            }
        )

    for m in history:
        messages.append({"role": m["role"], "content": m["content"]["text"]})

    # 8) Ask GPT (tools enabled, now with conversation_id in tool_context)
    try:
        assistant_text, tool_audit = generate_gpt_reply_with_tools(
            messages,
            tool_context={
                "primary_client_name": client.get("name"),
                "primary_client_id": client_id,
                "primary_client_website": client.get("website"),
                "last_user_message": content,
                "conversation_id": conversation_id,
                "has_uploaded_docs": has_uploaded_docs,
            },
        )
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"GPT/tool generation failed: {str(e)}"
        )

    # 9) Persist assistant reply
    assistant_msg = {
        "id": str(uuid4()),
        "conversation_id": conversation_id,
        "user_id": user_id,
        "role": "assistant",
        "content": {"text": assistant_text},
        "tokens": count_tokens(assistant_text),
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    supabase.table("messages").insert(assistant_msg).execute()

    # 10) Maybe update summary (non-fatal)
    try:
        maybe_update_summary(conversation_id)
    except Exception as e:
        print(f"⚠️ Summary update failed: {e}")

    return {
        "status": "success",
        "message": {"role": "assistant", "content": assistant_text},
        "client": {"name": client.get("name")},
        "debug": {
            "tool_audit": tool_audit,
            "attached_documents": attached_docs,
        },
    }