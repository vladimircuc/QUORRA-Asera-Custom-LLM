import os
from dotenv import load_dotenv
from notion_client import Client
import json
import sys

load_dotenv()

NOTION_TOKEN = os.getenv("NOTION_TOKEN")
DB_ID = os.getenv("DATABASE_ID")

if not NOTION_TOKEN or not DB_ID:
    raise RuntimeError("Missing NOTION_TOKEN or DATABASE_ID in .env")

notion = Client(auth=NOTION_TOKEN)

def list_client_names(limit=None):
    """
    Return account names from the whole database.
    If limit is None: fetch *all* pages.
    If limit is an int: stop after that many names.
    """
    names = []
    start_cursor = None

    while True:
        kwargs = {"database_id": DB_ID, "page_size": 100}
        if start_cursor:
            kwargs["start_cursor"] = start_cursor

        res = notion.databases.query(**kwargs)

        for row in res.get("results", []):
            props = row.get("properties", {})
            # Be defensive in case the property name changes or is missing
            title_prop = props.get("Account name", {}).get("title", [])
            name = "".join(t.get("plain_text", "") for t in title_prop)
            if name:
                names.append(name)
                if isinstance(limit, int) and len(names) >= limit:
                    return names

        if not res.get("has_more"):
            break
        start_cursor = res.get("next_cursor")

    return names

def build_clients_payload(query: str | None = None):
    names = list_client_names()
    if query:
        q = query.lower()
        names = [n for n in names if q in n.lower()]
    clients = [{"name": n} for n in names]
    return {"total": len(clients), "clients": clients}


def main():
    if len(sys.argv) < 2:
        print("Usage: python notion_api.py list_clients")
        sys.exit(1)

    command = sys.argv[1]

    if command == "list_clients":
        payload = build_clients_payload()
        print(json.dumps(payload, indent=2))
    else:
        print(f"Unknown command: {command}")

if __name__ == "__main__":
    main()