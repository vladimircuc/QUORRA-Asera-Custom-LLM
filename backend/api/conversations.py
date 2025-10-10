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
        "title": f"Conversation with client {client_id}",
        "created_at": datetime.now(timezone.utc).isoformat()
    }

    result = supabase.table("conversations").insert(new_conversation).execute()

    if not result.data:
        raise HTTPException(status_code=500, detail="Failed to create conversation")

    return {"status": "success", "conversation": result.data[0]}


@router.get("/{user_id}")
def list_conversations(user_id: str):
    """Fetch all conversations for a given user."""
    result = (
        supabase.table("conversations")
        .select("*")
        .eq("user_id", user_id)
        .order("created_at", desc=True)
        .execute()
    )
    return {"total": len(result.data), "conversations": result.data}
