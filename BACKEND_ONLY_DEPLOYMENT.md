# Backend-Only Deployment for EC2

## Overview

You're separating the deployment:
- **Frontend**: Vercel (separate repository: Enterprise-RAG-Frontend)
- **Backend**: EC2 with Docker (this repository)

This means only backend code gets pushed to this GitHub repo. The frontend is ignored in `.gitignore`.

---

## What Changed

### 1. `.gitignore` Updated

```
# Frontend - Completely ignore (deployed separately on Vercel)
frontend/
enterprise-rag-frontend/
*.vercel.json
.next/
```

**Result:** When you push to GitHub, the frontend folder is NOT uploaded.

### 2. New Files Created

- **`docker-compose.backend.yml`** - Backend-only Docker services (PostgreSQL, Redis, Qdrant, Backend API)
- **`EC2_BACKEND_DEPLOYMENT.md`** - Complete step-by-step deployment guide
- **`DEPLOYMENT_CHECKLIST.md`** - Quick reference checklist

---

## Quick Start on EC2

### 1. Pull Backend Code (First Time)

```bash
git clone https://github.com/YOUR_USERNAME/enterprise-rag.git
cd enterprise-rag
```

### 2. Create `.env` File

```bash
cat > .env << EOF
DB_USER=raguser
DB_PASSWORD=your-password
DB_NAME=enterprise_rag
SECRET_KEY=your-secret-key-min-32-chars
LLM_PROVIDER=gemini
GEMINI_API_KEY=your-api-key
GEMINI_MODEL=gemini-2.0-flash
FRONTEND_URL=https://your-app.vercel.app
EOF
```

### 3. Start Services

```bash
docker-compose -f docker-compose.backend.yml up -d
```

### 4. Verify Backend is Running

```bash
curl http://localhost:8000/api/v1/health

# Expected response:
# {"status":"ok","timestamp":"2024-08-06T10:30:00Z"}
```

### 5. Connect Vercel Frontend

In Vercel dashboard:
- Set `VITE_API_URL` = `http://your-ec2-ip:8000`
- Redeploy frontend

---

## File Structure on EC2

```
~/enterprise-rag/
├── app/                          # Backend code ✅
├── alembic/                      # Migrations ✅
├── backend.Dockerfile            # Backend image ✅
├── docker-compose.backend.yml    # Services ✅
├── requirements.txt              # Dependencies ✅
├── .env                          # Env vars (you create this) ✅
└── [NO frontend/ folder]         # Ignored by .gitignore ✅
```

---

## Useful Commands on EC2

```bash
# Check all services running
docker-compose -f docker-compose.backend.yml ps

# View backend logs
docker-compose -f docker-compose.backend.yml logs backend -f

# Stop all services
docker-compose -f docker-compose.backend.yml down

# Rebuild after code changes
git pull origin main
docker-compose -f docker-compose.backend.yml build
docker-compose -f docker-compose.backend.yml up -d

# Restart just backend
docker-compose -f docker-compose.backend.yml restart backend
```

---

## What Gets Deployed

### On EC2 (Backend)
- PostgreSQL database
- Redis cache
- Qdrant vector database
- Backend API (port 8000)
- All backend code from `app/` folder

### On Vercel (Frontend)
- React UI
- All frontend components
- API calls to EC2 backend
- Progressive Web App features

---

## API Architecture

```
Frontend (Vercel)
    ↓ API calls
    ↓ VITE_API_URL=http://ec2-ip:8000
    ↓
Backend API (EC2:8000)
    ├─ PostgreSQL (internal only)
    ├─ Redis (internal only)
    └─ Qdrant (internal only)
```

---

## Key Files to Know

| File | Purpose |
|------|---------|
| `docker-compose.backend.yml` | Defines all Docker services |
| `backend.Dockerfile` | Builds backend API image |
| `.gitignore` | Excludes frontend from push |
| `.env` | Environment variables (EC2 only) |
| `app/main.py` | Backend entry point |
| `requirements.txt` | Python dependencies |

---

## Troubleshooting

### Backend won't start
```bash
docker-compose -f docker-compose.backend.yml logs backend
# Check for missing dependencies or env vars
```

### Frontend can't connect
```bash
# 1. Check backend is running
curl http://localhost:8000/api/v1/health

# 2. Verify port 8000 is open in AWS security group

# 3. Check VITE_API_URL is correct in Vercel

# 4. Check CORS is configured
docker-compose -f docker-compose.backend.yml logs backend | grep CORS
```

### Out of memory
```bash
# Reduce workers in docker-compose.backend.yml
# Change: "gunicorn -w 4" to "gunicorn -w 2"
```

---

## No UI/Logic Changes

✅ All backend code remains **unchanged**  
✅ All API endpoints work the same  
✅ All database models unchanged  
✅ All business logic preserved  

This is purely a **deployment architecture change**.

---

## Summary

You now have:
1. ✅ Backend code pushed to GitHub (frontend ignored)
2. ✅ Docker setup ready for EC2 (docker-compose.backend.yml)
3. ✅ Complete deployment guides (EC2_BACKEND_DEPLOYMENT.md)
4. ✅ Checklist for easy reference (DEPLOYMENT_CHECKLIST.md)

**Ready to deploy!** 🚀
