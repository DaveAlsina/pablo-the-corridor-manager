# Architecture

Technical overview of how Pablito is structured internally.

---

## High-Level Overview

```
Telegram API
     │
     ▼
┌─────────────────────────────────────────────────────┐
│                    src/bot.py                       │
│              CorridorBot class                      │
│  • Registers all command handlers                   │
│  • Routes callback queries                          │
│  • Private/group chat enforcement                   │
│  • Group notification dispatch                      │
└────────┬──────────────┬──────────────┬──────────────┘
         │              │              │
         ▼              ▼              ▼
   src/handlers/   src/reminders.py  src/week_manager.py
   ├─ task_handlers   (scheduled jobs)  (week rollover)
   ├─ info_handlers
   └─ optout_handlers
         │
         ▼
   src/database.py ──► PostgreSQL
   src/models.py
```

---

## Module Responsibilities

### `src/bot.py` — CorridorBot
Entry point and routing layer. Does not contain business logic.

- Instantiates `Application` (python-telegram-bot)
- Registers `/command` handlers and `CallbackQueryHandler`
- Checks if action is private-only; redirects with button if not
- Calls `setup_reminders()` and `setup_week_rollover()` on startup
- `notify_group()` — helper to send messages to group chat
- Wrapper methods pass `is_private_chat` and `notify_group` to handlers that need them

### `src/handlers/task_handlers.py` — Task Actions
Handles the multi-step flows for completing, amending, and getting instructions.

- `handle_complete_flow(query, parts, notify_group_func)` — category → task → confirm
- `handle_amend_flow(query, parts, notify_group_func)` — undo a completion
- `handle_ask_flow(query, parts)` — show task instructions
- All actions are private-only; called only after `bot.py` validates the chat type

### `src/handlers/info_handlers.py` — Read-Only Info
Handles status, stats, task list, map, and opt-out list. Available in both group and private.

- `cmd_status` / `show_status_callback` — weekly overview with progress bars
- `cmd_tasks` / `show_tasks_callback` — all task types grouped by category
- `cmd_my_stats` / `show_stats_callback` — personal stats
- `cmd_show_map` / `show_map_callback` — sends corridor image
- `cmd_who_opted_out` / `show_whooptedout_callback` — exemption list

### `src/handlers/optout_handlers.py` — Opt-Out
Handles the `/optout` command and `optout:` callback flow.

### `src/menus.py` — Keyboard Builder
Creates all `InlineKeyboardMarkup` objects. Contains:
- `CATEGORY_AMOUNTS` — how many task slots per category per week
- `CATEGORY_EMOJIS` — emoji per category
- `create_main_menu(is_private)` — full or reduced menu
- `create_category_menu(action)` — category selection for complete/amend/ask
- `create_task_menu(category, action)` — task selection within a category

### `src/reminders.py` — Scheduler
Registers recurring APScheduler jobs via `python-telegram-bot`'s job queue.

- `setup_reminders(app, group_chat_id)` — called once at startup
- `send_reminder(app, group_chat_id)` — async, queries DB and sends message
- `get_week_deadline(week_number, year)` — utility for deadline calculation

### `src/week_manager.py` — Week Lifecycle
Manages the full week lifecycle.

- `setup_week_rollover(app, group_chat_id)` — registers daily check at 23:59
- `check_and_rollover_week(...)` — checks if deadline passed
- `perform_week_rollover(...)` — summary → close → new week
- `generate_week_summary(db, week)` — pure function, builds summary string
- `create_new_week(db, app, group_chat_id)` — creates Week + TaskInstances + announces
- `force_week_rollover(app, group_chat_id)` — manual trigger (not yet a bot command)

### `src/models.py` — Data Models
SQLAlchemy declarative models. See [DATABASE.md](DATABASE.md).

### `src/database.py` — DB Utilities
- `init_db()` — create all tables
- `drop_db()` — drop all tables
- `get_db()` — context manager returning a session
- `get_db_session()` — raw session (caller must close)

### `src/config.py` — Settings
Pydantic `BaseSettings` — loads from `.env`, validates types, exposes `settings` singleton.

---

## Callback Data Protocol

Button callbacks use a colon-separated string protocol:

```
action:sub_action:id
```

Examples:
```
menu                         → show main menu
status                       → show status
complete:categories          → show category list for completing
complete:category:kitchen    → show kitchen tasks for completing
complete:task:42             → complete task instance ID 42
amend:categories             → show category list for amending
ask:task:17                  → show instructions for task 17
optout:categories            → show opt-out category list
mystats                      → show my stats
whooptedout                  → show opt-out list
```

`handle_callback` in `bot.py` splits on `:`, reads `action = parts[0]`, and dispatches.

---

## Private vs Group Chat

```
Group chat: /status /tasks /whooptedout /help /menu /start
Private chat: all above + /mystats /map /optout

Action buttons that require private:
  complete, amend, ask, optout, mystats, map
```

When a private-only action is triggered from group chat, the bot responds with:
```
🔒 Complete is only available in private chat!
[💬 Open Private Chat]  ← button linking to t.me/botusername
```

---

## Job Queue

python-telegram-bot uses APScheduler internally. Jobs are registered as:

```python
job_queue.run_daily(callback, time=time(10, 0), days=(1,), name="reminder_1_10_0")
```

All jobs are in-memory — they are re-registered every time the bot starts. There is no persistence of scheduled jobs across restarts (but since they're daily/fixed-time this is fine).

---

## Dependency Stack

| Layer | Technology |
|---|---|
| Bot framework | python-telegram-bot 20.7 |
| Scheduler | APScheduler 3.10 (via PTB job queue) |
| ORM | SQLAlchemy 2.0 |
| DB | PostgreSQL 16 (Docker) |
| Settings | Pydantic Settings 2.1 |
| Migrations | Alembic 1.13 |
| Package manager | uv |
| Container | Docker Compose |
