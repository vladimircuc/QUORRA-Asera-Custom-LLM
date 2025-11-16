from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Routers
from api.clients import router as clients_router
from api.conversations import router as conversations_router
from api.messages import router as messages_router

app = FastAPI(title="QUORRA LLM API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # use ["*"] during local testing if needed
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Simple health check
@app.get("/health")
def health():
    return {"status": "ok"}

# Mount routers
app.include_router(clients_router, prefix="/clients", tags=["Clients"])
app.include_router(conversations_router, prefix="/conversations", tags=["Conversations"])
app.include_router(messages_router, prefix="/messages", tags=["Messages"])
