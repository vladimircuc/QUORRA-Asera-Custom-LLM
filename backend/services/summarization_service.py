import os
from datetime import datetime, timezone
from openai import OpenAI
from supabase_client import supabase
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# -----------------------------
# CONFIGURATION
# -----------------------------
SUMMARY_TRIGGER_INTERVAL = 10  # Summarize every 10 messages


# -----------------------------
# MAIN FUNCTIONS
# -----------------------------
def get_message_count(conversation_id: str) -> int:
    """Count total messages in a conversation."""
    res = (
        supabase.table("messages")
        .select("id", count="exact")
        .eq("conversation_id", conversation_id)
        .execute()
    )
    return res.count or 0


def get_latest_summary(conversation_id: str):
    """Return the latest summary for this conversation, if any."""
    res = (
        supabase.table("conversation_summary")
        .select("summary")
        .eq("conversation_id", conversation_id)
        .execute()
    )
    if res.data:
        return res.data[0]["summary"]
    return None


def generate_summary(conversation_id: str, existing_summary: str | None = None) -> str:
    """Generate or update the conversation summary with GPT."""
    # Fetch last 10-15 messages
    result = (
        supabase.table("messages")
        .select("role, content")
        .eq("conversation_id", conversation_id)
        .order("created_at", desc=False)
        .limit(15)
        .execute()
    )

    messages = [
        f"{m['role']}: {m['content']['text']}" for m in result.data
    ]
    joined_text = "\n".join(messages)

    # If there was already a summary, include it as context
    prompt = (
        "You are QUORRA, an AI assistant. Summarize the conversation below "
        "into a concise paragraph that captures all important context for future continuity.\n\n"
    )
    if existing_summary:
        prompt += f"Previous summary:\n{existing_summary}\n\n"

    prompt += f"Conversation:\n{joined_text}\n\nSummary:"

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.5,
    )

    return response.choices[0].message.content.strip()


def upsert_summary(conversation_id: str, summary_text: str):
    """Insert or update the summary in Supabase."""
    now = datetime.now(timezone.utc).isoformat()

    existing = (
        supabase.table("conversation_summary")
        .select("conversation_id")
        .eq("conversation_id", conversation_id)
        .execute()
    )

    if existing.data:
        # Update
        supabase.table("conversation_summary").update(
            {"summary": summary_text, "updated_at": now}
        ).eq("conversation_id", conversation_id).execute()
    else:
        # Insert
        supabase.table("conversation_summary").insert(
            {
                "conversation_id": conversation_id,
                "summary": summary_text,
                "created_at": now,
                "updated_at": now,
            }
        ).execute()


def maybe_update_summary(conversation_id: str):
    """
    Check message count and conditionally create/update the summary.
    Only runs when conversation length hits a multiple of SUMMARY_TRIGGER_INTERVAL.
    """
    message_count = get_message_count(conversation_id)
    if message_count % SUMMARY_TRIGGER_INTERVAL != 0:
        return  # Skip until threshold reached

    existing_summary = get_latest_summary(conversation_id)
    new_summary = generate_summary(conversation_id, existing_summary)
    upsert_summary(conversation_id, new_summary)

    print(f"🧩 Updated summary for conversation {conversation_id} (total {message_count} msgs)")
