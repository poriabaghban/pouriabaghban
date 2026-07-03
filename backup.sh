#!/bin/bash
# Backup script for pouriabaghban3
# Performs automated database and media files backup
# Add to crontab for scheduled execution

set -e

# Configuration
BACKUP_DIR="/home/appuser/backups"
DATE=$(date +%Y%m%d_%H%M%S)
DB_NAME="pouriabaghban3"
DB_USER="appuser"
DAYS_TO_KEEP=30

# Create backup directory
mkdir -p "$BACKUP_DIR"

echo "Starting backup at $(date)"
echo "================================"

# 1. Database Backup
echo "Backing up database..."
BACKUP_FILE="$BACKUP_DIR/db_$DATE.sql"
pg_dump -h localhost -U "$DB_USER" -d "$DB_NAME" -F c -b -v -f "$BACKUP_FILE"
gzip "$BACKUP_FILE"
echo "✓ Database backed up: ${BACKUP_FILE}.gz"

# 2. Media Files Backup
echo "Backing up media files..."
MEDIA_BACKUP="$BACKUP_DIR/media_$DATE.tar.gz"
tar -czf "$MEDIA_BACKUP" -C /home/appuser/pouriabaghban3 media/
echo "✓ Media files backed up: $MEDIA_BACKUP"

# 3. Static Files Backup (optional, can be regenerated)
echo "Backing up static files..."
STATIC_BACKUP="$BACKUP_DIR/static_$DATE.tar.gz"
tar -czf "$STATIC_BACKUP" -C /home/appuser/pouriabaghban3 staticfiles/
echo "✓ Static files backed up: $STATIC_BACKUP"

# 4. Remove old backups
echo "Cleaning up old backups..."
find "$BACKUP_DIR" -name "db_*.sql.gz" -mtime +$DAYS_TO_KEEP -delete
find "$BACKUP_DIR" -name "media_*.tar.gz" -mtime +$DAYS_TO_KEEP -delete
find "$BACKUP_DIR" -name "static_*.tar.gz" -mtime +$DAYS_TO_KEEP -delete
echo "✓ Old backups removed"

# 5. Summary
echo ""
echo "Backup completed at $(date)"
echo "================================"
du -sh "$BACKUP_DIR"

# 6. Log backup
echo "Backup completed at $(date) - Success" >> /var/log/pouriabaghban3_backup.log
