# ⚡ Celery Quick Guide

**TL;DR:** Celery = Background job processor for long tasks

---

## 🔄 Simple Flow

```
User uploads CSV
    ↓
FastAPI: "I'll process this in background" ✅
    ↓
Redis: Stores job in queue
    ↓
Celery Worker: "I got it, processing..."
    ↓
(While processing, user can do other things)
    ↓
Celery: "Done! Results stored in DB"
    ↓
User: "Let me check the status"
    ↓
App: "Job completed, 15 chunks processed"
```

---

## 🎯 3 Key Components

### 1. FastAPI (Producer)
```python
# When user uploads file
task = ingest_document.delay(file_path, kb_id)
# Returns immediately - doesn't wait!
return {"job_id": task.id}
```

### 2. Redis (Message Broker)
```
Queue holds all pending tasks:
- Task 1: ingest_document(file1.csv)
- Task 2: ingest_document(file2.csv)
- Task 3: ingest_document(file3.csv)
```

### 3. Celery Worker (Consumer)
```
Worker listens to Redis:
1. See task
2. Process it
3. Store result
4. Go back to step 1
```

---

## 📈 Why It's Better

### Before Celery ❌
```
User uploads 10MB CSV
→ Server waits 30 seconds
→ User sees loading spinner
→ Request might timeout
→ User frustrated
```

### With Celery ✅
```
User uploads 10MB CSV
→ Server responds in 0.5 seconds
→ User can upload another file
→ Processing happens in background
→ User checks status later
→ User happy
```

---

## 🚀 In Your Docker Setup

```
enterprise_rag_redis:
  Message queue (holds jobs)
  
enterprise_rag_backend:
  FastAPI app (creates jobs)
  
enterprise_rag_celery:
  Worker (processes jobs)
```

**How they talk:**

```
backend → Redis queue → celery worker
  ↓                        ↓
(return response)    (process CSV)
                          ↓
                    (store in DB)
```

---

## 🔍 What Celery Does

When document is uploaded:

1. **Parse CSV**
   - Read file content
   - Extract rows and columns

2. **Schema Discovery (ATLAS)**
   - Detect column types
   - Identify semantic roles
   - Store in PostgreSQL

3. **Generate Embeddings**
   - Convert text to vectors
   - Using Sentence-Transformers
   - 384-dimensional vectors

4. **Store in Qdrant**
   - Save vectors
   - For semantic search

5. **Store in DuckDB**
   - Save raw rows
   - For structured queries

6. **Index in Elasticsearch**
   - For keyword search

**All this happens asynchronously** ✅

---

## 💻 Commands to Monitor

### View running tasks
```bash
# Connect to container
docker exec -it enterprise_rag_celery bash

# List active tasks
celery -A app.tasks inspect active
```

### View logs
```bash
# Real-time logs
docker logs enterprise_rag_celery -f

# Shows:
# - Tasks received
# - Tasks processing
# - Tasks completed
# - Any errors
```

### Check task status
```bash
# From app
GET /api/v1/jobs/{job_id}

Response:
{
  "status": "completed",
  "result": {
    "chunks": 15,
    "vectors_stored": 15
  }
}
```

---

## 🎯 Task Status Values

| Status | Meaning | Action |
|--------|---------|--------|
| PENDING | Waiting in queue | Nothing yet |
| STARTED | Being processed | In progress... |
| PROGRESS | Still processing | X% done |
| SUCCESS | Completed | Results ready |
| FAILURE | Error occurred | Check logs |
| RETRY | Failed, retrying | Trying again |

---

## 📊 Performance Gains

**Single CSV upload (10MB):**

| Without Celery | With Celery |
|---|---|
| API response: 30s | API response: 0.5s |
| User waits: 30s | User waits: 0s |
| Can upload 1 file | Can upload 10 files |
| Concurrent limit: 1 | Concurrent limit: Many |

---

## 🔧 Common Tasks

### Check if Celery is running
```bash
docker ps | grep celery
# Should show: enterprise_rag_celery ... Up

docker logs enterprise_rag_celery
# Should show: worker online
```

### Restart Celery
```bash
docker restart enterprise_rag_celery
```

### View all pending tasks
```bash
docker exec enterprise_rag_celery \
  celery -A app.tasks inspect pending
```

### Clear all tasks
```bash
docker exec enterprise_rag_celery \
  celery -A app.tasks purge
```

---

## 🚨 Common Issues

### Celery not processing tasks
1. Check Redis is running: `docker ps | grep redis`
2. Check Celery is running: `docker ps | grep celery`
3. Restart both: `docker restart enterprise_rag_redis enterprise_rag_celery`

### Tasks failing
1. Check logs: `docker logs enterprise_rag_celery`
2. Common causes:
   - PostgreSQL not ready
   - Qdrant not responding
   - File permissions

### Connection refused
1. Redis running? `docker ps | grep redis`
2. Network OK? `docker network inspect enterprise_rag`
3. URL correct? `REDIS_URL=redis://redis:6379/0`

---

## 🎉 You Now Have

✅ **Async document ingestion** - No more waiting!  
✅ **Parallel processing** - Multiple files at once  
✅ **Background jobs** - Celery handles it  
✅ **Scalable** - Add more workers as needed  
✅ **Resilient** - Redis persists tasks  
✅ **Monitorable** - Check status anytime  

---

## 🚀 Next Steps

1. **Start everything:**
```bash
docker-compose -f docker-compose.backend.improved.yml up -d
```

2. **Upload a CSV:**
```
Go to http://localhost:8000
Create KB
Upload file
```

3. **Check Celery logs:**
```bash
docker logs enterprise_rag_celery -f
```

4. **Watch the magic:**
```
See: Received task
See: Processing...
See: Task succeeded
```

---

**Status: CELERY READY TO USE** ✅

**Docker containers running:**
- ✅ enterprise_rag_redis (broker)
- ✅ enterprise_rag_celery (worker)
- ✅ enterprise_rag_backend (API)

**All async tasks working!** 🎉
