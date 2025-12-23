# QUORRA LLM — Full-Stack AI Assistant

QUORRA is a full-stack AI system designed to act as an intelligent business assistant for digital agencies. It combines Notion, Supabase, a custom Retrieval-Augmented Generation (RAG) pipeline, and GPT tool-calling to generate context-aware answers based on client data, documents, and previous conversations.

---

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Prerequisites](#prerequisites)
- [Getting Started](#getting-started)
  - [API Keys Required](#api-keys-required)
  - [Backend Setup](#backend-setup)
  - [Frontend Setup](#frontend-setup)
- [Project Structure](#project-structure)
- [Architecture](#architecture)
  - [Backend Architecture](#backend-architecture)
  - [Frontend Architecture](#frontend-architecture)
- [Key Components](#key-components)
  - [RAG Pipeline](#rag-pipeline)
  - [GPT Tool-Calling Framework](#gpt-tool-calling-framework)
  - [Supabase Integration](#supabase-integration)
- [Usage](#usage)
- [Development Status](#development-status)
- [Contributing](#contributing)

---

## Overview

QUORRA is an intelligent business assistant that helps digital agencies manage client information, access historical meeting notes, retrieve standard operating procedures (SOPs), and maintain context-aware conversations. The system leverages:

- **Notion** for content management and document storage
- **Supabase** for authentication, database, and vector storage
- **OpenAI GPT** with tool-calling capabilities for intelligent responses
- **Custom RAG Pipeline** for semantic search over ingested documents

The project consists of two main components:

- **Backend**: FastAPI service with RAG engine, tool-calling layer, and Notion ingestion pipeline
- **Frontend**: React + Vite single-page application with Supabase authentication and chat interface

---

## Features

- 🔐 **User Authentication** via Supabase
- 💬 **Persistent Conversations** with full message history
- 🔍 **Semantic Search** over Notion documents using vector embeddings
- 🤖 **Intelligent Tool-Calling** for context-aware responses
- 📊 **Client Management** with structured data retrieval
- 📝 **Document Ingestion** from Notion databases (meetings, SOPs, clients)
- 🌐 **Website Content Fetching** for explicit URL requests
- 🎨 **Modern UI** with React and Tailwind CSS

---

## Tech Stack

### Backend
- **FastAPI** - Modern Python web framework
- **Supabase** - PostgreSQL database with pgvector extension
- **OpenAI API** - GPT models and embeddings (text-embedding-3-small)
- **Notion API** - Document ingestion
- **Python 3.x** - Backend runtime

### Frontend
- **React 19** - UI library
- **Vite** - Build tool and dev server
- **Tailwind CSS** - Styling framework
- **React Router** - Client-side routing
- **Supabase JS Client** - Authentication and database access

---

## Prerequisites

Before you begin, ensure you have the following installed:

- **Node.js** (v18 or higher) and npm
- **Python** (3.8 or higher) and pip
- **Git** for version control
- Access to the following services (API keys required - see below):
  - Supabase project
  - OpenAI API account
  - Notion workspace with configured databases

---

## Getting Started

### API Keys Required

**⚠️ Important**: To test and run this project, you need to request API keys and credentials from the project maintainers. The following are required:

1. **Supabase Credentials**
   - `SUPABASE_URL` - Your Supabase project URL
   - `SUPABASE_SERVICE_KEY` - Service role key (backend)
   - `VITE_SUPABASE_ANON_KEY` - Anonymous/public key (frontend)

2. **OpenAI API Key**
   - `OPENAI_API_KEY` - For GPT models and embeddings

3. **Notion Integration Token**
   - `NOTION_TOKEN` - Notion API integration token
   - `NOTION_MEETING_NOTES_DB_ID` - Database ID for meeting notes
   - `NOTION_SOPS_DB_ID` - Database ID for SOPs
   - `NOTION_CLIENTS_DB_ID` - Database ID for clients

**Please reach out to the project maintainers to request these API keys and credentials before proceeding with setup.**

---

### Backend Setup

1. **Navigate to the backend directory:**
   ```bash
   cd backend
   ```

2. **Create a virtual environment (recommended):**
   ```bash
   python -m venv venv
   
   # On Windows:
   venv\Scripts\activate
   
   # On macOS/Linux:
   source venv/bin/activate
   ```

3. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Create a `.env` file in the `backend` directory:**
   ```env
   # Supabase Configuration
   SUPABASE_URL=your_supabase_url_here
   SUPABASE_SERVICE_KEY=your_service_key_here
   
   # OpenAI Configuration
   OPENAI_API_KEY=your_openai_api_key_here
   
   # Notion Configuration
   NOTION_TOKEN=your_notion_token_here
   NOTION_MEETING_NOTES_DB_ID=your_meeting_notes_db_id
   NOTION_SOPS_DB_ID=your_sops_db_id
   NOTION_CLIENTS_DB_ID=your_clients_db_id
   
   # Optional: Notion Client Relation
   MEETING_NOTE_CLIENT_RELATION_NAME=Clients
   INCLUDE_TITLE_IN_EMBED=true
   ```

5. **Run the backend server:**
   ```bash
   # From the project root:
   uvicorn backend.app:app --reload --host 0.0.0.0 --port 8000
   
   # Or from the backend directory:
   uvicorn app:app --reload
   ```

   The API will be available at `http://localhost:8000`. You can check the health endpoint at `http://localhost:8000/health`.

---

### Frontend Setup

1. **Install Node.js dependencies:**
   ```bash
   npm install
   ```

2. **Create a `.env` file in the project root:**
   ```env
   # Supabase Configuration
   VITE_SUPABASE_URL=your_supabase_url_here
   VITE_SUPABASE_ANON_KEY=your_supabase_anon_key_here
   
   # Backend API URL
   VITE_BACKEND_URL=http://localhost:8000
   ```

3. **Start the development server:**
   ```bash
   npm run dev
   ```

   The frontend will be available at `http://localhost:5173` (default Vite port).

4. **Build for production:**
   ```bash
   npm run build
   ```

   The production build will be in the `dist` directory.

---

## Project Structure

```
QUORRA-Asera-Custom-LLM/
├── backend/
│   ├── api/                    # FastAPI routers
│   │   ├── clients.py         # Client management endpoints
│   │   ├── conversations.py   # Conversation endpoints
│   │   └── messages.py        # Message endpoints
│   ├── services/              # Business logic services
│   │   ├── llm/               # LLM services (GPT, summarization, titles)
│   │   ├── notion/            # Notion integration
│   │   ├── rag/               # RAG pipeline and tools
│   │   ├── storage/           # File upload handling
│   │   └── sync/              # Data synchronization scripts
│   ├── app.py                 # FastAPI application entry point
│   ├── config.py              # Configuration management
│   ├── supabase_client.py     # Supabase client initialization
│   └── requirements.txt       # Python dependencies
├── src/                        # Frontend React application
│   ├── components/            # React components
│   ├── pages/                 # Page components
│   ├── lib/                   # Utility libraries
│   ├── App.jsx                # Main app component
│   └── main.jsx               # Application entry point
├── public/                     # Static assets
├── dist/                       # Production build output
├── package.json               # Node.js dependencies
├── vite.config.js             # Vite configuration
└── README.md                  # This file
```

---

## Architecture

### Backend Architecture

The backend is structured around modular FastAPI routers:

- **`/clients`** - Client management endpoints
- **`/conversations`** - Create and retrieve conversations
- **`/messages`** - Store and fetch messages
- **`/rag`** - Semantic search and retrieval endpoint (used by tools)

Each router encapsulates its own logic and communicates with Supabase and OpenAI through shared service modules.

**Key Services:**
- `services/llm/gpt_tool_service.py` - GPT tool-calling orchestration
- `services/rag/core.py` - RAG query handling
- `services/notion/meetings.py` - Notion document fetching
- `services/sync/sync_notion_to_rag.py` - Notion ingestion pipeline

### Frontend Architecture

The frontend is a React single-page application with:

- **Routing**: React Router for navigation
- **Authentication**: Supabase auth with session persistence
- **State Management**: React hooks for local state
- **API Communication**: REST calls to FastAPI backend
- **Styling**: Tailwind CSS for modern UI

**Key Pages:**
- `ChatPage` - Main chat interface
- `LoginPage` / `RegisterPage` - Authentication
- `SettingsPage` - User settings
- `ProfilePage` - User profile management

---

## Key Components

### RAG Pipeline

The Retrieval-Augmented Generation pipeline enables semantic search over ingested documents.

#### Notion → Document → Chunk → Embedding

**Ingestion Process** (`sync_notion_to_rag.py`):

1. Connects to Notion API using integration token
2. Recursively fetches all blocks from configured databases
3. Flattens blocks into clean document text (preserves ordering)
4. Splits documents into ~400-600 token chunks with overlap
5. Computes SHA-256 hash for deduplication
6. Generates embeddings using `text-embedding-3-small` (1536 dimensions)
7. Stores in Supabase:
   - `knowledge_documents`: Document metadata (title, category, source URL, client)
   - `knowledge_chunks`: Chunk-level data with embeddings

#### Vector Retrieval

When the assistant needs context:

1. Embeds the user's query into the same 1536-dimensional space
2. Performs pgvector similarity search using cosine distance
3. Optionally filters by category and/or `client_id`
4. Returns top matching chunks with document metadata
5. Passes chunks as context to GPT for grounded responses

### GPT Tool-Calling Framework

The backend defines structured tools that GPT can invoke during conversations:

#### Available Tools

- **`search_rag`**
  - Performs semantic retrieval over the pgvector store
  - Can be scoped to a specific client and/or category
  - Returns relevant document chunks based on query similarity

- **`get_client_context`**
  - Returns structured data from the `clients` table
  - Used when the user asks about a specific client
  - Provides client metadata and relationships

- **`fetch_url`**
  - Fetches HTML content for a given URL
  - Only used for explicit "check this website" queries
  - Handles network errors and non-200 responses gracefully

- **`save_message`**
  - Persists user and assistant messages in the database
  - Maintains conversation history tied to a conversation ID

#### Tool Behavior Rules

- The assistant primarily relies on `search_rag` and `get_client_context`
- `fetch_url` is only used when the user explicitly provides a URL
- Tool results are fed back into the model to generate grounded replies
- All assistant replies are stored via `save_message` for conversation persistence

### Supabase Integration

Supabase provides three core services:

#### 1. Authentication
- Handled on the frontend using the Supabase JavaScript client
- Backend expects Supabase-issued JWTs for user identification
- Session persistence across page reloads

#### 2. PostgreSQL Database

**Schema includes:**
- `clients` - Client information and metadata
- `knowledge_documents` - Ingested Notion documents
- `knowledge_chunks` - Document chunks with embeddings
- `conversations` - Conversation metadata per user
- `messages` - All user and assistant messages

#### 3. pgvector for Embeddings
- **Model**: `text-embedding-3-small`
- **Dimension**: 1536
- **Storage**: `VECTOR(1536)` column in `knowledge_chunks`
- **Retrieval**: Cosine distance for semantic similarity ranking

---

## Usage

### Conversation Flow

1. User sends a message through the frontend chat interface
2. Frontend sends message and conversation ID to backend
3. Backend stores the user message in Supabase
4. Backend builds a prompt with:
   - System instructions and tool descriptions
   - Recent conversation history
   - Retrieved knowledge chunks (if applicable)
   - Client context (if applicable)
5. GPT may invoke one or more tools
6. Backend executes tools and returns results to GPT
7. GPT generates a final answer based on tool outputs
8. Backend stores the assistant message and returns it to frontend
9. Frontend displays the response in the chat UI

This flow provides persistent conversation memory and context-aware answers grounded in your agency data.

### Running Data Sync Scripts

To ingest Notion content into the RAG system:

```bash
cd backend
python -m services.sync.sync_notion_to_rag
```

To sync websites (if configured):

```bash
python -m services.sync.sync_websites_to_rag
```

---

## Development Status

### ✅ Currently Working

- FastAPI backend with modular routers
- Supabase database schema and integration
- Notion ingestion and chunking pipeline with deduplication
- pgvector integration with text-embedding-3-small
- Semantic retrieval with client/category filtering
- GPT tool-calling layer (RAG search, client context, URL fetch, message saving)
- End-to-end conversation flow with persistent history
- React + Vite frontend with Supabase authentication
- Chat interface connected to backend

### 🚧 Planned / Next Steps

- Improved frontend UX (message streaming, typing indicators, better layout)
- Additional tools (Slack integration, other data sources)
- Admin dashboard for inspecting clients and documents
- Enhanced observability and logging around tool calls
- Fine-grained permissions and multi-tenant support
- Performance optimizations for large document sets

---

## Contributing

This project is currently private and actively under development. APIs, database schema, and tool behavior may change as the system evolves.

**Before contributing:**
1. Ensure you have all required API keys (see [API Keys Required](#api-keys-required))
2. Set up both backend and frontend environments
3. Test your changes thoroughly
4. Follow existing code style and patterns

---

## Support

For questions, issues, or API key requests, please reach out to the project maintainers.

---

**Status**: This project is actively being built and improved. Check back regularly for updates!
