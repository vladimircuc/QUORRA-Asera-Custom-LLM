from fastapi import APIRouter, HTTPException
from supabase_client import supabase
from uuid import uuid4
from datetime import datetime
from pydantic import BaseModel

router = APIRouter()

DUMMY_USER_ID = "11111111-2222-3333-4444-555555555555"

# ------------------------------
# MODELS
# ------------------------------
class MessageCreate(BaseModel):
    conversation_id: str
    content: str
    role: str | None = "user"  # default "user"
    user_id: str | None = None


# ------------------------------
# ENDPOINTS
# ------------------------------

@router.post("/messages")
def create_message(data: MessageCreate):
    """Insert a new message into the conversation."""
    user_id = data.user_id or DUMMY_USER_ID

    message_data = {
        "id": str(uuid4()),
        "conversation_id": data.conversation_id,
        "user_id": user_id,
        "role": data.role or "user",
        "content": {"text": data.content},
        "tokens": None,
        "created_at": datetime.utcnow()
    }

    result = supabase.table("messages").insert(message_data).execute()

    if not result.data:
        raise HTTPException(status_code=400, detail="Failed to insert message")

    return {"status": "success", "message": result.data[0]}


@router.get("/messages/{conversation_id}")
def get_messages(conversation_id: str):
    """Fetch all messages for a specific conversation."""
    result = (
        supabase.table("messages")
        .select("*")
        .eq("conversation_id", conversation_id)
        .order("created_at", asc=True)
        .execute()
    )

    if not result.data:
        return {"messages": []}

    return {"total": len(result.data), "messages": result.data}
