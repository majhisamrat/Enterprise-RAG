#!/bin/bash

# ═══════════════════════════════════════════════════════════════════════════
# ATLAS Enterprise RAG - Live Logs Viewer
# Shows real-time logs from all running containers on EC2
# ═══════════════════════════════════════════════════════════════════════════

set -e

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
COMPOSE_FILE="docker-compose.backend.improved.yml"
LOG_DIR="./logs"
TIMESTAMP=$(date +"%Y-%m-%d %H:%M:%S")

# Functions
print_header() {
    echo -e "${BLUE}════════════════════════════════════════════════════════════════${NC}"
    echo -e "${GREEN}$1${NC}"
    echo -e "${BLUE}════════════════════════════════════════════════════════════════${NC}"
}

print_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

show_menu() {
    clear
    print_header "ATLAS Live Logs Viewer"
    echo ""
    echo -e "${BLUE}Select logs to view:${NC}"
    echo ""
    echo "  1) Backend (FastAPI)"
    echo "  2) Celery Worker"
    echo "  3) Both Backend + Celery"
    echo "  4) PostgreSQL"
    echo "  5) Redis"
    echo "  6) Qdrant"
    echo "  7) Elasticsearch"
    echo "  8) All Services"
    echo "  9) Container Status"
    echo "  0) Exit"
    echo ""
    echo -n "Enter choice [0-9]: "
}

view_logs() {
    local service=$1
    local lines=$2
    
    print_header "Live Logs: $service"
    print_info "Showing last $lines lines. Press Ctrl+C to stop."
    echo ""
    
    docker-compose -f "$COMPOSE_FILE" logs -f "$service" --tail="$lines"
}

view_multiple_logs() {
    local services=$1
    local lines=$2
    
    print_header "Live Logs: Multiple Services"
    print_info "Services: $services"
    print_info "Press Ctrl+C to stop."
    echo ""
    
    docker-compose -f "$COMPOSE_FILE" logs -f $services --tail="$lines"
}

show_status() {
    clear
    print_header "Container Status"
    echo ""
    docker-compose -f "$COMPOSE_FILE" ps
    echo ""
    print_info "Press Enter to continue..."
    read
}

show_health() {
    clear
    print_header "Health Check Status"
    echo ""
    docker-compose -f "$COMPOSE_FILE" ps | grep -E "postgres|redis|qdrant|elasticsearch|backend|celery" || true
    echo ""
    echo -e "${BLUE}Services Status:${NC}"
    docker-compose -f "$COMPOSE_FILE" ps --format "table {{.Service}}\t{{.Status}}\t{{.Health}}" || true
    echo ""
    print_info "Press Enter to continue..."
    read
}

show_stats() {
    clear
    print_header "Resource Usage"
    echo ""
    docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}"
    echo ""
    print_info "Press Enter to continue..."
    read
}

main() {
    # Check if docker-compose file exists
    if [ ! -f "$COMPOSE_FILE" ]; then
        print_error "docker-compose file not found: $COMPOSE_FILE"
        exit 1
    fi
    
    # Create logs directory if it doesn't exist
    mkdir -p "$LOG_DIR"
    
    while true; do
        show_menu
        read choice
        
        case $choice in
            1)
                view_logs "backend" 50
                ;;
            2)
                view_logs "celery" 50
                ;;
            3)
                view_multiple_logs "backend celery" 30
                ;;
            4)
                view_logs "postgres" 30
                ;;
            5)
                view_logs "redis" 30
                ;;
            6)
                view_logs "qdrant" 30
                ;;
            7)
                view_logs "elasticsearch" 30
                ;;
            8)
                view_multiple_logs "postgres redis qdrant elasticsearch backend celery" 20
                ;;
            9)
                show_status
                ;;
            0)
                print_info "Exiting..."
                exit 0
                ;;
            *)
                print_error "Invalid choice. Please try again."
                sleep 2
                ;;
        esac
    done
}

# Run main function
main
