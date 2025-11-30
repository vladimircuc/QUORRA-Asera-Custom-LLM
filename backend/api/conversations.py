from fastapi import APIRouter, HTTPException
from supabase_client import supabase
from uuid import uuid4
from datetime import datetime, timezone
from pydantic import BaseModel

router = APIRouter()

class ConversationCreate(BaseModel):
    client_id: str
    user_id: str | None = None  # optional for now

class ConversationRename(BaseModel):
    title: str


@router.post("/")
def create_conversation(data: ConversationCreate):
    """Create a new conversation for a given client (and optionally a user)."""
    client_id = data.client_id
    if not data.user_id:
        raise HTTPException(status_code=400, detail="user_id is required")
    user_id = data.user_id

    client_check = supabase.table("clients").select("id").eq("id", client_id).execute()
    if not client_check.data:
        raise HTTPException(status_code=404, detail="Client not found")

    new_conversation = {
        "id": str(uuid4()),
        "user_id": user_id,
        "client_id": client_id,
        "title": "Untitled Conversation",
        "created_at": datetime.now(timezone.utc).isoformat()
    }

    result = supabase.table("conversations").insert(new_conversation).execute()

    if not result.data:
        raise HTTPException(status_code=500, detail="Failed to create conversation")

    return {"status": "success", "conversation": result.data[0]}



@router.get("/{user_id}")
def list_conversations(user_id: str):
    """Fetch all conversations for a given user and delete any that have no messages."""
    # 1️⃣ Get all conversations
    result = (
        supabase.table("conversations")
        .select("id, title, created_at, client_id, user_id")
        .eq("user_id", user_id)
        .order("created_at", desc=True)
        .execute()
    )
    conversations = result.data or []

    # 2️⃣ Track empty conversations
    empty_convos = []

    for convo in conversations:
        msg_check = (
            supabase.table("messages")
            .select("id", count="exact")
            .eq("conversation_id", convo["id"])
            .execute()
        )

        # Supabase returns count in msg_check.count
        if getattr(msg_check, "count", 0) == 0:
            empty_convos.append(convo["id"])

    # 3️⃣ Delete empty conversations
    for convo_id in empty_convos:
        supabase.table("conversations").delete().eq("id", convo_id).execute()

    # 4️⃣ Return only active conversations
    active_convos = [c for c in conversations if c["id"] not in empty_convos]

    return {"total": len(active_convos), "conversations": active_convos}

@router.delete("/{conversation_id}")
def delete_conversation(conversation_id: str):
    """
    Delete a conversation and its related data:
    - messages
    - conversation_summary
    - message_documents links
    - knowledge_documents with source='upload' for this conversation
    - knowledge_chunks for those upload documents

    Notion / global docs (meeting_notes, sops, etc.) are NOT deleted.
    """
    # 0) Check conversation exists
    convo_res = (
        supabase.table("conversations")
        .select("id")
        .eq("id", conversation_id)
        .execute()
    )
    if not convo_res.data:
        raise HTTPException(status_code=404, detail="Conversation not found")

    # 1) Get all messages in this conversation (for cleaning message_documents)
    msg_res = (
        supabase.table("messages")
        .select("id")
        .eq("conversation_id", conversation_id)
        .execute()
    )
    message_ids = [m["id"] for m in (msg_res.data or [])]

    # 2) Get upload documents attached to this conversation
    doc_res = (
        supabase.table("knowledge_documents")
        .select("id")
        .eq("conversation_id", conversation_id)
        .eq("source", "upload")
        .execute()
    )
    upload_doc_ids = [d["id"] for d in (doc_res.data or [])]

    # 3) Delete message_documents links (by message and by document)
    if message_ids:
        supabase.table("message_documents").delete().in_("message_id", message_ids).execute()
    if upload_doc_ids:
        supabase.table("message_documents").delete().in_("document_id", upload_doc_ids).execute()

    # 4) Delete chunks for upload documents
    if upload_doc_ids:
        supabase.table("knowledge_chunks").delete().in_("document_id", upload_doc_ids).execute()

    # 5) Delete upload documents themselves
    if upload_doc_ids:
        supabase.table("knowledge_documents").delete().in_("id", upload_doc_ids).execute()

    # 6) Delete conversation summary (if any)
    supabase.table("conversation_summary").delete().eq("conversation_id", conversation_id).execute()

    # 7) Delete messages
    supabase.table("messages").delete().eq("conversation_id", conversation_id).execute()

    # 8) Finally, delete the conversation row
    supabase.table("conversations").delete().eq("id", conversation_id).execute()

    return {"status": "success", "conversation_id": conversation_id}

@router.patch("/{conversation_id}/title")
def rename_conversation(conversation_id: str, data: ConversationRename):
    """
    Rename an existing conversation.
    """
    update_res = (
        supabase.table("conversations")
        .update({"title": data.title})
        .eq("id", conversation_id)
        .execute()
    )

    if not update_res.data:
        raise HTTPException(status_code=404, detail="Conversation not found")

    return {
        "status": "success",
        "conversation": update_res.data[0],
    }
