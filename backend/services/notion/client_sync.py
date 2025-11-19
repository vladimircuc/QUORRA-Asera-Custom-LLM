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


def _extract_text(prop):
    """Helper to safely extract plain text from Notion property."""
    if isinstance(prop, list):
        return " ".join(p.get("plain_text", "") for p in prop)
    return ""


def _extract_multi_select(prop):
    """Helper to extract multi-select property names."""
    if isinstance(prop, list):
        return [p.get("name") for p in prop]
    return []


def _extract_date(prop):
    """Helper to get the start date from a Notion date field."""
    if not prop or not prop.get("start"):
        return None
    return prop["start"]

def fetch_clients_from_notion():
    """Fetch all client records from Notion DB → list of dicts."""
    clients = []
    start_cursor = None

    while True:
        kwargs = {"database_id": DATABASE_ID, "page_size": 100}
        if start_cursor:
            kwargs["start_cursor"] = start_cursor

        response = notion.databases.query(**kwargs)

        for row in response.get("results", []):
            props = row.get("properties", {})

            # Basic text fields
            name = _extract_text(props.get("Account name", {}).get("title", []))

            # Description
            desc_rich = props.get("Description", {}).get("rich_text", [])
            description = "".join(
                t.get("plain_text", "") for t in desc_rich
            ) if desc_rich else None

            # Account Manager
            account_manager = ""
            people = props.get("Account manager", {}).get("people")
            if isinstance(people, list) and people:
                account_manager = people[0].get("name", "")

            # Select fields
            status = (
                props.get("Status", {}).get("select", {}).get("name")
                if props.get("Status") and props["Status"].get("select")
                else None
            )

            priority = (
                props.get("Priority", {}).get("select", {}).get("name")
                if props.get("Priority") and props["Priority"].get("select")
                else None
            )

            # Email
            contact_email = (
                props.get("Contact email", {}).get("email")
                if props.get("Contact email")
                else None
            )

            # Website (NEW)
            website = (
                props.get("Website", {}).get("url")
                if props.get("Website")
                else None
            )

            # Multi-select
            products = _extract_multi_select(
                props.get("Products/Services", {}).get("multi_select", [])
                if props.get("Products/Services")
                else []
            )

            # Date
            service_end_date = _extract_date(
                props.get("Service End-Date", {}).get("date")
                if props.get("Service End-Date")
                else None
            )

            clients.append({
                "notion_page_id": row.get("id"),
                "name": name,
                "description": description,
                "account_manager": account_manager,
                "status": status,
                "priority": priority,
                "contact_email": contact_email,
                "website": website,          # ← NEW
                "products": products,
                "service_end_date": service_end_date,
            })

        if not response.get("has_more"):
            break

        start_cursor = response.get("next_cursor")

    return clients


def refresh_clients_from_notion():
    """
    Sync Notion clients with Supabase `clients` table.
    - Always overwrites fields for existing clients (no diff check).
    - Inserts new clients.
    - Marks missing ones as inactive.
    """
    notion_clients = fetch_clients_from_notion()

    # current state in Supabase
    sb_clients = (
        supabase.table("clients")
        .select(
            "id, notion_page_id, name, description, status, account_manager, "
            "priority, contact_email, website, products, service_end_date"
        )
        .execute()
        .data
    )

    summary = {"added": 0, "updated": 0, "inactivated": 0}

    # Map by notion_page_id for quick lookup
    sb_by_notion = {
        c["notion_page_id"]: c
        for c in sb_clients
        if c.get("notion_page_id")
    }
    notion_ids = {c["notion_page_id"] for c in notion_clients}

    # Upsert (insert + overwrite)
    for client in notion_clients:
        notion_id = client["notion_page_id"]

        row_data = {
            "name": client.get("name"),
            "description": client.get("description"),
            "status": (client.get("status") or "active").lower(),
            "account_manager": client.get("account_manager"),
            "priority": client.get("priority"),
            "contact_email": client.get("contact_email"),
            "website": client.get("website"),
            "products": client.get("products"),
            "service_end_date": client.get("service_end_date"),
        }

        if notion_id in sb_by_notion:
            # Always overwrite fields for existing row
            supabase.table("clients") \
                .update(row_data) \
                .eq("notion_page_id", notion_id) \
                .execute()
            summary["updated"] += 1
        else:
            # Insert new client
            insert_data = {
                "notion_page_id": notion_id,
                **row_data,
            }
            supabase.table("clients").insert(insert_data).execute()
            summary["added"] += 1

    # Mark clients missing from Notion as inactive
    for client in sb_clients:
        npid = client.get("notion_page_id")
        if npid and npid not in notion_ids and client.get("status") != "inactive":
            supabase.table("clients") \
                .update({"status": "inactive"}) \
                .eq("notion_page_id", npid) \
                .execute()
            summary["inactivated"] += 1

    print(f"[clients sync] added={summary['added']} updated={summary['updated']} inactivated={summary['inactivated']}")
    return summary


if __name__ == "__main__":
    # Example: run just the clients sync
    refresh_clients_from_notion()
    # Or test a specific client's meetings:
    # TEST_CLIENT_PAGE_ID = "20f9a8ee-e622-804b-a77d-e7745b23bd6e"
    # fetch_client_meetings(TEST_CLIENT_PAGE_ID)
