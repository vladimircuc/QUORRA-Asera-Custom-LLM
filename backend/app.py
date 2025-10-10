from fastapi import FastAPI
from config import SUPABASE_URL, SUPABASE_SERVICE_KEY
from supabase_client import supabase

# Routers
from api.clients import router as clients_router
from api.conversations import router as conversations_router
from api.messages import router as messages_router
from fastapi.middleware.cors import CORSMiddleware

# ------------------------------
# APP INITIALIZATION
# ------------------------------
app = FastAPI(title="QUORRA LLM API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # or ["*"] for testing
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers with optional prefixes
app.include_router(clients_router, prefix="/clients", tags=["Clients"])
app.include_router(conversations_router, prefix="/conversations", tags=["Conversations"])
app.include_router(messages_router, prefix="/messages", tags=["Messages"])

