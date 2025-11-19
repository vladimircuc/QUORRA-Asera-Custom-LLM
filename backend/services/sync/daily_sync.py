from datetime import datetime, timezone

from services.sync.sync_notion_to_rag import run_full_sync as run_notion_sync
from services.sync.sync_websites_to_rag import sync_websites_to_rag


def run_all_syncs() -> None:
    """
    Orchestrate all daily sync jobs:
      1) Notion → RAG (clients + sops + meeting_notes + clients DB, etc.)
      2) Websites → RAG (client websites)
    """
    now = datetime.now(timezone.utc).isoformat(timespec="seconds")
    print(f"=== QUORRA daily sync started at {now} ===", flush=True)

    # 1) Notion sync (includes clients refresh)
    print("\n--- Step 1/2: Notion → RAG sync ---", flush=True)
    try:
        run_notion_sync()
        print("--- Notion sync completed. ---", flush=True)
    except Exception as e:
        print(f"❌ Notion sync failed: {e}", flush=True)

    # 2) Website sync
    print("\n--- Step 2/2: Websites → RAG sync ---", flush=True)
    try:
        sync_websites_to_rag()
        print("--- Website sync completed. ---", flush=True)
    except Exception as e:
        print(f"❌ Website sync failed: {e}", flush=True)

    print("\n=== QUORRA daily sync finished ===", flush=True)


if __name__ == "__main__":
    run_all_syncs()
