# backend/api/messages.py
from fastapi import APIRouter, HTTPException
from supabase_client import supabase
from uuid import uuid4
from datetime import datetime, timezone
from pydantic import BaseModel

from services.gpt_tool_service import generate_gpt_reply_with_tools
from services.summarization_service import maybe_update_summary
from services.title_generator import generate_conversation_title
from services.summarization_service import count_tokens

router = APIRouter()

DUMMY_USER_ID = "11111111-2222-3333-4444-555555555555"


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
    user_id = data.user_id or DUMMY_USER_ID

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
- If the user asks what happened/what we promised: prefer meeting_notes (when available). If none support the claim, say so briefly and base guidance on SOPs/playbooks.
- For how-to/process questions: prefer SOPs/playbooks/templates.
- For adaptation/comparison: you may bring in examples from other clients; clearly name those clients and cite the snippet IDs used.
- Do not invent numbers or commitments. Only quote metrics or promises that appear in retrieved snippets.
- When adapting insights to the Primary Client, consider their segment, budget tier, geo, KPIs, and constraints.
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
                "otherwise answer directly."
            ),
        },
        {"role": "system", "content": client_context},
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
            tool_context={"primary_client_name": client.get("name")},
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
