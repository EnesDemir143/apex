#!/usr/bin/env bash
# weekly_restore_test.sh — Restore latest backup to a test DB and verify row counts.
# Run weekly (e.g. via cron or K8s CronJob) to validate backup integrity.
set -euo pipefail

BACKUP_DIR="${BACKUP_DIR:-backups/postgres}"
TEST_DB="${TEST_DB:-apex_restore_test}"
POSTGRES_HOST="${POSTGRES_HOST:-localhost}"
POSTGRES_PORT="${POSTGRES_PORT:-5432}"
POSTGRES_USER="${POSTGRES_USER:-apex}"
POSTGRES_PASSWORD="${POSTGRES_PASSWORD:-apex}"
PGPASSWORD="${POSTGRES_PASSWORD}"
export PGPASSWORD

# Find the most recent backup file
LATEST_BACKUP="$(ls -t "${BACKUP_DIR}"/apex-*.dump 2>/dev/null | head -1)"
if [[ -z "${LATEST_BACKUP}" ]]; then
  echo "ERROR: No backup files found in ${BACKUP_DIR}" >&2
  exit 1
fi
echo "Using backup: ${LATEST_BACKUP}"

# Drop and recreate the test database
psql -h "${POSTGRES_HOST}" -p "${POSTGRES_PORT}" -U "${POSTGRES_USER}" -d postgres \
  -c "DROP DATABASE IF EXISTS ${TEST_DB};"
psql -h "${POSTGRES_HOST}" -p "${POSTGRES_PORT}" -U "${POSTGRES_USER}" -d postgres \
  -c "CREATE DATABASE ${TEST_DB};"

# Restore
pg_restore \
  --host="${POSTGRES_HOST}" \
  --port="${POSTGRES_PORT}" \
  --username="${POSTGRES_USER}" \
  --dbname="${TEST_DB}" \
  --no-owner \
  --no-privileges \
  "${LATEST_BACKUP}"

echo "Restore complete. Verifying row counts..."

# Verify key tables have rows
STOCKS=$(psql -h "${POSTGRES_HOST}" -p "${POSTGRES_PORT}" -U "${POSTGRES_USER}" \
  -d "${TEST_DB}" -tAc "SELECT COUNT(*) FROM stocks;")
PRICES=$(psql -h "${POSTGRES_HOST}" -p "${POSTGRES_PORT}" -U "${POSTGRES_USER}" \
  -d "${TEST_DB}" -tAc "SELECT COUNT(*) FROM stock_prices;")

echo "  stocks:       ${STOCKS} rows"
echo "  stock_prices: ${PRICES} rows"

if [[ "${STOCKS}" -eq 0 ]]; then
  echo "FAIL: stocks table is empty after restore" >&2
  exit 1
fi

echo "PASS: Restore test succeeded (backup: $(basename "${LATEST_BACKUP}"))"

# Cleanup test database
psql -h "${POSTGRES_HOST}" -p "${POSTGRES_PORT}" -U "${POSTGRES_USER}" -d postgres \
  -c "DROP DATABASE IF EXISTS ${TEST_DB};"
