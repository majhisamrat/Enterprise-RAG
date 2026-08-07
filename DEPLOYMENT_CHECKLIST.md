# Backend Deployment Checklist

## ✅ Local Preparation (Windows)

- [ ] `.gitignore` updated to ignore `frontend/` and `enterprise-rag-frontend/`
- [ ] All backend code committed locally
- [ ] Verified repo only has backend files (no frontend)
- [ ] Pushed to GitHub: `git push origin main`

## ✅ EC2 Setup

- [ ] SSH connected to EC2 instance
- [ ] Docker installed: `docker --version`
- [ ] Docker Compose installed: `docker-compose --version`
- [ ] Backend code cloned/pulled: `git pull origin main`
- [ ] `.env` file created with all required variables
- [ ] Verified frontend folder is NOT on EC2

## ✅ Docker Build & Deploy

- [ ] Backend Docker image built: `docker-compose -f docker-compose.backend.yml build`
- [ ] Services started: `docker-compose -f docker-compose.backend.yml up -d`
- [ ] All containers running: `docker-compose -f docker-compose.backend.yml ps`
- [ ] Backend API responding: `curl http://localhost:8000/api/v1/health`

## ✅ AWS Security Group

- [ ] Port 8000 open for EC2 security group (or specific IP ranges)
- [ ] Port 5432 (PostgreSQL) blocked externally (only internal)
- [ ] Port 6379 (Redis) blocked externally (only internal)
- [ ] Port 6333 (Qdrant) blocked externally (only internal)

## ✅ Backend Configuration

- [ ] CORS updated to include Vercel frontend URL
- [ ] `FRONTEND_URL` environment variable set in `.env`
- [ ] Backend rebuilt after CORS changes
- [ ] Backend logs show no CORS errors

## ✅ Vercel Frontend

- [ ] Frontend deployed to Vercel (from Enterprise-RAG-Frontend repo)
- [ ] `VITE_API_URL` environment variable set in Vercel dashboard
- [ ] `VITE_API_URL` value = `http://your-ec2-ip:8000`
- [ ] Frontend redeployed after env var changes

## ✅ Testing

- [ ] Backend health check passes: `curl http://ec2-ip:8000/api/v1/health`
- [ ] Frontend loads in browser without errors
- [ ] API calls from frontend to backend work
- [ ] No CORS errors in browser console
- [ ] Backend logs show incoming requests from frontend

## ✅ Production Ready

- [ ] Services auto-restart on container failure (restart: unless-stopped)
- [ ] Health checks configured and passing
- [ ] Database backups configured
- [ ] Logs are being collected
- [ ] Monitoring/alerts setup (optional)
- [ ] SSL/HTTPS configured (optional but recommended)

---

## Quick Commands Reference

```bash
# On EC2:
docker-compose -f docker-compose.backend.yml ps                    # Check status
docker-compose -f docker-compose.backend.yml logs backend -f       # View logs
docker-compose -f docker-compose.backend.yml down                  # Stop all
docker-compose -f docker-compose.backend.yml up -d                 # Start all
docker-compose -f docker-compose.backend.yml build                 # Rebuild
```

---

## File Structure

```
~/enterprise-rag/
├── app/                          # Backend code (NO CHANGES)
├── alembic/                      # Database migrations (NO CHANGES)
├── backend.Dockerfile            # Backend Docker image (READY)
├── docker-compose.backend.yml    # Backend-only services (NEW)
├── requirements.txt              # Python dependencies (NO CHANGES)
├── .gitignore                    # Updated to ignore frontend
├── .env                          # Environment variables (EC2)
└── [NO FRONTEND FOLDER]          # Frontend is on Vercel only
```

---

## Environment Variables Template

Update `.env` with your values:

```env
# Database
DB_USER=raguser
DB_PASSWORD=your-secure-password
DB_NAME=enterprise_rag

# JWT
SECRET_KEY=your-secret-key-min-32-chars

# API
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
LOG_LEVEL=INFO

# LLM Configuration
LLM_PROVIDER=gemini
GEMINI_API_KEY=your-gemini-key
GEMINI_MODEL=gemini-2.0-flash

# RAG Configuration
TEMPERATURE=0.7
TOP_P=0.9
MAX_OUTPUT_TOKENS=2048
UPLOAD_DIR=/app/data/uploads
MAX_FILE_SIZE=52428800

# Frontend URL (for CORS)
FRONTEND_URL=https://your-app.vercel.app
```

---

## Debugging Tips

1. **Backend won't start?**
   ```bash
   docker-compose -f docker-compose.backend.yml logs backend
   ```

2. **Database connection failed?**
   ```bash
   docker-compose -f docker-compose.backend.yml logs postgres
   ```

3. **Frontend can't reach backend?**
   - Check `VITE_API_URL` in Vercel dashboard
   - Check port 8000 is open in AWS security group
   - Check CORS configuration in backend
   - View backend logs for CORS errors

4. **Out of memory?**
   - Reduce Gunicorn workers: `-w 2` instead of `-w 4`
   - Upgrade EC2 instance size

5. **Rebuild needed after code changes?**
   ```bash
   git pull origin main
   docker-compose -f docker-compose.backend.yml build
   docker-compose -f docker-compose.backend.yml up -d
   ```
