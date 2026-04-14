# Runbook: Deploy i setup serwera

## Pierwsze uruchomienie (jednorazowo)

```bash
# Na home serverze (SSH):
ssh kombat@<IP_SERWERA>

# Klonowanie repo
git clone `https://github.com/R3v3rS/AI-Trening-platform.git` \
    /home/kombat/cycling-app
cd /home/kombat/cycling-app

# Jednorazowy setup
chmod +x scripts/setup-server.sh
./scripts/setup-server.sh
```

## Aktualizacja aplikacji (każdy deploy)

```bash
ssh kombat@<IP_SERWERA>
cd /home/kombat/cycling-app
chmod +x scripts/deploy.sh
./scripts/deploy.sh
```

## Sprawdzenie stanu

```bash
./scripts/check-status.sh
```

## Przydatne komendy

```bash
# Logi na żywo
sudo journalctl -u cycling-api -f
sudo journalctl -u cycling-web -f

# Restart pojedynczej usługi
sudo systemctl restart cycling-api

# Zatrzymanie
sudo systemctl stop cycling-api cycling-web

# Status
sudo systemctl status cycling-api cycling-web
```

## Porty

| Usługa | Port |
|--------|------|
| Flask API | 5000 |
| React frontend | 3000 |

## Backup bazy

```bash
cp /home/kombat/cycling-app/data/cycling.db \
   /home/kombat/cycling-app/data/cycling.db.bak.$(date +%Y%m%d)
```
