import os
from datetime import datetime, timezone
from openai import OpenAI
from supabase_client import supabase
import tiktoken

# ------------------------------
# CONFIGURATION
# ------------------------------
TRIGGER_TOKENS = 4000          # When to summarize conversation
CHUNK_MESSAGES = 20            # Number of recent messages to summarize
MAX_SUMMARY_TOKENS = 1500      # If summary exceeds this, compress
COMPRESS_TARGET_TOKENS = 800   # Target length after compression
MODEL_NAME = "gpt-4-1106-preview"

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
encoding = tiktoken.encoding_for_model(MODEL_NAME)


def count_tokens(text: str) -> int:
    """Return approximate token count for a string."""
    try:
        return len(encoding.encode(text))
    except Exception as e:
        print(f"[⚠️ Tokenizer Error] {e}")
        return len(text.split())  # fallback approximation


def maybe_update_summary(conversation_id: str):
    """
    Token-aware summarization system.
    Triggers when total token count > TRIGGER_TOKENS.
    Compresses summary if it grows too large.
    """

    print("\n===============================")
    print(f"🧩 Checking summarization for conversation: {conversation_id}")
    print("===============================\n")

    # 1️⃣ Fetch all messages
    messages_res = (
        supabase.table("messages")
        .select("role, content")
        .eq("conversation_id", conversation_id)
        .order("created_at")
        .execute()
    )
    messages = messages_res.data or []
    total_msgs = len(messages)

    if total_msgs == 0:
        print("⚠️ No messages found for conversation.")
        return

    # 2️⃣ Compute token usage for all messages
    convo_text = "\n".join(f"{m['role']}: {m['content']['text']}" for m in messages)
    total_tokens = count_tokens(convo_text)

    print(f"📊 Total messages: {total_msgs}")
    print(f"📊 Estimated tokens in conversation: {total_tokens}")

    if total_tokens < TRIGGER_TOKENS:
        print(f"✅ Under {TRIGGER_TOKENS} tokens, skipping summarization.")
        return

    # 3️⃣ Fetch existing summary
    summary_res = (
        supabase.table("conversation_summary")
        .select("summary")
        .eq("conversation_id", conversation_id)
        .execute()
    )
    old_summary = summary_res.data[0]["summary"] if summary_res.data else ""
    summary_tokens = count_tokens(old_summary) if old_summary else 0

    print(f"📜 Old summary tokens: {summary_tokens}")
    print("🧠 Existing summary found!" if old_summary else "🆕 No existing summary found, will create one.")

    # 4️⃣ Prepare recent messages chunk to summarize
    recent_msgs = messages[-CHUNK_MESSAGES:]
    recent_text = "\n".join(f"{m['role']}: {m['content']['text']}" for m in recent_msgs)
    recent_tokens = count_tokens(recent_text)

    print(f"🪄 Summarizing last {len(recent_msgs)} messages (~{recent_tokens} tokens)")

    # 5️⃣ Build summarization prompt
    summarization_prompt = f"""
You are QUORRA, the Asera AI assistant.
Summarize the following chat segment while preserving client details, actions, and key outcomes.

Previous summary (if any):
{old_summary}

Recent conversation:
{recent_text}

Return a factual, concise summary that logically extends the previous one.
Do not repeat identical content.
    """.strip()

    # 6️⃣ Ask GPT for new summary chunk
    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[{"role": "user", "content": summarization_prompt}],
        temperature=0.3
    )
    new_summary = response.choices[0].message.content.strip()
    new_summary_tokens = count_tokens(new_summary)

    print(f"🧾 New summary chunk tokens: {new_summary_tokens}")

    # 7️⃣ Merge summaries
    merged_summary = (
        f"{old_summary}\n\n---\n\n{new_summary}" if old_summary else new_summary
    )
    merged_summary_tokens = count_tokens(merged_summary)

    print(f"📦 Merged summary token size: {merged_summary_tokens}")

    # 8️⃣ Compress if necessary
    if merged_summary_tokens > MAX_SUMMARY_TOKENS:
        print(f"⚙️ Compressing summary (too long: {merged_summary_tokens} tokens)...")

        compression_prompt = f"""
You are QUORRA, summarizing an ongoing client conversation.
The following summary is too long — compress it to around {COMPRESS_TARGET_TOKENS} tokens.
Retain all factual details, actions, and client insights.

Summary to compress:
{merged_summary}
        """.strip()

        compression_response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[{"role": "user", "content": compression_prompt}],
            temperature=0.3
        )
        merged_summary = compression_response.choices[0].message.content.strip()
        merged_summary_tokens = count_tokens(merged_summary)

        print(f"✅ Compressed summary now {merged_summary_tokens} tokens")

    # 9️⃣ Save to Supabase
    supabase.table("conversation_summary").upsert({
        "conversation_id": conversation_id,
        "summary": merged_summary,
        "updated_at": datetime.now(timezone.utc).isoformat()
    }).execute()

    print(f"💾 Summary updated for {conversation_id}")
    print(f"🧮 Final summary size: {merged_summary_tokens} tokens\n")
    print("===============================\n")
