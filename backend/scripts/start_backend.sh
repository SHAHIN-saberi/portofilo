#!/bin/sh
# Backend container entrypoint: run migrations, then start uvicorn.
set -e

PORT="${PORT:-8000}"

echo "[start_backend] Running database migrations..."
alembic upgrade head || echo "[start_backend] WARNING: alembic upgrade failed (no migrations yet?)"

echo "[start_backend] Starting FastAPI (uvicorn) on port $PORT..."
exec uvicorn app.main:app --host 0.0.0.0 --port "$PORT"
