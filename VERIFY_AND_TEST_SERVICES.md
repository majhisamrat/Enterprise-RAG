# ✅ Verify & Test All Services

**Objective:** Confirm all 4 services + Celery + FastAPI are working correctly  
**Prerequisites:** All 3 .bat scripts running (see QUICK_START_SERVICES.md)  
**Time:** 10-15 minutes  

---

## Task 5: Verify All 4 Services Are Working

### Step 5.1: Check Docker Containers Running

**Open Command Prompt and run:**

```bash
docker ps
```

**Expected output - You should see 4 containers:**

```
CONTAINER ID   IMAGE                    PORTS
xxxxxxxx       postgres:15-alpine       0.0.0.0:5432->5432/tcp
xxxxxxxx       qdrant/qdrant:latest     0.0.0.0:6333->6333/tcp, 6334/tcp
xxxxxxxx       elasticsearch:8.11.0     0.0.0.0:9200->9200/tcp, 9300/tcp
xxxxxxxx       redis:7-alpine           0.0.0.0:6379->6379/tcp
```

✅ **PASS** - All 4 containers running  
❌ **FAIL** - See troubleshooting below

---

### Step 5.2: Test PostgreSQL Connection

**Open Command Prompt and run:**

```bash
docker exec enterprise-postgres psql -U postgres -d enterprise_rag -c "SELECT 1;"
```

**Expected output:**
```
 ?column?
----------
        1
(1 row)
```

✅ **PASS** - PostgreSQL responding  
❌ **FAIL** - Run: `docker logs enterprise-postgres`

---

### Step 5.3: Test Qdrant Connection

**Open Command Prompt and run:**

```bash
curl http://localhost:6333/health
```

**Expected output:**
```json
{"status":"ok"}
```

✅ **PASS** - Qdrant responding  
❌ **FAIL** - Run: `docker logs enterprise-qdrant`

---

### Step 5.4: Test Elasticsearch Connection

**Open Command Prompt and run:**

```bash
curl http://localhost:9200/
```

**Expected output:**
```json
{
  "name" : "...",
  "cluster_name" : "docker-cluster",
  "version" : {...}
}
```

✅ **PASS** - Elasticsearch responding  
❌ **FAIL** - Run: `docker logs enterprise-elasticsearch`

---

### Step 5.5: Test Redis Connection

**Open Command Prompt and run:**

```bash
docker exec enterprise-redis redis-cli ping
```

**Expected output:**
```
PONG
```

✅ **PASS** - Redis responding  
❌ **FAIL** - Run: `docker logs enterprise-redis`

---

### Step 5.6: Check Celery Worker Status

**Look at the Celery terminal (from start_celery_worker.bat)**

**Expected output:**
```
celery@HOSTNAME v5.x.x (opal)
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
 connected to redis://localhost:6379/0
 Tasks:
    . app.tasks.ingest_document
```

✅ **PASS** - Celery worker online and connected to Redis  
❌ **FAIL** - Check Redis is running, then restart Celery

---

### Step 5.7: Check FastAPI Application Status

**Look at the FastAPI terminal (from start_app.bat)**

**Expected output:**
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete
```

✅ **PASS** - FastAPI is running  
❌ **FAIL** - Check all services are running first

---

## Task 6: Test End-to-End Ingestion with All Services

### Step 6.1: Create a Test CSV File

**Save this as `test_sales.csv`:**

```csv
Date,Product,Quantity,Price
2026-08-01,Laptop,51,1000.00
2026-08-02,Mouse,20,50.00
2026-08-03,Keyboard,100,75.00
2026-08-04,Monitor,5,300.00
```

Location: `c:\Users\Samratmajhi\Downloads\enterprise-rag\test_sales.csv`

---

### Step 6.2: Create Knowledge Base (via API)

**Open a new Command Prompt and run:**

```bash
curl -X POST http://localhost:8000/api/v1/knowledge \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d "{\"name\": \"Test KB\", \"description\": \"Test KB for services verification\"}"
```

**Replace `YOUR_TOKEN` with your actual JWT token** (you can get this from the frontend login)

**Expected response:**
```json
{
  "id": "kb-uuid-here",
  "name": "Test KB",
  "status": "active"
}
```

✅ **PASS** - Knowledge base created  
**Note:** If you don't have a token, use the web UI instead (http://localhost:8000)

---

### Step 6.3: Upload CSV File via Web UI

**Open browser: http://localhost:8000**

1. **Login** with your credentials
2. **Select or create** a Knowledge Base
3. **Click "Upload"**
4. **Select `test_sales.csv`**
5. **Click "Upload"**

---

### Step 6.4: Verify Ingestion in Celery Terminal

**Watch the Celery terminal (start_celery_worker.bat window)**

**Expected log sequence:**

```
Received task: ingest_document [...]
Starting document ingestion for file: test_sales.csv
Parsing document: test_sales.csv
Parsed successfully using PyMuPDF
Text cleaning completed
Metadata extracted successfully
Generated 1 chunks
Generating embeddings for 1 chunks
Generated embeddings for 1 chunks
Qdrant collection ensured
Upserting to Qdrant
Successfully ingested document
Task ingest_document[...] succeeded
```

✅ **PASS** - All logs show SUCCESS  
❌ **FAIL** - See troubleshooting below

---

### Step 6.5: Verify CSV in Database

**Check PostgreSQL has the file:**

```bash
docker exec enterprise-postgres psql -U postgres -d enterprise_rag \
  -c "SELECT * FROM uploads WHERE original_filename LIKE '%test_sales%';"
```

**Expected output:**
```
 id | original_filename | status | created_at
----+------------------+--------+------------
... | test_sales.csv   | completed | ...
```

✅ **PASS** - File in database  
❌ **FAIL** - Check ingestion logs

---

### Step 6.6: Verify Vectors in Qdrant

**Check Qdrant has the collection:**

```bash
curl http://localhost:6333/collections
```

**Expected output shows collections created:**
```json
{
  "collections": [
    {
      "name": "enterprise_documents",
      ...
    },
    {
      "name": "enterprise_documents_kb_...",
      ...
    }
  ]
}
```

✅ **PASS** - Collections created in Qdrant  
❌ **FAIL** - Check ingestion logs for Qdrant errors

---

### Step 6.7: Query the System

**Test a structured query:**

```bash
curl -X POST http://localhost:8000/api/v1/knowledge/KB_ID/query \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d "{\"query\": \"How many products were listed?\"}"
```

**Expected response (structured answer):**
```json
{
  "result": 4,
  "sources": ["test_sales.csv"],
  "provenance": {...}
}
```

✅ **PASS** - Structured query working  
❌ **FAIL** - Check all services are running

---

### Step 6.8: Upload Another CSV (Multi-File Test)

**Create `test_sales2.csv`:**

```csv
Date,Item,Qty,Cost
2026-08-05,Laptop,10,1000.00
2026-08-06,Mouse,15,50.00
```

**Upload it to the same KB**

**Then query:**

```bash
curl -X POST http://localhost:8000/api/v1/knowledge/KB_ID/query \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d "{\"query\": \"How many total products were sold?\"}"
```

**Expected response (multi-file aggregation):**
```json
{
  "result": 75,
  "sources": ["test_sales.csv", "test_sales2.csv"],
  "note": "Aggregated from multiple files"
}
```

✅ **PASS** - Multi-file aggregation working  
❌ **FAIL** - Check column mapping

---

## 📊 Verification Summary

| Component | Status | Details |
|-----------|--------|---------|
| PostgreSQL | ✅/❌ | See Step 5.2 |
| Qdrant | ✅/❌ | See Step 5.3 |
| Elasticsearch | ✅/❌ | See Step 5.4 |
| Redis | ✅/❌ | See Step 5.5 |
| Celery Worker | ✅/❌ | See Step 5.6 |
| FastAPI App | ✅/❌ | See Step 5.7 |
| CSV Ingestion | ✅/❌ | See Step 6.4 |
| Database Storage | ✅/❌ | See Step 6.5 |
| Vector Storage | ✅/❌ | See Step 6.6 |
| Structured Query | ✅/❌ | See Step 6.7 |
| Multi-File Query | ✅/❌ | See Step 6.8 |

---

## 🆘 Troubleshooting

### "Docker container not running"
```bash
# List all containers
docker ps -a

# Start a stopped container
docker start enterprise-postgres

# Check logs
docker logs enterprise-postgres

# Restart from scratch
docker rm enterprise-postgres
# Then re-run start_all_services.bat
```

### "Connection refused"
- Wait 10 seconds for service to initialize
- Try the test command again

### "Ingestion failed in Celery"
```bash
# Check Celery logs in the terminal window
# Look for error messages

# Restart Celery
# Close the Celery terminal (Ctrl+C)
# Run start_celery_worker.bat again
```

### "FastAPI won't start"
```bash
# Check if port 8000 is in use
netstat -ano | findstr :8000

# Kill the process using the port
taskkill /PID <PID> /F

# Or use a different port
python -m uvicorn app.app_config:app --port 8001
```

### "CSV not ingesting"
- Check Celery terminal for errors
- Check PostgreSQL is running
- Check Redis is running
- Restart FastAPI app

---

## ✅ All Tests Passed?

If all steps show ✅, then:

1. **PostgreSQL** - ✅ Working
2. **Qdrant** - ✅ Working
3. **Elasticsearch** - ✅ Working
4. **Redis** - ✅ Working
5. **Celery** - ✅ Working
6. **FastAPI** - ✅ Working
7. **ATLAS Structured Queries** - ✅ Working
8. **Multi-File Aggregation** - ✅ Working

**Status: 🎉 ALL SERVICES VERIFIED AND WORKING!**

---

## 📝 Documentation

All services are now ready for:
- ✅ Document ingestion (async via Celery)
- ✅ Vector storage (Qdrant)
- ✅ Keyword search (Elasticsearch)
- ✅ Structured queries (DuckDB + PostgreSQL)
- ✅ Multi-file aggregation (ATLAS)
- ✅ KB isolation
- ✅ Production deployment

---

## 🎯 Next Steps

After verification:
1. Test ATLAS structured queries (CSV-specific)
2. Test semantic search (PDF/DOCX)
3. Test hybrid queries
4. Deploy to production

**See PHASES_1_9_COMPLETE.md for ATLAS query examples.**

---

**All done? Mark tasks 5-6 complete and proceed to production deployment!** 🚀
