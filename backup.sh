#!/bin/bash

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Configuration
BACKUP_DIR="./backups"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
DB_BACKUP="$BACKUP_DIR/db_backup_$TIMESTAMP.sql.gz"
UPLOAD_BACKUP="$BACKUP_DIR/uploads_backup_$TIMESTAMP.tar.gz"
QDRANT_BACKUP="$BACKUP_DIR/qdrant_backup_$TIMESTAMP.tar.gz"
LOG_FILE="$BACKUP_DIR/backup_$TIMESTAMP.log"

# Functions
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1" | tee -a "$LOG_FILE"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1" | tee -a "$LOG_FILE"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1" | tee -a "$LOG_FILE"
}

# Create backup directory
mkdir -p "$BACKUP_DIR"

echo "============================================" | tee "$LOG_FILE"
echo "Starting Backup - Enterprise RAG" | tee -a "$LOG_FILE"
echo "Timestamp: $TIMESTAMP" | tee -a "$LOG_FILE"
echo "============================================" | tee -a "$LOG_FILE"

# Backup PostgreSQL Database
log_info "Backing up PostgreSQL database..."
if docker compose exec -T postgres pg_dump -U postgres enterprise_rag | gzip > "$DB_BACKUP"; then
    log_info "Database backup completed: $DB_BACKUP"
    log_info "Size: $(du -h "$DB_BACKUP" | cut -f1)"
else
    log_error "Database backup failed!"
    exit 1
fi

# Backup Uploads Directory
log_info "Backing up uploads directory..."
if [ -d "data/uploads" ] && [ "$(ls -A data/uploads)" ]; then
    tar -czf "$UPLOAD_BACKUP" -C data uploads/ 2>/dev/null && \
    log_info "Uploads backup completed: $UPLOAD_BACKUP" || \
    log_warn "Uploads backup failed or directory is empty"
else
    log_warn "No uploads to backup"
fi

# Backup Qdrant Data
log_info "Backing up Qdrant vector database..."
if docker compose exec -T qdrant tar -czf - /qdrant/storage > "$QDRANT_BACKUP" 2>/dev/null; then
    log_info "Qdrant backup completed: $QDRANT_BACKUP"
    log_info "Size: $(du -h "$QDRANT_BACKUP" | cut -f1)"
else
    log_warn "Qdrant backup failed"
fi

# Summary
echo "" | tee -a "$LOG_FILE"
echo "============================================" | tee -a "$LOG_FILE"
echo "Backup Summary" | tee -a "$LOG_FILE"
echo "============================================" | tee -a "$LOG_FILE"
echo "Database: $DB_BACKUP" | tee -a "$LOG_FILE"
[ -f "$UPLOAD_BACKUP" ] && echo "Uploads: $UPLOAD_BACKUP" | tee -a "$LOG_FILE"
[ -f "$QDRANT_BACKUP" ] && echo "Qdrant: $QDRANT_BACKUP" | tee -a "$LOG_FILE"
echo "Log: $LOG_FILE" | tee -a "$LOG_FILE"
echo "============================================" | tee -a "$LOG_FILE"

# Cleanup old backups (keep last 7 days)
log_info "Cleaning up backups older than 7 days..."
find "$BACKUP_DIR" -name "db_backup_*.sql.gz" -mtime +7 -delete
find "$BACKUP_DIR" -name "uploads_backup_*.tar.gz" -mtime +7 -delete
find "$BACKUP_DIR" -name "qdrant_backup_*.tar.gz" -mtime +7 -delete

log_info "Backup process completed successfully!"
