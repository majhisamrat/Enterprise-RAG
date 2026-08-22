# ATLAS - Enterprise AI-Powered Document Intelligence Platform

![ATLAS Logo](https://img.shields.io/badge/ATLAS-Enterprise%20RAG-blue?style=flat-square&logo=brain)

**ATLAS** is a production-grade, enterprise-ready Retrieval-Augmented Generation (RAG) platform that transforms how organizations extract insights from their knowledge bases. Built for scale, security, and intelligence—enabling teams to unlock the power of their documents through conversational AI.

[![Python](https://img.shields.io/badge/Python-3.13+-blue.svg?style=flat-square)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green.svg?style=flat-square)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-18.3+-blue.svg?style=flat-square)](https://reactjs.org/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.0+-blue.svg?style=flat-square)](https://www.typescriptlang.org/)
[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED.svg?style=flat-square)](https://www.docker.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg?style=flat-square)](LICENSE)

---

## 🎯 The Problem We Solve

**Enterprise Knowledge Chaos:**
- ❌ Employees spend 20% of their workday searching for information
- ❌ Critical documents scattered across multiple systems with no unified search
- ❌ Knowledge silos prevent collaboration and institutional learning
- ❌ Traditional search can't understand context or semantic meaning
- ❌ Legacy RAG systems lack enterprise security & multi-tenant isolation

**ATLAS solves this** by building an intelligent document AI layer that's secure, scalable, and enterprise-ready from day one.

---

## ✨ Why ATLAS?

### 🚀 **Lightning-Fast Deployment**
- One-click EC2 deployment with Docker Compose
- Pre-built infrastructure for hybrid cloud/on-prem setups
- Vercel frontend + AWS backend in minutes

### 🔐 **Enterprise-Grade Security**
- **Multi-tenant isolation**: Complete org/workspace separation
- **OTP email verification**: Secure manual registration + forgot password
- **Role-based access control**: Team-level knowledge base permissions
- **GDPR-compliant**: Full audit trails and data retention policies
- **JWT authentication**: Stateless, horizontally scalable auth

### 🧠 **Intelligent Search**
- **Hybrid retrieval**: Dense vectors (semantic) + sparse keywords (BM25)
- **Structured data queries**: CSV/Excel natural language SQL generation
- **Multi-format**: PDF, DOCX, PPTX, Excel, CSV, Markdown
- **Smart chunking**: Pattern detection for records, tables, etc.
- **Auto-reranking**: Cross-encoder maximizes accuracy

### 📊 **Real-Time Analytics**
- **Query insights**: What your teams search for
- **Performance tracking**: p50, p95, p99 latencies
- **Usage dashboards**: Throughput, vectors, uploads
- **System health**: Real-time service monitoring

### 🎨 **Beautiful UI/UX**
- **Chat interface**: Real-time responses with citations
- **Bulk uploads**: Drag-and-drop with progress tracking
- **Organization**: Semantic grouping with custom tags
- **Session management**: Multi-turn conversations + history
- **Mobile friendly**: Desktop, tablet, mobile support

---

## 🌟 Key Features

### 📚 **Knowledge Base Management**
- Create unlimited knowledge bases (organize by dept, project, client)
- Hierarchical organization with custom tags and metadata
- Per-KB access controls and sharing policies
- Automatic document versioning
- Bulk reindexing across all documents

### 💬 **Intelligent Chat**
- Ask in natural language, get instant answers
- Auto-routes to structured vs semantic data
- Inline citations showing answer sources
- Context-aware multi-turn conversations
- Auto-generated session titles

### 📄 **Smart Document Processing**
- **Multi-format**: PDF, DOCX, PPTX, Excel, CSV, Markdown, text
- **Auto-OCR**: Detects scanned PDFs and OCRs automatically
- **Smart chunking**: Context-preserving segmentation
- **Metadata extraction**: Author, title, dates detected
- **Duplicate detection**: Prevents re-indexing
- **Async processing**: Large files in background

### 🔍 **Powerful Search**
- **Hybrid search**: Semantic + keyword matching combined
- **Smart filtering**: By KB, type, date range
- **Relevance tuning**: Adjust vector vs keyword weight
- **Structured queries**: NL-to-SQL for Excel/CSV
- **Real-time**: Documents searchable in seconds

### 📈 **Analytics & Insights**
- **Query dashboard**: Most asked questions, trending topics
- **Performance**: Response times, accuracy metrics
- **Usage trends**: Upload volume, search frequency
- **System health**: Container status, resources
- **Export**: Download reports as CSV/JSON

### 👥 **Multi-Tenant Architecture**
- Complete workspace isolation
- Organization-level settings
- Department-based grouping
- User invitation and roles
- Compliance audit logs

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│     FRONTEND (React 18 + TypeScript + Tailwind CSS)             │
│  Chat | Upload | Analytics | Settings                          │
│  Deployed: Vercel (Global CDN)                                  │
└────────────────────┬────────────────────────────────────────────┘
                     │ REST API v1
┌────────────────────▼────────────────────────────────────────────┐
│     BACKEND (FastAPI + Python 3.13)                             │
│  Auth | RAG Orchestration | Analytics | Multi-tenancy           │
│  Deployed: EC2 + Docker Compose                                 │
├──────────┬──────────────────┬──────────────┬────────────────────┤
│          │                  │              │                    │
│  ┌───────▼────┐  ┌─────────▼──┐  ┌────────▼─┐  ┌─────────┐   │
│  │ Qdrant     │  │PostgreSQL  │  │ Celery   │  │ Redis   │   │
│  │ Vectors    │  │ Metadata   │  │ Workers  │  │ Cache   │   │
│  └────────────┘  └────────────┘  └──────────┘  └─────────┘   │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │     Elasticsearch (Full-Text Search)                    │  │
│  │  Hybrid Retrieval + Reciprocal Rank Fusion (RRF)       │  │
│  └─────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

### Data Flow:
1. **Upload** → Parsed, cleaned, chunked → Stored in `/app/data`
2. **Ingestion** → Celery processes async → Embeddings generated
3. **Indexing** → Vectors in Qdrant, keywords in Elasticsearch
4. **Query** → Routes semantic vs structured → Retrieves + Re-ranks
5. **Response** → LLM generates answer → Frontend shows with sources

---

## 📋 Quick Start

### Prerequisites

- **Python 3.11+** (3.13 recommended)
- **Node.js 18+** with npm/yarn/pnpm
- **Docker & Docker Compose**
- **AWS EC2** (Ubuntu 22.04 recommended)
- **API Keys**: Groq, Google Gemini, or OpenAI

---

### Local Development (5 minutes)

#### 1. Setup Backend

```bash
# Clone
git clone https://github.com/majhisamrat/Enterprise-RAG.git
cd Enterprise-RAG

# Virtual env
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install
pip install -r requirements.txt

# Configure
cp .env.example .env
# Edit .env with your API keys

# Migrate
alembic upgrade head

# Run
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Backend ready:** http://localhost:8000/docs

#### 2. Full Stack with Docker

```bash
# Start all (PostgreSQL, Redis, Qdrant, Elasticsearch, Backend, Celery)
docker-compose -f docker-compose.backend.improved.yml up -d

# Check status
docker-compose -f docker-compose.backend.improved.yml ps

# View logs
docker-compose -f docker-compose.backend.improved.yml logs -f backend celery
```

**Services:**
- FastAPI: http://localhost:8000
- Qdrant: http://localhost:6333/dashboard
- Elasticsearch: http://localhost:9200

---

### 🌐 Production Deployment (EC2)

#### 1. Launch EC2

```bash
# Recommended: Ubuntu 22.04 LTS, t3.medium
# Security: Allow 22 (SSH), 80 (HTTP), 443 (HTTPS), 8000 (API)
```

#### 2. Deploy Backend

```bash
ssh -i "your-key.pem" ubuntu@your-ec2-ip

git clone https://github.com/majhisamrat/Enterprise-RAG.git
cd Enterprise-RAG

nano .env  # Add production config

docker-compose -f docker-compose.backend.improved.yml up -d

# Verify
curl http://localhost:8000/api/v1/health
```

#### 3. Deploy Frontend (Vercel)

```bash
npm install -g vercel
cd frontend
vercel --prod

# Set in Vercel Dashboard:
# VITE_API_URL=https://your-ec2-domain.com
# VITE_GOOGLE_CLIENT_ID=your_id
```

#### 4. Setup SSL & Domain

```bash
# DuckDNS (free dynamic DNS) or Route53
# Nginx reverse proxy + Let's Encrypt SSL
```

---

## 📚 API Documentation

Interactive Swagger at `/docs` endpoint.

### Essential Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/v1/health` | GET | System status |
| `/api/v1/auth/register-init` | POST | Start OTP registration |
| `/api/v1/auth/register-verify` | POST | Complete with OTP |
| `/api/v1/knowledge` | POST | Create KB |
| `/api/v1/knowledge/{kb_id}/upload` | POST | Upload document |
| `/api/v1/chat` | POST | RAG query |
| `/api/v1/analytics/dashboard` | GET | Metrics |

---

## 🔧 Configuration

### Environment Variables

```env
# API
HOST=0.0.0.0
PORT=8000
DEBUG=False

# Database
DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/enterprise_rag
REDIS_URL=redis://localhost:6379/0

# Vector DB
QDRANT_URL=http://localhost:6333
ELASTICSEARCH_URL=http://localhost:9200

# LLM (choose one)
GROQ_API_KEY=gsk_...
GROQ_MODEL=llama-3.3-70b-versatile

# Frontend
VITE_API_URL=https://your-backend.com
FRONTEND_URL=https://your-frontend.com

# Email (OTP)
SMTP_HOST=smtp.gmail.com
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
OTP_EXPIRE_MINUTES=5

# Security
SECRET_KEY=your-secret-key
ACCESS_TOKEN_EXPIRE_MINUTES=60
```

---

## 📦 Tech Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **Backend** | FastAPI + SQLAlchemy | REST API & business logic |
| **Frontend** | React 18 + TypeScript + Tailwind | Web UI |
| **Vector DB** | Qdrant | Semantic search |
| **Full-text** | Elasticsearch | Keyword search |
| **Metadata** | PostgreSQL | Users, KBs, documents |
| **Cache** | Redis | Sessions, rate limiting |
| **Workers** | Celery | Async document processing |
| **LLM** | Groq/Gemini/OpenAI | Response generation |

---

## 🎓 Use Cases

### Sales & Marketing
- Find past proposals, contracts, customer emails
- Generate personalized pitches from company docs
- Track competitor intelligence

### Support & Customer Success
- Instant answers to FAQs
- Search ticket resolutions
- Faster team onboarding

### Legal & Compliance
- Search contract clauses
- Find relevant precedents
- Audit document access

### Research & Development
- Query research papers
- Extract key findings
- Track experimental results

### HR & Operations
- Search handbook and policies
- Find templates
- Quick compliance answers

---

## 🚀 Roadmap

- [ ] **v2.0**: Multi-model fine-tuning for custom domains
- [ ] **v2.1**: Real-time document collaboration
- [ ] **v2.2**: Advanced permissions & audit logging
- [ ] **v2.3**: Slack, Teams, Discord integrations
- [ ] **v3.0**: Mobile app (iOS/Android)

---

## 🤝 Support

- **Docs**: [atlas-ai.com/docs](https://atlas-ai.com/docs)
- **Email**: support@atlas-ai.com
- **Discord**: [Join Community](https://discord.gg/atlas)
- **GitHub Issues**: [Report bugs](https://github.com/majhisamrat/Enterprise-RAG/issues)

---

## 📄 License

MIT License - see [LICENSE](LICENSE) file

---

## 🙏 Acknowledgments

Built with 🧠 by ATLAS team. Powered by Groq, Qdrant, and open-source communities.

---

**Ready to transform your enterprise knowledge? [Launch ATLAS today →](https://atlas-nine-blue.vercel.app)**
