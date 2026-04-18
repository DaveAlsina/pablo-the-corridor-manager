# Deployment

How to run Pablito persistently in production.

---

## Recommended: Raspberry Pi + systemd

Pablito is lightweight. A Raspberry Pi 3/4/5 running 24/7 is the intended production environment. The bot process and PostgreSQL Docker container run alongside each other.

### Prerequisites

- Raspberry Pi with Raspberry Pi OS (or Ubuntu)
- Docker installed: `curl -fsSL https://get.docker.com | sh`
- uv installed: `curl -LsSf https://astral.sh/uv/install.sh | sh`
- Project cloned and configured (see [GET_STARTED.md](GET_STARTED.md))
- Database populated (`make populate`)

---

### systemd Service

Create `/etc/systemd/system/pablito.service`:

```ini
[Unit]
Description=Pablito Corridor Manager Bot
After=network.target docker.service
Requires=docker.service

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/pablo-the-corridor-manager
ExecStartPre=/usr/bin/docker-compose up -d
ExecStart=/home/pi/.local/bin/uv run python src/bot.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal
Environment=HOME=/home/pi

[Install]
WantedBy=multi-user.target
```

Adjust `User` and `WorkingDirectory` to match your setup.

Enable and start:
```bash
sudo systemctl daemon-reload
sudo systemctl enable pablito
sudo systemctl start pablito
sudo systemctl status pablito
```

Check logs:
```bash
journalctl -u pablito -f
```

---

## Alternative: Docker Compose (Bot + DB)

You can also run the bot itself as a Docker container alongside PostgreSQL.

Add to `docker-compose.yml`:

```yaml
  bot:
    build: .
    depends_on:
      - postgres
    env_file:
      - .env
    environment:
      POSTGRES_HOST: postgres
    restart: unless-stopped
```

Create a `Dockerfile`:
```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen
COPY . .
CMD ["uv", "run", "python", "src/bot.py"]
```

Then:
```bash
docker-compose up -d --build
docker-compose logs -f bot
```

> Remember to set `POSTGRES_HOST=postgres` in `.env` when running in Docker network.

---

## VPS Deployment

Same as Raspberry Pi + systemd. Any Ubuntu/Debian VPS works. The bot uses <100MB RAM under normal load.

### Firewall

No inbound ports needed — the bot uses Telegram long-polling, which is outbound-only. Only PostgreSQL port 5432 needs to be open locally (not publicly).

---

## Monitoring

### Check bot is alive

```bash
sudo systemctl status pablito
```

### Restart after crash

systemd handles this automatically with `Restart=always`. Manual restart:

```bash
sudo systemctl restart pablito
```

### Watch logs

```bash
journalctl -u pablito -n 100 -f
```

### Check PostgreSQL

```bash
docker-compose ps
docker-compose logs -f postgres
```

---

## Updating

```bash
git pull origin main
uv sync
sudo systemctl restart pablito
```

---

## Backup

### Database backup

```bash
# Manual
docker exec pablo-postgres pg_dump -U corridor_admin corridor > backup_$(date +%Y%m%d).sql

# Automated cron (daily at 02:00)
# Add to crontab: crontab -e
0 2 * * * docker exec pablo-postgres pg_dump -U corridor_admin corridor > /home/pi/backups/corridor_$(date +\%Y\%m\%d).sql
```

### Restore

```bash
docker exec -i pablo-postgres psql -U corridor_admin corridor < backup_20260418.sql
```

---

## Timezone

Reminder times in `src/reminders.py` use the **server's local time**. If your server runs UTC but your corridor is in Amsterdam (CET/CEST = UTC+1/+2), adjust:

```python
# src/reminders.py
REMINDER_TIMES = [
    time(9, 0),   # 10:00 CET (UTC+1)
    time(17, 0),  # 18:00 CET
]
```

Or set the server timezone:
```bash
sudo timedatectl set-timezone Europe/Amsterdam
```
