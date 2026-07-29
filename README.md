# Enterprise RAG - Production-Grade Full-Stack Application

A production-grade Enterprise Retrieval-Augmented Generation (RAG) system with hierarchical Knowledge Base management, hybrid vector + keyword search, real-time analytics, multi-tenant isolation, and a modern React frontend.

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green.svg)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-18.3.1-blue.svg)](https://reactjs.org/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.0+-blue.svg)](https://www.typescriptlang.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## 🌟 Features

### 🏢 Hierarchical Knowledge Bases & Ingestion
- 📚 **Knowledge Base Isolation**: Organize documents logically into domain-specific Knowledge Bases with organizational tenant scoping.
- 📄 **Multi-Format Ingestion**: Process PDF, DOCX, PPTX, XLSX, Markdown, CSV, and plain text files with automatic clean chunking and pre-warmed embeddings.
- ⚡ **Sync & Async Ingestion**: Real-time synchronous ingestion for fast files and Celery background workers for large batch workloads.
- 🔄 **Cascading KB Reindexing & Deletion**: Intelligently reindex or purge documents, upload records, and corresponding vector payloads cleanly.

### 🔍 Search & RAG Orchestration
- 🎯 **Hybrid Search**: Dense vector retrieval via Qdrant + Sparse keyword matching via Elasticsearch/BM25 with Reciprocal Rank Fusion (RRF).
- 🎛️ **Targeted Domain Filtering**: Filter RAG chat queries down to a specific `knowledge_base_id` or query globally across tenant assets.
- 🤖 **Multi-LLM Support**: Built-in integrations for Google Gemini, Groq, and OpenAI-compatible models.
- 🎯 **Cross-Encoder Reranking**: Opt-in re-ranking model for maximum retrieval precision.

### 📊 Enterprise Analytics & Dashboard
- 📈 **Query Analytics**: Track query frequencies, context document usages, and latency breakdowns ($p_{50}, p_{95}, p_{99}$).
- 📊 **Usage Metrics**: Daily throughput summaries, page count indexing tracking, and vector volume statistics.
- ⚡ **Real-time System Status**: Health monitoring across FastAPI, Postgres, Qdrant, Redis, and Elasticsearch.

### 🎨 Frontend & Design System
- 🎨 **Modern Minimalist UI**: Built with React 18, TypeScript, Tailwind CSS, and Framer Motion micro-animations.
- 💬 **Interactive RAG Chat Interface**: Real-time streaming response layout with verifiable inline citation badges and source snippets.
- 📱 **Responsive Dashboard**: Mobile, tablet, and desktop views for overview metrics, document upload pipelines, and workspace settings.

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        Frontend (React 18 + TS)                         │
│   • Home / Login   • Chat Interface   • Upload   • Analytics / Dashboard  │
└────────────────────────────────────┬────────────────────────────────────┘
                                     │ REST API (/api/v1)
┌────────────────────────────────────▼────────────────────────────────────┐
│                        Backend (FastAPI Engine)                         │
│   • Auth & Tenant   • Knowledge Base Mgr   • Hybrid RAG   • Analytics    │
└─────────┬───────────────────┬──────────────────────┬────────────────────┘
          │                   │                      │
    ┌─────▼─────┐       ┌─────▼─────┐          ┌─────▼─────┐
    │  Qdrant   │       │Elasticsearch│        │ PostgreSQL│
    │  Vector   │       │  BM25 /     │        │  Metadata │
    │   Store   │       │  Keyword    │        │  Store    │
    └───────────┘       └───────────┘          └───────────┘
```

---

## 📋 Table of Contents

- [Quick Start](#-quick-start)
  - [Prerequisites](#prerequisites)
  - [Backend Setup](#backend-setup)
  - [Frontend Setup](#frontend-setup)
  - [Docker Setup](#docker-setup)
- [Project Structure](#-project-structure)
- [Configuration](#-configuration)
- [API Documentation](#-api-documentation)
- [Testing](#-testing)
- [License](#-license)

---

## 🚀 Quick Start

### Prerequisites

- **Python 3.11+**
- **Node.js 18+** & npm / yarn / pnpm
- **PostgreSQL 14+**
- **Qdrant** vector database (port `6333`)
- **Redis** for task queuing and caching (port `6379`)
- **Elasticsearch 8+** (optional, for sparse keyword retrieval)

---

### Backend Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/majhisamrat/Enterprise-RAG.git
   cd Enterprise-RAG
   ```

2. **Create & activate virtual environment**
   ```bash
   # On Windows
   python -m venv .venv
   .venv\Scripts\activate

   # On macOS/Linux
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment configuration**
   ```bash
   cp .env.example .env
   ```

   Configure required keys in `.env`:
   ```env
   # Database & Storage
   DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/enterprise_rag
   REDIS_URL=redis://localhost:6379/0
   QDRANT_URL=http://localhost:6333

   # LLM Providers
   GOOGLE_API_KEY=your_gemini_api_key
   GROQ_API_KEY=your_groq_api_key

   # Security
   JWT_SECRET_KEY=your_secret_jwt_key
   ```

5. **Run database migrations**
   ```bash
   alembic upgrade head
   ```

6. **Start the backend development server**
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```
   - REST API Base: `http://localhost:8000/api/v1`
   - Interactive Swagger Docs: `http://localhost:8000/docs`

---

### Frontend Setup

1. **Navigate to the frontend directory**
   ```bash
   cd enterprise-rag-frontend
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Environment configuration**
   ```bash
   cp .env.example .env.local
   ```
   Set API URL in `.env.local`:
   ```env
   VITE_API_BASE_URL=http://localhost:8000/api/v1
   ```

4. **Start the frontend development server**
   ```bash
   npm run dev
   ```
   - Frontend Application: `http://localhost:5173`

---

### Docker Setup

To launch the full stack with dependencies using Docker Compose:

```bash
docker-compose up -d
```

- **Frontend App**: `http://localhost:3000`
- **Backend API**: `http://localhost:8000`
- **Qdrant Dashboard**: `http://localhost:6333/dashboard`

---

## 📁 Project Structure

```
Enterprise-RAG/
├── app/                          # FastAPI Backend
│   ├── api/                      # API router & route modules
│   │   ├── routes/
│   │   │   ├── analytics.py      # Usage & performance analytics
│   │   │   ├── auth.py           # Registration & JWT authentication
│   │   │   ├── chat.py           # RAG chat & query orchestration
│   │   │   ├── health.py         # System status & diagnostic health check
│   │   │   ├── knowledge.py      # Knowledge Base CRUD & upload management
│   │   │   └── upload.py         # Document upload ingestion endpoint
│   │   ├── dependencies.py      # Dependency injection & tenant contexts
│   │   └── router.py            # Central APIRouter definition
│   ├── config/                   # App settings & environment parameters
│   ├── db/                       # SQLAlchemy models & repository layer
│   │   ├── models.py            # Database tables (KnowledgeBase, Upload, QueryLog, etc.)
│   │   └── repositories/        # Data access repositories
│   ├── embeddings/              # Embedding generation models
│   ├── ingestion/               # Parsers, cleaners, and chunkers
│   ├── llm/                     # Provider integrations (Gemini, Groq, OpenAI)
│   ├── orchestrator/            # Core RAG retrieval & prompt building engine
│   ├── reranker/                # Cross-encoder reranking
│   ├── retrieval/               # Dense, sparse, hybrid search & RRF score fusion
│   ├── storage/                 # File storage & uploads manager
│   ├── vectorstore/             # Qdrant client wrappers
│   └── main.py                  # FastAPI application entry point & CORS
│
├── enterprise-rag-frontend/     # React 18 + TypeScript Frontend
│   ├── src/
│   │   ├── api/                # Axios API service hooks
│   │   ├── components/         # Reusable UI, chat, and upload components
│   │   ├── layouts/            # Dashboard layout & navigation sidebar
│   │   ├── pages/              # App pages (Home, Chat, Dashboard, Upload, Analytics, Settings)
│   │   ├── routes/             # React Router configuration
│   │   ├── store/              # Zustand state stores
│   │   └── styles/             # Tailwind CSS & global styling
│   └── vite.config.ts           # Vite build configuration
│
├── alembic/                     # Database migrations
├── scripts/                     # Data migration & utility scripts
├── tests/                       # E2E & unit test suites
├── docker-compose.yml           # Multi-container docker stack
└── README.md                    # Project documentation
```

---

## 📚 API Documentation

Once the backend is running, browse interactive docs at `http://localhost:8000/docs`.

### Core API Endpoints Overview

| Scope | Method | Endpoint | Description |
|---|---|---|---|
| **Health** | `GET` | `/api/v1/health` | System status check |
| **Auth** | `POST` | `/api/v1/auth/register` | Register new user |
| **Auth** | `POST` | `/api/v1/auth/login` | Login and receive JWT |
| **Auth** | `GET` | `/api/v1/auth/me` | Fetch active profile |
| **Knowledge** | `POST` | `/api/v1/knowledge` | Create Knowledge Base |
| **Knowledge** | `GET` | `/api/v1/knowledge` | List Knowledge Bases |
| **Knowledge** | `GET` | `/api/v1/knowledge/{kb_id}` | Get KB details & upload list |
| **Knowledge** | `DELETE` | `/api/v1/knowledge/{kb_id}` | Delete KB and cascade vectors |
| **Knowledge** | `POST` | `/api/v1/knowledge/{kb_id}/upload` | Upload file to Knowledge Base |
| **Knowledge** | `GET` | `/api/v1/knowledge/{kb_id}/history` | Get KB upload history |
| **Knowledge** | `GET` | `/api/v1/knowledge/{kb_id}/statistics` | Get KB indexing statistics |
| **Knowledge** | `POST` | `/api/v1/knowledge/{kb_id}/reindex` | Trigger Celery KB re-indexing |
| **Chat** | `POST` | `/api/v1/chat/` | RAG query with optional KB filtering |
| **Analytics** | `GET` | `/api/v1/analytics/dashboard` | Workspace summary dashboard |
| **Analytics** | `GET` | `/api/v1/analytics/queries` | Query latency & retrieval metrics |
| **Analytics** | `GET` | `/api/v1/analytics/usage` | Time-series usage breakdown |
| **Analytics** | `GET` | `/api/v1/analytics/performance` | Percentile latency stats ($p_{50}, p_{95}, p_{99}$) |

---

## 🧪 Testing

Run test suites using `pytest`:

```bash
# Run all tests
pytest

# Run End-to-End Enterprise RAG tests
pytest tests/test_enterprise_rag_e2e.py -v
```

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
