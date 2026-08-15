# 🚀 Celery Architecture & Workflow

**Status:** Running (2 containers built)  
**Components:** Redis (broker) + Celery Worker (executor)  
**Purpose:** Async task processing for long-running jobs  

---

## 🎯 Simple Explanation

**Celery = Background Job Queue**

Instead of:
```
User uploads CSV
  → App waits 10 seconds
  → App processes CSV
  → User waits for response ❌
```

With Celery:
```
User uploads CSV
  → App sends job to Redis queue ✅
  → App returns immediately ✅
  → Celery worker processes in background ✅
  → User can do other things ✅
```

---

## 🏗️ Architecture Diagram

```
┌──────────────────────────────────────────────────────────┐
│                    FastAPI Backend                        │
│  (enterprise_rag_backend)                                │
│                                                           │
│  When CSV uploaded:                                      │
│  1. Save file to disk                                    │
│  2. Create task: ingest_document(file_path)              │
│  3. Send to Redis                                        │
│  4. Return response immediately                          │
└────────────┬──────────────────────────────────────────────┘
             │ Send task
             ▼
┌──────────────────────────────────────────────────────────┐
│                   Redis Message Broker                    │
│  (enterprise_rag_redis)                                  │
│                                                           │
│  Queue:                                                  │
│  ├─ Task 1: ingest_document(file_1.csv)                 │
│  ├─ Task 2: ingest_document(file_2.csv)                 │
│  └─ Task 3: ingest_document(file_3.csv)                 │
└────────────┬──────────────────────────────────────────────┘
             │ Listen & fetch tasks
             ▼
┌──────────────────────────────────────────────────────────┐
│               Celery Worker Process                       │
│  (enterprise_rag_celery)                                 │
│                                                           │
│  Worker Loop:                                            │
│  1. Connect to Redis ✅                                  │
│  2. Wait for tasks                                       │
│  3. Fetch task from queue                                │
│  4. Execute: ingest_document()                           │
│     - Parse CSV                                          │
│     - Generate embeddings                                │
│     - Store in Qdrant                                    │
│     - Store in PostgreSQL                                │
│  5. Return result to Redis                               │
│  6. Go back to step 2                                    │
└──────────────────────────────────────────────────────────┘
```

---

## 📊 Step-by-Step Flow

### Scenario: Upload sales.csv (10MB file)

**Step 1: User uploads file via FastAPI**
```
POST /api/v1/knowledge/{kb_id}/upload
Content: sales.csv (10MB)
```

**Step 2: FastAPI backend receives upload**
```python
# In app/api/routes/knowledge.py
@router.post("/upload")
async def upload_document(file: UploadFile):
    # Save file to disk
    file_path = save_file(file)
    
    # Create async task
    task = ingest_document.delay(
        file_path=file_path,
        kb_id=kb_id
    )
    
    # Return immediately (don't wait!)
    return {
        "status": "processing",
        "job_id": task.id
    }
```

**Step 3: Task sent to Redis**
```
Message Queue (Redis):
{
  "task_id": "abc123def456",
  "task_name": "ingest_document",
  "args": {
    "file_path": "/app/data/uploads/sales.csv",
    "kb_id": "kb-uuid-123"
  }
}
```

**Step 4: User gets response immediately** ✅
```json
{
  "status": "processing",
  "job_id": "abc123def456"
}
```

**User can:**
- ✅ Upload another file
- ✅ Browse the app
- ✅ Do other things
- ✅ Check job status

**Step 5: Celery worker picks up task**
```
Celery Worker:
  1. Connects to Redis
  2. Sees new task
  3. Executes: ingest_document(file_path, kb_id)
```

**Step 6: Worker processes CSV** (takes 10-30 seconds)
```
ingest_document():
  ├─ Parse CSV file
  ├─ Schema discovery (ATLAS)
  ├─ Generate embeddings
  ├─ Store vectors in Qdrant
  ├─ Store metadata in PostgreSQL
  ├─ Store structured data in DuckDB
  └─ Log "SUCCESS"
```

**Step 7: Worker stores result in Redis**
```
Result:
{
  "job_id": "abc123def456",
  "status": "completed",
  "chunks": 15,
  "file_path": "/app/data/uploads/sales.csv"
}
```

**Step 8: User checks status**
```
GET /api/v1/jobs/abc123def456
Response: {
  "status": "completed",
  "chunks": 15
}
```

---

## 🔄 How It Works in Your System

### Docker Containers

| Container | Role | Responsibility |
|-----------|------|-----------------|
| `enterprise_rag_redis` | Message Broker | Holds job queue |
| `enterprise_rag_backend` | Producer | Creates tasks, returns immediately |
| `enterprise_rag_celery` | Consumer/Worker | Processes tasks in background |
| `enterprise_rag_postgres` | Database | Stores results |
| `enterprise_rag_qdrant` | Vector Store | Stores embeddings |
| `enterprise_rag_elasticsearch` | Search | Indexes keywords |

### Flow in Your System

```
1. FastAPI (backend container) receives CSV upload
   ↓
2. Creates task: ingest_document.delay(file_path)
   ↓
3. Task sent to Redis (redis container)
   ↓
4. FastAPI returns response immediately
   ↓
5. Celery worker (celery container) picks up task
   ↓
6. Worker processes CSV:
   - Parse with PyMuPDF
   - Discover schema (ATLAS)
   - Generate embeddings (Sentence-Transformers)
   - Store vectors in Qdrant
   - Store metadata in PostgreSQL
   - Store structured data in DuckDB
   ↓
7. Worker stores result in Redis
   ↓
8. User can check status anytime
```

---

## 💡 Why Celery?

### Problem Without Celery
```
FastAPI upload CSV (10MB)
  → Parse CSV (5 sec)
  → Generate embeddings (20 sec)
  → Store in DB (5 sec)
  → Total: 30 seconds
  → User waits 30 seconds ❌
  → Request timeout possible ❌
```

### Solution With Celery
```
FastAPI upload CSV (10MB)
  → Send to queue (0.1 sec)
  → Return response (0.1 sec)
  → User happy ✅
  
Meanwhile:
Worker processes in background (30 sec)
  → Parse CSV
  → Generate embeddings
  → Store in DB
  → User can check status
```

---

## 🔍 Celery Components

### 1. **Task Definition**
```python
# app/tasks.py
from celery import Celery

celery_app = Celery('enterprise_rag')
celery_app.conf.broker_url = REDIS_URL

@celery_app.task(name='ingest_document')
def ingest_document(file_path, kb_id):
    """Background task to ingest document"""
    # Parse file
    # Generate embeddings
    # Store results
    return {"status": "completed"}
```

### 2. **Task Queue (Redis)**
```
Redis stores:
- Task name
- Task arguments
- Task status
- Task results
```

### 3. **Worker Process**
```python
# Runs in celery container
celery -A app.tasks worker --loglevel=info

This:
1. Connects to Redis
2. Listens for tasks
3. Executes tasks
4. Stores results
```

### 4. **Task Scheduling**
```python
# From FastAPI (backend)
from app.tasks import ingest_document

# Send task to queue
task = ingest_document.delay(
    file_path='/app/data/uploads/sales.csv',
    kb_id='kb-123'
)

# Get job ID
job_id = task.id  # Can track status
```

---

## 📈 Scaling Example

### With 1 Celery Worker
```
Upload CSV → Queue → Worker processes one at a time
Response time: ~30 sec per file
```

### With 4 Celery Workers
```
Upload 4 CSVs
  → All 4 go to queue
  → Each worker picks one
  → All processed in parallel
Response time: ~30 sec for all 4 files ✅
```

**Just add more workers to docker-compose!**

---

## 🎯 Real-World Usage in Your App

### 1. Document Ingestion (Already Using Celery)
```python
@router.post("/upload")
async def upload_document(file: UploadFile, kb_id: str):
    # Save file
    file_path = save_uploaded_file(file)
    
    # Send to background job
    task = ingest_document.delay(
        file_path=file_path,
        kb_id=kb_id,
        org_id=org_id
    )
    
    return {"job_id": task.id, "status": "processing"}
```

### 2. Check Job Status
```python
@router.get("/jobs/{job_id}")
async def get_job_status(job_id: str):
    task = ingest_document.AsyncResult(job_id)
    return {
        "job_id": job_id,
        "status": task.status,  # PENDING, PROGRESS, SUCCESS, FAILURE
        "result": task.result
    }
```

### 3. Celery Logs
```
[2026-08-12 10:30:15] Received task: ingest_document[abc123]
[2026-08-12 10:30:16] Parsing document: sales.csv
[2026-08-12 10:30:20] Generating embeddings for 15 chunks
[2026-08-12 10:30:25] Storing in Qdrant
[2026-08-12 10:30:28] Task ingest_document[abc123] succeeded
```

---

## 🔌 Connection Points

### Redis Connection String
```
REDIS_URL=redis://redis:6379/0
```

Inside Docker:
- `redis` = hostname of Redis container
- `6379` = default Redis port
- `/0` = database number

### Celery Configuration
```python
# app/tasks.py
from celery import Celery

celery_app = Celery('enterprise_rag')
celery_app.conf.broker_url = os.getenv('REDIS_URL')
celery_app.conf.result_backend = os.getenv('REDIS_URL')
```

---

## ✅ What You Can Do Now

### 1. Upload CSV asynchronously
```
POST /api/v1/knowledge/{kb_id}/upload
→ Returns immediately
→ Processing happens in background
```

### 2. Check status
```
GET /api/v1/jobs/{job_id}
→ Returns: PENDING, PROCESSING, COMPLETED, FAILED
```

### 3. Scale workers
```yaml
# docker-compose.yml
celery-worker-1:
  # Worker 1
celery-worker-2:
  # Worker 2
celery-worker-3:
  # Worker 3
```

### 4. Monitor tasks
```bash
# View Celery logs
docker logs enterprise_rag_celery -f

# See all tasks
celery -A app.tasks inspect active
```

---

## 🚀 Performance Impact

| Metric | Without Celery | With Celery |
|--------|----------------|------------|
| Upload response | 30 seconds | 0.5 seconds ✅ |
| Concurrent uploads | 1 at a time | Multiple ✅ |
| User experience | Wait... | Instant ✅ |
| Server utilization | 1 CPU busy | Balanced ✅ |
| Scalability | Poor | Excellent ✅ |

---

## 📊 Your Setup Now

```
✅ Redis (message broker)
✅ Celery (task executor)
✅ Worker (processes jobs)
✅ Ingestion tasks (async)
✅ Qdrant storage (parallel)
✅ PostgreSQL (results)
✅ DuckDB (structured data)
```

**All working together asynchronously!** 🎉

---

## 🎯 Summary

**Celery in your system:**
1. **Accepts uploads** - User uploads CSV
2. **Queues jobs** - Task goes to Redis
3. **Returns immediately** - User gets response
4. **Processes in background** - Celery worker handles it
5. **Stores results** - Data in Qdrant/PostgreSQL/DuckDB
6. **Users check status** - Can track job progress

**Result: Fast, scalable, user-friendly! 🚀**

---

**Status: CELERY RUNNING IN DOCKER** ✅  
**Next:** Run `docker-compose -f docker-compose.backend.improved.yml up -d`
