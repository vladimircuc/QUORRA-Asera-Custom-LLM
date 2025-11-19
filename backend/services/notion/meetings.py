import os
from notion_client import Client
from supabase_client import supabase
from dotenv import load_dotenv

load_dotenv()

NOTION_TOKEN = os.getenv("NOTION_TOKEN")
DATABASE_ID = os.getenv("DATABASE_ID")

if not NOTION_TOKEN or not DATABASE_ID:
    raise RuntimeError("Missing NOTION_TOKEN or DATABASE_ID in .env")

notion = Client(auth=NOTION_TOKEN)

def _get_all_blocks(page_id):
    """Fetch all blocks (with pagination) for a given Notion page."""
    all_blocks = []
    next_cursor = None

    while True:
        kwargs = {"block_id": page_id, "page_size": 100}
        if next_cursor:
            kwargs["start_cursor"] = next_cursor

        resp = notion.blocks.children.list(**kwargs)
        results = resp.get("results", [])
        all_blocks.extend(results)

        if not resp.get("has_more"):
            break
        next_cursor = resp.get("next_cursor")

    return all_blocks


def fetch_client_meetings(notion_page_id: str, limit: int = 2):
    """
    Fetch all 'Meeting Notes' pages linked to a given client (via relation property),
    pull full page content (paragraphs, headings, etc.), sort by date, and print latest ones.
    """
    try:
        client_page = notion.pages.retrieve(notion_page_id)
        props = client_page.get("properties", {})

        meeting_relation = props.get("Meeting Notes", {}).get("relation", [])
        if not meeting_relation:
            print("⚠️ No meeting notes found for this client.")
            return

        print(f"🗂 Found {len(meeting_relation)} meetings for this client.")

        meetings = []

        for rel in meeting_relation:
            meeting_id = rel["id"]
            meeting_data = notion.pages.retrieve(meeting_id)
            meeting_props = meeting_data.get("properties", {})

            title_prop = meeting_props.get("Name", {}).get("title", [])
            title = title_prop[0]["plain_text"] if title_prop else "Untitled Meeting"

            date_prop = meeting_props.get("Date", {}).get("date")
            date = date_prop["start"] if date_prop else None

            blocks = _get_all_blocks(meeting_id)
            paragraphs = []
            for block in blocks:
                btype = block["type"]
                if btype in ["paragraph", "heading_1", "heading_2", "heading_3"]:
                    texts = block[btype].get("rich_text", [])
                    content = "".join(t.get("plain_text", "") for t in texts)
                    if content:
                        paragraphs.append(content)

            full_text = "\n".join(paragraphs)
            meetings.append({
                "id": meeting_id,
                "title": title,
                "date": date,
                "content": full_text,
            })

        meetings.sort(key=lambda m: m["date"] or "", reverse=True)

        for i, m in enumerate(meetings[:limit], start=1):
            print(f"\n=== 🗓 Meeting {i}: {m['title']} ({m['date']}) ===")
            print(m["content"])
            print("\n" + "=" * 70)

    except Exception as e:
        print(f"❌ Error fetching client meetings: {e}")


if __name__ == "__main__":
    # test a specific client's meetings:
    TEST_CLIENT_PAGE_ID = "20f9a8ee-e622-804b-a77d-e7745b23bd6e"
    fetch_client_meetings(TEST_CLIENT_PAGE_ID)
