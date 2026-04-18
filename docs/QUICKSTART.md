# Quick Start

## 🚀 Get Running in 5 Minutes

### Prerequisites

```bash
python --version      # Must be 3.12+
docker --version
uv --version          # https://docs.astral.sh/uv/
```

No `uv`? Install it:
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

---

### Step 1 — Get a Telegram Bot Token

1. Open Telegram → search `@BotFather`
2. Send `/newbot` and follow prompts
3. Copy the token: `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`

### Step 2 — Get Your Group Chat ID

1. Add your bot to the corridor group
2. Send any message in the group
3. Visit: `https://api.telegram.org/bot<YOUR_TOKEN>/getUpdates`
4. Look for `"chat":{"id":-1001234567890}` — copy that number

### Step 3 — Configure

```bash
cp .env.example .env
```

Edit `.env`:
```env
TELEGRAM_BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrsTUVwxyz
TELEGRAM_CHAT_ID=-1001234567890
POSTGRES_PASSWORD=choose_something_secure
```

### Step 4 — Start Database

```bash
docker-compose up -d
# Wait 10 seconds for PostgreSQL to initialize
```

### Step 5 — Install Dependencies

```bash
uv sync
```

### Step 6 — Initialize Database

```bash
uv run python scripts/populate_db.py
```

Expected output:
```
INFO - Creating task types... ✅ 22 task types created
INFO - Creating test users...  ✅ 3 test users created
INFO - Creating current week... ✅ Week 16/2026 created
```

### Step 7 — Verify

```bash
uv run python scripts/test_setup.py
```

All checks should pass ✅.

### Step 8 — Start Pablito

```bash
make start
# or: uv run python src/bot.py
```

Output:
```
✅ Reminders scheduled: Days [1, 4], Times: ['10:00', '18:00']
✅ Week rollover scheduled: Check time: 23:59 daily
INFO - Starting Pablito's Corridor Manager Bot...
```

---

## Test It

In your Telegram group:
1. Send `/start` — bot welcomes you
2. Send `/status` — shows this week's tasks
3. Go to private chat with the bot → tap **✅ Complete Task** → pick a task

---

## Makefile Shortcuts

```bash
make help       # All available commands
make setup      # Steps 4+5 in one go
make start      # Run the bot
make populate   # Step 6
make test       # Step 7
make reset      # Wipe all data (⚠️ careful)
```

---

## Common Issues

| Problem | Fix |
|---|---|
| "connection refused" | `docker-compose up -d`, wait 15s |
| "No active week found" | `make populate` |
| Bot doesn't respond in group | Check `TELEGRAM_CHAT_ID` is correct |
| `uv: command not found` | Install uv (see above) |

→ More help: [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
