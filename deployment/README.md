# Enterprise RAG - Deployment Package

This folder contains everything needed to deploy Enterprise RAG to AWS EC2.

## 📦 Contents

```
deployment/
├── app/                      Backend application code
├── frontend/                 Pre-built React frontend (dist/)
├── alembic/                  Database migrations
├── nginx/                    Reverse proxy configuration
│   ├── default.conf         Nginx config (HTTP/HTTPS, rate limiting)
│   └── Dockerfile           Nginx container setup
├── .env.example             Environment template (copy to .env and configure)
├── requirements.txt         Python dependencies (65 packages, optimized)
├── docker-compose.yml       Docker services orchestration
├── Dockerfile               Backend container setup
└── README.md               This file
```

## 🚀 Quick Start (5 Steps)

### 1. Launch EC2 Instance
```bash
# AWS Console → EC2 → Instances → Launch Instance
# - AMI: Ubuntu 22.04 LTS (free tier)
# - Type: t2.micro (free) or t3.small
# - Storage: 30-50 GB SSD
# - Security: Allow ports 22, 80, 443, 8000
```

### 2. Connect to EC2
```bash
chmod 400 your-key.pem
ssh -i your-key.pem ubuntu@your-ec2-ip
```

### 3. Install Docker
```bash
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker ubuntu

sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

### 4. Deploy
```bash
cd /home/ubuntu/enterprise-rag
cp .env.example .env
nano .env  # Edit with your API keys

docker-compose build
docker-compose up -d
sleep 30
docker-compose exec api alembic upgrade head
```

### 5. Access Application
```
Frontend: http://your-ec2-ip
API Docs: http://your-ec2-ip/api/docs
Health: http://your-ec2-ip/health
```

---

## 🔑 Environment Variables

Copy `.env.example` to `.env` and configure:

```bash
# Database
DATABASE_URL=postgresql://postgres:password@db:5432/enterprise_rag
POSTGRES_PASSWORD=your_secure_password

# API
API_HOST=0.0.0.0
API_PORT=8000

# Frontend
VITE_API_URL=http://your-ec2-ip:8000

# LLM Provider (Groq or Gemini)
GROQ_API_KEY=your-groq-key
GROQ_MODEL=qwen/qwen3.6-27b
GEMINI_API_KEY=your-gemini-key

# Security
SECRET_KEY=your-secure-random-key-32-chars-min

# Google OAuth (optional)
GOOGLE_CLIENT_ID=your-client-id
GOOGLE_CLIENT_SECRET=your-client-secret
```

---

## 🐳 Docker Services

The `docker-compose.yml` includes:

| Service | Port | Purpose |
|---------|------|---------|
| **api** | 8000 | FastAPI backend |
| **db** | 5432 | PostgreSQL database |
| **redis** | 6379 | Caching & session store |
| **qdrant** | 6333 | Vector database |
| **nginx** | 80/443 | Reverse proxy |

---

## ✅ Verification

After deployment, verify everything works:

```bash
# Check containers
docker-compose ps

# Test health
curl http://localhost:8000/health

# View logs
docker-compose logs -f

# Test API
curl http://localhost:8000/api/docs
```

---

## 🔒 Security

### Pre-Production
1. **Strong passwords**: 16+ chars, mix of case/numbers/symbols
2. **API keys**: Never hardcode, use environment variables
3. **SSL/TLS**: Get certificate from Let's Encrypt (see below)
4. **Security groups**: Restrict access by IP

### HTTPS Setup
```bash
# Install certbot
sudo apt install -y certbot python3-certbot-nginx

# Get certificate (requires domain)
sudo certbot certonly --standalone -d your-domain.com

# Nginx will auto-configure SSL
sudo systemctl reload nginx
```

---

## 📊 Architecture

```
User Browser
    ↓
Nginx (SSL/TLS, rate limiting)
    ↓
FastAPI Backend (8000)
    ├→ PostgreSQL (5432) - Data
    ├→ Redis (6379) - Cache
    ├→ Qdrant (6333) - Vectors
    └→ LLM API (Groq/Gemini)
```

---

## 🔧 Common Commands

```bash
# Start services
docker-compose up -d

# Stop services
docker-compose down

# View logs
docker-compose logs -f api

# Restart service
docker-compose restart api

# SSH into container
docker-compose exec api bash

# Database migrations
docker-compose exec api alembic upgrade head

# Backup database
docker-compose exec -T db pg_dump -U postgres enterprise_rag > backup.sql

# Resource usage
docker stats
```

---

## 📈 Monitoring

### Check Application Health
```bash
curl http://localhost:8000/health
# Response: {"status":"ok"}
```

### View Logs
```bash
# All services
docker-compose logs -f

# Last 100 lines
docker-compose logs --tail 100 api

# Specific service
docker-compose logs -f nginx
```

### Performance
```bash
# Container stats
docker stats

# System resources
free -h
df -h
```

---

## ⚠️ Troubleshooting

### "Connection Refused"
```bash
docker-compose restart
docker-compose logs -f
```

### "502 Bad Gateway"
```bash
curl http://localhost:8000/health
docker-compose restart api
```

### "Database Connection Failed"
```bash
sleep 30
docker-compose exec api alembic upgrade head
```

### "Out of Memory"
```bash
docker stats
# Increase in docker-compose.yml or EC2 instance
```

---

## 🚀 Production Readiness

✅ **Completed**
- Multi-container orchestration
- Nginx reverse proxy with rate limiting
- Database migrations
- Environment variable management
- Health checks
- Optimized dependencies (65 packages)

⚠️ **Recommended**
- HTTPS/SSL certificate
- Domain name configuration
- Automated backups
- Monitoring (CloudWatch/DataDog)
- Auto-scaling setup
- Load balancer

---

## 📞 Support

### View Detailed Guides
- `DEPLOYMENT_EC2_GUIDE.md` - Full step-by-step guide
- `DEPLOYMENT_QUICK_START.md` - 15-minute fast deployment
- `DEPLOYMENT_READY_CHECKLIST.md` - Pre-deployment verification
- `DEPENDENCY_CLEANUP_GUIDE.md` - Understanding optimized dependencies

### Common Issues
1. Check Docker is running: `docker ps`
2. View logs: `docker-compose logs -f`
3. Verify ports open: `sudo netstat -tlnp`
4. Check disk space: `df -h`
5. Restart services: `docker-compose restart`

---

## 💡 Tips

1. **Always backup before updates**
   ```bash
   docker-compose exec -T db pg_dump -U postgres enterprise_rag > backup_$(date +%s).sql
   ```

2. **Monitor logs in production**
   ```bash
   docker-compose logs -f --tail 50
   ```

3. **Update dependencies safely**
   ```bash
   docker-compose build --no-cache
   docker-compose up -d
   ```

4. **Test database recovery**
   ```bash
   docker-compose exec -T db psql -U postgres < backup.sql
   ```

---

## 📋 Deployment Checklist

- [ ] EC2 instance launched
- [ ] Docker installed
- [ ] Code uploaded
- [ ] `.env` configured
- [ ] `docker-compose build` successful
- [ ] `docker-compose up -d` successful
- [ ] Migrations run: `alembic upgrade head`
- [ ] Frontend loads at http://ec2-ip
- [ ] API responds at http://ec2-ip/api/docs
- [ ] Login works
- [ ] Can upload document
- [ ] Chat/query works
- [ ] Logs are clean

---

## 🎯 Next Steps

1. **Immediate**: Deploy to EC2 (follow 5 steps above)
2. **Day 1**: Setup HTTPS and domain
3. **Week 1**: Enable monitoring and backups
4. **Month 1**: Configure auto-scaling

---

**Ready to deploy!** 🚀

For detailed instructions, see `DEPLOYMENT_EC2_GUIDE.md`

---

**Version**: 1.0  
**Date**: August 6, 2026  
**Status**: Production Ready ✅
