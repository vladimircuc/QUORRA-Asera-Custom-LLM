from config import SUPABASE_URL, SUPABASE_SERVICE_KEY
from fastapi import FastAPI
from supabase_client import supabase
from api.clients import router as clients_router
from api.conversations import router as conversations_router
from api.messages import router as messages_router


app = FastAPI()

app.include_router(clients_router)
app.include_router(conversations_router)
app.include_router(messages_router)

@app.get("/clients")
def get_clients():
    result = supabase.table("clients").select("*").execute()
    return result.data

@app.post("/clients/seed")
def seed_client():
    result = supabase.table("clients").insert({
        "name": "Test Client",
        "notion_page_id": "abc123",
        "industry": "AI",
        "plan_tier": "pro",
        "timezone": "US/Eastern"
    }).execute()
    return result.data
