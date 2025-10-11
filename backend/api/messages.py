from fastapi import APIRouter, HTTPException
from supabase_client import supabase
from uuid import uuid4
from datetime import datetime, timezone
from pydantic import BaseModel
from services.gpt_service import generate_gpt_reply
from services.summarization_service import maybe_update_summary  


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

@router.post("/")
def create_message(data: MessageCreate):
    """Insert a user message, load client context, and generate GPT reply."""
    user_id = data.user_id or DUMMY_USER_ID

    # 1️⃣ Save the user message
    user_msg = {
        "id": str(uuid4()),
        "conversation_id": data.conversation_id,
        "user_id": user_id,
        "role": "user",
        "content": {"text": data.content},
        "tokens": None,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    supabase.table("messages").insert(user_msg).execute()

    # 2️⃣ Fetch client info
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

    # 3️⃣ Build client context
    products_list = ", ".join(client.get("products") or [])
    client_context = f"""
        This conversation is about the following client:

        - Name: {client.get('name')}
        - Status: {client.get('status')}
        - Account Manager: {client.get('account_manager')}
        - Priority: {client.get('priority')}
        - Contact Email: {client.get('contact_email')}
        - Products: {products_list}
        - Service End Date: {client.get('service_end_date')}
        - Description: {client.get('description')}

        Always keep this information in mind when answering.
        Never discuss other clients.
    """.strip()

    # 4️⃣ Load summary if it exists
    summary_result = (
        supabase.table("conversation_summary")
        .select("summary")
        .eq("conversation_id", data.conversation_id)
        .execute()
    )
    summary_text = summary_result.data[0]["summary"] if summary_result.data else None

    # 5️⃣ Fetch last few messages
    history_result = (
        supabase.table("messages")
        .select("role, content")
        .eq("conversation_id", data.conversation_id)
        .order("created_at")
        .limit(10)
        .execute()
    )

    # 6️⃣ Assemble GPT input in correct order
    messages = [
        {
            "role": "system",
            "content": (
                "You are QUORRA, the Asera AI assistant. "
                "Be concise, smart, and aware of past messages."
            ),
        },
        {"role": "system", "content": client_context},
    ]

    if summary_text:
        messages.append(
            {
                "role": "system",
                "content": f"Summary of previous conversation:\n{summary_text}",
            }
        )

    for m in history_result.data:
        messages.append({"role": m["role"], "content": m["content"]["text"]})

    messages.append({"role": "user", "content": data.content})

    # 7️⃣ Generate GPT reply
    try:
        assistant_text = generate_gpt_reply(messages)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"GPT generation failed: {str(e)}")

    # 8️⃣ Save assistant reply
    assistant_msg = {
        "id": str(uuid4()),
        "conversation_id": data.conversation_id,
        "user_id": user_id,
        "role": "assistant",
        "content": {"text": assistant_text},
        "tokens": None,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    supabase.table("messages").insert(assistant_msg).execute()

    # 9️⃣ Update summary in the background
    try:
        maybe_update_summary(data.conversation_id)
    except Exception as e:
        print(f"⚠️ Summary update failed: {e}")

    # 🔟 Return reply
    return {
        "status": "success",
        "message": {"role": "assistant", "content": assistant_text},
        "client": {"name": client.get("name")},
    }



@router.get("/{conversation_id}")
def get_messages(conversation_id: str):
    """Fetch all messages for a specific conversation."""
    result = (
        supabase.table("messages")
        .select("*")
        .eq("conversation_id", conversation_id)
        .order("created_at")  # ascending (default)
        .execute()
    )

    if not result.data:
        return {"messages": []}

    return {"total": len(result.data), "messages": result.data}

