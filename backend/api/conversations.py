from fastapi import APIRouter, HTTPException
from supabase_client import supabase
from uuid import uuid4
from datetime import datetime, timezone
from pydantic import BaseModel

router = APIRouter()

class ConversationCreate(BaseModel):
    client_id: str
    user_id: str | None = None  # optional for now

@router.post("/")
def create_conversation(data: ConversationCreate):
    """Create a new conversation for a given client (and optionally a user)."""
    client_id = data.client_id
    user_id = data.user_id or "11111111-2222-3333-4444-555555555555"

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
