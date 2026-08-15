# 🚀 Quick Start: Fix All 4 Services

**Status:** Ready to start  
**Prerequisites:** Docker Desktop installed  
**Time:** 10-15 minutes  

---

## ⚠️ IMPORTANT: Start Docker Desktop First!

1. **Open Docker Desktop** (search "Docker" in Windows Start Menu)
2. **Wait 30 seconds** for it to fully load
3. **Then proceed below**

---

## Step 1: Start All Services (PostgreSQL, Qdrant, Elasticsearch, Redis)

**Open Command Prompt** (not PowerShell) and run:

```bash
cd c:\Users\Samratmajhi\Downloads\enterprise-rag
start_all_services.bat
```

**This will:**
- ✅ Create PostgreSQL container (localhost:5432)
- ✅ Create Qdrant container (localhost:6333)
- ✅ Create Elasticsearch container (localhost:9200)
- ✅ Create Redis container (localhost:6379)

**Wait for all to finish (you'll see "SUCCESS")** ✅

---

## Step 2: Start Celery Worker

**Open a NEW Command Prompt** and run:

```bash
cd c:\Users\Samratmajhi\Downloads\enterprise-rag
start_celery_worker.bat
```

**Keep this window open.** You should see:
```
celery@HOSTNAME v5.x.x (...)
[queues]
```

---

## Step 3: Start FastAPI Application

**Open ANOTHER NEW Command Prompt** and run:

```bash
cd c:\Users\Samratmajhi\Downloads\enterprise-rag
start_app.bat
```

**Keep this window open.** You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete
```

---

## Step 4: Verify Everything Works

Open your browser and go to:
- **http://localhost:8000** - FastAPI app
- **http://localhost:8000/docs** - API documentation

---

## 📊 You Should Now Have 3 Command Prompts Open

| Prompt 1 | Prompt 2 | Prompt 3 |
|----------|----------|----------|
| (services already finished) | Celery worker running | FastAPI app running |

---

## ✅ Services Summary

| Service | Host | Port | Status |
|---------|------|------|--------|
| PostgreSQL | localhost | 5432 | Running in Docker |
| Qdrant | localhost | 6333 | Running in Docker |
| Elasticsearch | localhost | 9200 | Running in Docker |
| Redis | localhost | 6379 | Running in Docker |
| Celery | - | - | Running in Prompt 2 |
| FastAPI | localhost | 8000 | Running in Prompt 3 |

---

## 🧪 Test Upload CSV

1. Go to http://localhost:8000
2. Create a knowledge base
3. Upload a CSV file
4. **Check Celery terminal** - should see:
   ```
   Received task: ingest_document
   Task completed: ingest_document
   ```

---

## 🆘 Troubleshooting

### "Docker is not running"
- Open Docker Desktop app
- Wait 30 seconds
- Try again

### "Port 5432 already in use"
```bash
docker ps
docker stop enterprise-postgres
docker rm enterprise-postgres
# Then run start_all_services.bat again
```

### "Celery connection refused"
- Make sure Redis container is running (check prompt 1)
- Wait 10 seconds and try again

### "FastAPI won't start"
- Check that PostgreSQL, Qdrant, Elasticsearch are running
- Check Celery worker is running in Prompt 2

---

## 📋 Files You Need to Run

```
start_all_services.bat     → Run FIRST
start_celery_worker.bat    → Run SECOND (new prompt)
start_app.bat              → Run THIRD (new prompt)
```

---

## ✨ After Setup

All services are ready for:
- ✅ ATLAS Structured Queries (CSV/XLSX)
- ✅ Semantic Search (PDF/DOCX)
- ✅ Keyword Search
- ✅ Async Document Ingestion
- ✅ Multi-user Support

---

## 🎯 Common Questions

**Q: Do I need to run these scripts every time?**  
A: Yes, but Docker containers persist. Next time you can just do `docker start enterprise-*` instead.

**Q: Can I run on Windows directly (not Docker)?**  
A: Yes, but it's more complex. Docker is recommended.

**Q: What if I close a terminal?**  
A: Restart it with the same .bat file.

**Q: How do I stop all services?**  
A: Close all terminals, then: `docker stop $(docker ps -q)`

---

## ✅ Status Check Command

Verify all services running:
```bash
docker ps | findstr "enterprise-"
```

Should show 4 containers:
- enterprise-postgres
- enterprise-qdrant
- enterprise-elasticsearch
- enterprise-redis

---

**Ready to start? Begin with Step 1 above!** 🚀
