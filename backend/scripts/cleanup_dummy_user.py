# backend/scripts/cleanup_dummy_user.py

from supabase_client import supabase

# The dummy user we used everywhere
DUMMY_USER_ID = "11111111-2222-3333-4444-555555555555"


def main():
    print(f"🔎 Looking for conversations for dummy user: {DUMMY_USER_ID}")

    # 1) All conversations for the dummy user
    convo_res = (
        supabase.table("conversations")
        .select("id")
        .eq("user_id", DUMMY_USER_ID)
        .execute()
    )
    conversations = convo_res.data or []
    convo_ids = [c["id"] for c in conversations]

    if not convo_ids:
        print("✅ No conversations found for dummy user. Nothing to delete.")
        return

    print(f"🗂️ Found {len(convo_ids)} conversation(s) to delete.")

    # 2) All messages in those conversations
    msg_res = (
        supabase.table("messages")
        .select("id, conversation_id")
        .in_("conversation_id", convo_ids)
        .execute()
    )
    messages = msg_res.data or []
    message_ids = [m["id"] for m in messages]
    print(f"📝 Found {len(message_ids)} message(s) to delete.")

    # 3) All upload documents belonging to those conversations
    doc_res = (
        supabase.table("knowledge_documents")
        .select("id")
        .eq("source", "upload")
        .in_("conversation_id", convo_ids)
        .execute()
    )
    upload_docs = doc_res.data or []
    upload_doc_ids = [d["id"] for d in upload_docs]
    print(f"📄 Found {len(upload_doc_ids)} upload document(s) to delete.")

    # 4) Delete message_documents links (by message and by document)
    if message_ids:
        print("🧹 Deleting message_documents by message_id…")
        supabase.table("message_documents").delete().in_("message_id", message_ids).execute()

    if upload_doc_ids:
        print("🧹 Deleting message_documents by document_id…")
        supabase.table("message_documents").delete().in_("document_id", upload_doc_ids).execute()

    # 5) Delete chunks for upload documents
    if upload_doc_ids:
        print("🧹 Deleting knowledge_chunks for upload documents…")
        supabase.table("knowledge_chunks").delete().in_("document_id", upload_doc_ids).execute()

    # 6) Delete upload documents
    if upload_doc_ids:
        print("🧹 Deleting knowledge_documents (source='upload')…")
        supabase.table("knowledge_documents").delete().in_("id", upload_doc_ids).execute()

    # 7) Delete conversation summaries
    print("🧹 Deleting conversation_summary rows…")
    supabase.table("conversation_summary").delete().in_("conversation_id", convo_ids).execute()

    # 8) Delete messages themselves
    print("🧹 Deleting messages…")
    supabase.table("messages").delete().in_("conversation_id", convo_ids).execute()

    # 9) Delete conversations
    print("🧹 Deleting conversations…")
    supabase.table("conversations").delete().in_("id", convo_ids).execute()

    print("✅ Cleanup complete. Dummy user conversations and related data removed.")


if __name__ == "__main__":
    main()
