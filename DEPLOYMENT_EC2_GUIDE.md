# Deploy Enterprise RAG to AWS EC2 - Complete Guide

## Prerequisites

✅ AWS Account (with EC2 access)
✅ EC2 instance running (Ubuntu 22.04 LTS recommended)
✅ Security group configured (ports 22, 80, 443, 8000, 5432)
✅ Key pair (.pem file) for SSH access
✅ Domain name (optional, for production)

---

## Phase 1: Prepare Your Local Environment

### Step 1.1: Build Frontend
```bash
cd frontend
npm run build
# Output: dist/ folder created
```

### Step 1.2: Build Backend (if needed)
```bash
# Backend uses Python, no build needed
# Just ensure requirements.txt is up to date
pip freeze > requirements.txt
```

### Step 1.3: Create Deployment Package
```bash
# From project root
mkdir -p deployment
cp -r frontend/dist deployment/frontend
cp -r app deployment/app
cp -r alembic deployment/alembic
cp requirements.txt deployment/
cp .env.example deployment/.env.example
cp docker-compose.yml deployment/
cp Dockerfile deployment/
cp nginx/nginx.conf deployment/nginx.conf
```

---

## Phase 2: Launch EC2 Instance

### Step 2.1: Create EC2 Instance (AWS Console)
1. Go to AWS Console → EC2 → Instances
2. Click "Launch Instance"
3. Choose Ubuntu 22.04 LTS (free tier eligible)
4. Instance type: t2.micro (free) or t3.small (recommended for production)
5. Configure storage: 30-50 GB SSD
6. Add security group rules:
   - SSH (22): Your IP
   - HTTP (80): 0.0.0.0/0
   - HTTPS (443): 0.0.0.0/0
   - Custom TCP (8000): 0.0.0.0/0 (for backend)
   - PostgreSQL (5432): 0.0.0.0/0 or just your IP
7. Review and launch
8. Select/create key pair and download .pem file

### Step 2.2: Get EC2 Public IP
```bash
# AWS Console → Instances → Select your instance
# Copy "Public IPv4 address"
# Example: 54.123.45.67
```

---

## Phase 3: Connect to EC2 via SSH

### Step 3.1: Set Permissions on Key Pair
```bash
chmod 400 /path/to/your-key.pem
```

### Step 3.2: SSH into EC2
```bash
ssh -i /path/to/your-key.pem ubuntu@your-ec2-public-ip
# Example: ssh -i ~/Downloads/my-key.pem ubuntu@54.123.45.67
```

### Step 3.3: Update System
```bash
sudo apt update
sudo apt upgrade -y
```

---

## Phase 4: Install Dependencies

### Step 4.1: Install Docker and Docker Compose
```bash
# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Add user to docker group
sudo usermod -aG docker ubuntu

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Verify installation
docker --version
docker-compose --version
```

### Step 4.2: Install Git
```bash
sudo apt install -y git
```

### Step 4.3: Install Python & Node.js (for direct deployment without Docker)
```bash
# Python
sudo apt install -y python3.11 python3.11-venv python3-pip

# Node.js
sudo curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt install -y nodejs
```

---

## Phase 5: Upload Code to EC2

### Option A: Using Git (Recommended)
```bash
# On EC2:
cd /home/ubuntu
git clone https://github.com/YOUR-USERNAME/enterprise-rag.git
cd enterprise-rag
```

### Option B: Using SCP (from your local machine)
```bash
# From your local machine
scp -i /path/to/your-key.pem -r /path/to/local/enterprise-rag ubuntu@54.123.45.67:/home/ubuntu/
```

---

## Phase 6: Deploy Using Docker (Recommended)

### Step 6.1: Create Environment File
```bash
cd /home/ubuntu/enterprise-rag

# Copy example env
cp .env.example .env

# Edit .env with your settings
nano .env
```

**Important .env variables:**
```bash
# Database
DATABASE_URL=postgresql://postgres:your_password@db:5432/enterprise_rag
POSTGRES_PASSWORD=your_secure_password

# API Settings
API_HOST=0.0.0.0
API_PORT=8000

# Frontend
VITE_API_URL=http://your-ec2-ip:8000

# Google OAuth (if using)
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret

# Mem0 API (if using)
MEM0_API_KEY=your-mem0-api-key

# JWT Secret
SECRET_KEY=your-secure-jwt-secret-key
```

### Step 6.2: Build Frontend
```bash
cd frontend
npm install
npm run build
# Creates dist/ folder

# Back to root
cd ..
```

### Step 6.3: Start Docker Containers
```bash
# Build images
docker-compose build

# Start containers
docker-compose up -d

# Verify containers running
docker-compose ps
```

### Step 6.4: Run Database Migrations
```bash
# Wait for database to be ready (about 30 seconds)
sleep 30

# Run migrations
docker-compose exec api alembic upgrade head

# Create superuser (optional)
docker-compose exec api python -m scripts.create_superuser
```

### Step 6.5: Check Logs
```bash
# View all logs
docker-compose logs

# View specific service logs
docker-compose logs api
docker-compose logs db
docker-compose logs nginx
```

---

## Phase 7: Deploy Without Docker (Alternative)

### Step 7.1: Setup Python Virtual Environment
```bash
cd /home/ubuntu/enterprise-rag

# Create venv
python3.11 -m venv venv

# Activate venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Step 7.2: Setup Frontend
```bash
cd frontend
npm install
npm run build

cd ..
```

### Step 7.3: Setup Database (PostgreSQL)
```bash
# Install PostgreSQL
sudo apt install -y postgresql postgresql-contrib

# Start PostgreSQL
sudo systemctl start postgresql
sudo systemctl enable postgresql

# Create database and user
sudo -u postgres psql << EOF
CREATE USER rag_user WITH PASSWORD 'your_password';
CREATE DATABASE enterprise_rag OWNER rag_user;
GRANT ALL PRIVILEGES ON DATABASE enterprise_rag TO rag_user;
EOF
```

### Step 7.4: Run Database Migrations
```bash
# Activate venv
source venv/bin/activate

# Update .env with local database URL
# DATABASE_URL=postgresql://rag_user:your_password@localhost:5432/enterprise_rag

# Run migrations
alembic upgrade head
```

### Step 7.5: Start Backend Service
```bash
# Option 1: Direct run (for testing)
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000

# Option 2: Using systemd (for production)
sudo nano /etc/systemd/system/enterprise-rag.service
```

**Content for enterprise-rag.service:**
```ini
[Unit]
Description=Enterprise RAG Backend
After=network.target

[Service]
Type=notify
User=ubuntu
WorkingDirectory=/home/ubuntu/enterprise-rag
Environment="PATH=/home/ubuntu/enterprise-rag/venv/bin"
ExecStart=/home/ubuntu/enterprise-rag/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**Enable and start:**
```bash
sudo systemctl daemon-reload
sudo systemctl enable enterprise-rag
sudo systemctl start enterprise-rag
```

---

## Phase 8: Configure Nginx (Reverse Proxy)

### Step 8.1: Install Nginx
```bash
sudo apt install -y nginx
```

### Step 8.2: Create Nginx Config
```bash
sudo nano /etc/nginx/sites-available/enterprise-rag
```

**Content:**
```nginx
upstream backend {
    server localhost:8000;
}

server {
    listen 80;
    server_name your-domain.com your-ec2-ip;
    
    client_max_body_size 100M;

    # Frontend
    location / {
        root /home/ubuntu/enterprise-rag/frontend/dist;
        try_files $uri $uri/ /index.html;
    }

    # API
    location /api/ {
        proxy_pass http://backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Health check
    location /health {
        proxy_pass http://backend;
    }
}
```

### Step 8.3: Enable Config
```bash
sudo ln -s /etc/nginx/sites-available/enterprise-rag /etc/nginx/sites-enabled/

# Remove default config (optional)
sudo rm /etc/nginx/sites-enabled/default

# Test config
sudo nginx -t

# Restart Nginx
sudo systemctl restart nginx
```

---

## Phase 9: Setup HTTPS with Let's Encrypt (Production)

### Step 9.1: Install Certbot
```bash
sudo apt install -y certbot python3-certbot-nginx
```

### Step 9.2: Get SSL Certificate
```bash
sudo certbot certonly --nginx -d your-domain.com
# Follow prompts to setup certificate
```

### Step 9.3: Update Nginx Config
```bash
sudo nano /etc/nginx/sites-available/enterprise-rag
```

**Add to server block:**
```nginx
listen 443 ssl;
ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;

# Redirect HTTP to HTTPS
server {
    listen 80;
    server_name your-domain.com;
    return 301 https://$server_name$request_uri;
}
```

### Step 9.4: Reload Nginx
```bash
sudo nginx -t
sudo systemctl reload nginx
```

---

## Phase 10: Verification & Testing

### Step 10.1: Check Services Status
```bash
# Check if backend is running
curl http://localhost:8000/health

# Check if Nginx is running
sudo systemctl status nginx

# Check if database is running
sudo systemctl status postgresql
```

### Step 10.2: Access Application
```bash
# From browser: http://your-ec2-ip or https://your-domain.com
# Frontend should load
# Try logging in
# Check if API calls work
```

### Step 10.3: Check Logs
```bash
# Backend logs
tail -f /var/log/syslog | grep enterprise-rag

# Nginx logs
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log

# Docker logs (if using Docker)
docker-compose logs -f
```

---

## Phase 11: Monitoring & Maintenance

### Step 11.1: Setup Log Rotation
```bash
sudo nano /etc/logrotate.d/enterprise-rag
```

**Content:**
```
/var/log/enterprise-rag/*.log {
    daily
    rotate 7
    compress
    delaycompress
    notifempty
    create 0640 ubuntu ubuntu
    sharedscripts
}
```

### Step 11.2: Backup Database
```bash
# Create backup directory
mkdir -p /home/ubuntu/backups

# Daily backup script
sudo nano /usr/local/bin/backup-rag.sh
```

**Content:**
```bash
#!/bin/bash
BACKUP_DIR="/home/ubuntu/backups"
DATE=$(date +%Y%m%d_%H%M%S)

# Using Docker
docker-compose exec -T db pg_dump -U postgres enterprise_rag > $BACKUP_DIR/rag_backup_$DATE.sql

# Compress
gzip $BACKUP_DIR/rag_backup_$DATE.sql

# Keep only last 7 days
find $BACKUP_DIR -name "*.sql.gz" -mtime +7 -delete
```

**Make executable:**
```bash
sudo chmod +x /usr/local/bin/backup-rag.sh

# Add to crontab (daily at 2 AM)
sudo crontab -e
# Add: 0 2 * * * /usr/local/bin/backup-rag.sh
```

### Step 11.3: Monitor Disk Space
```bash
# Check current usage
df -h

# Alert if disk usage > 80%
# Add to monitoring script or crontab
```

---

## Phase 12: Troubleshooting

### Problem: Connection Refused
```bash
# Check if service is running
sudo systemctl status enterprise-rag
docker-compose ps

# Restart service
sudo systemctl restart enterprise-rag
docker-compose restart api
```

### Problem: 502 Bad Gateway
```bash
# Check Nginx logs
sudo tail -f /var/log/nginx/error.log

# Verify backend is running
curl http://localhost:8000/health

# Check firewall
sudo ufw status
sudo ufw allow 8000
```

### Problem: Database Connection Failed
```bash
# Check PostgreSQL
sudo systemctl status postgresql

# Check connection string in .env
# Verify credentials

# Test connection
psql -U postgres -h localhost -d enterprise_rag
```

### Problem: Out of Memory
```bash
# Check memory usage
free -h

# Check running processes
ps aux --sort=-%mem

# Increase swap (if needed)
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

---

## Phase 13: Post-Deployment

### Step 13.1: Update Security Group
```bash
# AWS Console → Security Groups → Your SG
# Edit inbound rules:
# SSH (22): Only your IP
# HTTP (80): 0.0.0.0/0
# HTTPS (443): 0.0.0.0/0
# PostgreSQL (5432): Only app server IP
```

### Step 13.2: Setup Auto-Scaling (Optional)
```bash
# AWS Console → Auto Scaling Groups
# Create launch template
# Set min/max capacity
```

### Step 13.3: Setup Load Balancer (Optional)
```bash
# AWS Console → Load Balancers
# Create Application Load Balancer
# Point to EC2 instances
```

---

## Quick Reference Commands

### Docker Deployment
```bash
# Start all services
docker-compose up -d

# Stop all services
docker-compose down

# View logs
docker-compose logs -f

# Restart specific service
docker-compose restart api

# SSH into container
docker-compose exec api bash

# Database migration
docker-compose exec api alembic upgrade head
```

### Direct Deployment
```bash
# Start backend
source venv/bin/activate
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000

# Check service status
sudo systemctl status enterprise-rag

# View logs
sudo journalctl -u enterprise-rag -f

# Restart service
sudo systemctl restart enterprise-rag
```

### Common Operations
```bash
# Check if port is in use
lsof -i :8000

# Kill process on port
sudo lsof -t -i :8000 | xargs kill -9

# Check disk space
df -h

# Check memory
free -h

# Update system
sudo apt update && sudo apt upgrade -y

# Reboot
sudo reboot
```

---

## Security Best Practices

✅ Keep security groups restrictive
✅ Use strong database passwords
✅ Use HTTPS in production
✅ Keep system updated
✅ Use .env for sensitive data
✅ Regularly backup database
✅ Monitor logs for errors
✅ Use managed database (RDS) for production
✅ Enable VPC for database security
✅ Rotate API keys regularly

---

## Performance Optimization

### For Production:
- Use t3.small or larger instance
- Enable RDS for database (managed PostgreSQL)
- Use CloudFront for CDN
- Enable auto-scaling
- Use Application Load Balancer
- Setup CloudWatch monitoring
- Enable S3 for file uploads
- Use ElastiCache for caching

---

## Support & Monitoring

### Key Metrics to Monitor:
- CPU usage
- Memory usage
- Disk space
- Network throughput
- API response time
- Error rate
- Database connections

### Tools:
- AWS CloudWatch
- New Relic
- Datadog
- Prometheus + Grafana

---

## Cost Estimation (AWS Free Tier)

- EC2: t2.micro - FREE (12 months)
- RDS: db.t2.micro - FREE (12 months, 20GB storage)
- CloudFront: 1GB free/month
- S3: 5GB free
- Total: ~$0 first 12 months, then ~$20-50/month

---

## Final Checklist

- [x] EC2 instance created and running
- [x] Security groups configured
- [x] Code uploaded to EC2
- [x] Dependencies installed
- [x] Database configured
- [x] Backend running
- [x] Frontend deployed
- [x] Nginx configured
- [x] SSL certificate (production)
- [x] Application accessible
- [x] Logs monitored
- [x] Backups configured

**Status: READY FOR PRODUCTION** ✅

---

## Next Steps

1. Test application thoroughly
2. Monitor logs and metrics
3. Setup monitoring alerts
4. Configure backups
5. Plan scaling strategy
6. Document deployment
7. Create runbook for team

---

**Last Updated**: August 6, 2026
**Version**: 1.0
**Status**: Production Ready ✅
