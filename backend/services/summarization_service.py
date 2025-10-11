import os
from datetime import datetime, timezone
from openai import OpenAI
from supabase_client import supabase

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# ---------------------------------------------------------
# Create or update summary for a conversation
# ---------------------------------------------------------
def maybe_update_summary(conversation_id: str):
    """
    Summarizes the conversation if the number of messages
    is a multiple of 16, merging with any existing summary.
    """
    # Fetch all messages
    messages = (
        supabase.table("messages")
        .select("role, content")
        .eq("conversation_id", conversation_id)
        .order("created_at")
        .execute()
        .data
    )
    total = len(messages)
    if total < 16 or total % 16 != 0:
        return  # Only summarize every 16 messages

    # Fetch old summary (if any)
    old_summary_result = (
        supabase.table("conversation_summary")
        .select("summary")
        .eq("conversation_id", conversation_id)
        .execute()
    )
    old_summary = (
        old_summary_result.data[0]["summary"]
        if old_summary_result.data
        else ""
    )

    # Build conversation text
    convo_text = "\n".join(
        f"{m['role'].capitalize()}: {m['content']['text']}"
        for m in messages[-16:]
    )

    # Ask GPT to summarize
    prompt = f"""
You are QUORRA, summarizing this conversation for future context memory.
Previous summary (if any):
{old_summary}

Recent messages:
{convo_text}

Summarize concisely what was discussed, key client details, and questions.
Keep the summary factual and neutral.
    """.strip()

    response = client.chat.completions.create(
        model="gpt-4-1106-preview",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3
    )

    new_summary = response.choices[0].message.content.strip()

    # Merge summaries (keep old info + new additions)
    merged_summary = (
        f"{old_summary}\n\n---\n\n{new_summary}" if old_summary else new_summary
    )

    # Upsert summary
    supabase.table("conversation_summary").upsert({
        "conversation_id": conversation_id,
        "summary": merged_summary,
        "updated_at": datetime.now(timezone.utc).isoformat()
    }).execute()

    print(f"🧩 Updated summary for conversation {conversation_id} ({total} msgs)")
