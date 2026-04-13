#!/bin/bash
set -e
cd /home/kombat/cycling-app
git pull origin main
pip3 install -r apps/api/requirements.txt --break-system-packages
cd apps/web && npm install && npm run build && cd ../..
sudo systemctl restart cycling-api
sudo systemctl restart cycling-web
echo "Deploy zakończony: $(date)"
