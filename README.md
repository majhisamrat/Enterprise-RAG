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
1. **Ingestion** → Celery processes async → Embeddings generated
2. **Indexing** → Vectors in Qdrant, keywords in Elasticsearch
3. **Query** → Routes semantic vs structured → Retrieves + Re-ranks
4. **Response** → LLM generates answer → Frontend shows with sources

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
