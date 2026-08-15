# 🚀 Complete Services Setup Guide

**Objective:** Start PostgreSQL, Qdrant, Elasticsearch, and Redis/Celery  
**Time Required:** 15-20 minutes  
**Platform:** Windows with Docker Desktop  

---

## Prerequisites

- [ ] Docker Desktop installed and running
- [ ] PowerShell or Command Prompt
- [ ] Python 3.10+
- [ ] `enterprise-rag` project ready

---

## Step 1: Start PostgreSQL

### Option A: Docker (Recommended)

**Create PostgreSQL container:**

```bash
docker run --name enterprise-postgres \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=password123 \
  -e POSTGRES_DB=enterprise_rag \
  -p 5432:5432 \
  -d \
  postgres:15-alpine
```

**Verify it's running:**

```bash
docker ps | grep enterprise-postgres
```

Expected output:
```
enterprise-postgres ... postgres:15-alpine Up 2 minutes
```

**Test connection:**

```bash
psql -h localhost -U postgres -d enterprise_rag -c "SELECT 1;"
```

If `psql` not installed, skip this test (Docker knows it's running).

---

### Option B: Local PostgreSQL Installation

If you prefer local installation (not Docker):

1. **Download:** https://www.postgresql.org/download/windows/
2. **Install** with default settings
3. **Create database:**

```sql
CREATE DATABASE enterprise_rag;
```

4. **Verify connection:**

```bash
psql -h localhost -U postgres -d enterprise_rag -c "SELECT 1;"
```

---

## Step 2: Start Qdrant Vector Store

### Docker (Recommended)

```bash
docker run --name enterprise-qdrant \
  -p 6333:6333 \
  -p 6334:6334 \
  -d \
  qdrant/qdrant:latest
```

**Verify it's running:**

```bash
docker ps | grep enterprise-qdrant
```

**Test connection:**

```bash
curl http://localhost:6333/health
```

Expected response:
```json
{"status":"ok"}
```

---

## Step 3: Start Elasticsearch

### Docker (Recommended)

```bash
docker run --name enterprise-elasticsearch \
  -e discovery.type=single-node \
  -e xpack.security.enabled=false \
  -p 9200:9200 \
  -p 9300:9300 \
  -d \
  docker.elastic.co/elasticsearch/elasticsearch:8.11.0
```

**Verify it's running:**

```bash
docker ps | grep enterprise-elasticsearch
```

**Test connection:**

```bash
curl http://localhost:9200/
```

Expected response:
```json
{
  "name": "...",
  "cluster_name": "docker-cluster",
  "version": {...}
}
```

---

## Step 4: Start Redis & Celery

### Step 4A: Start Redis

```bash
docker run --name enterprise-redis \
  -p 6379:6379 \
  -d \
  redis:7-alpine
```

**Verify it's running:**

```bash
docker ps | grep enterprise-redis
```

**Test connection:**

```bash
docker exec enterprise-redis redis-cli ping
```

Expected: `PONG`

---

### Step 4B: Start Celery Worker

Open a new terminal and run:

```bash
cd c:\Users\Samratmajhi\Downloads\enterprise-rag

# Activate virtual environment (if you have one)
# .venv\Scripts\Activate.ps1

# Start Celery worker
celery -A app.tasks worker --loglevel=info
```

You should see:
```
 -------------- celery@HOSTNAME v5.x.x (opal)
--- ***** -----
-- ******* ----
- *** --- * ---
- ** ---------- [config]
- ** ----------
- *** --- * --- celery@HOSTNAME v5.x.x
- ** ---------- [queues]
- ** ----------
- *** --- * --- .
-------------- [2026-08-12 HH:MM:SS,000: WARNING/MainProcess]
```

**Keep this terminal open.** Celery will run in the foreground.

---

## Step 5: Verify All Services

Run this verification script in a new PowerShell window:

```powershell
# Save as: verify_services.ps1

Write-Host "🔍 Verifying All Services..." -ForegroundColor Cyan
Write-Host ""

# 1. PostgreSQL
Write-Host "1️⃣  PostgreSQL" -ForegroundColor Yellow
try {
    docker exec enterprise-postgres pg_isready -U postgres -d enterprise_rag 2>&1
    Write-Host "   ✅ PostgreSQL is running on localhost:5432" -ForegroundColor Green
} catch {
    Write-Host "   ❌ PostgreSQL not responding" -ForegroundColor Red
}

# 2. Qdrant
Write-Host "2️⃣  Qdrant" -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://localhost:6333/health" -ErrorAction Stop
    Write-Host "   ✅ Qdrant is running on localhost:6333" -ForegroundColor Green
} catch {
    Write-Host "   ❌ Qdrant not responding" -ForegroundColor Red
}

# 3. Elasticsearch
Write-Host "3️⃣  Elasticsearch" -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://localhost:9200/" -ErrorAction Stop
    Write-Host "   ✅ Elasticsearch is running on localhost:9200" -ForegroundColor Green
} catch {
    Write-Host "   ❌ Elasticsearch not responding" -ForegroundColor Red
}

# 4. Redis
Write-Host "4️⃣  Redis" -ForegroundColor Yellow
try {
    docker exec enterprise-redis redis-cli ping | Out-Null
    Write-Host "   ✅ Redis is running on localhost:6379" -ForegroundColor Green
} catch {
    Write-Host "   ❌ Redis not responding" -ForegroundColor Red
}

# 5. Celery
Write-Host "5️⃣  Celery" -ForegroundColor Yellow
Write-Host "   ⏳ Check Celery terminal - should show 'worker online'" -ForegroundColor Yellow

Write-Host ""
Write-Host "✅ Service Setup Complete!" -ForegroundColor Green
```

Save and run:

```bash
.\verify_services.ps1
```

---

## Step 6: Update .env (if needed)

Your `.env` already has correct settings:

```bash
# Database
DATABASE_URL=postgresql+asyncpg://postgres:password123@localhost:5432/enterprise_rag
SYNC_DATABASE_URL=postgresql+psycopg2://postgres:password123@localhost:5432/enterprise_rag

# Qdrant
QDRANT_URL=http://localhost:6333

# Elasticsearch
ELASTICSEARCH_URL=http://localhost:9200

# Redis (for Celery)
REDIS_URL=redis://localhost:6379/0
```

✅ No changes needed.

---

## Step 7: Run Database Migrations

After PostgreSQL is running:

```bash
cd c:\Users\Samratmajhi\Downloads\enterprise-rag

# Run migrations
alembic upgrade head
```

Expected output:
```
INFO  [alembic.runtime.migration] Context impl PostgresqlImpl.
INFO  [alembic.runtime.migration] Will assume transactional DDL.
INFO  [alembic.runtime.migration] Running upgrade... -> ...
```

---

## Step 8: Start the FastAPI Application

In a new terminal:

```bash
cd c:\Users\Samratmajhi\Downloads\enterprise-rag

# Activate venv if needed
# .venv\Scripts\Activate.ps1

# Start the app
python -m uvicorn app.app_config:app --reload --host 0.0.0.0 --port 8000
```

Expected output:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete
```

---

## Step 9: Test Full Integration

### Upload a CSV file

```bash
curl -X POST "http://localhost:8000/api/v1/knowledge/YOUR_KB_ID/upload" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@sales.csv"
```

### Check logs

You should see in the app terminal:
```
✅ Starting document ingestion
✅ Parsing document
✅ Text cleaning completed
✅ Generated embeddings
✅ Qdrant collection ensured
✅ Upserting to Qdrant
✅ Elasticsearch index check/creation
✅ Successfully ingested document
```

---

## 🚨 Troubleshooting

### PostgreSQL Connection Failed

```bash
# Check if container is running
docker ps | grep enterprise-postgres

# If not, restart it
docker start enterprise-postgres

# Check logs
docker logs enterprise-postgres

# Reset if corrupted
docker stop enterprise-postgres
docker rm enterprise-postgres
# Then run the docker run command again
```

### Qdrant Not Connecting

```bash
# Check if running
docker ps | grep enterprise-qdrant

# Check logs
docker logs enterprise-qdrant

# Restart
docker restart enterprise-qdrant
```

### Elasticsearch Not Connecting

```bash
# Check if running
docker ps | grep enterprise-elasticsearch

# Check logs
docker logs enterprise-elasticsearch

# Restart
docker restart enterprise-elasticsearch
```

### Redis Not Connecting

```bash
# Check if running
docker ps | grep enterprise-redis

# Test ping
docker exec enterprise-redis redis-cli ping

# Restart
docker restart enterprise-redis
```

### Celery Not Working

Make sure you're running:
```bash
celery -A app.tasks worker --loglevel=info
```

And Redis is running (docker ps should show enterprise-redis).

---

## 📋 Complete Setup Checklist

Terminal 1 - PostgreSQL (Docker):
```bash
docker run --name enterprise-postgres \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=password123 \
  -e POSTGRES_DB=enterprise_rag \
  -p 5432:5432 \
  -d \
  postgres:15-alpine
```
- [ ] Container running: `docker ps | grep enterprise-postgres`

Terminal 2 - Qdrant (Docker):
```bash
docker run --name enterprise-qdrant \
  -p 6333:6333 \
  -p 6334:6334 \
  -d \
  qdrant/qdrant:latest
```
- [ ] Container running: `docker ps | grep enterprise-qdrant`
- [ ] Health check: `curl http://localhost:6333/health`

Terminal 3 - Elasticsearch (Docker):
```bash
docker run --name enterprise-elasticsearch \
  -e discovery.type=single-node \
  -e xpack.security.enabled=false \
  -p 9200:9200 \
  -p 9300:9300 \
  -d \
  docker.elastic.co/elasticsearch/elasticsearch:8.11.0
```
- [ ] Container running: `docker ps | grep enterprise-elasticsearch`
- [ ] Health check: `curl http://localhost:9200/`

Terminal 4 - Redis (Docker):
```bash
docker run --name enterprise-redis \
  -p 6379:6379 \
  -d \
  redis:7-alpine
```
- [ ] Container running: `docker ps | grep enterprise-redis`
- [ ] Health check: `docker exec enterprise-redis redis-cli ping`

Terminal 5 - Celery Worker:
```bash
cd c:\Users\Samratmajhi\Downloads\enterprise-rag
celery -A app.tasks worker --loglevel=info
```
- [ ] Worker running (see "worker online" in logs)

Terminal 6 - FastAPI App:
```bash
cd c:\Users\Samratmajhi\Downloads\enterprise-rag
python -m uvicorn app.app_config:app --reload
```
- [ ] App running: `http://localhost:8000`

---

## ✅ Final Verification

All services ready when you see:

```
✅ PostgreSQL: localhost:5432
✅ Qdrant: localhost:6333
✅ Elasticsearch: localhost:9200
✅ Redis: localhost:6379
✅ Celery: worker online
✅ FastAPI: http://localhost:8000
```

---

## 🎯 Quick Start (Copy-Paste)

**Run these commands in separate terminals:**

```bash
# Terminal 1: PostgreSQL
docker run --name enterprise-postgres -e POSTGRES_USER=postgres -e POSTGRES_PASSWORD=password123 -e POSTGRES_DB=enterprise_rag -p 5432:5432 -d postgres:15-alpine

# Terminal 2: Qdrant
docker run --name enterprise-qdrant -p 6333:6333 -p 6334:6334 -d qdrant/qdrant:latest

# Terminal 3: Elasticsearch
docker run --name enterprise-elasticsearch -e discovery.type=single-node -e xpack.security.enabled=false -p 9200:9200 -p 9300:9300 -d docker.elastic.co/elasticsearch/elasticsearch:8.11.0

# Terminal 4: Redis
docker run --name enterprise-redis -p 6379:6379 -d redis:7-alpine

# Terminal 5: Celery (in project directory)
celery -A app.tasks worker --loglevel=info

# Terminal 6: FastAPI (in project directory)
python -m uvicorn app.app_config:app --reload
```

---

**Status:** Ready to start all services  
**Time to complete:** 15-20 minutes  
**Next step:** Follow the checklist above
