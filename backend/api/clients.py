from fastapi import APIRouter, HTTPException
from supabase_client import supabase
from services.notion.client_sync import refresh_clients_from_notion

router = APIRouter()

@router.get("/")
def get_clients():
    """Return all clients except churned, prospect, or null statuses."""
    result = (
        supabase.table("clients")
        .select("id, name, status")
        .order("name", desc=False)
        .execute()
    )
    filtered = [
        c for c in result.data
        if c.get("status") not in (None, "churned", "prospect")
    ]
    return filtered


@router.post("/refresh")
def refresh_clients():
    """Refresh clients from Notion."""
    try:
        summary = refresh_clients_from_notion()
        return {"status": "success", "summary": summary}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
