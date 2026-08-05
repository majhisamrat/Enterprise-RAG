#!/bin/bash

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Functions
check_service() {
    local service=$1
    local url=$2
    local container=$3
    
    echo -n "Checking $service... "
    
    if [ -z "$container" ]; then
        if curl -sf "$url" > /dev/null 2>&1; then
            echo -e "${GREEN}✓${NC}"
            return 0
        else
            echo -e "${RED}✗${NC}"
            return 1
        fi
    else
        if docker compose exec -T "$container" curl -sf "$url" > /dev/null 2>&1; then
            echo -e "${GREEN}✓${NC}"
            return 0
        else
            echo -e "${RED}✗${NC}"
            return 1
        fi
    fi
}

check_container() {
    local container=$1
    
    echo -n "Checking container $container is running... "
    
    if docker compose ps "$container" | grep -q "Up"; then
        echo -e "${GREEN}✓${NC}"
        return 0
    else
        echo -e "${RED}✗${NC}"
        return 1
    fi
}

echo "============================================"
echo "Health Check - Enterprise RAG"
echo "============================================"

# Check containers are running
echo ""
echo "Container Status:"
check_container "postgres" || true
check_container "redis" || true
check_container "qdrant" || true
check_container "backend" || true
check_container "frontend" || true
check_container "nginx" || true

# Check services
echo ""
echo "Service Health Checks:"

# PostgreSQL
echo -n "Checking PostgreSQL... "
if docker compose exec -T postgres pg_isready -U postgres > /dev/null 2>&1; then
    echo -e "${GREEN}✓${NC}"
else
    echo -e "${RED}✗${NC}"
fi

# Redis
echo -n "Checking Redis... "
if docker compose exec -T redis redis-cli ping | grep -q "PONG"; then
    echo -e "${GREEN}✓${NC}"
else
    echo -e "${RED}✗${NC}"
fi

# Qdrant
echo -n "Checking Qdrant... "
if docker compose exec -T qdrant curl -sf http://localhost:6333/health > /dev/null 2>&1; then
    echo -e "${GREEN}✓${NC}"
else
    echo -e "${RED}✗${NC}"
fi

# Backend API
echo -n "Checking Backend API... "
if docker compose exec -T backend curl -sf http://localhost:8000/api/v1/health > /dev/null 2>&1; then
    echo -e "${GREEN}✓${NC}"
else
    echo -e "${RED}✗${NC}"
fi

# Nginx
echo -n "Checking Nginx... "
if docker compose exec -T nginx curl -sf http://localhost/health > /dev/null 2>&1; then
    echo -e "${GREEN}✓${NC}"
else
    echo -e "${RED}✗${NC}"
fi

echo ""
echo "============================================"
echo "Health check complete!"
echo "============================================"
