# QUORRA LLM — Full-Stack AI Assistant (Work in Progress)

QUORRA is a full-stack AI system designed to act as an intelligent business assistant for digital agencies.  
It combines Notion, Supabase, a custom Retrieval-Augmented Generation (RAG) pipeline, and GPT tool-calling to generate context-aware answers based on client data, documents, and previous conversations.

This README describes the current state of the project as it exists now: both backend and frontend.

---

## Overview

The project is split into two main components:

- Backend  
  - FastAPI service  
  - RAG engine over Supabase pgvector  
  - Tool-calling layer for GPT  
  - Notion ingestion pipeline  

- Frontend  
  - React + Vite single-page app  
  - Supabase authentication  
  - Chat interface connected to the backend  

The assistant can use:

- Client information stored in Supabase  
- Notion pages (meeting notes, SOPs, client docs) ingested into a vector store  
- Conversation history saved in the database  
- Website content, when explicitly requested by the user (URL tool)

The project is under active development; more tools and UI features will be layered on top of the existing foundation.

---

## Backend Architecture

### FastAPI Service

The backend is structured around modular routers, for example:

- /clients – client management endpoints  
- /conversations – create and retrieve conversations  
- /messages – store and fetch messages  
- /rag – semantic search and retrieval endpoint used by tools  

Each router encapsulates its own logic and talks to Supabase and OpenAI through shared service modules.

---

## Supabase Integration

Supabase is responsible for:

1. Authentication  
   - Handled on the frontend using the official Supabase JavaScript client.  
   - The backend expects a Supabase-issued JWT when it needs to know which user is calling.

2. Postgres Database  
   Current schema (simplified) includes:
   - clients – one row per client
   - knowledge_documents – one row per ingested Notion document
   - knowledge_chunks – chunk-level rows with embeddings
   - conversations – conversation metadata per user
   - messages – all user and assistant messages tied to a conversation

3. pgvector for Embeddings  
   - Embedding model: text-embedding-3-small  
   - Embedding dimension: 1536  
   - Stored in a VECTOR(1536) column in the knowledge_chunks table  
   - Retrieval uses cosine distance to rank chunks by semantic similarity to the query embedding  

---

## RAG Pipeline

The project has a working Retrieval-Augmented Generation pipeline linking Notion, Supabase, and GPT.

### Notion → Document → Chunk → Embedding

Ingestion is implemented in sync_notion_to_rag.py and currently does the following:

- Connects to the Notion API using a secret token from environment variables  
- Recursively fetches all blocks from the configured Notion databases (for example meeting notes, SOPs, clients)  
- Flattens blocks into clean document text while preserving ordering  
- Splits each document into roughly 400–600 token chunks with overlap so that context is not lost between boundaries  
- Computes a SHA-256 hash of each chunk to avoid inserting duplicates if the syncing script is run multiple times  
- Uses OpenAI’s text-embedding-3-small to embed each chunk into a 1536-dimensional vector  
- Stores results in Supabase:
  - knowledge_documents: document-level metadata (title, category, source URL, client ownership)  
  - knowledge_chunks: one row per chunk including document_id, chunk_index, content, category, client_id, and its embedding vector  

### Vector Retrieval Query (Conceptual)

When the assistant needs context, the backend:

1. Embeds the user’s query into the same 1536-dimensional embedding space.  
2. Runs a pgvector similarity search over knowledge_chunks using cosine distance.  
3. Optionally filters by category (for example only meeting notes) and/or by client_id so results are specific to the right client.  
4. Returns the top matching chunks together with their related document metadata.  
5. Passes these chunks as context into the GPT model to ground its answer.

In short: the system performs semantic search over Notion content that has been ingested into Supabase, rather than simple keyword search.

---

## GPT Tool-Calling Framework

The backend defines a set of structured tools that GPT can call during a conversation. These tools are described to the model in the system prompt and resolved by the backend.

Current tools (high level):

- search_rag  
  - Performs semantic retrieval over the pgvector store.  
  - Can be scoped to a specific client and/or category.  

- get_client_context  
  - Returns structured data from the clients table for a given client identifier.  
  - Used when the user asks about a specific client.  

- fetch_url  
  - Fetches HTML content for a given URL.  
  - Intended only for explicit “check this website” style queries.  
  - Backend handles network errors and non-200 responses gracefully.  

- save_message  
  - Persists user and assistant messages in the messages table, tied to a conversation.  

### Tool Behavior Rules

- The assistant must not blindly “search the web”; it should rely primarily on search_rag and get_client_context.  
- fetch_url is only used when the user clearly provides or mentions a URL or explicitly asks to inspect a website.  
- After tools execute, their results are fed back into the model to generate a grounded, final reply.  
- Every assistant reply is stored through save_message to maintain the full conversation history.

---

## Conversation and Message Flow

The high-level flow for each message:

1. The frontend sends the user’s message and conversation identifier to the backend.  
2. The backend stores the user message in Supabase.  
3. The backend builds a model prompt that includes:
   - System instructions and tool descriptions  
   - Recent messages from this conversation  
   - Any retrieved knowledge chunks from search_rag  
   - Optional client context from get_client_context  
4. GPT may invoke one or more tools; the backend executes them and returns the results to the model.  
5. GPT then produces a final answer based on the tool outputs and RAG context.  
6. The backend stores the assistant message in Supabase and returns it to the frontend.  
7. The frontend updates the chat UI with the new message.

This gives persistent conversation memory and context-aware answers grounded in your agency data.

---

## Frontend Architecture

The frontend is a React + Vite application.

### Tech Stack

- React single-page application  
- Vite for development and bundling  
- JavaScript (ESNext)  
- Supabase JavaScript client for authentication  
- REST calls to the FastAPI backend for all chat operations  

### Current Frontend Features

- Supabase authentication (sign in, sign out, and session handling).  
- Session persisted across page reloads.  
- A basic chat UI that:
  - Loads or creates a conversation for the authenticated user.  
  - Sends user messages to the backend.  
  - Renders assistant responses returned by the backend.  

The frontend has enough wiring to fully exercise the current backend functionality; additional UI polish and features (streaming, typing indicators, admin views) can be added on top.

---

## What Is Working Right Now

- FastAPI backend with modular routers.  
- Supabase database schema for clients, documents, chunks, conversations, and messages.  
- Notion ingestion and chunking pipeline with deduplication and embeddings.  
- pgvector integration using text-embedding-3-small (1536-dimensional vectors).  
- Semantic retrieval over the vector store with client/category filtering.  
- Tool-calling layer for RAG search, client context, website fetch, and message saving.  
- End-to-end conversation flow with persistent history.  
- React + Vite frontend connected to the backend.  
- Supabase authentication integrated into the frontend.  

---

## Planned / Next Steps

- Improved frontend UX (message streaming, typing indicators, better layout).  
- Additional tools such as Slack or other data-source ingestion.  
- Admin dashboard for inspecting clients and documents.  
- More robust observability and logging around tool calls and model responses.  
- Fine-grained permissions and multi-tenant support for agencies with multiple clients.

---

## Running the Project

Backend (example):

- Install Python dependencies.  
- Run uvicorn with the main FastAPI app module; for example:  
  uvicorn backend.api.app:app --reload  

Frontend (example):

- Run npm install at the frontend root.  
- Start the dev server:  
  npm run dev  

---

## Environment Variables (Examples)

Backend may require values such as:

- OPENAI_API_KEY  
- SUPABASE_URL  
- SUPABASE_SERVICE_KEY  
- NOTION_TOKEN  
- NOTION_MEETING_NOTES_DB_ID  
- NOTION_SOPS_DB_ID  
- NOTION_CLIENTS_DB_ID  

Frontend may require values such as:

- VITE_SUPABASE_URL  
- VITE_SUPABASE_ANON_KEY  
- VITE_BACKEND_URL  

---

## Status

This project is currently private and actively being built.  
APIs, database schema, and tool behavior may still change as the system evolves.
