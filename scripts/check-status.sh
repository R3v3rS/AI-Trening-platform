#!/bin/bash
# Szybki przegląd stanu aplikacji na serwerze.

echo "=== Status usług ==="
systemctl is-active cycling-api && echo "cycling-api: DZIAŁA" \
    || echo "cycling-api: ZATRZYMANA"
systemctl is-active cycling-web && echo "cycling-web: DZIAŁA" \
    || echo "cycling-web: ZATRZYMANA"

echo ""
echo "=== Healthcheck API ==="
curl -s http://localhost:5000/api/v1/health | python3 -m json.tool \
    || echo "API nie odpowiada"

echo ""
echo "=== Ostatnie logi API (10 linii) ==="
sudo journalctl -u cycling-api -n 10 --no-pager

echo ""
echo "=== Baza danych ==="
DB="/home/kombat/cycling-app/data/cycling.db"
if [ -f "$DB" ]; then
    SIZE=$(du -sh "$DB" | cut -f1)
    echo "Plik: $DB ($SIZE)"
else
    echo "Baza nie istnieje jeszcze: $DB"
fi
