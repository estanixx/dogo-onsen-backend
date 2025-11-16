#!/bin/bash
set -e

echo "Running database migrations..."

# Convert postgresql:// to postgresql+asyncpg:// if needed
if [[ "$DATABASE_URL" == postgresql://* ]]; then
    export DATABASE_URL="${DATABASE_URL/postgresql:\/\//postgresql+asyncpg:\/\/}"
fi

# Run alembic migrations
alembic upgrade head

echo "Migrations completed successfully!"
