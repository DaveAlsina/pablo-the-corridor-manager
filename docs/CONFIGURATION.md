# Configuration

All configuration is loaded from the `.env` file via Pydantic Settings (`src/config.py`).

---

## Quick Setup

```bash
cp .env.example .env
# Edit .env with your values
```

---

## Required Variables

| Variable | Example | Description |
|---|---|---|
| `TELEGRAM_BOT_TOKEN` | `123456:ABCdef...` | Token from [@BotFather](https://t.me/botfather) |
| `TELEGRAM_CHAT_ID` | `-1001234567890` | Your corridor group's chat ID |
| `POSTGRES_PASSWORD` | `s3cur3pass!` | PostgreSQL password |

### Getting `TELEGRAM_BOT_TOKEN`
1. Open Telegram → search `@BotFather`
2. Send `/newbot`
3. Follow prompts, copy the token

### Getting `TELEGRAM_CHAT_ID`
1. Add your bot to the group
2. Send any message in the group
3. Visit: `https://api.telegram.org/bot<TOKEN>/getUpdates`
4. Find `"chat":{"id":-1001234567890}` — that's your chat ID

---

## Optional Variables

| Variable | Default | Description |
|---|---|---|
| `POSTGRES_DB` | `corridor` | Database name |
| `POSTGRES_USER` | `corridor_admin` | Database user |
| `POSTGRES_HOST` | `localhost` | DB host (use `postgres` in Docker network) |
| `POSTGRES_PORT` | `5432` | DB port |
| `LOG_LEVEL` | `INFO` | Logging level (`DEBUG`, `INFO`, `WARNING`, `ERROR`) |
| `DEBUG` | `false` | Debug mode |
| `WEEK_DEADLINE_DAY` | `sunday` | Week deadline day name |
| `WEEK_DEADLINE_HOUR` | `12` | Deadline hour |
| `WEEK_DEADLINE_MINUTE` | `0` | Deadline minute |

---

## Complete `.env` Example

```env
# ===== REQUIRED =====
TELEGRAM_BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrsTUVwxyz
TELEGRAM_CHAT_ID=-1001234567890
POSTGRES_PASSWORD=choose_something_secure_here

# ===== DATABASE (optional) =====
POSTGRES_DB=corridor
POSTGRES_USER=corridor_admin
POSTGRES_HOST=localhost
POSTGRES_PORT=5432

# ===== APPLICATION (optional) =====
LOG_LEVEL=INFO
DEBUG=false

# ===== WEEK SETTINGS (optional) =====
WEEK_DEADLINE_DAY=sunday
WEEK_DEADLINE_HOUR=12
WEEK_DEADLINE_MINUTE=0
```

---

## pgAdmin (optional)

The Docker Compose file includes pgAdmin for database inspection:

| Variable | Default | Description |
|---|---|---|
| `PGADMIN_EMAIL` | `admin@corridor.local` | pgAdmin login email |
| `PGADMIN_PASSWORD` | `admin` | pgAdmin password |

Access at: `http://localhost:5050`

---

## In-Code Configuration

Some scheduling settings are currently configured as constants in source files rather than env vars. These can be changed directly:

**`src/reminders.py`:**
```python
REMINDER_DAYS = [1, 4]      # 0=Mon … 6=Sun
REMINDER_TIMES = [time(10, 0), time(18, 0)]
```

**`src/week_manager.py`:**
```python
NEW_WEEK_DEADLINE_DAY = 6    # 6=Sunday
ROLLOVER_CHECK_TIME = (23, 59)
```

Moving these to `.env` is planned for a future release.

---

## Docker vs Local Postgres Host

If running the bot **inside Docker** (same network as `postgres` container), set:
```env
POSTGRES_HOST=postgres
```

If running the bot **on your host machine** while PostgreSQL is in Docker:
```env
POSTGRES_HOST=localhost
```
