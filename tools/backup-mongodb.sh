#!/bin/bash
# Daily MongoDB backup — runs at midnight, saves to brain

DATE=$(date +%Y-%m-%d)
BACKUP_DIR="/home/r2d2/brain/backups/mongodb"
mkdir -p "$BACKUP_DIR"

echo "📦 Backing up MongoDB — $DATE"

docker exec r2d2-mongodb mongodump \
  --db analytics \
  --archive \
  --gzip > "$BACKUP_DIR/analytics-$DATE.gz"

if [ $? -eq 0 ]; then
  echo "✅ Backup saved: $BACKUP_DIR/analytics-$DATE.gz"
  # Keep only last 30 days
  find "$BACKUP_DIR" -name "*.gz" -mtime +30 -delete
  echo "🧹 Old backups cleaned up"
else
  echo "❌ Backup failed"
  exit 1
fi
