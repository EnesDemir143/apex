#!/usr/bin/env bash
set -euo pipefail

if [[ $# -ne 1 ]]; then
  echo "Usage: $0 <backup-file.dump>" >&2
  exit 64
fi

BACKUP_FILE="$1"
DATABASE_URL="${DATABASE_URL:-postgresql://apex:${POSTGRES_PASSWORD:-apex}@localhost:5432/apex}"

if [[ ! -f "${BACKUP_FILE}" ]]; then
  echo "Backup file not found: ${BACKUP_FILE}" >&2
  exit 66
fi

pg_restore "${BACKUP_FILE}" \
  --dbname="${DATABASE_URL}" \
  --clean \
  --if-exists \
  --no-owner

echo "Restored PostgreSQL backup: ${BACKUP_FILE}"
