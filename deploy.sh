#!/bin/bash
# ─── SGS Faculty Backend — Deployment Script ───────────────────────────────
# Installs dependencies and cleans up to minimize disk usage

set -e

echo "🚀 Starting backend deployment..."

# 1. Pull latest code
echo "📥 Pulling latest code..."
git pull origin main

# 2. Set up virtual environment (only if not exists)
if [ ! -d ".venv" ]; then
  echo "🐍 Creating virtual environment..."
  python3 -m venv .venv
fi

# 3. Activate and install dependencies (no cache)
echo "📦 Installing dependencies..."
source .venv/bin/activate
pip install --no-cache-dir -q -r requirements.txt

# 4. Run database migrations
echo "🗄️  Running database migrations..."
alembic upgrade head

# 5. Clean up to save disk space
echo "🧹 Cleaning up..."
find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
find . -type f -name "*.pyc" -delete 2>/dev/null || true
pip cache purge 2>/dev/null || true

# 6. Restart PM2 process
echo "⚙️  Restarting PM2..."
pm2 describe sgs-faculty-backend > /dev/null 2>&1 \
  && pm2 restart sgs-faculty-backend \
  || pm2 start ".venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000" --name "sgs-faculty-backend"

pm2 save

echo "✅ Backend deployed successfully!"
echo "   Running on: http://localhost:8000"
