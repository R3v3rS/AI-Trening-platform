#!/bin/bash
set -e

PROJECT_DIR="/home/kombat/cycling-app"
VENV_DIR="$PROJECT_DIR/.venv"
API_DIR="$PROJECT_DIR/apps/api"
WEB_DIR="$PROJECT_DIR/apps/web"

echo "========================================"
echo "Deploy: $(date)"
echo "========================================"

# 1. Pull najnowszego kodu
cd "$PROJECT_DIR"
git pull origin main

# 2. Backend – virtualenv i zależności
echo "[1/4] Instalacja zależności backendu..."
if [ ! -d "$VENV_DIR" ]; then
    python3 -m venv "$VENV_DIR"
    echo "      Utworzono nowy virtualenv."
fi
source "$VENV_DIR/bin/activate"
pip install --quiet -r "$API_DIR/requirements.txt"
deactivate

# 3. Frontend – build
echo "[2/4] Build frontendu..."
cd "$WEB_DIR"
npm ci --silent
npm run build
cd "$PROJECT_DIR"

# 4. Restart usług
echo "[3/4] Restart usług systemd..."
sudo systemctl restart cycling-api
sudo systemctl restart cycling-web

# 5. Healthcheck
echo "[4/4] Healthcheck..."
sleep 2
STATUS=$(curl -s -o /dev/null -w "%{http_code}" \
    http://localhost:5000/api/v1/health)
if [ "$STATUS" = "200" ]; then
    echo "      OK – API odpowiada (HTTP $STATUS)"
else
    echo "      BŁĄD – API nie odpowiada (HTTP $STATUS)"
    echo "      Sprawdź: sudo journalctl -u cycling-api -n 50"
    exit 1
fi

echo "========================================"
echo "Deploy zakończony pomyślnie: $(date)"
echo "========================================"
