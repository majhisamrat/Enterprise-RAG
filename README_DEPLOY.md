# Enterprise RAG - Production Deployment Guide

Complete guide for deploying Enterprise RAG on a single AWS EC2 Ubuntu instance using Docker Compose.

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Ubuntu EC2 Setup](#ubuntu-ec2-setup)
3. [Docker Installation](#docker-installation)
4. [Repository Setup](#repository-setup)
5. [Configuration](#configuration)
6. [Deployment](#deployment)
7. [SSL/HTTPS Setup](#sslhttps-setup-with-lets-encrypt)
8. [Management Commands](#management-commands)
9. [Monitoring & Logs](#monitoring--logs)
10. [Backup & Recovery](#backup--recovery)
11. [Troubleshooting](#troubleshooting)

---

## Prerequisites

- AWS Account with EC2 access
- Ubuntu 22.04 LTS or 24.04 LTS instance
- t3.large or larger (recommended: t3.xlarge for production)
- 50GB+ storage (100GB recommended)
- Security Group with ports:
  - 80 (HTTP)
  - 443 (HTTPS)
  - 22 (SSH)
- Domain name for SSL certificate

---

## Ubuntu EC2 Setup

### 1. Launch EC2 Instance

```bash
# Recommended specifications:
# - AMI: Ubuntu Server 24.04 LTS
# - Instance Type: t3.large (at minimum)
# - Volume: 100GB gp3
# - Security Group: Allow SSH (22), HTTP (80), HTTPS (443)
```

### 2. Connect to Instance

```bash
ssh -i "your-key.pem" ubuntu@your-ec2-ip
```

### 3. Update System

```bash
sudo apt update
sudo apt upgrade -y
sudo apt install -y curl git wget htop
```

### 4. Create Application User (Optional but Recommended)

```bash
sudo useradd -m -s /bin/bash deploy
sudo usermod -aG docker deploy
sudo su - deploy
```

---

## Docker Installation

### 1. Install Docker

```bash
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER
```

Verify installation:

```bash
docker --version
docker run hello-world
```

### 2. Install Docker Compose

```bash
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

Verify installation:

```bash
docker-compose --version
```

### 3. Enable Docker Service

```bash
sudo systemctl enable docker
sudo systemctl start docker
```

---

## Repository Setup

### 1. Clone Repository

```bash
cd /home/ubuntu
git clone https://github.com/your-username/enterprise-rag.git
cd enterprise-rag
```

### 2. Create Necessary Directories

```bash
mkdir -p data/uploads data/logs backups nginx/ssl
chmod 755 deploy.sh healthcheck.sh backup.sh
```

### 3. Build Frontend (Important!)

```bash
cd frontend
npm install
npm run build
cd ..
```

---

## Configuration

### 1. Create Environment File

```bash
cp production.env.example .env
nano .env
```

**Critical variables to update:**

```bash
# Security
SECRET_KEY=generate-a-random-string-here  # Use: openssl rand -hex 32

# Database
DB_PASSWORD=generate-strong-password      # Use: openssl rand -base64 32

# LLM Provider
GEMINI_API_KEY=your-actual-gemini-api-key

# Other services...
```

### 2. Generate Secret Key

```bash
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

### 3. Generate Database Password

```bash
openssl rand -base64 32
```

### 4. Verify .env File

```bash
# Make sure .env file is NOT committed to git
cat .gitignore | grep ".env"
```

---

## Deployment

### 1. Initial Deployment

```bash
# Make script executable
chmod +x deploy.sh

# Run deployment
bash deploy.sh
```

### 2. Verify Deployment

```bash
# Check all services
docker compose ps

# Run health checks
bash healthcheck.sh

# View logs
docker compose logs -f backend
```

### 3. Database Initialization

The deployment script automatically runs migrations. Verify:

```bash
docker compose exec backend alembic current
```

---

## SSL/HTTPS Setup with Let's Encrypt

### 1. Install Certbot

```bash
sudo apt install -y certbot python3-certbot-nginx
```

### 2. Generate Certificate

```bash
sudo certbot certonly --standalone -d your-domain.com -d www.your-domain.com
```

### 3. Copy Certificates to Nginx

```bash
sudo cp /etc/letsencrypt/live/your-domain.com/fullchain.pem nginx/ssl/cert.pem
sudo cp /etc/letsencrypt/live/your-domain.com/privkey.pem nginx/ssl/key.pem
sudo chown $USER:$USER nginx/ssl/*.pem
```

### 4. Update Nginx Configuration

Edit `nginx/default.conf` to match your domain:

```nginx
server_name your-domain.com www.your-domain.com;
```

### 5. Restart Nginx

```bash
docker compose restart nginx
```

### 6. Setup Auto-Renewal

```bash
sudo systemctl enable certbot.timer
sudo systemctl start certbot.timer

# Test renewal
sudo certbot renew --dry-run
```

---

## Management Commands

### Start Services

```bash
docker compose up -d
```

### Stop Services

```bash
docker compose down
```

### Restart Services

```bash
docker compose restart
docker compose restart backend    # Restart specific service
```

### View Logs

```bash
docker compose logs -f           # All services
docker compose logs -f backend   # Specific service
docker compose logs -f --tail=100 backend  # Last 100 lines
```

### Execute Commands in Container

```bash
# Access backend shell
docker compose exec backend bash

# Run Python scripts
docker compose exec backend python script.py

# Run migrations
docker compose exec backend alembic upgrade head
```

### Database Management

```bash
# Backup database
bash backup.sh

# Access database directly
docker compose exec postgres psql -U postgres -d enterprise_rag

# List databases
\l

# Exit psql
\q
```

---

## Monitoring & Logs

### 1. System Resource Usage

```bash
# Overall usage
docker stats

# Specific container
docker stats enterprise_rag_backend
```

### 2. Container Logs

```bash
# Check backend errors
docker compose logs --tail=50 backend

# Follow logs in real-time
docker compose logs -f backend

# Log timestamps
docker compose logs --timestamps backend
```

### 3. Service Health

```bash
# Check health status
bash healthcheck.sh

# Manual health checks
curl https://your-domain.com/api/v1/health
curl https://your-domain.com/health
```

### 4. Disk Usage

```bash
df -h              # Overall
docker system df   # Docker-specific
du -sh data/       # Data directory
```

---

## Backup & Recovery

### 1. Regular Backups

```bash
# Manual backup
bash backup.sh

# View backups
ls -lh backups/

# Backup location: ./backups/
```

### 2. Automated Backups (Cron)

```bash
# Open crontab
crontab -e

# Add daily backup at 2 AM
0 2 * * * cd /home/ubuntu/enterprise-rag && bash backup.sh >> /var/log/rag-backup.log 2>&1
```

### 3. Restore Database

```bash
# Stop services
docker compose down

# Restore backup
gunzip -c backups/db_backup_YYYYMMDD_HHMMSS.sql.gz | docker compose exec -T postgres psql -U postgres

# Start services
docker compose up -d
```

### 4. Restore Uploads

```bash
# Extract to data/uploads
tar -xzf backups/uploads_backup_YYYYMMDD_HHMMSS.tar.gz -C data/
```

---

## Troubleshooting

### Services Won't Start

```bash
# Check logs
docker compose logs backend

# Common issues:
# 1. Port already in use - change docker-compose.yml ports
# 2. Database connection - verify DATABASE_URL in .env
# 3. Missing environment variables - check .env file
```

### Database Connection Error

```bash
# Check PostgreSQL is running
docker compose ps postgres

# Verify credentials in .env
grep DATABASE_URL .env

# Test connection
docker compose exec postgres psql -U postgres -c "SELECT 1;"
```

### Memory Issues

```bash
# Increase Docker memory
# Edit /etc/docker/daemon.json
{
  "memory": 4000000000
}

# Restart Docker
sudo systemctl restart docker
docker compose restart
```

### SSL Certificate Issues

```bash
# Check certificate validity
openssl x509 -in nginx/ssl/cert.pem -text -noout

# Regenerate if needed
sudo certbot certonly --force-renewal -d your-domain.com

# Copy new certificates
sudo cp /etc/letsencrypt/live/your-domain.com/fullchain.pem nginx/ssl/cert.pem
sudo cp /etc/letsencrypt/live/your-domain.com/privkey.pem nginx/ssl/key.pem
docker compose restart nginx
```

### API Errors

```bash
# Check backend logs
docker compose logs -f backend

# Test API endpoint
curl -v https://your-domain.com/api/v1/health

# Common issues:
# 1. CORS errors - check nginx configuration
# 2. Timeout errors - increase timeout in nginx/default.conf
# 3. 502 Bad Gateway - backend not responding, check logs
```

### Frontend Not Loading

```bash
# Check Nginx logs
docker compose logs nginx

# Verify frontend build
ls -la frontend/dist/

# Rebuild frontend if needed
cd frontend && npm run build && cd ..
docker compose restart nginx
```

---

## Production Best Practices

1. **Regular Backups**: Automate daily backups using cron
2. **Monitoring**: Setup CloudWatch or similar for alerts
3. **SSL Certificates**: Auto-renew using certbot timer
4. **Log Rotation**: Use logrotate for application logs
5. **Security**: Keep ubuntu packages updated
   ```bash
   sudo apt update && sudo apt upgrade -y
   ```
6. **Resource Limits**: Monitor disk space and memory usage
7. **Database**: Periodically verify and optimize database
8. **Updates**: Plan regular updates with maintenance windows

---

## Support & Resources

- Documentation: See README.md
- Health Check: `bash healthcheck.sh`
- Logs Directory: `./logs/`
- Backups Directory: `./backups/`
- Issues: Check docker-compose logs

---

## Quick Reference

```bash
# Deploy
bash deploy.sh

# Check health
bash healthcheck.sh

# View logs
docker compose logs -f backend

# Backup
bash backup.sh

# Restart services
docker compose restart

# Stop services
docker compose down

# Start services
docker compose up -d
```

---

**Last Updated**: 2026-08-05  
**Version**: 1.0.0
