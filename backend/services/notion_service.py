import os
from datetime import datetime
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
    """Fetch all client records from Notion DB."""
    clients = []
    start_cursor = None

    while True:
        kwargs = {"database_id": DATABASE_ID, "page_size": 100}
        if start_cursor:
            kwargs["start_cursor"] = start_cursor

        response = notion.databases.query(**kwargs)

        for row in response.get("results", []):
            props = row.get("properties", {})

            # Use safe .get() with defaults for each property
            name = _extract_text(props.get("Account name", {}).get("title", []))
            account_manager = ""
            if isinstance(props.get("Account manager", {}).get("people"), list):
                if props["Account manager"]["people"]:
                    account_manager = props["Account manager"]["people"][0].get("name", "")

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

            contact_email = (
                props.get("Contact email", {}).get("email")
                if props.get("Contact email")
                else None
            )

            products = _extract_multi_select(
                props.get("Products/Services", {}).get("multi_select", [])
                if props.get("Products/Services")
                else []
            )

            service_end_date = _extract_date(
                props.get("Service End-Date", {}).get("date")
                if props.get("Service End-Date")
                else None
            )

            clients.append({
                "notion_page_id": row.get("id"),
                "name": name,
                "account_manager": account_manager,
                "status": status,
                "priority": priority,
                "contact_email": contact_email,
                "products": products,
                "service_end_date": service_end_date,
            })

        if not response.get("has_more"):
            break

        start_cursor = response.get("next_cursor")

    return clients



def refresh_clients_from_notion():
    """Sync Notion clients with Supabase (clean schema)."""
    notion_clients = fetch_clients_from_notion()
    sb_clients = (
        supabase.table("clients")
        .select("id, notion_page_id, name, status, account_manager, priority, contact_email, products, service_end_date")
        .execute()
        .data
    )

    summary = {"added": 0, "updated": 0, "inactivated": 0}
    sb_by_notion = {c["notion_page_id"]: c for c in sb_clients if c.get("notion_page_id")}
    notion_ids = {c["notion_page_id"] for c in notion_clients}

    for client in notion_clients:
        notion_id = client["notion_page_id"]
        if notion_id in sb_by_notion:
            existing = sb_by_notion[notion_id]
            updates = {}

            # only update if value changed and new value is not None
            for field in ["name", "status", "account_manager", "priority", "contact_email", "products", "service_end_date"]:
                new_val = client.get(field)
                if new_val is not None and new_val != existing.get(field):
                    updates[field] = new_val

            if updates:
                supabase.table("clients").update(updates).eq("notion_page_id", notion_id).execute()
                summary["updated"] += 1
        else:
            # insert new client
            insert_data = {
                "notion_page_id": notion_id,
                "name": client.get("name"),
                "status": (client.get("status") or "active").lower(),
                "account_manager": client.get("account_manager"),
                "priority": client.get("priority"),
                "contact_email": client.get("contact_email"),
                "products": client.get("products"),
                "service_end_date": client.get("service_end_date"),
            }
            supabase.table("clients").insert(insert_data).execute()
            summary["added"] += 1

    # mark missing clients as inactive
    for client in sb_clients:
        if client.get("notion_page_id") not in notion_ids and client.get("status") != "inactive":
            supabase.table("clients").update({"status": "inactive"}).eq("notion_page_id", client["notion_page_id"]).execute()
            summary["inactivated"] += 1

    return summary



