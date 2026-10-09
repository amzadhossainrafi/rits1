#!/bin/bash
# Daily database backup. Run from the project folder. Keeps 14 days.
set -e
cd "$(dirname "$0")/.."
mkdir -p backups
docker compose exec -T db pg_dump -U ritsone ritsone | gzip > "backups/ritsone-$(date +%F).sql.gz"
find backups -name 'ritsone-*.sql.gz' -mtime +14 -delete
echo "Backup done: backups/ritsone-$(date +%F).sql.gz"
