# EC2 Deployment - Quick Start (5 Steps)

## TL;DR - Fast Deployment

### Step 1: Launch EC2 Instance (5 minutes)
```bash
# AWS Console:
# 1. Go to EC2 → Instances
# 2. Launch Instance
# 3. Choose: Ubuntu 22.04 LTS
# 4. Type: t2.micro (free) or t3.small (recommended)
# 5. Storage: 30GB SSD
# 6. Security: Add rules for ports 22, 80, 443, 8000
# 7. Launch and download key pair (.pem file)
```

### Step 2: Connect to EC2 (2 minutes)
```bash
# Local machine:
chmod 400 your-key.pem
ssh -i your-key.pem ubuntu@your-ec2-public-ip

# On EC2:
sudo apt update && sudo apt upgrade -y
```

### Step 3: Clone & Setup Code (3 minutes)
```bash
# On EC2:
cd /home/ubuntu
git clone https://github.com/YOUR-USERNAME/enterprise-rag.git
cd enterprise-rag

# Copy environment file
cp .env.example .env

# Edit with your settings
nano .env
```

### Step 4: Deploy with Docker (5 minutes)
```bash
# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Build and start
cd enterprise-rag
docker-compose build
docker-compose up -d

# Wait 30 seconds for database to be ready
sleep 30

# Run migrations
docker-compose exec api alembic upgrade head
```

### Step 5: Setup Nginx (2 minutes)
```bash
# Install Nginx
sudo apt install -y nginx

# Create config
sudo nano /etc/nginx/sites-available/enterprise-rag
```

**Paste this content:**
```nginx
upstream backend {
    server localhost:8000;
}

server {
    listen 80;
    server_name _;
    client_max_body_size 100M;

    location / {
        root /home/ubuntu/enterprise-rag/frontend/dist;
        try_files $uri $uri/ /index.html;
    }

    location /api/ {
        proxy_pass http://backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

**Enable and start:**
```bash
sudo ln -s /etc/nginx/sites-available/enterprise-rag /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

---

## Total Time: ~15 minutes

Now open: `http://your-ec2-public-ip`

---

## Verify Everything Works

### Check Backend
```bash
curl http://localhost:8000/health
# Should return: {"status":"ok"}
```

### Check Frontend
```bash
# Open in browser: http://your-ec2-ip
# Should show login page
```

### Check Containers
```bash
docker-compose ps
# Should show: api, db, nginx (all running)
```

### Check Logs
```bash
docker-compose logs -f
# Should show: database ready, API running
```

---

## Common Issues & Fixes

### "Connection refused"
```bash
# Container not running?
docker-compose up -d

# Port already in use?
lsof -i :8000
sudo kill -9 <PID>
```

### "502 Bad Gateway"
```bash
# Backend not responding?
curl http://localhost:8000/health

# Restart backend
docker-compose restart api
```

### "Database error"
```bash
# Wait for database to be ready
sleep 30

# Then run migrations
docker-compose exec api alembic upgrade head
```

### "Frontend not loading"
```bash
# Rebuild frontend
cd frontend
npm install
npm run build
cd ..

# Restart containers
docker-compose restart
```

---

## Essential Commands

```bash
# View logs
docker-compose logs -f

# Restart everything
docker-compose restart

# Stop everything
docker-compose down

# See running containers
docker-compose ps

# Access backend shell
docker-compose exec api bash

# View Nginx logs
sudo tail -f /var/log/nginx/error.log
```

---

## Setup HTTPS (Optional but Recommended)

```bash
# Install certbot
sudo apt install -y certbot python3-certbot-nginx

# Get certificate (requires domain name)
sudo certbot certonly --nginx -d your-domain.com

# Nginx will auto-configure
sudo systemctl reload nginx
```

---

## Monitoring

```bash
# Watch all logs
docker-compose logs -f

# Check CPU/Memory
docker stats

# Check disk space
df -h

# Check service health
docker-compose ps
```

---

## Security Quick Setup

1. **Restrict SSH** (only your IP):
   - AWS Console → Security Groups
   - Edit inbound rule for SSH (22)
   - Change "0.0.0.0/0" to your IP

2. **Strong Database Password**:
   - Edit .env: `POSTGRES_PASSWORD=your-very-strong-password`
   - Use: 16+ characters, mix of letters/numbers/symbols

3. **API Key**:
   - Edit .env: `SECRET_KEY=your-random-secret-key`
   - Use: `python -c "import secrets; print(secrets.token_urlsafe(32))"`

---

## Next Steps (Optional)

1. **Domain Name**: Point domain to EC2 IP (A record)
2. **Auto-Scaling**: Setup load balancer + auto-scaling group
3. **Backups**: Configure automated database backups
4. **Monitoring**: Setup CloudWatch or Datadog
5. **CDN**: Setup CloudFront for static files

---

## Production Checklist

- [ ] Domain name configured
- [ ] HTTPS enabled (Let's Encrypt)
- [ ] Security groups restricted
- [ ] Database password changed
- [ ] Backups configured
- [ ] Monitoring setup
- [ ] Error logging enabled
- [ ] Rate limiting configured

---

## Cost Estimation

- **First 12 months**: FREE (within AWS free tier)
- **After 12 months**: 
  - EC2 t2.micro: ~$10/month
  - RDS (optional): ~$15-30/month
  - **Total**: ~$25-40/month

---

## Support

If stuck, check:
1. EC2 logs: `docker-compose logs -f`
2. Nginx logs: `sudo tail -f /var/log/nginx/error.log`
3. Security group rules (ports open?)
4. Environment variables (.env correct?)
5. Docker running? `docker-compose ps`

---

**All set!** Your application is now live on AWS EC2. 🚀

For detailed troubleshooting, see `DEPLOYMENT_EC2_GUIDE.md`
