from fastapi import APIRouter, HTTPException
from supabase_client import supabase
from uuid import uuid4
from datetime import datetime
from pydantic import BaseModel

router = APIRouter()

class MessageCreate(BaseModel):
    conversation_id: str
    user_id: str
    role: str   # "user" or "assistant"
    content: dict  # JSON object
    tokens: int | None = None

@router.post("/messages")
def create_message(data: MessageCreate):
    result = supabase.table("messages").insert({
        "id": str(uuid4()),
        "conversation_id": data.conversation_id,
        "user_id": data.user_id,
        "role": data.role,
        "content": data.content,
        "tokens": data.tokens,
        "created_at": datetime.utcnow()
    }).execute()

    if not result.data:
        raise HTTPException(status_code=400, detail="Failed to insert message")

    return result.data[0]


@router.get("/messages/{conversation_id}")
def get_messages(conversation_id: str):
    result = supabase.table("messages") \
        .select("*") \
        .eq("conversation_id", conversation_id) \
        .order("created_at", asc=True) \
        .execute()

    return result.data
