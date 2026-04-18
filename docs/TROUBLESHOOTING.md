# Troubleshooting

---

## Bot Won't Start

### "TELEGRAM_BOT_TOKEN is required"
Your `.env` file is missing or incomplete.

```bash
# Check if .env exists
ls -la .env

# Create from template
cp .env.example .env
# Then edit with your token
```

### "connection refused" / database error at startup

PostgreSQL isn't running.

```bash
docker-compose ps            # Check container status
docker-compose up -d         # Start it
docker-compose logs postgres # Check for errors
```

Wait 10–15 seconds after starting PostgreSQL before launching the bot.

### Bot starts but crashes immediately

Check logs for the actual error. Most common causes:
- Wrong `TELEGRAM_BOT_TOKEN` → verify with `curl https://api.telegram.org/bot<TOKEN>/getMe`
- Bad `TELEGRAM_CHAT_ID` → must be negative for groups (e.g. `-1001234567890`)
- Database credentials mismatch between `.env` and `docker-compose.yml`

---

## Bot Doesn't Respond

### In group chat
- Make sure you've added the bot to the group
- Verify `TELEGRAM_CHAT_ID` matches the group's chat ID exactly
- Bot doesn't need to be admin, but group privacy mode affects message visibility — disable privacy mode in @BotFather if needed

### In private chat
- Send `/start` first to register
- Check if the bot process is still running

### Commands show in BotFather but nothing happens
The bot process died. Restart it.

---

## "No active week found"

The current week doesn't exist in the database.

**If you just set up the bot:**
```bash
make populate
```

**If it's mid-deployment:**
The Sunday rollover may have failed (bot was down). See [ADMIN_GUIDE.md](ADMIN_GUIDE.md#manual-rollover).

**If week closed too early:**
The `deadline` field in the `weeks` table may be in the past. Check with pgAdmin or psql.

---

## Reminders Not Firing

1. Check that the bot is running — reminders only work while the process is alive
2. Verify timezone: the server clock determines when "Tuesday 10:00" fires. If your server is UTC and you want Amsterdam time (CET/CEST), adjust `REMINDER_TIMES` in `src/reminders.py` accordingly
3. Check logs for job queue errors

---

## Wrong Deadline / Week Closes on Wrong Day

The deadline day is controlled by `NEW_WEEK_DEADLINE_DAY` in `src/week_manager.py` (default: `6` = Sunday). If you changed it but existing weeks still have old deadlines, you need to update them manually or wait for the next rollover.

---

## Task Not Found When Completing

**"No pending tasks in X"** — All tasks in that category are already done. Use Amend if one was marked by mistake.

**Category not showing** — Verify the task type's `category` field matches a key in `CATEGORY_AMOUNTS` (`src/menus.py`).

---

## Duplicate Week Error

```
sqlalchemy.exc.IntegrityError: UNIQUE constraint failed: weeks.year, weeks.week_number
```

A week for this year/number already exists. The `create_new_week` function creates a duplicate. This can happen if rollover ran twice. Check and manually close/delete the duplicate:

```bash
docker exec -it pablo-postgres psql -U corridor_admin -d corridor
SELECT id, year, week_number, closed FROM weeks ORDER BY id;
-- Delete duplicate (keep the one with task instances)
DELETE FROM weeks WHERE id = <duplicate_id>;
```

---

## pgAdmin Can't Connect

1. Make sure `docker-compose up -d` is running
2. Visit `http://localhost:5050`
3. Login with `PGADMIN_EMAIL` / `PGADMIN_PASSWORD` from `.env`
4. Add server manually:
   - Host: `postgres` (container name)
   - Port: `5432`
   - Database: `corridor`
   - User/Password: from your `.env`

---

## Permission Denied on Scripts

```bash
chmod +x scripts/*.py
# Or use uv run directly:
uv run python scripts/populate_db.py
```

---

## uv Not Found

Install it:
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Then restart your shell or run `source ~/.bashrc`.

See [UV_SETUP.md](UV_SETUP.md) for full guide.

---

## Checking the Database Directly

```bash
docker exec -it pablo-postgres psql -U corridor_admin -d corridor

# Useful queries:
\dt                            -- list tables
SELECT * FROM people;          -- all users
SELECT * FROM weeks;           -- all weeks
SELECT count(*) FROM task_instances WHERE status='pending';
```
