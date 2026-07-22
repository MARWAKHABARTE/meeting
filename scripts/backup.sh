#!/bin/bash
# backup.sh — Sauvegarde automatique de la base de données PostgreSQL
# Usage : ./scripts/backup.sh
# Cron suggéré : 0 2 * * * /chemin/vers/scripts/backup.sh

set -euo pipefail

# ─── Configuration ─────────────────────────────────────────────
BACKUP_DIR="./backups/postgres"
CONTAINER="meeting_ai_postgres"
DB_USER="${POSTGRES_USER:-postgres}"
DB_NAME="${POSTGRES_DB:-meeting_ai}"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_FILE="${BACKUP_DIR}/meeting_ai_${TIMESTAMP}.sql.gz"
RETENTION_DAYS=7

# ─── Création du répertoire de sauvegarde ──────────────────────
mkdir -p "$BACKUP_DIR"

echo "[$(date)] Démarrage de la sauvegarde PostgreSQL..."

# ─── Dumping et compression de la base ─────────────────────────
docker exec "$CONTAINER" \
  pg_dump -U "$DB_USER" -d "$DB_NAME" --no-password \
  | gzip > "$BACKUP_FILE"

echo "[$(date)] Sauvegarde créée : $BACKUP_FILE"

# ─── Rotation : suppression des anciennes sauvegardes ──────────
find "$BACKUP_DIR" -name "*.sql.gz" -mtime +$RETENTION_DAYS -delete
echo "[$(date)] Rotation : sauvegardes de plus de $RETENTION_DAYS jours supprimées."

echo "[$(date)] Sauvegarde terminée avec succès."
