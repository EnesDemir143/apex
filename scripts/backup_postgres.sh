#!/usr/bin/env bash
set -euo pipefail

BACKUP_DIR="${BACKUP_DIR:-backups/postgres}"
TIMESTAMP="$(date -u +%Y%m%dT%H%M%SZ)"
DATABASE_URL="${DATABASE_URL:-postgresql://apex:${POSTGRES_PASSWORD:-apex}@localhost:5432/apex}"
BACKUP_FILE="${BACKUP_DIR}/apex-${TIMESTAMP}.dump"

mkdir -p "${BACKUP_DIR}"

pg_dump "${DATABASE_URL}" \
  --format=custom \
  --compress=9 \
  --no-owner \
  --file="${BACKUP_FILE}"

echo "Created PostgreSQL backup: ${BACKUP_FILE}"

if [[ -n "${OCI_BUCKET_URI:-}" ]]; then
  oci os object put \
    --bucket-uri "${OCI_BUCKET_URI}" \
    --file "${BACKUP_FILE}" \
    --force
  echo "Uploaded backup to OCI bucket: ${OCI_BUCKET_URI}"
fi
