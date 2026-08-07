# EC2 Backend-Only Deployment Guide

This guide explains how to deploy **only the backend** to EC2 with Docker. The frontend is deployed separately on Vercel.

## Architecture

```
┌─────────────────────┐
│  Vercel Frontend    │
│ (Enterprise-RAG-FE) │
└──────────┬──────────┘
           │ API calls
           ▼
┌─────────────────────────────────────┐
│         EC2 Backend (Docker)        │
│ ┌─────────────┬────────────────┐   │
│ │  PostgreSQL │  Redis │Qdrant│   │
│ └─────────────┴────────────────┘   │
│         Backend API (8000)          │
└─────────────────────────────────────┘
```

---

## Step 1: Prepare Backend Code Locally

### 1.1 Update `.gitignore` to Ignore Frontend

The frontend folder is now ignored in `.gitignore`:

```bash
# Frontend - Completely ignore (deployed separately on Vercel)
frontend/
enterprise-rag-frontend/
```

This ensures only **backend code** is pushed to GitHub.

### 1.2 Commit and Push Backend Code

```bash
cd C:\Users\Samratmajhi\Downloads\enterprise-rag
git add .
git commit -m "Backend-only deployment setup - Frontend deployed on Vercel"
git push origin main
```

**Verify:** Check your GitHub repo - you should NOT see `frontend/` or `enterprise-rag-frontend/` folders.

---

## Step 2: SSH to EC2 and Pull Backend Code

### 2.1 Connect to EC2

```bash
ssh -i your-key.pem ubuntu@your-ec2-ip
```

### 2.2 Clone Backend Repository (or Pull if Already Cloned)

**First time:**
```bash
git clone https://github.com/YOUR_USERNAME/enterprise-rag.git
cd enterprise-rag
```

**Already cloned (just pull latest):**
```bash
cd ~/enterprise-rag
git pull origin main
```

### 2.3 Verify Only Backend Code is Present

```bash
ls -la
# Output should show: app/, alembic/, requirements.txt, backend.Dockerfile, etc.
# Output should NOT show: frontend/, enterprise-rag-frontend/
```

---

## Step 3: Configure Environment Variables on EC2

### 3.1 Create `.env` File

```bash
cat > .env << EOF
# Database
DB_USER=raguser
DB_PASSWORD=your-secure-password
DB_NAME=enterprise_rag

# JWT
SECRET_KEY=your-secret-key-here-min-32-chars

# API
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
LOG_LEVEL=INFO

# LLM Configuration
LLM_PROVIDER=gemini
GEMINI_API_KEY=your-gemini-api-key
GEMINI_MODEL=gemini-2.0-flash

# RAG Configuration
TEMPERATURE=0.7
TOP_P=0.9
MAX_OUTPUT_TOKENS=2048
UPLOAD_DIR=/app/data/uploads
MAX_FILE_SIZE=52428800

# Frontend URL (for CORS) - Update with your Vercel frontend URL
FRONTEND_URL=https://your-enterprise-rag-frontend.vercel.app
EOF
```

### 3.2 Install Docker & Docker Compose (if not already installed)

```bash
# Update system
sudo apt-get update
sudo apt-get upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker ubuntu

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Verify
docker --version
docker-compose --version

# Exit and reconnect SSH for group changes to take effect
exit
ssh -i your-key.pem ubuntu@your-ec2-ip
```

---

## Step 4: Build and Deploy Backend on EC2

### 4.1 Build Docker Images

```bash
cd ~/enterprise-rag

# Build all services
docker-compose -f docker-compose.backend.yml build
```

Expected output:
```
[+] Building 2/2
 ✔ postgres Already exists
 ✔ backend Built successfully
```

### 4.2 Start Backend Services

```bash
docker-compose -f docker-compose.backend.yml up -d
```

Expected output:
```
[+] Running 4/4
 ✔ Container enterprise_rag_postgres   Started
 ✔ Container enterprise_rag_redis       Started
 ✔ Container enterprise_rag_qdrant      Started
 ✔ Container enterprise_rag_backend     Started
```

### 4.3 Verify Services are Running

```bash
docker-compose -f docker-compose.backend.yml ps

# Output should show all containers RUNNING
```

### 4.4 Check Backend Logs

```bash
docker-compose -f docker-compose.backend.yml logs backend -f

# Should show: "Uvicorn running on http://0.0.0.0:8000"
```

---

## Step 5: Verify Backend API is Accessible

### 5.1 Test from EC2 (Local)

```bash
curl http://localhost:8000/api/v1/health

# Expected response:
# {"status":"ok","timestamp":"2024-08-06T10:30:00Z"}
```

### 5.2 Test from Your Local Machine

```bash
curl http://your-ec2-ip:8000/api/v1/health
```

If it fails, open port 8000 in EC2 security group:
- Go to AWS Console → EC2 → Security Groups
- Add Inbound Rule: TCP port 8000 from anywhere (0.0.0.0/0) or specific Vercel IPs

---

## Step 6: Update Backend CORS Configuration

### 6.1 Check Current CORS Settings

```bash
# View CORS configuration in backend
docker exec enterprise_rag_backend cat app/main.py | grep -A 5 "CORSMiddleware"
```

### 6.2 Update CORS to Allow Vercel Frontend

Edit `app/main.py` in your **local repo** and update CORS:

```python
from fastapi.middleware.cors import CORSMiddleware

# Read allowed origins from environment
allowed_origins = [
    "http://localhost:3000",
    "http://localhost:5173",
    os.getenv("FRONTEND_URL", "http://localhost:3000"),
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### 6.3 Rebuild and Restart Backend

```bash
# Commit changes locally
git add app/main.py
git commit -m "Update CORS to allow Vercel frontend"
git push origin main

# On EC2: Pull latest and rebuild
cd ~/enterprise-rag
git pull origin main
docker-compose -f docker-compose.backend.yml down
docker-compose -f docker-compose.backend.yml build
docker-compose -f docker-compose.backend.yml up -d
```

---

## Step 7: Connect Vercel Frontend to Backend

### 7.1 Update Frontend Environment Variables in Vercel

1. Go to Vercel Dashboard → Project Settings → Environment Variables
2. Add or update:
   - **Name:** `VITE_API_URL`
   - **Value:** `http://your-ec2-ip:8000`
3. Click Save → Trigger a redeploy

### 7.2 Test Frontend → Backend Connection

1. Open your Vercel frontend URL
2. Try logging in or making an API call
3. Check browser console for errors
4. Backend logs should show incoming requests:
   ```bash
   docker-compose -f docker-compose.backend.yml logs backend -f
   ```

---

## Step 8: Manage Services on EC2

### View Running Services
```bash
docker-compose -f docker-compose.backend.yml ps
```

### View Logs
```bash
docker-compose -f docker-compose.backend.yml logs -f

# Specific service
docker-compose -f docker-compose.backend.yml logs backend -f
docker-compose -f docker-compose.backend.yml logs postgres -f
```

### Stop All Services
```bash
docker-compose -f docker-compose.backend.yml down
```

### Restart Services
```bash
docker-compose -f docker-compose.backend.yml restart backend
```

### Rebuild and Restart After Code Changes
```bash
cd ~/enterprise-rag
git pull origin main
docker-compose -f docker-compose.backend.yml build
docker-compose -f docker-compose.backend.yml up -d
```

---

## Step 9: Production Best Practices

### Enable HTTPS (Recommended)

Use AWS Certificate Manager or Let's Encrypt with a reverse proxy (nginx).

### Setup Monitoring

```bash
# Monitor disk usage
docker system df

# Clean up old images/containers
docker system prune -a
```

### Backup Database

```bash
# Backup PostgreSQL
docker-compose -f docker-compose.backend.yml exec postgres pg_dump -U raguser enterprise_rag > backup.sql

# Restore from backup
docker-compose -f docker-compose.backend.yml exec -T postgres psql -U raguser enterprise_rag < backup.sql
```

### Auto-start Services on EC2 Reboot

Create a systemd service:

```bash
sudo cat > /etc/systemd/system/enterprise-rag.service << EOF
[Unit]
Description=Enterprise RAG Backend
After=docker.service
Requires=docker.service

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/enterprise-rag
ExecStart=/usr/local/bin/docker-compose -f docker-compose.backend.yml up
ExecStop=/usr/local/bin/docker-compose -f docker-compose.backend.yml down
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl enable enterprise-rag
sudo systemctl start enterprise-rag
```

---

## Troubleshooting

### Issue: "Connection refused" when accessing backend from frontend

**Solution:**
- Check backend is running: `docker ps`
- Check port 8000 is open in EC2 security group
- Check CORS is configured correctly
- Verify `VITE_API_URL` in Vercel is set to correct backend URL

### Issue: PostgreSQL/Redis/Qdrant health checks fail

**Solution:**
```bash
# Check logs
docker-compose -f docker-compose.backend.yml logs postgres

# Ensure ports are not in use
docker-compose -f docker-compose.backend.yml down
docker system prune -a
docker-compose -f docker-compose.backend.yml up -d
```

### Issue: Out of Memory errors

**Solution:**
```bash
# Check system resources
free -h
df -h

# Reduce Gunicorn workers in docker-compose.backend.yml
# Change: "gunicorn -w 4" to "gunicorn -w 2"
```

### Issue: Files already exist/Permission denied

**Solution:**
```bash
# Fix permissions
sudo chown -R ubuntu:ubuntu ~/enterprise-rag
chmod -R 755 ~/enterprise-rag
```

---

## Summary

✅ Backend code pushed to GitHub (frontend ignored)  
✅ EC2 pulls backend code  
✅ Docker images built for PostgreSQL, Redis, Qdrant, Backend API  
✅ Services started on EC2  
✅ Backend API accessible at `http://ec2-ip:8000`  
✅ Vercel frontend configured with `VITE_API_URL`  
✅ Frontend makes API calls to backend on EC2  

**Your system is now ready for production!** 🚀
