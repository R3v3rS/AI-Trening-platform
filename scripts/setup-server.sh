#!/bin/bash
# Skrypt jednorazowego setupu home servera.
# Uruchom raz po pierwszym git clone na serwerze.
# Wymaga: Ubuntu 24.04, użytkownik kombat z sudo

set -e

PROJECT_DIR="/home/kombat/cycling-app"
VENV_DIR="$PROJECT_DIR/.venv"
API_DIR="$PROJECT_DIR/apps/api"
WEB_DIR="$PROJECT_DIR/apps/web"
DATA_DIR="$PROJECT_DIR/data"

echo "=== Setup: Treningowy Asystent Kolarza ==="

# 1. Zależności systemowe
echo "[1/6] Instalacja zależności systemowych..."
sudo apt-get update -qq
sudo apt-get install -y python3-venv python3-pip nodejs npm curl

# 2. Katalog danych
echo "[2/6] Tworzenie katalogu danych..."
mkdir -p "$DATA_DIR"
touch "$DATA_DIR/.gitkeep"

# 3. Plik .env
echo "[3/6] Konfiguracja .env..."
if [ ! -f "$PROJECT_DIR/.env" ]; then
    cp "$PROJECT_DIR/.env.example" "$PROJECT_DIR/.env"
    # Generuj losowy SECRET_KEY
    SECRET=$(python3 -c "import secrets; print(secrets.token_hex(32))")
    sed -i "s/change-me-in-production/$SECRET/" "$PROJECT_DIR/.env"
    echo "      Utworzono .env z wygenerowanym SECRET_KEY."
else
    echo "      .env już istnieje, pomijam."
fi

# 4. Backend virtualenv
echo "[4/6] Konfiguracja backendu..."
python3 -m venv "$VENV_DIR"
source "$VENV_DIR/bin/activate"
pip install --quiet -r "$API_DIR/requirements.txt"
deactivate

# 5. Frontend build
echo "[5/6] Build frontendu..."
cd "$WEB_DIR"
npm ci --silent
npm run build
cd "$PROJECT_DIR"

# 6. Systemd units
echo "[6/6] Instalacja usług systemd..."

sudo tee /etc/systemd/system/cycling-api.service > /dev/null << EOF
[Unit]
Description=Cycling Training Assistant – Flask API
After=network.target

[Service]
User=kombat
WorkingDirectory=$API_DIR
EnvironmentFile=$PROJECT_DIR/.env
Environment=PYTHONPATH=$API_DIR/src
ExecStart=$VENV_DIR/bin/python $API_DIR/src/main.py
Restart=on-failure
RestartSec=5
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

sudo tee /etc/systemd/system/cycling-web.service > /dev/null << EOF
[Unit]
Description=Cycling Training Assistant – React Frontend
After=network.target

[Service]
User=kombat
WorkingDirectory=$WEB_DIR
ExecStart=/usr/bin/npx serve dist -l 3000
Restart=on-failure
RestartSec=5
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable cycling-api cycling-web
sudo systemctl start cycling-api cycling-web

echo ""
echo "=== Setup zakończony ==="
echo ""
echo "Sprawdź status:"
echo "  sudo systemctl status cycling-api"
echo "  sudo systemctl status cycling-web"
echo ""
echo "Healthcheck:"
echo "  curl http://localhost:5000/api/v1/health"
echo ""
echo "Logi:"
echo "  sudo journalctl -u cycling-api -f"
echo "  sudo journalctl -u cycling-web -f"
