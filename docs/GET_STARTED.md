# Getting Started

This guide is for first-time setup. It covers everything from creating a Telegram bot to having Pablito running for your corridor.

---

## Before You Begin

You need:
- A Linux/macOS/Windows machine (or a Raspberry Pi) that stays online
- Docker Desktop (or Docker Engine + Docker Compose)
- Python 3.12+ and [uv](https://docs.astral.sh/uv/)
- A Telegram account
- Your corridor group on Telegram

---

## Part 1 — Create the Telegram Bot

### 1.1 Talk to @BotFather

1. Open Telegram
2. Search for `@BotFather` (verified blue checkmark)
3. Send `/newbot`
4. Choose a name: e.g. `Pablito Corridor Manager`
5. Choose a username (must end in `bot`): e.g. `pablito_corridor_bot`
6. Copy the token — it looks like: `1234567890:ABCdefGHIjklMNOpqrsTUVwxyz`

Keep this token secret. Anyone with it can control your bot.

### 1.2 Configure Bot Privacy (important for groups)

Still in @BotFather:
1. Send `/mybots`
2. Select your bot
3. → **Bot Settings** → **Group Privacy**
4. Turn it **OFF** — otherwise the bot can't see group messages

### 1.3 Add the Bot to Your Group

1. Open your corridor Telegram group
2. Tap the group name → Edit → Add Member
3. Search for your bot's username and add it

### 1.4 Get the Group Chat ID

1. Send any message in the group (e.g., "test")
2. In a browser, visit:
   ```
   https://api.telegram.org/bot<YOUR_TOKEN>/getUpdates
   ```
3. Find `"chat":{"id":-1001234567890}` in the JSON
4. Copy the negative number — that's your `TELEGRAM_CHAT_ID`

---

## Part 2 — Set Up the Project

### 2.1 Clone the Repository

```bash
git clone https://github.com/your-username/pablo-the-corridor-manager
cd pablo-the-corridor-manager
```

### 2.2 Install uv (if not already)

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
source ~/.bashrc  # or restart your terminal
```

Verify: `uv --version`

### 2.3 Configure Environment

```bash
cp .env.example .env
```

Open `.env` and fill in:

```env
# Required
TELEGRAM_BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
TELEGRAM_CHAT_ID=-1001234567890
POSTGRES_PASSWORD=choose_a_strong_password_here

# Optional — defaults are fine for most setups
POSTGRES_DB=corridor
POSTGRES_USER=corridor_admin
POSTGRES_HOST=localhost
LOG_LEVEL=INFO
```

Save and close.

### 2.4 Start PostgreSQL

```bash
docker-compose up -d
```

This starts:
- PostgreSQL on port 5432
- pgAdmin (optional web UI) on port 5050

Wait 15 seconds for the database to initialize.

### 2.5 Install Python Dependencies

```bash
uv sync
```

This reads `pyproject.toml`, creates a `.venv`, and installs everything. No manual `pip install` or `venv` activation needed.

### 2.6 Initialize the Database

```bash
uv run python scripts/populate_db.py
```

This creates:
- All 22 task type definitions (toilets, showers, kitchen, etc.)
- 3 test users (Alice, Bob, Charlie)
- The current week with task instances

### 2.7 Verify the Setup

```bash
uv run python scripts/test_setup.py
```

You should see all green ✅. If anything fails, see [TROUBLESHOOTING.md](TROUBLESHOOTING.md).

---

## Part 3 — First Run

### 3.1 Start the Bot

```bash
make start
# or: uv run python src/bot.py
```

You should see:
```
✅ Reminders scheduled: Days [1, 4], Times: ['10:00', '18:00']
✅ Week rollover scheduled: Check time: 23:59 daily
INFO - Starting Pablito's Corridor Manager Bot...
INFO - Application started
```

### 3.2 Test in Telegram

1. **In the group:** send `/start` — bot should welcome you
2. **In the group:** send `/status` — should show this week's task list
3. **In private chat with the bot:** send `/start`, then tap **✅ Complete Task**

### 3.3 Have Corridor Mates Register

Each person in your corridor needs to:
1. Find the bot by its username in Telegram
2. Send `/start` to register
3. OR: they can send `/start` in the group too

---

## Part 4 — Remove Test Data

Once you've verified everything works, remove the test users:

```bash
make reset
make populate
```

> ⚠️ `make reset` wipes everything. Only do this before going live, not after people start using it.

If you only want to remove test users (Alice, Bob, Charlie) without resetting:
```bash
docker exec -it pablo-postgres psql -U corridor_admin -d corridor
DELETE FROM people WHERE name IN ('Alice', 'Bob', 'Charlie');
```

---

## Part 5 — Keep It Running

For persistent deployment (bot survives reboots), see [DEPLOYMENT.md](DEPLOYMENT.md).

For everyday admin tasks, see [ADMIN_GUIDE.md](ADMIN_GUIDE.md).

---

## Summary Checklist

- [ ] Created bot via @BotFather
- [ ] Disabled group privacy for bot
- [ ] Added bot to corridor group
- [ ] Got `TELEGRAM_CHAT_ID`
- [ ] Configured `.env`
- [ ] Started PostgreSQL (`docker-compose up -d`)
- [ ] Installed dependencies (`uv sync`)
- [ ] Populated database (`make populate`)
- [ ] Verified setup (`scripts/test_setup.py`)
- [ ] Bot running and responding
- [ ] All corridor mates registered via `/start`
- [ ] Test users removed
- [ ] Set up systemd/persistent runner (see DEPLOYMENT.md)
