# backend/api/conversations.py

from fastapi import APIRouter, HTTPException
from supabase_client import supabase
from uuid import uuid4
from datetime import datetime
from pydantic import BaseModel

router = APIRouter()  

class ConversationCreate(BaseModel):
    client_id: str
    user_id: str

@router.post("/conversations")
def create_conversation(data: ConversationCreate):
    client_id = data.client_id
    user_id = data.user_id

    context_versions = supabase \
        .table("client_context_versions") \
        .select("*") \
        .eq("client_id", client_id) \
        .order("created_at", desc=True) \
        .limit(1) \
        .execute()

    if context_versions.data:
        context_version_id = context_versions.data[0]["id"]
    else:
        raise HTTPException(status_code=400, detail="No client context version exists for this client")

    result = supabase \
        .table("conversations") \
        .insert({
            "id": str(uuid4()),
            "user_id": user_id,
            "client_id": client_id,
            "context_version_id": context_version_id,
            "created_at": datetime.utcnow()
        }) \
        .execute()

    return result.data[0]