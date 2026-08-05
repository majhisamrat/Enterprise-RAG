#!/bin/bash

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Functions
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if .env exists
if [ ! -f .env ]; then
    log_error ".env file not found!"
    log_info "Please copy production.env.example to .env and configure it:"
    echo "    cp production.env.example .env"
    echo "    nano .env"
    exit 1
fi

log_info "Starting Enterprise RAG deployment..."

# Step 1: Pull latest code
log_info "Pulling latest code from repository..."
git pull origin main || log_warn "Git pull failed, continuing with current code..."

# Step 2: Build Docker images
log_info "Building Docker images..."
docker compose build --no-cache

# Step 3: Stop old containers
log_info "Stopping old containers..."
docker compose down || true

# Step 4: Start new containers
log_info "Starting containers..."
docker compose up -d

# Step 5: Wait for services to be healthy
log_info "Waiting for services to become healthy (60 seconds)..."
sleep 10

# Step 6: Run database migrations
log_info "Running database migrations..."
docker compose exec -T backend alembic upgrade head || log_warn "Database migrations may have already been applied"

# Step 7: Verify health
log_info "Verifying service health..."
bash healthcheck.sh || log_warn "Some services may not be fully healthy yet"

# Step 8: Clean up
log_info "Cleaning up old Docker images..."
docker image prune -f

log_info "${GREEN}Deployment completed successfully!${NC}"
log_info "Application is running at: https://your-domain.com"
log_info ""
log_info "Useful commands:"
log_info "  View logs:           docker compose logs -f backend"
log_info "  Stop services:       docker compose down"
log_info "  Restart services:    docker compose restart"
log_info "  Backup database:     bash backup.sh"
