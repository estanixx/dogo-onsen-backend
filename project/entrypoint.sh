#!/bin/sh
set -e

echo "Entry point: running database migrations"

# Ensure DATABASE_URL uses asyncpg dialect if necessary
if [ -n "$DATABASE_URL" ] && echo "$DATABASE_URL" | grep -q '^postgresql://'; then
  export DATABASE_URL="${DATABASE_URL/postgresql:\/\//postgresql+asyncpg:\/\/}"
fi

if [ -x ./migrate.sh ]; then
  ./migrate.sh
else
  echo "migrate.sh not found or not executable"
  exit 1
fi

echo "Starting uvicorn"
exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000} --proxy-headers
