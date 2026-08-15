# 🐳 Docker Build Guide

**Status:** Ready to Build  
**Time:** 10-15 minutes  

---

## ⚡ Quick Start (Copy-Paste Commands)

```bash
cd c:\Users\Samratmajhi\Downloads\enterprise-rag

# Build all services
docker-compose -f docker-compose.backend.improved.yml build

# Start all services
docker-compose -f docker-compose.backend.improved.yml up -d

# Check status
docker-compose -f docker-compose.backend.improved.yml ps

# View logs
docker-compose -f docker-compose.backend.improved.yml logs -f

# Access app
# Browser: http://localhost:8000
```

---

## 📋 Pre-Build Checklist

### Docker Desktop
- [ ] Docker Desktop installed
- [ ] Docker Desktop running (check system tray)
- [ ] At least 10GB free disk space
- [ ] At least 4GB free RAM

### Project Files
- [ ] `.env` file exists with credentials
- [ ] `backend.Dockerfile` exists
- [ ] `requirements.txt` exists
- [ ] `app/` folder exists

### Environment Variables (.env)
Verify these are set:
```bash
# Database
DB_USER=postgres
DB_PASSWORD=password123
DB_NAME=enterprise_rag

# API Keys
GROQ_API_KEY=gsk_...
GEMINI_API_KEY=...

# LLM Settings
LLM_PROVIDER=groq
TEMPERATURE=0.2
TOP_P=0.95
MAX_OUTPUT_TOKENS=2048

# App Settings
SECRET_KEY=super-secret-key
ACCESS_TOKEN_EXPIRE_MINUTES=60
REFRESH_TOKEN_EXPIRE_DAYS=7
LOG_LEVEL=INFO

# Paths
UPLOAD_DIR=/app/data/uploads
MAX_FILE_SIZE=52428800

# URLs
FRONTEND_URL=http://localhost:3000
```

---

## 🚀 Step-by-Step Build

### Step 1: Navigate to Project
```bash
cd c:\Users\Samratmajhi\Downloads\enterprise-rag
```

### Step 2: Build Docker Images
```bash
docker-compose -f docker-compose.backend.improved.yml build
```

**Expected output:**
```
Building postgres
Building redis
Building qdrant
Building elasticsearch
Building backend
Building celery
Successfully built ...
```

⏱️ **Takes 3-5 minutes first time** (downloads base images)

### Step 3: Start All Services
```bash
docker-compose -f docker-compose.backend.improved.yml up -d
```

**Expected output:**
```
Creating enterprise_rag_postgres ... done
Creating enterprise_rag_redis ... done
Creating enterprise_rag_qdrant ... done
Creating enterprise_rag_elasticsearch ... done
Creating enterprise_rag_backend ... done
Creating enterprise_rag_celery ... done
```

⏱️ **Takes 30-60 seconds**

### Step 4: Verify Services
```bash
docker-compose -f docker-compose.backend.improved.yml ps
```

**Expected output:**
```
NAME                       STATUS
enterprise_rag_postgres    Up (healthy)
enterprise_rag_redis       Up (healthy)
enterprise_rag_qdrant      Up (healthy)
enterprise_rag_elasticsearch  Up (healthy)
enterprise_rag_backend     Up
enterprise_rag_celery      Up
```

All should show "Up" ✅

### Step 5: Check Logs
```bash
# All services
docker-compose -f docker-compose.backend.improved.yml logs -f

# Specific service
docker-compose -f docker-compose.backend.improved.yml logs -f backend
docker-compose -f docker-compose.backend.improved.yml logs -f celery
```

### Step 6: Access the App
Open browser: **http://localhost:8000**

You should see the FastAPI app! ✅

---

## 📊 What's Running

After successful build:

| Service | Port | Status | Container |
|---------|------|--------|-----------|
| PostgreSQL | 5432 | ✅ Running | enterprise_rag_postgres |
| Redis | 6379 | ✅ Running | enterprise_rag_redis |
| Qdrant | 6333 | ✅ Running | enterprise_rag_qdrant |
| Elasticsearch | 9200 | ✅ Running | enterprise_rag_elasticsearch |
| FastAPI | 8000 | ✅ Running | enterprise_rag_backend |
| Celery | - | ✅ Running | enterprise_rag_celery |

---

## 🔍 Verification Commands

```bash
# Check all containers running
docker ps

# Check specific service logs
docker logs enterprise_rag_backend
docker logs enterprise_rag_celery

# Test FastAPI is responding
curl http://localhost:8000/docs

# Test PostgreSQL
docker exec enterprise_rag_postgres psql -U postgres -d enterprise_rag -c "SELECT 1;"

# Test Redis
docker exec enterprise_rag_redis redis-cli ping

# Test Qdrant
curl http://localhost:6333/health

# Test Elasticsearch
curl http://localhost:9200/
```

---

## 📈 Common Issues & Fixes

### "docker-compose command not found"
```bash
# Use full path
docker compose -f docker-compose.backend.improved.yml up -d
# (without hyphen - newer Docker syntax)
```

### "Port 8000 already in use"
```bash
# Stop existing containers
docker stop $(docker ps -q)

# Or remove all containers
docker rm $(docker ps -aq)

# Then rebuild
docker-compose -f docker-compose.backend.improved.yml up -d
```

### "Build failed"
```bash
# Check Docker is running
docker ps

# Clean and rebuild
docker-compose -f docker-compose.backend.improved.yml down
docker-compose -f docker-compose.backend.improved.yml build --no-cache
docker-compose -f docker-compose.backend.improved.yml up -d
```

### "Backend service crashed"
```bash
# Check logs
docker logs enterprise_rag_backend

# Common causes:
# - Missing .env variables
# - Database not ready yet
# - Port already in use
```

### "Celery not connecting"
```bash
# Check Redis is running
docker ps | grep redis

# Check Celery logs
docker logs enterprise_rag_celery

# Restart Celery
docker restart enterprise_rag_celery
```

---

## 🛑 Managing Services

### Stop All Services
```bash
docker-compose -f docker-compose.backend.improved.yml down
```

### Stop Specific Service
```bash
docker stop enterprise_rag_backend
```

### Restart Service
```bash
docker restart enterprise_rag_backend
```

### Remove Everything (Fresh Start)
```bash
# Stop and remove containers + volumes
docker-compose -f docker-compose.backend.improved.yml down -v

# Rebuild
docker-compose -f docker-compose.backend.improved.yml build
docker-compose -f docker-compose.backend.improved.yml up -d
```

---

## 📊 Docker Dashboard

View in Docker Desktop:
1. Open Docker Desktop app
2. Click "Containers" tab
3. You'll see all 6 containers running
4. Click to view logs, stats, etc.

---

## 🎯 Test The System

After build, test:

### 1. Test API
```bash
curl http://localhost:8000/api/v1/health
```

Expected: `{"status": "ok"}`

### 2. Test Database
```bash
curl http://localhost:8000/docs
```

Expected: Swagger UI loads

### 3. Upload a CSV
1. Go to http://localhost:8000
2. Create Knowledge Base
3. Upload test_sales.csv
4. Watch Celery terminal process it

---

## 📝 Environment for Docker

Your `.env` needs these for Docker:

```bash
# Services communication (use internal Docker DNS)
# Inside Docker: postgres means postgres:5432
DATABASE_URL=postgresql+asyncpg://postgres:password123@postgres:5432/enterprise_rag
REDIS_URL=redis://redis:6379/0
QDRANT_URL=http://qdrant:6333
ELASTICSEARCH_URL=http://elasticsearch:9200

# These are already correct! ✅
```

---

## 🚀 Production Checklist

- [ ] All 6 services running
- [ ] Health checks passing
- [ ] Database persisting (postgresql_data volume)
- [ ] Volumes backed up
- [ ] Logs aggregated
- [ ] Monitoring enabled
- [ ] Secrets in .env (not docker-compose.yml)

---

## 📚 Reference

| Need | Command |
|------|---------|
| Build | `docker-compose -f docker-compose.backend.improved.yml build` |
| Start | `docker-compose -f docker-compose.backend.improved.yml up -d` |
| Logs | `docker-compose -f docker-compose.backend.improved.yml logs -f` |
| Status | `docker-compose -f docker-compose.backend.improved.yml ps` |
| Stop | `docker-compose -f docker-compose.backend.improved.yml down` |
| Restart | `docker-compose -f docker-compose.backend.improved.yml restart` |
| Rebuild | `docker-compose -f docker-compose.backend.improved.yml up -d --build` |

---

## ✅ Success Indicators

When everything is working:

```
✅ Docker Desktop running
✅ docker-compose building...
✅ 6 containers created
✅ All services "Up" and "(healthy)"
✅ http://localhost:8000 loads
✅ Can create Knowledge Base
✅ Can upload CSV
✅ Celery processes async tasks
✅ Logs show no errors
```

---

## 🎉 Ready to Deploy!

```bash
# One command to start everything
docker-compose -f docker-compose.backend.improved.yml up -d

# Access app
http://localhost:8000

# View logs
docker-compose -f docker-compose.backend.improved.yml logs -f
```

**That's it!** All services running! 🚀

---

**Status: READY TO BUILD**  
**Next:** Run the build commands above
