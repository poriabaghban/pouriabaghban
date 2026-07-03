#!/bin/bash
# Restore backup for pouriabaghban3
# This script restores database and media files from backup

set -e

if [ -z "$1" ]; then
    echo "Usage: $0 <backup_date>"
    echo "Example: $0 20240101_120000"
    echo ""
    echo "Available backups:"
    ls -la /home/appuser/backups/ | grep "db_"
    exit 1
fi

BACKUP_DATE="$1"
BACKUP_DIR="/home/appuser/backups"
DB_NAME="pouriabaghban3"
DB_USER="appuser"
PROJECT_PATH="/home/appuser/pouriabaghban3"

echo "Restoring backup from: $BACKUP_DATE"
echo "================================"

# Confirm
read -p "Are you sure? This will overwrite current data. (yes/no) " -n 3 -r
echo
if [[ ! $REPLY =~ ^[Yy][Ee][Ss]$ ]]; then
    echo "Cancelled."
    exit 1
fi

# 1. Restore Database
if [ -f "$BACKUP_DIR/db_${BACKUP_DATE}.sql.gz" ]; then
    echo "Restoring database..."
    
    # Drop and recreate database
    dropdb -h localhost -U "$DB_USER" "$DB_NAME" || true
    createdb -h localhost -U "$DB_USER" "$DB_NAME"
    
    # Restore
    gunzip -c "$BACKUP_DIR/db_${BACKUP_DATE}.sql.gz" | psql -h localhost -U "$DB_USER" -d "$DB_NAME"
    echo "✓ Database restored"
else
    echo "✗ Database backup not found"
    exit 1
fi

# 2. Restore Media Files
if [ -f "$BACKUP_DIR/media_${BACKUP_DATE}.tar.gz" ]; then
    echo "Restoring media files..."
    cd "$PROJECT_PATH"
    rm -rf media/
    tar -xzf "$BACKUP_DIR/media_${BACKUP_DATE}.tar.gz"
    echo "✓ Media files restored"
else
    echo "⚠ Media backup not found (skipping)"
fi

echo ""
echo "Restore completed at $(date)"
echo "================================"
echo "Please restart the application:"
echo "sudo systemctl restart gunicorn"
