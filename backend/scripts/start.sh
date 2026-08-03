#!/bin/bash
set -e
echo "🛡️  CITADEL Shield starting..."
alembic upgrade head
python -c "import asyncio; from app.seed import seed_threats; asyncio.run(seed_threats())"
echo "🚀 Launching API server..."
exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}
