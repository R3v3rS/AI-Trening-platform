#!/bin/bash
set -e

PROJECT_DIR="/home/kombat/cycling-app"
VENV_DIR="$PROJECT_DIR/.venv"

echo "=== Deploy: $(date) ==="

cd "$PROJECT_DIR"
git pull origin main

# Backend – izolowany virtualenv
if [ ! -d "$VENV_DIR" ]; then
    python3 -m venv "$VENV_DIR"
fi
source "$VENV_DIR/bin/activate"
pip install -r apps/api/requirements.txt

# Frontend
cd apps/web
npm ci
npm run build
cd "$PROJECT_DIR"

sudo systemctl restart cycling-api
sudo systemctl restart cycling-web

echo "=== Deploy zakończony: $(date) ==="
